# -*- coding: utf-8 -*-
"""
pandastim/examples/input_param_control.py

Part of pandastim package: https://github.com/EricThomson/pandastim
"""

from utils import Emitter
import textures
import stimuli
from datetime import datetime

# Create emitter to generate pseudo x, y, theta values
x = [0, .02, .03, .04, .05, .06, .07, 0.2, 0.19, 0.18, 0.17, 0.17, 0.17, 0.2, 0.2,  0.2, 0.2, 0.2,
     0.2, 0.17, 0.17, 0.17, 0.18, 0.19, 0.2, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0]
y = [0, -.02, -.03, -.04, -.05, -.06, -.07, -0.2, -0.15, -0.12, -0.07, 0, 0.05, 0.1, 0.1, 0.1, 0.1, 0.1,
     0.1, 0.05, 0, -0.07, -0.12, -0.15, -0.2, -0.07, -0.06, -0.05, -0.04, -0.03, -0.02, 0]
theta = [0, -2, -4, -5, -5, -5, -5, -20, -25, -27, -27, -30, -35, -40, -40, -40, -40, -40,
         -40, -35, -30, -27, -27, -25, -20, -5, -5, -5, -5, -4, -2, 0]
em = Emitter(x, y, theta, period = .1, pause = 2)

#InputControlParams shows texture controlled by emitter.
# Set up filepath for saving
current_dt = datetime.now()
filename = current_dt.strftime(("ipc_%Y%m%d_%H%M%S.txt"))
save_dir = r'./examples/data/'
file_path = save_dir + filename

tex = textures.GratingRgbTex(spatial_frequency = 30, texture_size = 1024, rgb = (255, 0, 0))
binocular_show = stimuli.InputControlParams(tex,
                                            initial_position = (0, 0),
                                            stim_angles = (0, 0),
                                            initial_angle = 0, #130,
                                            strip_width = 6,
                                            velocities = (-0.07, .07),
                                            window_size = 512,
                                            window_name = 'input control example',
                                            fps = 50,
                                            profile_on = True,
                                            save_path = file_path)
binocular_show.run()
em.kill()
if binocular_show.filestream:
    binocular_show.filestream.close()
