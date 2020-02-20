# -*- coding: utf-8 -*-
"""
pandastim/examples/drifting_fullfield_red_grating.py
Example of how to show a drifting red grating.

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from stimuli import FullFieldDrift
from textures import grating_texture_rgb
#from panda3d.core import PStatClient
#PStatClient.connect()

stim_params = {'velocity': -0.18, 'spatial_freq': 13, 'angle': -30, 'rgb': (255, 0, 0)}
texture_size = 512
window_size = 512
frame_rate = 50
#grating_texture_rgb(texture_size = 512, spatial_frequency = 10, rgb = (255, 255, 255)):
    
red_grating = grating_texture_rgb(texture_size, spatial_frequency = stim_params['spatial_freq'], rgb = stim_params['rgb'])
grating_drifter = FullFieldDrift(red_grating, angle = stim_params["angle"], 
                                   velocity = stim_params["velocity"], 
                                   window_size = window_size, 
                                   texture_size = texture_size,
                                   frame_rate = frame_rate)

grating_drifter.run()