# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 01:30:05 2021

@author: Usuario
"""

import bcg_auxiliary as bcg
#import matplotlib.pyplot as plt
import numpy as np

import sys
path_to_module = r"E:\\Users\Usuario\\Documents\\TheBrainCodeGame\\TBCG_SocioAstros\\"
sys.path.append(path_to_module)
import utils as ut


datapath = "../data/Som2"
data_Som2, fs, session_name_Som2 = bcg.load_data(datapath)
n_ch = data_Som2.shape[1]
ripples_tags_Som2 = bcg.load_ripples_tags(datapath, fs)

datapath = "../data/Amigo2"
data_Amigo2, fs, session_name_Amigo2 = bcg.load_data(datapath)
ripples_tags_Amigo2 = bcg.load_ripples_tags(datapath, fs)

#downsample
desired_fs = 1250
window_seconds = 0.04 #seconds
overlapping = 0.6

down_sampling_factor =int(fs/desired_fs)
window_size = int(desired_fs*window_seconds)
input_shape = (window_size,n_ch,1)

data_Som2 = ut.mov_av_downsample(data_Som2, down_sampling_factor)
signal_Som2 = bcg.get_ripples_tags_as_signal(data_Som2, ripples_tags_Som2,desired_fs)
x_train_Som2, indx_map_Som2 = ut.adapt_input_to_CNN(data_Som2, window_size, overlapping)
y_train_Som2 = ut.adapt_label_to_CNN(signal_Som2, window_size, overlapping)

data_Amigo2 = ut.mov_av_downsample(data_Amigo2, down_sampling_factor)
signal_Amigo2 = bcg.get_ripples_tags_as_signal(data_Amigo2, ripples_tags_Amigo2, desired_fs)
x_train_Amigo2, indx_map_Amigo2 = ut.adapt_input_to_CNN(data_Amigo2, window_size, overlapping)
y_train_Amigo2 = ut.adapt_label_to_CNN(signal_Amigo2, window_size, overlapping)

fs = desired_fs


from tensorflow.keras.models import Sequential
from tensorflow.keras import layers, optimizers



model = Sequential()
model.add(layers.Conv2D(filters = 12, kernel_size=(2,2), activation='relu',
                 input_shape=input_shape, padding='same', strides = (1,1)))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(filters = 4, kernel_size=(2,2), activation='relu',
                       padding='same'))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(filters = 4, kernel_size=(3,2), activation='relu',
                       padding='same'))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(filters = 8, kernel_size=(4,1), activation='relu',
                       padding='same'))
model.add(layers.BatchNormalization())
model.add(layers.LeakyReLU())
model.add(layers.Conv2D(filters = 16, kernel_size=(6,1), activation='relu',
                       padding='same'))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.Conv2D(filters = 8, kernel_size=(6,1), activation='relu',
                       padding='same'))
model.add(layers.BatchNormalization())
model.add(layers.ReLU())
model.add(layers.Flatten())
model.add(layers.Dense(1, activation='sigmoid'))
model.summary()
model.build()

model.compile(
    optimizer= optimizers.Adam(learning_rate=1e-5), 
    loss='mean_absolute_error', 
    metrics=['Accuracy']  
)


'''
t_train = np.vstack((indx_map_Amigo2[126:190,:,:],indx_map_Amigo2[500:800,:,:], 
                        indx_map_Amigo2[1000:1300,:,:], indx_map_Amigo2[1900:2200,:,:],
                        indx_map_Amigo2[2300:2325,:,:], indx_map_Amigo2[2690:2850,:,:], 
                        indx_map_Amigo2[3000:3350,:,:]))

x_train = np.vstack((x_train_Amigo2[126:190,:,:,:],x_train_Amigo2[500:800,:,:,:], 
                        x_train_Amigo2[1000:1300,:,:,:], x_train_Amigo2[1900:2200,:,:,:],
                        x_train_Amigo2[2300:2325,:,:,:], x_train_Amigo2[2690:2850,:,:,:], 
                        x_train_Amigo2[3000:3350,:,:,:]))

y_train = np.vstack((y_train_Amigo2[126:190],y_train_Amigo2[500:800], 
                        y_train_Amigo2[1000:1300], y_train_Amigo2[1900:2200],
                        y_train_Amigo2[2300:2325], y_train_Amigo2[2690:2850], 
                        y_train_Amigo2[3000:3350]))
'''

x_train = np.vstack((x_train_Amigo2, x_train_Som2))
y_train = np.vstack((np.expand_dims(y_train_Amigo2,axis=1), np.expand_dims(y_train_Som2,axis=1)))
t_train = np.vstack((indx_map_Amigo2, indx_map_Som2))

model.fit(x_train,y_train, shuffle = True, epochs = 5000, batch_size = 32)



'''
y_predict = model.predict(x_train)
events_predicted = ut.get_ripple_times_from_CNN_output(y_predict, t_train, verbose=True)
events_truth = ut.get_ripple_times_from_CNN_output(y_train, t_train, verbose=True)
bcg.get_score (events_truth, events_predicted, threshold=0.1)
'''
plt.plot(y_train)
plt.plot(y_predict)
plt.xlim([1000, 2000])
