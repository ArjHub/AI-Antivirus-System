"@author: NavinKumarMNK"
from torch.utils.data import DataLoader, Dataset
import pytorch_lightning as pl
import cv2
import torch
from utils import utils
import numpy as np
import pandas as pd

class ApiCallsDataset(Dataset):
    def __init__(self, annotation:str, data_dir_path:str):
        self.dataset = pd.read_csv(annotation)
        self.data_dir_path = data_dir_path
        
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, index:int):
        file_name = self.dataset.iloc[index, 1]
        label = self.dataset.iloc[index, 2]
        print(file_name, label)
        file_path = self.data_dir_path + file_name
        data = np.load(file_path)
        return data, label
    
if __name__ == '__main__':
    params = utils.config_parse('APICALLDATASET')
    data = ApiCallsDataset()