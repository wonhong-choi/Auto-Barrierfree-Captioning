import torch
import pandas as pd
import pytorch_lightning as pl
from pytorch_lightning import Trainer


from train import FT_BEATs, BEATsLDS

if __name__ == "__main__":
    base_checkpoint_path = "/home/wonhong/workspace/AIVLE/BigProject/Barrier-free-subtitles/ai/BEATs/models/BEATs_iter3_plus_AS2M.pt"
    checkpoint_path = "/home/wonhong/workspace/AIVLE/BigProject/Barrier-free-subtitles/ai/BEATs/models/finetuned/epoch=19-step=1600.ckpt"

    # data
    meta_df = pd.read_csv("/home/wonhong/workspace/AIVLE/BigProject/Barrier-free-subtitles/ai/datas/esc50_data/esc50.csv")
    data_path = "/home/wonhong/workspace/AIVLE/BigProject/Barrier-free-subtitles/ai/datas/esc50_data/esc-50_data"

    dataset = BEATsLDS(metadata=meta_df, data_path=data_path)

    # model & trainer
    model = FT_BEATs.load_from_checkpoint(checkpoint_path, base_checkpoint_path=base_checkpoint_path)
    trainer = Trainer(accelerator="gpu", devices=1)

    # prediction
    output = trainer.predict(model, dataloaders=dataset)
    
    print(output) # [batch, batch, ...], batch: tensor(probs of each label) * batch size