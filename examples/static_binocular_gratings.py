"""
pandastim/examples/static_binocular_gratings.py
How to show different gratings to the left and right side of window.

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path

from stimulus_classes import BinocularStatic
from textures import grating_texture
            
if __name__ == '__main__':
    stim_params = {'spatial_freq': 20, 'angle': 30, 
                   'position': (0, 0, 0), 'band_radius': 4}
    texture_size = 512
    window_size = 512  
    bgcolor = (0, 0, 0, 1)
    grating_texture = grating_texture(texture_size, stim_params['spatial_freq'])

    binocular_static = BinocularStatic(grating_texture, 
                                       angle = stim_params["angle"],
                                       position = stim_params["position"], 
                                       band_radius = stim_params['band_radius'],
                                       window_size = window_size,
                                       texture_size = texture_size, 
                                       bgcolor = bgcolor)
    binocular_static.run()
        
