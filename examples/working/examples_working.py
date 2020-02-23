# -*- coding: utf-8 -*-
"""
Script for tweaking examples until they are ready for prime time
"""

import stimuli
import textures
import utils
from datetime import datetime

example_ind = 5




if example_ind == 0:
    sin_grey_tex = textures.SinGrayTex(texture_size = 512,
                                       spatial_frequency = 20)
    sin_stim = stimuli.TexFixed(sin_grey_tex,
                                     angle = -30,
                                     profile_on = False,
                                     window_name = 'gray static sin example')
    sin_stim.run()


elif example_ind == 1:
    sin_red_tex = textures.SinRgbTex(texture_size = 512,
                                     spatial_frequency = 30,
                                     rgb = (255, 0, 0))
    sin_red_stim = stimuli.TexMoving(sin_red_tex,
                                         angle = 33, 
                                         velocity = -0.05,
                                         fps = 30,
                                         window_name = 'red sin moving example',
                                         profile_on = True)
    sin_red_stim.run()


elif example_ind == 2:
    stim = textures.SinRgbTex(rgb = (255, 0 , 0), spatial_frequency = 20)
    binocular_show = stimuli.BinocularMoving(stim,
                                              position = (-0.5, 0.25),
                                              stim_angles = (40, 40),
                                              strip_angle = 40, #130,
                                              strip_width = 6,
                                              velocities = (-0.05, 0.05),
                                              window_name = 'binocular red sin ex', 
                                              profile_on = True)
    binocular_show.run()

elif example_ind == 3:
    stim = textures.SinRgbTex(rgb = (0, 255, 0), spatial_frequency = 20)
    binocular_stat = stimuli.BinocularFixed(stim,
                                            position = (-0.5, 0.25),
                                            stim_angles = (-40, -40),
                                            strip_angle = 50,
                                            strip_width = 8,
                                            profile_on = True)
    binocular_stat.run()
    
    
elif example_ind == 4:
    tex1 = textures.SinRgbTex(rgb = (50, 255, 255))
    tex2 = textures.SinRgbTex(rgb = (0, 0, 255))
    tex_classes = [tex1, tex2]
    stim_params = [{'angle': 45, 'velocity': 0.1},
                   {'angle': -45, 'velocity': -0.1}]
    frame_rate = 40
    current_dt = datetime.now()
    filename = current_dt.strftime(("toggle_%Y%m%d_%H%M%S.txt"))
    save_dir = r'C:/Users/Eric/Desktop/tmp_stuff/pstim_data/'
    file_path = save_dir + filename
    toggle_show = stimuli.KeyboardToggleTex(tex_classes,
                                            stim_params,
                                            profile_on = False,
                                            fps = frame_rate,
                                            save_path = file_path)
    toggle_show.run()
    # close open file
    if toggle_show.filestream:
        toggle_show.filestream.close()
    

elif example_ind == 5:
    print("For this to work make sure you are running pub_class_toggle.py at same time.")
    sub = utils.Subscriber(topic = "stim", port = "1234")
    monitor = utils.Monitor(sub)

    tex1 = textures.SinRgbTex(rgb = (255, 0, 0))
    params1 = {'stim_type': 's', 'angle': 45, 'velocity': 0.1}

    tex2 = textures.GratingGrayTex(spatial_frequency = 20)
    params2 = {'stim_type': 's', 'angle': 80, 'velocity': -0.05}

    stim_texts = [tex1, tex2]
    stim_params = [params1, params2]
    current_dt = datetime.now()
    filename = current_dt.strftime(("toggle_%Y%m%d_%H%M%S.txt"))
    save_dir = r'C:/Users/Eric/Desktop/tmp_stuff/pstim_data/'
    file_path = save_dir + filename
    
    frame_rate = 30
    closed_loop = stimuli.InputControlStim(stim_texts,
                                           stim_params,
                                           profile_on = False,
                                           fps = frame_rate, 
                                           save_path = file_path)
    closed_loop.run()
    monitor.kill()
    if closed_loop.filestream:
        closed_loop.filestream.close()



elif example_ind == 6:
    print("Make sure you are running pub_class_toggle.py at same time.")
    sub = utils.Subscriber(topic = "stim", port = "1234")
    monitor = utils.Monitor(sub)

    tex1 = textures.SinRgbTex(rgb = (255, 0, 0))
    params1 = {'stim_type': 'b', 'angles': (45, 45), 'velocities': (0.1, -0.1), 
               'position': (0, 0), 'strip_angle': 45, 'strip_width': 8}

    tex2 = textures.GratingGrayTex(spatial_frequency = 20)
    params2 = {'stim_type': 'b', 'angles': (-40, -40), 'velocities': (-0.05, .05),
               'position': (0.25, 0.25), 'strip_angle': -40, 'strip_width': 8}

    stim_texts = [tex1, tex2]
    stim_params = [params1, params2]
    current_dt = datetime.now()
    filename = current_dt.strftime(("toggle_%Y%m%d_%H%M%S.txt"))
    save_dir = r'C:/Users/Eric/Desktop/tmp_stuff/pstim_data/'
    file_path = save_dir + filename
    frame_rate = 30
    binocular = stimuli.InputControlStim(stim_texts,
                                         stim_params,
                                         initial_tex_ind = 0,
                                         profile_on = True,
                                         fps = frame_rate,
                                         save_path = file_path)
    binocular.run()
    monitor.kill()
    if binocular.filestream:
        binocular.filestream.close()
        
        
elif example_ind == 7:
    print("\nFor this to work properly,run pub_class_toggle3.py at same time.\n")
    sub = utils.Subscriber(topic = "stim", port = "1234")
    monitor = utils.Monitor(sub)

    tex0 = textures.RgbTex(rgb = (0,0,0))
    params0 = {'stim_type': 's', 'angle': 0, 'velocity': 0}

    tex1 = textures.SinRgbTex(rgb = (255, 0, 0))
    params1 = {'stim_type': 's', 'angle': 45, 'velocity': 0.1}

    tex2 = textures.GratingGrayTex(spatial_frequency = 20)
    params2 = {'stim_type': 'b', 'angles': (-40, -40), 'velocities': (-0.05, .05),
               'position': (0.25, 0.25), 'strip_angle': -40, 'strip_width': 8}

    stim_texts = [tex0, tex1, tex2]
    stim_params = [params0, params1, params2]
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
                                           save_path = None)
    closed_loop.run()
    monitor.kill()
    if closed_loop.filestream:
        closed_loop.filestream.close()