
# -*- coding: utf-8 -*-
"""
experiments.py: module in pandastim package
Code related to running experiments
https://github.com/EricThomson/pandastim

Includes classes and functions for running experiments (e.g., generating
sequences of stimuli, saving data) and other resources directly related
to running experiments.

"""

import numpy as np


from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage
from direct.showbase import ShowBaseGlobal  #global vars defined by p3d
from panda3d.core import WindowProperties, KeyboardButton, ClockObject
import textures
from panda3d.core import PStatClient

class FullFieldDriftInputExperiment(ShowBase):
    """
    Takes in input and toggles between different stim.
    Uses zeromq. Initially just get it working with keyboard toggle (enter 't' and it toggles?)
    https://www.pythonforthelab.com/blog/using-pyzmq-for-inter-process-communication-part-1/
    
    How to handle keyboard events:
        https://docs.panda3d.org/1.10/python/programming/hardware-support/keyboard-support
    Could use the polling interface to do this relatively fast (but that also does it every frame)
        
    Another example from SDK:
        https://github.com/panda3d/panda3d/blob/017b4b58350b98666580ae92b74fbf06cd477890/samples/roaming-ralph/main.py
    This shows how to use keyboard functionality more thoroughly.
        
    Event handling: 
        https://docs.panda3d.org/1.10/python/programming/tasks-and-events/event-handlers
    Mouse modes example: 
        https://www.panda3d.org/manual/?title=Sample_Programs:_Mouse_Modes
        https://github.com/panda3d/panda3d/blob/master/samples/mouse-modes/main.py
            
    To do: have it handle keyboard input of keyboard t going up.
    """
    def __init__(self, stim_params, texture_functions,
                 window_size = 512, texture_size = 512, 
                 file_path = None, profile = False, fps = 30):
        super().__init__()

        # Following turns on verbose messenger: shows every message generated.
        #self.messenger = ShowBaseGlobal.base.messenger
        #self.messenger.toggleVerbose()
        print(self.messenger)
        from json_tricks import dump

        self.current_stim_num = 1
        self.stim_params = stim_params
        self.texture_functions = texture_functions
        self.texture_size = texture_size
        self.window_size = window_size
        self.bgcolor = (0.5, 0.5, 0.5, 1)
        self.texture_initialized = False  #to handle case from -1 (uninitalize) to 0 (first stim)
        self.fps = fps
        #Set up key control mechanism
        self.blank_button = KeyboardButton.ascii_key('b')
        self.grating_button = KeyboardButton.ascii_key('g')
        self.is_down = ShowBaseGlobal.base.mouseWatcherNode.is_button_down

        if file_path is not None:
            data_to_save = {'stim_params': self.stim_params,
                            'window_size': self.window_size,
                            'texture_size': self.texture_size}
            with open(file_path, 'w') as outfile:
                dump(data_to_save, outfile, indent = 4)

        #Window properties
        self.windowProps = WindowProperties()
        self.windowProps.setSize(self.window_size, self.window_size)
        self.set_title("Initializing")

        #Create scenegraph
        cm = CardMaker('card1')
        cm.setFrameFullscreenQuad()
        self.card1 = self.aspect2d.attachNewNode(cm.generate())
        self.card1.setScale(np.sqrt(8))
        self.card1.setColor(self.bgcolor)  #make this an add mode

        # Set frame rate
        ShowBaseGlobal.globalClock.setMode(ClockObject.MLimited)
        ShowBaseGlobal.globalClock.setFrameRate(self.fps)  #can lock this at whatever
        #Show frame rate
        ShowBaseGlobal.base.setFrameRateMeter(True) 
        
        if profile:
            PStatClient.connect()
        #Set initial texture
        self.set_texture('')  #have this call move texture when appropriate
        
        # Set up event handlers and tasks
        self.accept('b', self.set_texture, ['b']) #event handler
        self.accept('g', self.set_texture, ['g'])
        self.taskMgr.add(self.move_texture_task, "move_texture") #task


    @property
    def current_stim_params(self):
        """ 
        returns actual value of current stimulus 
        """
        return self.stim_params[self.current_stim_num]
    
    
    
    def set_texture(self, data):
        """ 
        Called with relevant keyboard events
        """
        if not self.texture_initialized:
            """
            If the first texture has not yet been shown, then toggle initialization to on
            and do not clear previous texture (there is no previous texture). Otherwise
            clear previous texture otherwise it will cover new textures."""
            self.texture_initialized = True
        else:
            self.card1.clearTexture(self.texture_stage)  #turn off stage


        if data == 'b':
            print("Switching to blank")
            self.current_stim_num = 1
            
        elif data == 'g':
            print("Switching to grating")
            self.current_stim_num = 0



        texture_function_name = self.current_stim_params['texture']
        texture_function = self.texture_functions[texture_function_name]
        texture_params = self.current_stim_params['kwargs']
        texture_array = texture_function(**texture_params)
        texture_dtype = type(texture_array.flat[0])
        texture_ndims = texture_array.ndim

        #Create texture stage
        self.texture = Texture("stim_texture")

        #ComponentType depends on dtype (uint8 or whatever)
        if texture_dtype == np.uint8:
            texture_component_type = Texture.T_unsigned_byte
        elif texture_dtype == np.uint16:
            texture_component_type = Texture.T_unsigned_short
        else:
            raise ValueError("Texture needs to be uint8 or uint16. Let me know if you have others.")

        #Texture format depends on ndims
        if texture_ndims == 2:
            texture_format = Texture.F_luminance
            provided_format = "L"  #Luminance (grayscale)
        elif texture_ndims == 3:
            texture_format = Texture.F_rgb8
            provided_format = "RGB"
        else:
            raise ValueError("Texture needs to be 2d or 3d (rgb). Let us know if you have others.")
        self.texture.setup2dTexture(self.texture_size, self.texture_size,
                               texture_component_type, texture_format)
        self.texture.setRamImageAs(texture_array, provided_format)
        self.texture_stage = TextureStage('stim_texture_stage')

        self.card1.setColor((1, 1, 1, 1))
        self.card1.setTexture(self.texture_stage, self.texture)
        self.card1.setR(self.current_stim_params['angle'])
        #self.set_title("FFDE {0}/{1}: {2}".format(self.current_stim_num, self.num_stim-1, texture_function_name))

        #For debugging:
        print('Set texture: ', self.current_stim_num, ':',
              self.current_stim_params['velocity'], self.current_stim_params['texture'])
        return

    
    def move_texture_task(self, task):
        """
        The stimulus (texture) is set: now move it if needed.
        """
        if self.current_stim_params['velocity'] == 0:
            pass
        else:
            new_position = -task.time*self.current_stim_params['velocity']
            self.card1.setTexPos(self.texture_stage, new_position, 0, 0) #u, v, w
        return task.cont #taskMgr will continue to call task


    def set_title(self, title):
        self.windowProps.setTitle(title)
        ShowBaseGlobal.base.win.requestProperties(self.windowProps)  #base is a panda3d global



