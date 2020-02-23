# -*- coding: utf-8 -*-
"""
pandastim/examples/drifting_binocular_grating.py

Part of pandastim package: https://github.com/EricThomson/pandastim
"""
import textures
import stimuli

tex = textures.GratingRgbTex(rgb = (255, 0, 0), 
                             spatial_frequency = 30)

binocular_drift = stimuli.BinocularMoving(tex,
                                          position = (-0.5, 0.25),
                                          stim_angles = (40, 40),
                                          strip_angle = 130, 
                                          strip_width = 10,
                                          velocities = (-0.05, 0.05),
                                          window_name = 'binocular drift example', 
                                          profile_on = False)
binocular_drift.run()
