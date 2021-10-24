# -*- coding: utf-8 -*-
"""
Created on Sun Oct 24 02:13:57 2021

@author: Usuario
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Oct 24 01:22:22 2021

@author: Usuario
"""


import bcg_auxiliary as bcg
#import matplotlib.pyplot as plt
import numpy as np

import sys
path_to_module = r"E:\\Users\Usuario\\Documents\\TheBrainCodeGame\\TBCG_SocioAstros\\"
sys.path.append(path_to_module)
import utils as ut
import model_builders as mb

import os 

fs=1250
window_seconds = 0.05 #seconds
overlapping = 0.7
batch_size = 32
learning_rate = 1e-5
binary = False
Unet = False

###############################################################################
#                               TRAINING DATA                                 #
###############################################################################

### LOAD TRAIN DATA ###
datapath = "../data/Amigo2"
data_Amigo2, ripples_tags_Amigo2, signal_Amigo2, x_train_Amigo2, y_train_Amigo2, indx_map_Amigo2 = ut.load_data_pipeline(
    datapath, desired_fs=fs, window_seconds = window_seconds, overlapping = overlapping, zscore= True, binary = binary)

datapath = "../data/Som2"
data_Som2, ripples_tags_Som2, signal_Som2, x_train_Som2, y_train_Som2, indx_map_Som2 = ut.load_data_pipeline(
    datapath, desired_fs=fs, window_seconds = window_seconds, overlapping = overlapping, zscore=True, binary = binary)

### MERGE TRAINING DATA ###
x_train = np.vstack((x_train_Amigo2, x_train_Som2))
if binary:
    y_train = np.vstack((y_train_Amigo2, y_train_Som2))
else:
    y_train = np.vstack((np.expand_dims(y_train_Amigo2,axis=1), np.expand_dims(y_train_Som2,axis=1)))
indx_map_train = np.vstack((indx_map_Amigo2, indx_map_Som2))

###############################################################################
#                             VALIDATION DATA                                 #
###############################################################################
### LOAD VALIDATION DATA ###
datapath = "../data/Dlx1"
data_Dlx1, ripples_tags_Dlx1, signal_Dlx1, x_validation_Dlx1, y_validation_Dlx1, indx_map_Dlx1 = ut.load_data_pipeline(
    datapath, desired_fs=fs, window_seconds = window_seconds, overlapping = overlapping, zscore=True, binary = binary)

datapath = "../data/Thy7"
data_Thy7, ripples_tags_Thy7, signal_Thy7, x_validation_Thy7, y_validation_Thy7, indx_map_Thy7 = ut.load_data_pipeline(
    datapath, desired_fs=fs, window_seconds = window_seconds, overlapping = overlapping, zscore=True, binary = binary)

### MERGE VALIDATION DATA ###
x_validation = np.vstack((x_validation_Dlx1, x_validation_Thy7))
if binary:
    y_validation = np.vstack((y_validation_Dlx1, y_validation_Thy7))
else:
    y_validation = np.vstack((np.expand_dims(y_validation_Dlx1,axis=1), np.expand_dims(y_validation_Thy7,axis=1)))
indx_map_validation = np.vstack((indx_map_Dlx1, indx_map_Thy7))

###############################################################################
#                                CNN BUILDING                                 #
###############################################################################

from tensorflow.keras.callbacks import ModelCheckpoint
n_ch = data_Som2.shape[1]
input_shape = (int(fs*window_seconds),n_ch,1)

if binary:
    model = mb.model_builder_binary(filters_Conv1 = 32, filters_Conv2 = 16, filters_Conv3=8, filters_Conv4 = 16,
                      filters_Conv5 =16, units_Dense = 60, input_shape = input_shape,
                      learning_rate = 1e-5)
    checkpoint_path = "../training_cp/training_binary_v1/cp-{epoch:04d}.ckpt"

else:
    if Unet:
        model= mb.model_builder_Unet(filters_Conv1 = 10, filters_Conv2 = 15, filters_Conv3=15, filters_Conv4 = 15,
                               input_shape = input_shape, learning_rate  = 1e-4)
        checkpoint_path = "../training_cp/training_unet_v1/cp-{epoch:04d}.ckpt"
    else:
        model = mb.model_builder_prob(filters_Conv1 = 32, filters_Conv2 = 16, filters_Conv3=8, filters_Conv4 = 16,
                          filters_Conv5 =16, filters_Conv6=8, input_shape = input_shape, 
                          learning_rate  = 1e-5)
        checkpoint_path = "../training_cp/training_prob_v3/cp-{epoch:04d}.ckpt"

checkpoint_dir = os.path.dirname(checkpoint_path)
save_freq = int(25*np.ceil(x_train.shape[0]/batch_size))
cp_callback = ModelCheckpoint(
    filepath=checkpoint_path, 
    verbose=1, 
    save_weights_only=True,
    save_freq=save_freq
 )

###############################################################################
#                                  TRAIN CNN                                  #
###############################################################################
 ## MERGE ALL DATA ##
 

model.fit(x_train,y_train, shuffle = True, epochs = 1000, batch_size = batch_size, 
          callbacks=[cp_callback], validation_data = (x_validation, y_validation))
model.save_weights(checkpoint_path)

