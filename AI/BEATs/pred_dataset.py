import os
import sys
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from pytorch_lightning.utilities.types import EVAL_DATALOADERS
import torch
from torch.utils.data import DataLoader, Dataset, random_split
import pytorch_lightning as pl

from utils.audio_util import AudioUtil
from configure import CFG

BEATs_PRED_LDS_BATCHSIZE = 20

class BEATsPredDS(Dataset):
    def __init__(self, signal, sr, max_ms, nonsilent_intervals):
        self.signal = signal
        self.sr = sr
        self.max_ms = max_ms
        self.nonsilent_intervals = nonsilent_intervals
        
    
    def __len__(self):
        return len(self.nonsilent_intervals)
    
    
    def __getitem__(self, index):
        start, end = int(self.nonsilent_intervals[index][0] * self.sr), int(self.nonsilent_intervals[index][1] * self.sr)
        audio = self.signal[start:end+1]
        audio = audio.view([1, -1])
        audio = AudioUtil.rechannel((audio, self.sr), 1)
        audio, sr = AudioUtil.pad_trunc(audio, self.max_ms)
        audio = audio.view(-1)
        padding_mask = torch.zeros_like(audio).bool()
        
        return audio, padding_mask


class BEATsPredLDS(pl.LightningDataModule):
    def __init__(self, signal, sr, nonsilence_intervals, max_ms):
        super().__init__()
        self.BEATs_pred_dataset = BEATsPredDS(signal, sr, max_ms, nonsilence_intervals)
        
    def prepare_data(self) -> None:
        pass
    
    
    def predict_dataloader(self) -> EVAL_DATALOADERS:
        return DataLoader(self.BEATs_pred_dataset,
                          batch_size=BEATs_PRED_LDS_BATCHSIZE,
                          shuffle=False)