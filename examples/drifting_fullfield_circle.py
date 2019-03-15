# -*- coding: utf-8 -*-
"""
pandastim/examples/drifting_fullfield_circle.py
Example of how to show a drifting circle 

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from stimulus_classes import FullFieldDrift
from textures import circle_texture

stim_params = {'velocity': 0.15, 'angle': 30}
texture_size = 512
window_size = 512
circle_tex = circle_texture(texture_size, circle_radius = 25)
circle_drifter = FullFieldDrift(circle_tex, angle = stim_params["angle"], 
                                   velocity = stim_params["velocity"], 
                                   window_size = window_size, 
                                   texture_size = texture_size)
circle_drifter.run()