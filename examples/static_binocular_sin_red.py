# -*- coding: utf-8 -*-
"""
pandastim/examples/drifting_binocular_sin_red.py
Example of how to present a static binocular colored sinusoid.

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from stimulus_classes import BinocularStatic
from textures import sin_texture_rgb

stim_params = {'spatial_freq': 20, 'stim_angles': (45, -45), 
               'position': (0, 0), 'band_radius': 1}
mask_angle = 0  #this will change frequently in practice so not in dict
texture_size = 512
window_size = 512
red_sin = sin_texture_rgb(texture_size = texture_size, 
                          spatial_frequency = stim_params['spatial_freq'], 
                          rgb = (255, 0, 0))

binocular_static_sin = BinocularStatic(red_sin, 
                                   stim_angles = stim_params["stim_angles"],
                                   mask_angle = mask_angle,
                                   position = stim_params["position"], 
                                   band_radius = stim_params['band_radius'],
                                   window_size = window_size,
                                   texture_size = texture_size)
binocular_static_sin.run()