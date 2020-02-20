# -*- coding: utf-8 -*-
"""
pandastim/examples/drifting_binocular_grating.py
Example of how to present a drifting binocular grating.

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from stimuli import BinocularDrift
from textures import grating_texture

stim_params = {'spatial_freq': 20, 'stim_angles': (45, 45), 'velocities': (0.05, .05),
               'position': (0, 0), 'band_radius': 5}
mask_angle = 45  #this will change frequently in practice so not in dict
texture_size = 512
window_size = 512  
texture = grating_texture(texture_size, stim_params['spatial_freq'])
binocular_drifter = BinocularDrift(texture, 
                                   stim_angles = stim_params["stim_angles"],
                                   mask_angle = mask_angle,
                                   position = stim_params["position"], 
                                   velocities = stim_params["velocities"],
                                   band_radius = stim_params['band_radius'],
                                   window_size = window_size,
                                   texture_size = texture_size)
binocular_drifter.run()