class FullFieldDriftExperiment(ShowBase):
    """
    This class needs docs.
    Takes in stim_params and experiment structure, and shows textures.
    """
    def __init__(self, stim_params, experiment_structure, texture_functions,
                 window_size = 512, texture_size = 512, file_path = None):
        super().__init__()
        from json_tricks import dump
        self.stimuli = experiment_structure['stim_values']
        self.stim_change_times = experiment_structure['stim_change_times']
        self.stim_durations = experiment_structure['stim_durations']
        self.current_stim_num = -1
        self.num_stim = len(self.stimuli)
        self.stim_params = stim_params
        self.texture_functions = texture_functions
        self.texture_size = texture_size
        self.window_size = window_size
        self.bgcolor = (0.5, 0.5, 0.5, 1)
        self.texture_initialized = False  #to handle case from -1 (uninitalize) to 0 (first stim)

        if file_path is not None:
            data_to_save = {'stim_params': self.stim_params,
                            'exp_structure': experiment_structure,
                            'window_size': self.window_size,
                            'texture_size': self.texture_size}
            with open(file_path, 'w') as outfile:
                dump(data_to_save, outfile, indent = 4)

        #Window properties
        self.windowProps = WindowProperties()
        self.windowProps.setSize(self.window_size, self.window_size)
        self.set_title("FFDE Initializing")

        #Create scenegraph
        cm = CardMaker('card1')
        cm.setFrameFullscreenQuad()
        self.card1 = self.aspect2d.attachNewNode(cm.generate())
        self.card1.setScale(np.sqrt(8))
        self.card1.setColor(self.bgcolor)  #make this an add mode


        #Set initial texture
        self.taskMgr.add(self.set_texture_task, "set_texture")  #have this call move texture when appropriate
        self.taskMgr.add(self.move_texture_task, "move_texture")

    @property
    def current_stim_ind(self):
        """
        returns index, from stim list, of current stimulus
        typical events = [3 1 3 0 3 3 1 3 2] so self.current_stim_ind[2] = 3
        """
        return self.stimuli[self.current_stim_num]

    @property
    def current_stim_params(self):
        """ returns actual value of current stimulus """
        return self.stim_params[self.current_stim_ind]


    def set_texture_task(self, task):
        """ doc here
        task is a global"""
        if task.time <= self.stim_change_times[-1]:
            if task.time >= self.stim_change_times[self.current_stim_num] or not self.texture_initialized:
                """
                If the first texture has not yet been shown, then toggle initialization to on
                and do not clear previous texture (there is no previous texture). Otherwise
                clear previous texture otherwise it will cover new textures."""
                if not self.texture_initialized:
                    self.texture_initialized = True
                else:
                    self.card1.clearTexture(self.texture_stage)  #turn off stage
                self.current_stim_num += 1
                texture_function_name = self.current_stim_params['texture']
                texture_function = self.texture_functions[texture_function_name]
                texture_params = self.current_stim_params['kwargs']
                texture_array = texture_function(**texture_params)
                texture_dtype = type(texture_array.flat[0])
                texture_ndims = texture_array.ndim

                #Create texture stage
                self.texture = Texture("stim_texture")

                #ComponentType depends on dtype (uint8 or whatever)
                if texture_dtype == np.uint8:
                    texture_component_type = Texture.T_unsigned_byte
                elif texture_dtype == np.uint16:
                    texture_component_type = Texture.T_unsigned_short
                else:
                    raise ValueError("Texture needs to be uint8 or uint16. Let me know if you have others.")

                #Texture format depends on ndims
                if texture_ndims == 2:
                    texture_format = Texture.F_luminance
                    provided_format = "L"  #Luminance (grayscale)
                elif texture_ndims == 3:
                    texture_format = Texture.F_rgb8
                    provided_format = "RGB"
                else:
                    raise ValueError("Texture needs to be 2d or 3d (rgb). Let us know if you have others.")
                self.texture.setup2dTexture(self.texture_size, self.texture_size,
                                       texture_component_type, texture_format)
                self.texture.setRamImageAs(texture_array, provided_format)
                self.texture_stage = TextureStage('stim_texture_stage')

                self.card1.setColor((1, 1, 1, 1))
                self.card1.setTexture(self.texture_stage, self.texture)
                self.card1.setR(self.current_stim_params['angle'])
                #self.set_title("FFDE {0}/{1}: {2}".format(self.current_stim_num, self.num_stim-1, texture_function_name))

                print('Set texture: ', self.current_stim_num, ':',
                      self.current_stim_params['velocity'], self.current_stim_params['texture'])
            return task.cont
        else:
            return task.done

    def move_texture_task(self, task):
        """
        Set texture to move. Should have conditional if it is not a moving texture,
        this should probably not even be called. 
        See stimulus_classes.FullFieldDrift()
        """
        if task.time <= self.stim_change_times[-1]:
            new_position = -task.time*self.current_stim_params['velocity']
            self.card1.setTexPos(self.texture_stage, new_position, 0, 0) #u, v, w
            #print('\tMove texture: ', self.current_stim_num, ':', self.current_stim_params['velocity'], self.current_stim_params['texture'])
            return task.cont #taskMgr will continue to call task
        else:
            print("Last stimulus has been shown")
            self.set_title("FFDE Done")
            #Put text into arena
            return task.done  #taskMgr will not call task

    def set_title(self, title):
        self.windowProps.setTitle(title)
        ShowBaseGlobal.base.win.requestProperties(self.windowProps)  #base is a panda3d global

