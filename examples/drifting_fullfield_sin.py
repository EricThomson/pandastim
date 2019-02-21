# -*- coding: utf-8 -*-
"""
pandastim/examples/drifting_fullfield_sin: module in pandastim package
https://github.com/EricThomson/pandastim

Simple full-field drifting sinusoid example
"""
import sys
sys.path.append('..')  #put parent directory in python path

from drifting_fullfield_stimulus import FullFieldDrift
from stimuli import sin_texture_byte

stim_params = {'velocity': 0.15, 'spatial_freq': 10, 'angle': 30}
texture_size = 512
window_size = 512
sine_texture = sin_texture_byte(texture_size, stim_params['spatial_freq'])
sine_drifter = FullFieldDrift(sine_texture, angle = stim_params["angle"], 
                                   velocity = stim_params["velocity"], window_size = window_size, 
                                   texture_size = texture_size)
sine_drifter.run()