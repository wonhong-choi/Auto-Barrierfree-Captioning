import os
import sys
import datetime
import pytz
import joblib
import json

import numpy as np
import pandas as pd
import torch
import torchaudio
import pytorch_lightning as pl
from pytorch_lightning import Trainer
import tensorflow as tf
import whisper

from splitter.splitter import separate_soundtrack_file
from utils.extract_audio import download_audio_from_youtube_link
from utils.silence_removal import silence_removal
from BEATs.pred_dataset import BEATsPredLDS
from BEATs.train import FT_BEATs


with open("/home/wonhong/workspace/AIVLE/BigProject/Barrier-free-subtitles/ai/setting.json", "r") as f:
    FILE_PATHS = json.load(f)


class BarrierFreeCaptionCFG:
    # models, configure, and etc.
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    # splitter
    splitter_sr = 44100
    splitter_model = FILE_PATHS["splitter_model"]
    
    # stt
    stt_model_size = "large"
    stt_model = whisper.load_model(stt_model_size, device=device)
    stt_model.eval()
    stt_sr = 16000
    
    # music
    music_sr = 44100
    music_silence_removal_st_win = 0.5
    music_silence_removal_st_step = 0.5
    music_silence_removal_smoothing_window = 7.5  # default : 0.5
    music_silence_removal_weight = 0.65            # default : 0.5

    # sfx
    sfx_batchsize = 20
    sfx_sr = 16000
    silence_removal_st_win = 0.05
    silence_removal_st_step = 0.05
    silence_removal_smoothing_window = 0.5  # default : 0.5
    silence_removal_weight = 0.5            # default : 0.5
    sfx_label2eng_sound = joblib.load(FILE_PATHS["sfx_label2eng_sound"])
    sfx_label2kor_sound = joblib.load(FILE_PATHS["sfx_label2kor_sound"])
    base_checkpoint_path = FILE_PATHS["base_checkpoint_path"]
    sfx_checkpoint_path = FILE_PATHS["sfx_checkpoint_path"]
    sfx_model = FT_BEATs.load_from_checkpoint(sfx_checkpoint_path, base_checkpoint_path=base_checkpoint_path)
    sfx_model.eval()
    sfx_trainer = Trainer(accelerator="gpu", devices=1, logger=False)
    sfx_confidence_threshold = 0.90
    
    sfx_labels = set(range(0, 50)) - set([35, 39, 5, 7, 25])
    
    # for SVM method
    sfx_max_ms = 5000
    
    # for sliding window
    FRAME_LENGTH = 1000 / 1000
    max_ms = int(FRAME_LENGTH * 1000)
    HOP_LENGTH = 700 / 1000