#    def plot_timeline(self):
#        """ 
#        I'm not sure this works. Also it is used in a lot of different methods. Make
#        it a function?
#        plots step plot of stimulus versus time
#        NOTE since you changed so baseline isn't -1 anymore yoiu should fix this (e.g., yticks)
#        """
#        full_time = np.arange(0, self.stim_change_times[-1], 0.5)
#        full_stimulus = -1*np.ones(len(full_time))
#        stim_num = 0
#        for time_ind in range(len(full_time)):
#            time_val = full_time[time_ind]
#            if time_val >= self.stim_change_times[stim_num]:
#                stim_num += 1
#            full_stimulus[time_ind] =  self.stimuli[stim_num]
#        plt.step(full_time, full_stimulus)
#        #plt.yticks(np.arange(-1, np.max(full_stimulus)+1, 1))
#        plt.xlabel('Time (s)')
#        plt.ylabel('Stimulus')
#        plt.title('Stimuli over full experiment')
#        plt.show()

class OpenLoop(ShowBase):
    """
    Takes in experiment_structure (dict of stim classses, and corresponding list 
    of stim_values and stim_durations to show) and presents the stim_classes in
    stim_values for stim_durations time.
    """
    def __init__(self, stim_params, experiment_structure, texture_functions,
                 window_size = 512, texture_size = 512):
        super().__init__()
        self.stim_classes = experiment_structure['stim_classes']
        self.stim_values = experiment_structure['stim_values']
        self.stim_durations = experiment_structure['stim_durations']
        self.stim_change_times = np.cumsum(self.stim_durations)

        self.current_stim_num = -1
        self.num_stim = len(self.stim_classes)
        self.bgcolor = (0.5, 0.5, 0.5, 1)
        self.stim_initialized = False  #to handle case from -1 (uninitalize) to 0 (first stim)

        #Window properties
        self.windowProps = WindowProperties()
        self.windowProps.setSize(self.window_size, self.window_size)
        self.set_title("OL Init")

        #Create scenegraph
        cm = CardMaker('card1')
        cm.setFrameFullscreenQuad()
        self.card1 = self.aspect2d.attachNewNode(cm.generate())
        self.card1.setScale(np.sqrt(8))
        self.card1.setColor(self.bgcolor)  #make this an add mode


        #Set initial texture
        self.taskMgr.add(self.set_stim_task, "set_texture")  #have this call move texture when appropriate
        #self.taskMgr.add(self.move_texture_task, "move_texture")

    @property
    def current_stim_ind(self):
        """
        returns index, from stim list, of current stimulus
        typical events = [3 1 3 0 3 3 1 3 2] so self.current_stim_ind[2] = 3
        """
        return self.stimuli[self.current_stim_num]

    @property
    def current_stim_class(self):
        """ 
        returns actual value of current stimulus 
        """
        return self.stim_classes[self.current_stim_ind]


    def set_stim_task(self, task):
        """ doc here
        task is a global"""
        if task.time <= self.stim_change_times[-1]:
            if task.time >= self.stim_change_times[self.current_stim_num] or not self.stim_initialized:
                """
                If the first stim has not yet been shown, then toggle initialization to on
                and do not clear previous texture (there is no previous texture). Otherwise
                clear previous texture otherwise it will cover new textures."""
                if not self.texture_initialized:
                    self.texture_initialized = True
                else:
                    #self.current_stim_class.destroy()
                    self.card1.clearTexture(self.current_stim_class.texture_stage)  #turn off stage
                self.current_stim_num += 1
                print(type(self.current_stim_class))
                self.current_stim_class.run()

                self.set_title(self.current_stim_num)
            return task.cont
        else:
            return task.done

