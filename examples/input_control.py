# -*- coding: utf-8 -*-
"""
pandastim/examples/input_control.py

Must be run with publisher instance publish_random3.py or else it will just
show one stimulus forever.

Part of pandastim package: https://github.com/EricThomson/pandastim
"""
import stimuli
import textures
import utils
from datetime import datetime

#Set up thread to monitor the publisher
sub = utils.Subscriber(topic = "stim", port = "1234")
monitor = utils.Monitor(sub)

# Create list of textures, and parameter list for the two textures
# Note parameters include a 'stim_type' ('s' for single texture, 'b' for binocular)
tex0 = textures.RgbTex(rgb = (0,0,0))
params0 = {'stim_type': 's', 'angle': 0, 'velocity': 0}
tex1 = textures.SinRgbTex(rgb = (255, 0, 0))
params1 = {'stim_type': 's', 'angle': 45, 'velocity': 0.1}
tex2 = textures.GratingGrayTex(spatial_frequency = 20)
params2 = {'stim_type': 'b', 'angles': (-40, -40), 'velocities': (-0.05, .05),
           'position': (0.25, 0.25), 'strip_angle': -40, 'strip_width': 8}
stim_texts = [tex0, tex1, tex2]
stim_params = [params0, params1, params2]

# Set up filepath for saving
current_dt = datetime.now()
filename = current_dt.strftime(("toggle_%Y%m%d_%H%M%S.txt"))
save_dir = r'C:/Users/Eric/Desktop/tmp_stuff/pstim_data/'
file_path = save_dir + filename

frame_rate = 30
closed_loop = stimuli.InputControlStim(stim_texts,
                                       stim_params,
                                       initial_tex_ind = 0,
                                       profile_on = True,
                                       fps = frame_rate, 
                                       save_path = file_path)
closed_loop.run()
monitor.kill()
if closed_loop.filestream:
    closed_loop.filestream.close()