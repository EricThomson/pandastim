# -*- coding: utf-8 -*-
"""
pandastim/examples/static_fullfield_red.py
Example of how to show a static rgb stimuilus (simple full field color)

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from stimulus_classes import FullFieldStatic
from textures import sin_texture_rgb

rgb_red = (255, 10, 10)  
texture_size = 512
window_size = 512
red_sin = sin_texture_rgb(texture_size = 512, spatial_frequency = 10, rgb = (255, 0, 0))

red_static = FullFieldStatic(red_sin, angle = -40, 
                              window_size = window_size, texture_size = texture_size)
red_static.run()