class BarrierFreeCaptionGenerator:
    def __init__(self):
        pass
    
    # for DEBUG
    def make_caption_from_file_direct_stt(self, filepath:str, language:str="ko") -> str:
        # stt - resampling
        origin_audio, sr = torchaudio.load(filepath)
        resampled_audio = torchaudio.functional.resample(origin_audio, sr, BarrierFreeCaptionCFG.stt_sr)[0]
        result = BarrierFreeCaptionCFG.stt_model.transcribe(audio=resampled_audio)
        stt_segments = [self._to_segment(chunk['start'], chunk['end'], chunk['text'], is_sfx=False) for chunk in result['segments']]
        
        seperated_audios = self._separate_audio_from_file(filepath)
        sfx_segments = self._classify_sfx_brute_force(seperated_audios["sfx"], language=language)

        merged_segments = self._merge_segments(stt_segments, sfx_segments)
        
        return self._generate_vtt(merged_segments)
        
    
    def make_caption_from_file(self, filepath:str, language:str='ko') -> str:
        """Generate caption

        Args:
            filepath (str): mp4 file path.
            language (str, optional): caption language which should be 'ko' or 'en'. Defaults to 'ko'.

        Returns:
            str: caption string
        """
        # audio separation
        seperated_audios = self._separate_audio_from_file(filepath)
        
        # stt
        stt_segments = self._stt(seperated_audios["speech"])
        
        # sfx
        #sfx_segments = self._classify_sfx(seperated_audios["sfx"], language=language)
        sfx_segments = self._classify_sfx_brute_force(seperated_audios["sfx"], language=language)
        #sfx_segments = self._classify_sfx_brute_force_with_nonsilence(seperated_audios["sfx"], language=language)
        
        # music
        music_segments = None
        #music_segments = self._classify_music(seperated_audios["music"])
        
        # merge
        merged_segments = self._merge_segments(stt_segments, sfx_segments)
        merged_segments = self._merge_segments(merged_segments, music_segments)
        
        return self._generate_vtt(merged_segments)


    def make_caption_from_youtube_link(self, link:str, default_subtitle_code:str):
        try:
            downloaded_filepath, default_caption = download_audio_from_youtube_link(youtube_link=link, subtitles_code=default_subtitle_code)
            
            if downloaded_filepath is None:
                raise Exception("fail to download")
            else:
                return self.make_caption_from_file(downloaded_filepath, default_caption)
        
        except Exception as e:
            print(e)
            
            
    def _generate_vtt(self, merged_segments):
        vtt_txt = "WEBVTT\n\n"
        
        idx = 1
        for seg in merged_segments:
            vtt_txt += str(idx) + "\n"
            idx += 1
            vtt_txt += seg['start'][:-3] + " --> " + seg['end'][:-3] + "\n"
            vtt_txt += seg['text'] + "\n\n"
            
        return vtt_txt[:-1]

    
    def _separate_audio_from_file(self, filepath):
        """mrx seperate audio

        Args:
            filepath (str): filepath

        Returns:
            dict: seprated_soundtrack with key('speech', 'music', 'sfx') and values(torch.tensor(s))
        """
        return separate_soundtrack_file(filepath, model_path=BarrierFreeCaptionCFG.splitter_model, device=BarrierFreeCaptionCFG.device)
        
    
    def _stt(self, audio:torch.Tensor):
        # STT
        # resampling
        resampled_audio = torchaudio.functional.resample(audio, BarrierFreeCaptionCFG.splitter_sr, BarrierFreeCaptionCFG.stt_sr)[0]
        result = BarrierFreeCaptionCFG.stt_model.transcribe(audio=resampled_audio)
        for seg in result['segments']:
            if seg['text'] == "music":
                seg['text'] = "[ ♫ ]"
        return [self._to_segment(chunk['start'], chunk['end'], chunk['text'], is_sfx=False) for chunk in result['segments']]
    
    
    def _classify_music(self, audio):
        # classifier model run
        resampled_audio = torchaudio.functional.resample(audio, BarrierFreeCaptionCFG.splitter_sr, BarrierFreeCaptionCFG.music_sr)[0].cpu()
        
        # step 1 : silence_removal
        nonsilence_intervals = silence_removal(resampled_audio,
                                               sampling_rate=BarrierFreeCaptionCFG.music_sr,
                                               st_win=BarrierFreeCaptionCFG.music_silence_removal_st_win,
                                               st_step=BarrierFreeCaptionCFG.music_silence_removal_st_step,
                                               smooth_window=BarrierFreeCaptionCFG.music_silence_removal_smoothing_window,
                                               weight=BarrierFreeCaptionCFG.music_silence_removal_weight)
        
        if nonsilence_intervals is None:
            return None
        
        return [self._to_segment(start, end, "[ ♫ ]", is_sfx=False) for start, end in nonsilence_intervals]
        
    
    
    def _classify_sfx(self, audio, language):
        # classifier model run
        resampled_audio = torchaudio.functional.resample(audio, BarrierFreeCaptionCFG.splitter_sr, BarrierFreeCaptionCFG.stt_sr)[0].cpu()
        # step 1 : silence_removal
        nonsilence_intervals = silence_removal(resampled_audio,
                                               sampling_rate=BarrierFreeCaptionCFG.sfx_sr,
                                               st_win=BarrierFreeCaptionCFG.silence_removal_st_win,
                                               st_step=BarrierFreeCaptionCFG.silence_removal_st_step,
                                               smooth_window=BarrierFreeCaptionCFG.silence_removal_smoothing_window,
                                               weight=BarrierFreeCaptionCFG.silence_removal_weight)

        # step 2 : classify each interval
        if nonsilence_intervals is None:
            return None

        dataloader = BEATsPredLDS(resampled_audio,
                                  BarrierFreeCaptionCFG.sfx_sr,
                                  nonsilence_intervals,
                                  max_ms=min(BarrierFreeCaptionCFG.sfx_max_ms, max([(end-start)*1000 for start, end in nonsilence_intervals])))
        output = BarrierFreeCaptionCFG.sfx_trainer.predict(BarrierFreeCaptionCFG.sfx_model, dataloaders=dataloader)
        
        result = []
        interval_idx = 0
        for batch in output:
            #pred = torch.argmax(batch, dim=1).tolist()
            prob, pred = batch.max(dim=1)
            
            for p, label in zip(prob, pred):
                if p.item()>=BarrierFreeCaptionCFG.sfx_confidence_threshold:
                    result += [(nonsilence_intervals[interval_idx][0], nonsilence_intervals[interval_idx][1], label.item())]
                interval_idx += 1
                
        return [self._to_segment(start, end, BarrierFreeCaptionCFG.sfx_label2eng_sound[label] if language=="en"\
            else BarrierFreeCaptionCFG.sfx_label2kor_sound[label], is_sfx=True) for start, end, label in result]
        #return [self._to_segment(start, end, BarrierFreeCaptionCFG.sfx_index2label_dict[label]) for [start, end], label in zip(nonsilence_intervals, pred)]
    
    
    def _classify_sfx_brute_force(self, audio, language):
        # classifier model run
        resampled_audio = torchaudio.functional.resample(audio, BarrierFreeCaptionCFG.splitter_sr, BarrierFreeCaptionCFG.stt_sr)[0].cpu()
        
        # step 1 : sliding window
        seek = 0
        intervals = []
        while seek < resampled_audio.size()[0] // BarrierFreeCaptionCFG.sfx_sr:
            if (seek + BarrierFreeCaptionCFG.FRAME_LENGTH)*BarrierFreeCaptionCFG.sfx_sr < resampled_audio.size()[0]:
                intervals.append([seek, seek+BarrierFreeCaptionCFG.FRAME_LENGTH])
            seek += BarrierFreeCaptionCFG.HOP_LENGTH
        dataloader = BEATsPredLDS(resampled_audio,
                                  BarrierFreeCaptionCFG.sfx_sr,
                                  intervals,
                                  max_ms=BarrierFreeCaptionCFG.max_ms)
        output = BarrierFreeCaptionCFG.sfx_trainer.predict(BarrierFreeCaptionCFG.sfx_model, dataloaders=dataloader)
        
        # threshold
        candidates = []
        interval_idx = 0
        for batch in output:
            #pred = torch.argmax(batch, dim=1).tolist()
            prob, pred = batch.max(dim=1)
            
            for p, label in zip(prob, pred):
                if p.item()>=BarrierFreeCaptionCFG.sfx_confidence_threshold and label.item() in BarrierFreeCaptionCFG.sfx_labels:
                    candidates += [[intervals[interval_idx][0], intervals[interval_idx][1], label.item()]]
                    print(p.item(), label.item())
                interval_idx += 1
                
        # merge intervals
        result = []
        candidates.sort(key=lambda x: x[0])
        if candidates:
            prev = candidates[0]
            idx = 1
            while idx < len(candidates):
                cur_start, cur_end, cur_label = candidates[idx]
                if (prev[1] < cur_start) or (prev[1] >= cur_start and cur_label != prev[2]):
                    result.append(prev[:])
                    prev = candidates[idx]
                elif prev[1] >= cur_start and cur_label == prev[2]:
                    prev[1] = max(prev[1], cur_end)
                idx += 1
            result.append(prev[:])
            return [self._to_segment(start, end, BarrierFreeCaptionCFG.sfx_label2eng_sound[label] if language=="en"\
                else BarrierFreeCaptionCFG.sfx_label2kor_sound[label], is_sfx=True) for start, end, label in result]
        else:
            return None
    
    
    def _classify_sfx_brute_force_with_nonsilence(self, audio, language):
        # classifier model run
        resampled_audio = torchaudio.functional.resample(audio, BarrierFreeCaptionCFG.splitter_sr, BarrierFreeCaptionCFG.stt_sr)[0].cpu()
        # step 1 : Get silence_removal
        nonsilence_intervals = silence_removal(resampled_audio,
                                               sampling_rate=BarrierFreeCaptionCFG.sfx_sr,
                                               st_win=BarrierFreeCaptionCFG.silence_removal_st_win,
                                               st_step=BarrierFreeCaptionCFG.silence_removal_st_step,
                                               smooth_window=BarrierFreeCaptionCFG.silence_removal_smoothing_window,
                                               weight=BarrierFreeCaptionCFG.silence_removal_weight)
        
        # step 2 : nonsilence_intervals with sliding window
        # frame_length, hop_length
        seek = 0
        intervals = []
        for start, end in nonsilence_intervals:
            seek = start
            while seek < end:
                if (seek + BarrierFreeCaptionCFG.FRAME_LENGTH) < end:
                    intervals.append([seek, seek+BarrierFreeCaptionCFG.FRAME_LENGTH])
                seek += BarrierFreeCaptionCFG.HOP_LENGTH
        
        dataloader = BEATsPredLDS(resampled_audio,
                                  BarrierFreeCaptionCFG.sfx_sr,
                                  intervals,
                                  max_ms=BarrierFreeCaptionCFG.max_ms)
        output = BarrierFreeCaptionCFG.sfx_trainer.predict(BarrierFreeCaptionCFG.sfx_model, dataloaders=dataloader)
        
        # threshold
        candidates = []
        interval_idx = 0
        for batch in output:
            #pred = torch.argmax(batch, dim=1).tolist()
            prob, pred = batch.max(dim=1)
            
            for p, label in zip(prob, pred):
                if p.item()>=BarrierFreeCaptionCFG.sfx_confidence_threshold and label.item() in BarrierFreeCaptionCFG.sfx_labels:
                    candidates += [[intervals[interval_idx][0], intervals[interval_idx][1], label.item()]]
                interval_idx += 1
                
        # merge intervals
        result = []
        candidates.sort(key=lambda x: x[0])
        if candidates:
            prev = candidates[0]
            idx = 1
            while idx < len(candidates):
                cur_start, cur_end, cur_label = candidates[idx]
                if (prev[1] < cur_start) or (prev[1] >= cur_start and cur_label != prev[2]):
                    result.append(prev[:])
                    prev = candidates[idx]
                elif prev[1] >= cur_start and cur_label == prev[2]:
                    prev[1] = max(prev[1], cur_end)
                idx += 1
            result.append(prev[:])
            return [self._to_segment(start, end, BarrierFreeCaptionCFG.sfx_label2eng_sound[label] if language=="en"\
                else BarrierFreeCaptionCFG.sfx_label2kor_sound[label], is_sfx=True) for start, end, label in result]
        else:
            return None
        

    def _merge_segments(self, segments_a:list, segments_b:list):
        if segments_a is not None and segments_b is not None:
            merged_segments = segments_a + segments_b
        elif segments_a is not None:
            merged_segments = segments_a
        elif segments_b is not None:
            merged_segments = segments_b
        merged_segments.sort(key=lambda seg : seg['start'])
        return merged_segments
        
        
    def _to_segment(self, start, end, text, is_sfx=False) -> dict:
        return {
            'start' : datetime.datetime.fromtimestamp(float(start), tz=pytz.UTC).strftime('%H:%M:%S.%f'),
            'end' : datetime.datetime.fromtimestamp(float(end), tz=pytz.UTC).strftime('%H:%M:%S.%f'),
            'text' : "[ " + text.strip() + " ]" if is_sfx else text.strip()
        }
    

# if __name__ == "__main__":
#     bfcg = BarrierFreeCaptionGenerator()
    
#     for i in range(2, 2+1):
#         input_path = "/home/wonhong/workspace/AIVLE/BigProject/outputs/fin" + str(i) + ".mp4"
#         output_path = "./outputs/"
#         test_caption = bfcg.make_caption_from_file(filepath=input_path, language="en")
    
#         with open(input_path[:-4] + ".vtt", mode="w", encoding="utf-8") as text_file:
#             text_file.write(test_caption)