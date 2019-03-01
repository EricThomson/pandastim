# -*- coding: utf-8 -*-
"""
pandastim/examples/static_fullfield_red.py
Example of how to show a super-simple static rgb stimuilus (simple full field color)

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from stimulus_classes import FullFieldStatic
from textures import rgb_texture_byte

rgb_red = (255, 10, 10)  
texture_size = 512
window_size = 512
red_texture = rgb_texture_byte(texture_size, rgb = rgb_red)
red_static = FullFieldStatic(red_texture, angle = 0, 
                              window_size = window_size, texture_size = texture_size)
red_static.run()

