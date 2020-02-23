# -*- coding: utf-8 -*-
"""
pandastim/examples/moving_red_sin.py

For info about profiling and the profile_on keyword, see pandastim/readme.md

Part of pandastim package: https://github.com/EricThomson/pandastim
"""
import textures
import stimuli

sin_red_tex = textures.SinRgbTex(texture_size = 512,
                                 spatial_frequency = 30,
                                 rgb = (255, 0, 0))
sin_red_stim = stimuli.TexMoving(sin_red_tex,
                                     angle = 33, 
                                     velocity = -0.05,
                                     fps = 30,
                                     window_name = 'red drifting sin example',
                                     profile_on = True)
sin_red_stim.run()