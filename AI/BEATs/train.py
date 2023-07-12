import os
import sys
sys.path.append(os.path.dirname(__file__))
import math
import random
from pathlib import Path
from typing import Any, List, Union

import numpy as np
import pandas as pd
import librosa
import mlflow
import torch
from torch.utils.data import DataLoader, random_split
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
from pytorch_lightning import Trainer
from pytorch_lightning.utilities.types import EVAL_DATALOADERS, STEP_OUTPUT, TRAIN_DATALOADERS
from pytorch_lightning.loggers import MLFlowLogger

from configure import CFG
from BEATsBase import *
from BEATsDataset import BEATsDS

    
class BEATsLDS(pl.LightningDataModule):
    def __init__(self, metadata:pd.DataFrame, data_path:str):
        super().__init__()
        
        self.dataset = BEATsDS(metadata, data_path)
        n_train = round(len(self.dataset) * CFG.train_ratio)
        n_val = len(self.dataset) - n_train

        self.train_dataset, self.val_dataset = random_split(self.dataset, [n_train, n_val])
        
        
    def prepare_data(self) -> None:
        pass
    
    
    def train_dataloader(self) -> TRAIN_DATALOADERS:
        return DataLoader(self.train_dataset, batch_size=CFG.batch_size, shuffle=True, num_workers=-1)
    
    
    def val_dataloader(self) -> EVAL_DATALOADERS:
        return DataLoader(self.val_dataset, batch_size=CFG.batch_size)
    
    
    def test_dataloader(self) -> EVAL_DATALOADERS:
        return DataLoader(self.val_dataset, batch_size=CFG.batch_size)
    
    # not implemented, just for DEBUG
    def predict_dataloader(self) -> EVAL_DATALOADERS:
        return DataLoader(self.dataset, batch_size=CFG.batch_size, shuffle=False)
    

class FT_BEATs(pl.LightningModule):
    def __init__(self, base_checkpoint_path, dropout=CFG.dropout, n_labels=CFG.n_labels):
        super(FT_BEATs, self).__init__()
        checkpoint = torch.load(base_checkpoint_path)
        
        cfg = BEATsConfig(checkpoint['cfg'])
        self.BEATs = BEATs(cfg)
        self.BEATs.load_state_dict(checkpoint['model'])
        self.dropout = nn.Dropout(p=dropout)
        self.linear = nn.Linear(768, n_labels)
        
        self.loss_fn = nn.CrossEntropyLoss()
        
    
    def forward(self, x, padding_mask):
        x, _ = self.BEATs.extract_features(x, padding_mask)
        x = x.mean(dim=1)
        x = self.dropout(x)
        x = self.linear(x)
        x = torch.softmax(x, dim=1)
        return x
    
    
    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=CFG.lr, betas=(CFG.beta1, CFG.beta2))
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=CFG.cosine_T_max, eta_min=CFG.cosine_eta_min)
        return [optimizer], [scheduler]
    
    
    def on_train_start(self) -> None:
        self.log_dict({k:v for k, v in CFG.__dict__.items() if "__" not in k}, prog_bar=False, logger=True)
    
    
    def training_step(self, batch, batch_idx):
        inputs, masks, labels = batch[0], batch[1], batch[2]
        y_pred = self(inputs, masks)
        loss = self.loss_fn(y_pred, labels)
        acc = (torch.argmax(y_pred, dim=1) == labels).float().mean()
        
        self.log("train_loss", loss.item(), True, True, False, True)
        self.log("train_acc", acc.item(), True, True, False, True)
        return {"loss":loss, "train_acc":acc}
    
    
    def validation_step(self, batch, batch_idx):
        inputs, masks, labels = batch[0], batch[1], batch[2]
        y_pred = self(inputs, masks)
        loss = self.loss_fn(y_pred, labels)
        acc = (torch.argmax(y_pred, dim=1) == labels).float().mean()
        
        self.log("val_loss", loss.item(), True, True, False, True)
        self.log("val_acc", acc.item(), True, True, False, True)
        #self.logger.log_metrics(metrics)
        return {"val_loss":loss, "val_acc":acc}
    
    
    def test_step(self, batch, batch_idx):
        inputs, masks, labels = batch[0], batch[1], batch[2]
        y_pred = self(inputs, masks)
        loss = self.loss_fn(y_pred, labels)
        acc = (torch.argmax(y_pred, dim=1) == labels).float().mean()
        self.log("loss", loss.item(), True, True, False, True)
        self.log("test_acc", acc.item(), True, True, False, True)
        return {"test_loss":loss, "test_acc":acc}
    
    # not implemented, just for DEBUG
    def predict_step(self, batch: Any, batch_idx: int, dataloader_idx: int = 0) -> Any:
        inputs, masks = batch[0], batch[1]
        return self(inputs, masks)


# if __name__ == "__main__":
#     meta_df = pd.read_csv("/home/wonhong/workspace/AIVLE/BigProject/Barrier-free-subtitles/ai/datas/esc50_data/esc50.csv")
#     data_path = "/home/wonhong/workspace/AIVLE/BigProject/Barrier-free-subtitles/ai/datas/esc50_data/esc-50_data"
#     base_checkpoint_path = "/home/wonhong/workspace/AIVLE/BigProject/Barrier-free-subtitles/ai/BEATs/models/BEATs_iter3_plus_AS2M.pt"
    
#     dataset = BEATsLDS(metadata=meta_df, data_path=data_path)
    
#     model = FT_BEATs(base_checkpoint_path)
    
#     callbacks = [
#         ModelCheckpoint("/home/wonhong/workspace/AIVLE/BigProject/Barrier-free-subtitles/ai/BEATs/models/finetuned2",
#                         monitor="val_loss",
#                         verbose=True,
#                         save_top_k=3,
#                         mode="min"),
#         EarlyStopping(monitor="val_loss", min_delta=CFG.min_delta, patience=CFG.patience, verbose=True, mode="min")
#     ]
    
#     mlflow_logger = MLFlowLogger(experiment_name="BEATs",
#                                  tracking_uri="sqlite:///barrier_free_test.sqlite")

#     trainer = Trainer(logger=mlflow_logger, max_epochs=CFG.epochs, callbacks=callbacks, accelerator="gpu", devices=1)
    
#     trainer.fit(model, datamodule=dataset)