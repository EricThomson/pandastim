# -*- coding: utf-8 -*-
"""
Zebrafish experiment for testing fluorescence.

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

import numpy as np
from pathlib import Path
from os import makedirs
from datetime import datetime
from stimulus_classes import FullFieldDriftExperiment
from textures import grating_texture_rgb, rgb_texture, circle_texture

#Set up save path
timenow = datetime.now()
now_string = timenow.strftime('%m%d%Y_%H%M%S')
filename = r'experiment_data_' + now_string + '.json'
dir_path = Path(r'./data/')
file_path = dir_path / filename
try:
    makedirs(dir_path)
except FileExistsError:
    print("Storing data in", dir_path, ", which already exists.")
    
#Set up stimuli
"""
Note we set up texture functions as a dictionary that is passed in, rather than just giving
giving the function direction, so we can encode/save the name and not have to deal with encoding/saving
the function objecty itself (e.g., it is a lazy way to circumvent jsonifying a function object directly)
"""

#circle params: texture_size, circle_center = (0,0), circle_radius = 100,  bg_intensity = 0, face_intensity = 255
    


"""texture parameters"""    
window_size = 512
texture_size = window_size 
spatial_freq = 40
speed = 0.10
circle_radius = 20
circle_center = (0, -75)

"""experimental timing parameters"""
stim_duration = 8
post_stim_duration = 3 #10
circle_duration = 1 #2.5
post_circle_duration = 3 #10
texture_functions = {'rgb_grating': grating_texture_rgb,
                     'rgb': rgb_texture,
                     'circle': circle_texture} 
stim_params = [{'texture': 'rgb_grating', 'angle':  0, 'velocity': speed, 
                'kwargs': {'spatial_frequency': spatial_freq, 'texture_size': texture_size, 'rgb': (255,0,0)}},
               {'texture': 'rgb_grating', 'angle':  0, 'velocity': -speed, 
                'kwargs': {'spatial_frequency': spatial_freq, 'texture_size': texture_size, 'rgb': (255,0,0)}},    
               {'texture': 'rgb_grating', 'angle':  90, 'velocity': speed, 
                'kwargs': {'spatial_frequency': spatial_freq, 'texture_size': texture_size, 'rgb': (255,0,0)}},
               {'texture': 'rgb_grating', 'angle':  90, 'velocity': -speed,  
                'kwargs': {'spatial_frequency': spatial_freq, 'texture_size': texture_size, 'rgb': (255,0,0)}},
               {'texture': 'rgb', 'angle': 0, 'velocity': 0,  
                'kwargs': {'rgb': (0, 0, 0), 'texture_size': texture_size}}, 
               {'texture': 'circle', 'angle': 0, 'velocity': 0,
                'kwargs': {'circle_radius': circle_radius, 'circle_center': circle_center}} ]
#Arrays of stimulus values and durations
stimulus_values =  [4, 5, 4, 2, 
                   4, 5, 4, 1, 
                   4, 5, 4, 3, 
                   4, 5, 4, 0, 4, ]
stim_durations =  [post_stim_duration, circle_duration, post_circle_duration, stim_duration, 
                   post_stim_duration, circle_duration, post_circle_duration, stim_duration, 
                   post_stim_duration, circle_duration, post_circle_duration, stim_duration, 
                   post_stim_duration, circle_duration, post_circle_duration, stim_duration, post_stim_duration, ]
stim_change_times =  np.cumsum(stim_durations); 
experiment_structure = {'stim_values': stimulus_values,  
                        'stim_durations': stim_durations, 
                        'stim_change_times': stim_change_times}     
#%%       
exp_app = FullFieldDriftExperiment(stim_params, experiment_structure, texture_functions,
                                   window_size = window_size, texture_size = texture_size,
                                   file_path = file_path)
#app.plot_timeline()
exp_app.run()