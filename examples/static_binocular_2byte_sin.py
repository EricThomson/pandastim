# -*- coding: utf-8 -*-
"""
pandastim/examples/drifting_binocular_2byte_sin.py
Example of how to present a static sinusoidal grating with 2 byte representation
of the image. Left is horizontal (90 degrees) right is vertical (0 degrees)

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from stimulus_classes import BinocularStatic
from textures import sin_texture_2byte

stim_params = {'spatial_freq': 15, 'stim_angles': (90, 0), 
               'position': (0, 0), 'band_radius': 1}
mask_angle = 0  #this will change frequently in practice so not in dict
texture_size = 512
window_size = 512  
sin_texture = sin_texture_2byte(texture_size, stim_params['spatial_freq'])
binocular_static_sin = BinocularStatic(sin_texture, 
                                   stim_angles = stim_params["stim_angles"],
                                   mask_angle = mask_angle,
                                   position = stim_params["position"], 
                                   band_radius = stim_params['band_radius'],
                                   window_size = window_size,
                                   texture_size = texture_size)
binocular_static_sin.run()