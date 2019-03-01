# -*- coding: utf-8 -*-
"""
pandastim/examples/drifting_fullfield_2byte_sin.py
Example of how to show a drifting sinusoidal grating @2byte resolution.

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from stimulus_classes import FullFieldDrift
from textures import sin_texture_2byte

stim_params = {'velocity': 0.2, 'spatial_freq': 5, 'angle': -45}
texture_size = 512
window_size = 512
sin_texture = sin_texture_2byte(texture_size, stim_params['spatial_freq'])
sin_drifter = FullFieldDrift(sin_texture, angle = stim_params["angle"], 
                                   velocity = stim_params["velocity"], 
                                   window_size = window_size, 
                                   texture_size = texture_size)
sin_drifter.run()