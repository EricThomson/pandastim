# -*- coding: utf-8 -*-
"""
pandastim/examples/static_binocular_circle.py
Example of how to present a static circle. Just for fun to show what you can do.

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from stimulus_classes import BinocularStatic, BinocularDrift
from textures import circle_texture


stim_params = {'stim_angles': (0, 0), 'position': (0, 0), 'band_radius': 1}
mask_angle = 0  #this will change frequently in practice so not in dict
texture_size = 512
window_size = 512  
circle_tex = circle_texture(texture_size, circle_radius = 20, circle_center = (0, -120))
if False:  #for debugging
    import matplotlib.pyplot as plt
    plt.imshow(circle_tex, cmap = 'gray')
    plt.show()
circle_drifter = BinocularDrift(circle_tex, 
                               stim_angles = stim_params["stim_angles"],
                               mask_angle = mask_angle,
                               position = stim_params["position"], 
                               velocities = (.1, -.08),
                               band_radius = stim_params['band_radius'],
                               window_size = window_size,
                               texture_size = texture_size)

circle_drifter.run()