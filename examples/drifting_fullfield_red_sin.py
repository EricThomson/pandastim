# -*- coding: utf-8 -*-
"""
pandastim/examples/drifting_fullfield_red_sin.py
Example of how to show a drifting red sinusoid.

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from stimuli import FullFieldDrift
from textures import sin_texture_rgb

stim_params = {'velocity': -0.15, 'angle': -35}
texture_size = 512
window_size = 512
red_sin = sin_texture_rgb(texture_size = 512, spatial_frequency = 10, rgb = (255, 0, 0))
sin_drifter = FullFieldDrift(red_sin, angle = stim_params["angle"], 
                                   velocity = stim_params["velocity"], 
                                   window_size = window_size, 
                                   texture_size = texture_size)
sin_drifter.run()