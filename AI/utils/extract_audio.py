import os

import librosa
from pytube import YouTube

import matplotlib.pyplot as plt

#
# TODO:
#   test other codecs (eg. avi ...)
def extract_audio_from_file(filepath:str, sr:int=44100):
    """extract audio np.array(or tensor) from video/audio file.

    Args:
        filepath (str): video/audio file path
        sr (int, optional): sampling rate to extract. Defaults to 44100.
        is_video_file (bool, optional): if is_video_file then True, else False. Defaults to True.

    Return:
        audio_array (np.array | None): If the clip have any audio, else None
        sr (int): sampling rate
    """
    try:
        signal, sr = librosa.load(filepath, sr=sr)
    except FileNotFoundError as e:
        print("File Not Found.")
        signal = None
    except ValueError as e: # duration not exist
        print(e) 
        signal = None
    except Exception as e:
        print(e)
        signal = None
        pass
    return signal, sr


#
# TODO:
#   handling login required content
def download_audio_from_youtube_link(youtube_link:str, subtitles_code:str='kr'):
    """download audio from youtube link.

    Args:
        youtube_link (str): youtube video link
        file_extension (str, optional): video file extension for saving. Defaults to 'mp4'.

    Return:
        dst_name (str | None): absolute filepath of saved audio, If failed to download, then None
        subtitles: If video already has default subtitles on youtube video, else None
    """
    try:
        yt = YouTube(youtube_link) 
        audio_stream = yt.streams.filter(only_audio=True, mime_type="audio/mp4", adaptive=True).order_by('abr').last().download()
        dst_name = audio_stream[:-1] + "3"
        os.rename(audio_stream, dst_name) # mp4 to mp3
        default_uploaded_subtitles = yt.captions.get_by_language_code(subtitles_code)
    except Exception as e:
        # if video link is not accessible OR download failed, then RAISE ERROR
        print(e)
        raise Exception
    
    return dst_name, default_uploaded_subtitles.generate_srt_captions() if default_uploaded_subtitles is not None else None
    

if __name__ == "__main__":
    file_path = "/home/wonhong/workspace/AIVLE/BigProject/Barrier-free-subtitles/담배꽁초 줍는 기계로 하루에 얼마를 벌 수 있을까_....100만원 벌기 도전!!.mp4"
    arr, sr = extract_audio_from_file(file_path)
    if arr is not None:
        librosa.display.waveshow(arr, sr=sr)
        plt.show()
    else:
        print("error")