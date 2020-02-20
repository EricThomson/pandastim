# -*- coding: utf-8 -*-
"""
pandastim/examples/drifting_fullfield_grating_experiment.py
Example of how to show a drifting grating in an experiment, interspersed with black rgb texture.

Note experiment examples are more comp
Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

import numpy as np
from pathlib import Path
from os import makedirs
from datetime import datetime
from experiments import FullFieldDriftExperiment
from textures import grating_texture, rgb_texture

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
#Note we set up texture functions as a dictionary that is passed in, rather than just giving
#giving the function direction, so we can encode/save the name and not have to deal with encoding/saving
#the function objecty itself (e.g., it is a lazy way to circumvent jsonifying a function object directly)
window_size = 512
texture_size = window_size 



texture_functions = {'grating': grating_texture,
                     'rgb': rgb_texture}  #this is needed b/c I'm not going to jsonify the functions themselves when saving
stim_params = [{'texture': 'grating', 'angle': -20, 'velocity': 0.10, 'kwargs': {'spatial_frequency': 15, 'texture_size': texture_size}},
               {'texture': 'grating', 'angle':  20, 'velocity': -0.08, 'kwargs': {'spatial_frequency': 10, 'texture_size': texture_size}},
               {'texture': 'grating', 'angle':  90, 'velocity': 0.05,  'kwargs': {'spatial_frequency': 5, 'texture_size': texture_size}},
               {'texture': 'rgb', 'angle': 0, 'velocity': 0,  'kwargs': {'rgb': (0, 0, 0), 'texture_size': texture_size}}, 
                                                                          ]
#Arrays of stimulus values and durations
stimulus_values = [3, 2, 3, 1, 3, 0, 3, 1, 3, ]
stim_durations =  [5, 4, 2, 3, 4, 3, 2, 3, 4, ]
stim_change_times =  np.cumsum(stim_durations); 
experiment_structure = {'stim_values': stimulus_values,  
                        'stim_durations': stim_durations, 
                        'stim_change_times': stim_change_times}            
exp_app = FullFieldDriftExperiment(stim_params, experiment_structure, texture_functions,
                                   window_size = window_size, texture_size = texture_size,
                                   file_path = file_path)
#app.plot_timeline()
exp_app.run()