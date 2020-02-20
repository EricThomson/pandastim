# -*- coding: utf-8 -*-
"""
pandastim/examples/drifting_binocular_green_sin.py
Example of how to present a drifting binocular green sin.

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from stimuli import BinocularDrift
from textures import sin_texture_rgb

stim_params = {'spatial_freq': 20, 'stim_angles': (30, -25), 'velocities': (0.05, -.06),
               'position': (0, 0), 'band_radius': 1}
mask_angle = 20  #this will change frequently in practice so not in dict
texture_size = 512
window_size = 512  
green_sin = sin_texture_rgb(texture_size = texture_size, 
                          spatial_frequency = stim_params['spatial_freq'], 
                          rgb = (0, 255, 0))

if True:  #debug
    import matplotlib.pyplot as plt
    plt.imshow(green_sin)
binocular_drifter = BinocularDrift(green_sin, 
                                   stim_angles = stim_params["stim_angles"],
                                   mask_angle = mask_angle,
                                   position = stim_params["position"], 
                                   velocities = stim_params["velocities"],
                                   band_radius = stim_params['band_radius'],
                                   window_size = window_size,
                                   texture_size = texture_size)
binocular_drifter.run()