import os
import glob
import numpy as np
from fairseq.data import FairseqDataset
import sys
import random
import math
import torch
import torchaudio
from torch.utils.data import Dataset
import pickle

class pickleDataset(Dataset):

    def __init__(self,data_path,target,hp):
        self.data_list= [x for x in glob.glob(os.path.join(data_path,target+'*' ,'**'), recursive=True) if not os.path.isdir(x)]     
        self.frame_num = hp.train.frame_num
        self.fs = int(hp.train.fs/16)
                
    def __getitem__(self, index):
        data_item = self.data_list[index]
    
        with open(data_item, 'rb') as f:
            data = pickle.load(f)
       
        tgt_wav_len = data["clean_wav_len"]
         
        frame_num = self.frame_num
        time_len = data["audio_data_Real"][0].shape[1]
        wav_len = data["audio_wav"][0].shape[1]
        
        # Not en
        if data["audio_data_Real"][0].shape[1]-frame_num <= 0 :
            empty_in_r = torch.zeros(data["audio_data_Real"][0].shape[0],frame_num)
            empty_in_r[:,:time_len]=data["audio_data_Real"][0]
            data["audio_data_Real"][0] = empty_in_r 
            empty_in_i = torch.zeros(data["audio_data_Imagine"][0].shape[0],frame_num)
            empty_in_i[:,:time_len]=data["audio_data_Imagine"][0]
            data["audio_data_Imagine"][0] = empty_in_i
            
            empty_in_r = torch.zeros(data["audio_data_Real"][1].shape[0],frame_num)
            empty_in_r[:,:time_len]=data["audio_data_Real"][1]
            data["audio_data_Real"][1] = empty_in_r 
            empty_in_i = torch.zeros(data["audio_data_Imagine"][1].shape[0],frame_num)
            empty_in_i[:,:time_len]=data["audio_data_Imagine"][1]
            data["audio_data_Imagine"][1] = empty_in_i
    
            empty_in_wav = torch.zeros(data["audio_wav"][0].shape[0],frame_num*256*self.fs-1)
            empty_in_wav[:,:wav_len]=data["audio_wav"][0]
            data["audio_wav"][0] = empty_in_wav
            
            empty_tgt_wav = torch.zeros(data["audio_wav"][1].shape[0],frame_num*256*self.fs-1)
            empty_tgt_wav[:,:wav_len]=data["audio_wav"][1]
            data["audio_wav"][1] = empty_tgt_wav
            
            empty_tgt_wav = torch.zeros(data["audio_data_Real"][0].shape[0],frame_num)
       
        # random sampling
        else :
            k = np.random.randint(low=0, high = data["audio_data_Real"][0].shape[1]-frame_num)
            data["audio_data_Real"][0] = data["audio_data_Real"][0][:,k:k+frame_num]
            data["audio_data_Imagine"][0] = data["audio_data_Imagine"][0][:,k:k+frame_num]
            
            data["audio_data_Real"][1] = data["audio_data_Real"][1][:,k:k+frame_num]
            data["audio_data_Imagine"][1] = data["audio_data_Imagine"][1][:,k:k+frame_num]
            data["audio_wav"][0] = data["audio_wav"][0][:,k*256*self.fs:k*256*self.fs+frame_num*256*self.fs-1]
            data["audio_wav"][1] = data["audio_wav"][1][:,k*256*self.fs:k*256*self.fs+frame_num*256*self.fs-1]

        return data

    def __len__(self):
        return len(self.data_list)
    

