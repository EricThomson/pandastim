"""
drifting_sinusoid_experiment_working
Trying to get a good thorough experiment class up and running.

To do:
    -User input: stimulus vector and duration vectors (duration for stim and for delay)
        stimulus_values (N)
        stim_durations (N)
        delay_durations (N)
        baseline_duration (scalar)
           delay0 stim0 delay1 stim1 delay2 stim2 delay3
    - Need to somehow keep texture and experiment params separate (use * and **?)
    -How to best handle these arrays: n-d array and then one number for 
        baseline? As a user what would you find intuitive?
    -Block structure: implement here, or build a wrapper for this: after all that's just a variant in stim_durations.
    -Save to file (stim/delays/blocks).
    - Once it has saved, put text on screen to indicate it is safe to close.
    -Gui element to pause/play?
    -Change window title with each stimulus?
    -Add debug function to plot stimulus versus time (stem plot)    
    - Add trial number (events are more fine-grained than trials)
    
"""
import numpy as np 
import matplotlib.pyplot as plt
from itertools import zip_longest
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage
from panda3d.core import WindowProperties
from direct.showbase import ShowBaseGlobal  #global vars defined by p3d


import sys
sys.path.append('..')  #put parent directory in python path
import textures  


class FullFieldDriftExperiment(ShowBase):
    """
    Doc here
    To do: make texture_size and window_size inputs.
    """
    def __init__(self, texture_function, stim_params, experiment_structure,
                 window_size = 512, texture_size = 512):
        super().__init__()
        self.events = experiment_structure['event_values']
        self.event_change_times = experiment_structure['event_change_times']
        self.event_durations = experiment_structure['event_durations']
        self.current_event_num = 0
        self.num_events = len(self.events)
        self.stim_params = stim_params
        self.texture_size = texture_size
        self.window_size = window_size
        self.bgcolor = (0.5, 0.5, 0.5, 1)
        
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

        self.taskMgr.add(self.move_texture_task, "move_texture")
        self.taskMgr.add(self.set_texture_task, "set_texture")
        
    @property
    def current_event_ind(self):
        """ returns index of current event (e.g., -1 for baseline, 1 for sine xyz)
        typical events = [-1 2 0 1 -1 1 0 2] so events[5] = 1"""
        return self.events[self.current_event_num]
    
    @property
    def current_stim_params(self):
        """ returns actual value of current event """
        return self.stim_params[self.current_event_ind]
    
       
    def set_texture_task(self, task):
        """ doc here"""
        if task.time <= event_change_times[-1]:
            if task.time >= self.event_change_times[self.current_event_num]:
                self.current_event_num += 1
                if self.current_event_ind  == -1:
                    self.card1.setColor(self.bgcolor)  
                    self.card1.clearTexture(self.texture_stage)  #turn off stage
                    self.set_title("FFDE {0}: {1}".format(self.current_event_num, "baseline"))
                    
                else:
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
                        texture_format = Texture.F_luminance #grayscale
                        provided_format = "L"
                    elif texture_ndims == 3:
                        texture_format = Texture.F_rgb8
                        provided_format = "RGB"
                    else:
                        raise ValueError("Texture needs to be 2d or 3d (rgb). Let us know if you have others.")
            

                    self.texture.setup2dTexture(texture_size, texture_size, 
                                           texture_component_type, texture_format)  
                    self.texture.setRamImageAs(texture_array, provided_format)  
                    self.texture_stage = TextureStage('stim_texture_stage')
                                       
                    self.card1.setColor((1, 1, 1, 1))  
                    self.card1.setTexture(self.texture_stage, self.texture) 
                    self.card1.setR(self.current_stim_params['angle']) 
                    self.set_title("FFDE {0}: {1}".format(self.current_event_num,  self.current_event_ind))

            return task.cont 
        else:
            return task.done  

    def move_texture_task(self, task):
        """doc here"""         
        if task.time <= event_change_times[-1]:
            if self.current_event_ind != -1:
                new_position = -task.time*self.current_stim_params['velocity']
                self.card1.setTexPos(self.texture_stage, new_position, 0, 0) #u, v, w
            return task.cont #taskMgr will continue to call task
        else:
            print("Last stimulus has been shown")
            self.set_title("FFDE Done")
            #Put text into arena
            return task.done  #taskMgr will not call task
        
    def set_title(self, title):
        self.windowProps.setTitle(title)
        ShowBaseGlobal.base.win.requestProperties(self.windowProps)  #base is a panda3d global
        
    def plot_timeline(self):
        """ plots step plot of stimulus versus time"""
        full_time = np.arange(0, self.event_change_times[-1], 0.5)
        full_stimulus = -1*np.ones(len(full_time))
        event_num = 0
        for time_ind in range(len(full_time)):
            time_val = full_time[time_ind]
            if time_val >= event_change_times[event_num]:
                event_num += 1             
            full_stimulus[time_ind] =  all_events[event_num]
        plt.step(full_time, full_stimulus)
        plt.yticks(np.arange(-1, np.max(full_stimulus)+1, 1))
        plt.xlabel('Time (s)')
        plt.ylabel('Stimulus')
        plt.title('Stimuli over full experiment (-1 is baseline)')
        plt.show()
        
