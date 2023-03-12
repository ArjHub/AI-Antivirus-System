"@author: NavinKumarMNK"
import os
import sys
if os.path.abspath('../../') not in sys.path:
    sys.path.append(os.path.abspath('../../'))
from torch.utils.data import random_split, Dataset, DataLoader
import pytorch_lightning as pl
import cv2
import torch
from utils import utils
import numpy as np
import pandas as pd

class ApiCallsDataset(Dataset):
    def __init__(self, annotation:str, data_dir_path:str):
        self.data_dir_path = utils.ROOT_PATH + data_dir_path
        self.dataset = pd.read_csv(self.data_dir_path + annotation)
        
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, index:int):
        file_name = self.dataset.iloc[index, 1] + '.npy'
        label = self.dataset.iloc[index, 2]
        print(file_name, label)
        file_path = self.data_dir_path + "samples/"+ file_name
        data = np.load(file_path)
        data = torch.tensor(data)
        return data, label

class ApiCallsDataModule(pl.LightningDataModule):
    def __init__(self, annotation, data_dir_path, batch_size, num_workers):
        self.batch_size = batch_size
        self.num_workers = num_workers 
        self.annotation = annotation
        self.data_dir = data_dir_path

    def setup(self):
        dataset = ApiCallsDataModule(self.annotation, self.data_dir)
        total_len = len(dataset)        
        val_len = int(0.1 * total_len)
        test_len = int(0.1 * total_len)
        train_len = total_len - val_len - test_len

        self.train_dataset, self.val_dataset, self.test_dataset = random_split(
            dataset, [train_len, val_len, test_len]
        )
    
    def train_dataloader(self):
        train_loader = DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers
        )
        return train_loader

    def val_dataloader(self):
        val_loader = DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers
        )
        return val_loader

    def test_dataloader(self):
        test_loader = DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers
        )
        return test_loader



if __name__ == '__main__':
    params = utils.config_parse('APICALLS_DATASET')
    print(ApiCallsDataset('label.csv', '/data/system_call/')[0])