# -*- coding: utf-8 -*-
"""
pandastim/examples/keyboard_switcher.py

This is not something you would use in an experiment, but is useful for showing the 
logic of input-driven stimuli.

Part of pandastim package: https://github.com/EricThomson/pandastim
"""
import textures
import stimuli
from datetime import datetime

# Create list of textures, and parameter list for the two textures
tex1 = textures.SinRgbTex(rgb = (50, 255, 255))
tex2 = textures.SinRgbTex(rgb = (0, 0, 255))
tex_classes = [tex1, tex2]
stim_params = [{'angle': 45, 'velocity': 0.1},
               {'angle': -45, 'velocity': -0.1}]

# Set up file path
current_dt = datetime.now()
filename = current_dt.strftime(("toggle_%Y%m%d_%H%M%S.txt"))
save_dir = r'./examples/data/'
file_path = save_dir + filename

# Run the show
toggle_show = stimuli.KeyboardToggleTex(tex_classes,
                                        stim_params,
                                        profile_on = False,
                                        save_path = file_path)
toggle_show.run()
# Stuff that will be run after you close the panda3d window (close filestream)
if toggle_show.filestream:
    toggle_show.filestream.close()