#%%
if __name__ == '__main__':
    window_size = 512
    texture_size = window_size 
    #texture_function =  textures.sin_texture_2byte; #textures.grating_texture;
    #Following are for grating, sin, sine2byte
#    stim_params = [{'angle': -20, 'velocity': 0.10, 'kwargs': {'spatial_frequency': 15, 'texture_size': texture_size}},
#                   {'angle':  20, 'velocity': -0.08, 'kwargs': {'spatial_frequency': 10, 'texture_size': texture_size}},
#                   {'angle':  90, 'velocity': 0.05,  'kwargs': {'spatial_frequency': 5, 'texture_size': texture_size}}]
    #To test out sin_rgb
    texture_function = textures.sin_texture_rgb; #(texture_size = 512, spatial_frequency = 10, rgb = (255, 255, 255)):
    rgbs = [(255, 0, 0), (255, 0, 255), (0, 255, 0)]
    stim_params = [{'angle': -20, 'velocity': 0.10, 
                    'kwargs': {'spatial_frequency': 15, 'texture_size': texture_size, 'rgb': rgbs[0]}},
                   {'angle':  20, 'velocity': -0.08, 
                    'kwargs': {'spatial_frequency': 10, 'texture_size': texture_size, 'rgb': rgbs[1]}},
                   {'angle':  90, 'velocity': 0.05,  
                    'kwargs': {'spatial_frequency': 5, 'texture_size': texture_size, 'rgb': rgbs[2]}}]
    
    #Arrays of stimulus values and durations
    stimulus_values = [2, 1, 0, 1, ]
    stim_durations =  [4, 4, 2, 3,]
    delay_durations = [4, 2, 3, 2,]  #time after each stimulus to show baseline
    initial_baseline_duration = [2] #time before first stimulus to show baseline
    baseline_durations = initial_baseline_duration + delay_durations
    num_stim = len(stim_durations)    
    num_baselines = len(baseline_durations)
    #Create list of all events, including baseline as -1
    all_events = [y for x in zip_longest(-1*np.ones(num_baselines), stimulus_values) for y in x if y is not None]
    
    #Derive event structure
    event_durations =  [y for x in zip_longest(baseline_durations, stim_durations) for y in x if y is not None]
    event_change_times = np.cumsum(event_durations)   #-1 because final baseline never ends
    num_event_changes = len(event_change_times)
    num_events = num_event_changes
    experiment_structure = {'event_values': all_events,  
                            'event_durations': event_durations, 
                            'event_change_times': event_change_times}   #redundant, contained in event_durs
    #quick tests
    assert(len(baseline_durations) == num_stim+1)
    assert(num_event_changes == num_stim*2+1)
           
    app = FullFieldDriftExperiment(texture_function, stim_params, experiment_structure,
                                   window_size = window_size, texture_size = texture_size)
    #app.plot_timeline()
    app.run()
