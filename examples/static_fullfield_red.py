# -*- coding: utf-8 -*-
"""
pandastim/examples/static_fullfield_red.py
Example of how to show a static stimulus, in this case full-field red window

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from fullfield_static_stimulus import FullFieldStatic
from stimuli import rgb_texture_byte

rgb_red = (0, 0, 255)  #more like pink  does panda3d use b g r?
texture_size = 512
window_size = 512
red_texture = rgb_texture_byte(texture_size, rgb = rgb_red)
red_static = FullFieldStatic(red_texture, angle = 0, 
                              window_size = window_size, texture_size = texture_size)
red_static.run()

