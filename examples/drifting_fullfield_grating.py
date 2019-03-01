# -*- coding: utf-8 -*-
"""
pandastim/examples/drifting_fullfield_grating.py
Example of how to show a drifting grating.

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from stimulus_classes import FullFieldDrift
from textures import grating_texture_byte

stim_params = {'velocity': -0.18, 'spatial_freq': 10, 'angle': -30}
texture_size = 512
window_size = 512
grating_texture = grating_texture_byte(texture_size, stim_params['spatial_freq'])
sine_drifter = FullFieldDrift(grating_texture, angle = stim_params["angle"], 
                                   velocity = stim_params["velocity"], window_size = window_size, 
                                   texture_size = texture_size)
sine_drifter.run()