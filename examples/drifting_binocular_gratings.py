"""
pandastim/examples/drifting_binocular_gratings.py
How to show different gratings to the left and right side of window.

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from stimulus_classes import BinocularDrift
from textures import grating_texture

            
if __name__ == '__main__':
    stim_params = {'spatial_freq': -30, 'angle': 30, 'velocity': 0.03, 
                   'position': (0, 0, 0), 'band_radius': 4}
    texture_size = 512
    window_size = 512  
    bgcolor = (0, 0, 0, 1)
    grating_texture = grating_texture(texture_size, stim_params['spatial_freq'])

    binocular_drifting = BinocularDrift(grating_texture, 
                                       angle = stim_params["angle"],
                                       position = stim_params["position"], 
                                       velocity = stim_params["velocity"],
                                       band_radius = stim_params['band_radius'],
                                       window_size = window_size,
                                       texture_size = texture_size, 
                                       bgcolor = bgcolor)
    binocular_drifting.run()