#    def move_texture_task(self, task):
#        """
#        Set texture to move. Should have conditional if it is not a moving texture,
#        this should probably not even be called. 
#        See stimulus_classes.FullFieldDrift()
#        """
#        if task.time <= self.stim_change_times[-1]:
#            new_position = -task.time*self.current_stim_params['velocity']
#            self.card1.setTexPos(self.current_stim_class.texture_stage, new_position, 0, 0) #u, v, w
#            #print('\tMove texture: ', self.current_stim_num, ':', self.current_stim_params['velocity'], self.current_stim_params['texture'])
#            return task.cont #taskMgr will continue to call task
#        else:
#            print("Last stimulus has been shown")
#            self.set_title("FFDE Done")
#            #Put text into arena
#            return task.done  #taskMgr will not call task

    def set_title(self, title):
        self.windowProps.setTitle(title)
        ShowBaseGlobal.base.win.requestProperties(self.windowProps)  #base is a panda3d global
       
#%%

if __name__ == '__main__':
    from stimuli import FullFieldDrift, FullFieldStatic
    from textures import sin_texture_rgb, circle_texture

    drift_params = {'velocity': -0.15, 'angle': -35}
    texture_size = 512
    window_size = 512
    red_sin = sin_texture_rgb(texture_size = 512, spatial_frequency = 10, rgb = (255, 0, 0))
    red_drifter = FullFieldDrift(red_sin, angle = drift_params["angle"], 
                                       velocity = drift_params["velocity"], 
                                       window_size = window_size, 
                                       texture_size = texture_size)
    green_sin = sin_texture_rgb(texture_size = 512, spatial_frequency = 10, rgb = (0, 255, 0))
    green_drifter = FullFieldDrift(green_sin, angle = drift_params["angle"], 
                                       velocity = drift_params["velocity"], 
                                       window_size = window_size, 
                                       texture_size = texture_size)
    
    circle_params = {'radius': 20, 'center': (100, -100), 'bg_intensity': 50, 'face_intensity': 255}
    circle_texture = circle_texture(texture_size, circle_params['center'], circle_params['radius'], 
                                         circle_params['bg_intensity'], circle_params['face_intensity'])   
    circle_static = FullFieldStatic(circle_texture, angle = 0, 
                                  window_size = window_size, texture_size = texture_size)

    stim_classes = {1: circle_static, 2: red_drifter, 3: green_drifter}
            
    #Arrays of stimulus values and durations to show
    stim_values = [0, 1, 0, 1, 0, 2, 0, 1, ]
    stim_durations =  [2, 3, 1, 2, 3, 1, 2, 1, ]
    num_stim = len(stim_durations)
    stim_change_times =  np.cumsum(stim_durations); # np.concatenate([np.zeros(1), np.cumsum(stim_durations)])
    experiment_structure = {'stim_classes': stim_classes,
                            'stim_values': stim_values,
                            'stim_durations': stim_durations}


exp_app = OpenLoop(experiment_structure)
exp_app.run()





        #%% hi
