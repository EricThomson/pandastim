# -*- coding: utf-8 -*-
"""
pandastim/examples/fixed_binocular_sin.py

For info about profiling and the profile_on keyword, see pandastim/readme.md

Part of pandastim package: https://github.com/EricThomson/pandastim
"""
import textures
import stimuli

stim = textures.SinRgbTex(rgb = (0, 255, 0), 
                          spatial_frequency = 20)
binocular_fixed = stimuli.BinocularFixed(stim,
                                         position = (-0.5, 0.25),
                                         stim_angles = (-40, -40),
                                         strip_angle = 50,
                                         strip_width = 8,
                                         profile_on = True,
                                         window_name = 'green binocular example')
binocular_fixed.run()