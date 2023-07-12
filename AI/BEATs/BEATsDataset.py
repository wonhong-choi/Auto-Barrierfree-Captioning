import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import torch
from torch.utils.data import DataLoader, Dataset, random_split
import pytorch_lightning as pl

from utils.audio_util import AudioUtil
from configure import CFG


class BEATsDS(Dataset):
    def __init__(self, df, data_path):
        self.df = df                        # metadata dataframe
        self.data_path = str(data_path)     # data path
        self.duration = CFG.duration        # ms
        self.sr = CFG.sr                    # hz
        self.channel = 1                    # mono
        self.shift_pct = CFG.shift_pct
        
    
    def __len__(self):
        return len(self.df)
    
    
    def __getitem__(self, index):
        audio_file = self.data_path + "/" + self.df.loc[index, "filename"]
        label = self.df.loc[index, "target"]
        
        audio = AudioUtil.open(audio_file)
        audio = AudioUtil.resample(audio, self.sr)
        #audio = AudioUtil.rechannel(audio, self.channel)
        audio = AudioUtil.pad_trunc(audio, self.duration)
        audio = AudioUtil.time_shift(audio, self.shift_pct)
        
        padding_mask = torch.zeros_like(audio[0]).bool()
        
        return audio[0], padding_mask, label