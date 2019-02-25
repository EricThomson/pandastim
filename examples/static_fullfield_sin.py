# -*- coding: utf-8 -*-
"""
pandastim/examples/static_fullfield_sin.py
Example of how to show a static stimulus, in this case a sinusoidal grating.

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from fullfield_static_stimulus import FullFieldStatic
from stimuli import sin_texture_byte

stim_params = {'spatial_freq': 15, 'angle': -45}
texture_size = 512
window_size = 512
sin_texture = sin_texture_byte(texture_size, stim_params['spatial_freq'])
sin_static = FullFieldStatic(sin_texture, angle = stim_params["angle"], 
                              window_size = window_size, texture_size = texture_size)
sin_static.run()


