# -*- coding: utf-8 -*-
"""
pandastim/examples/drifting_fullfield_sin.py
Example of how to show a drifting sinusoidal grating.

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from stimuli import FullFieldDrift
from textures import sin_texture

stim_params = {'velocity': 0.15, 'spatial_freq': 10, 'angle': 60}
texture_size = 512
window_size = 512
sin_texture = sin_texture(texture_size, stim_params['spatial_freq'])
sin_drifter = FullFieldDrift(sin_texture, angle = stim_params["angle"], 
                                   velocity = stim_params["velocity"], 
                                   window_size = window_size, 
                                   texture_size = texture_size)
sin_drifter.run()