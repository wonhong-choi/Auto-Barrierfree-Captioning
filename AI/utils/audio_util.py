import random

import librosa
import torch
import torchaudio
from torchaudio import transforms


class AudioUtil:
    @staticmethod
    def open(audio_file):
        signal, sr = librosa.load(audio_file, sr=16000)
        signal = torch.tensor(signal)
        return signal, sr
    
    @staticmethod
    def rechannel(audio, new_channel):
        signal, sr = audio
        
        if signal.shape[0] == new_channel:
            return audio
        
        if new_channel == 1:
            re_signal = signal[:1, :]
        else:
            re_signal = torch.cat([signal, signal])
        
        return re_signal, sr
    
    @staticmethod
    def resample(audio, new_sr):
        signal, sr = audio
        
        if sr == new_sr:
            return audio

        num_channels = signal.shape[0]
        re_signal = torchaudio.transforms.Resample(sr, new_sr)(signal[:1, :])
        if num_channels > 1: # streo type
            re_sec_signal = torchaudio.transforms.Resample(sr, new_sr)(signal[1:, :])
            re_signal = torch.cat([re_signal, re_sec_signal])
        return re_signal, new_sr
    
    @staticmethod
    def pad_trunc(audio, max_ms):
        signal, sr = audio
        signal_len = signal.size()[-1]
        max_len = int(sr/1000 * max_ms)
        
        if signal_len > max_len: # trunc
            signal = signal[:, :max_len]
        
        elif signal_len < max_len: # pad
            pad_begin_len = random.randint(0, max_len - signal_len)
            pad_end_len = max_len - signal_len - pad_begin_len
            
            pad_begin = torch.zeros((1, pad_begin_len))
            pad_end = torch.zeros((1, pad_end_len))
            
            signal = torch.concat((pad_begin, signal, pad_end), dim=1)
            
        return signal, sr
            
    @staticmethod
    def time_shift(audio, shift_limit):
        sig, sr = audio
        sig_len = len(sig)
        shift_amt = int(random.random() * shift_limit * sig_len)
        return sig.roll(shift_amt), sr
    
    
    @staticmethod
    def spectrogram(audio, n_mels=64, n_fft=1024, hop_len=None):
        signal, sr = audio
        top_db = 80
        
        spec = transforms.MelSpectrogram(sample_rate=sr,
                                         n_fft=n_fft,
                                         hop_length=hop_len,
                                         n_mels=n_mels)(signal)
        spec = transforms.AmplitudeToDB(top_db=top_db)(spec)
        return spec
    
    @staticmethod
    def mask_spectrogram(spec, max_mask_pct=0.1, n_freq_masks=1, n_time_masks=1):
        _, n_mels, n_steps = spec.shape
        mask_value = spec.mean()
        aug_spec = spec
        
        freq_mask_param = max_mask_pct * n_mels
        for _ in range(n_freq_masks):
            aug_spec = transforms.FrequencyMasking(freq_mask_param)(aug_spec, mask_value)
        
        time_mask_param = max_mask_pct * n_steps
        for _ in range(n_time_masks):
            aug_spec = transforms.TimeMasking(time_mask_param)(aug_spec, mask_value)
        return aug_spec