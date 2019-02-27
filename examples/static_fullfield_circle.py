# -*- coding: utf-8 -*-
"""
pandastim/examples/static_fullfield_circle.py
Example of how to show a static stimulus, in this case a sinusoidal grating.

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from stimulus_classes import FullFieldStatic
from textures import circle_texture_byte

stim_params = {'radius': 20, 'center': (100, -100), 'bg_intensity': 50, 'face_intensity': 255}
texture_size = 512
window_size = 512
circle_texture = circle_texture_byte(texture_size, stim_params['center'], stim_params['radius'], 
                                     stim_params['bg_intensity'], stim_params['face_intensity'])

circle_static = FullFieldStatic(circle_texture, angle = 0, 
                              window_size = window_size, texture_size = texture_size)
circle_static.run()



