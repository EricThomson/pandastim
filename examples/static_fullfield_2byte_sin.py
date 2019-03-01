# -*- coding: utf-8 -*-
"""
pandastim/examples/static_fullfield_2byte_sin.py
Showing a sinusoide with 2byte resolution. Usually 1 byte is enough.

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from stimulus_classes import FullFieldStatic
from textures import sin_texture_2byte

stim_params = {'spatial_freq': 12, 'angle': 45}
texture_size = 512
window_size = 512
sin_texture = sin_texture_2byte(texture_size, stim_params['spatial_freq'])
sin_static = FullFieldStatic(sin_texture, angle = stim_params["angle"], 
                              window_size = window_size, texture_size = texture_size)
sin_static.run()


