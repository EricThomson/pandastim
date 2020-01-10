"""
drifting_sinusoid_experiment_working
Trying to get a good thorough experiment class up and running.

To do:
    -User input: stimulus vector and duration vectors (duration for stim and for delay)
        stim_values (N)
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


#General parameters



class FullFieldDriftExperiment(ShowBase):
    def __init__(self, texture_function, stim_params, experiment_structure):
        super().__init__()
        self.event_change_num = 0
        self.stim_num = 0  #increments to 0 when we hit stimulus time
        self.baseline_stim_on = True #when stim is baseline vs texture
        self.initial_baseline_on = True
        self.stim_values = experiment_structure['stimulus_values']
        
        #Set window title (need to update with each stim) and size
        self.windowProps = WindowProperties()
        self.windowProps.setSize(window_size, window_size)
        self.set_title("FFDE {0}: {1}".format(self.stim_num, self.stim_values[self.stim_num]))

        #Initialize texture stim 0 
        texture_kwargs = {'texture_size': texture_size, 
                          'spatial_frequency': stim_params[self.stim_num]['spatial_freq'] }
        initial_texture = texture_function(**texture_kwargs)
        #Create texture stage
        self.texture = Texture("stim_texture")
        self.texture.setup2dTexture(texture_size, texture_size, 
                                       Texture.T_unsigned_byte, Texture.F_luminance) 
        self.texture.setRamImage(initial_texture)   
        self.texture_stage = TextureStage('stim_texture_stage')
                                                                    
        #Create scenegraph
        cm = CardMaker('card1')
        cm.setFrameFullscreenQuad()
        self.card1 = self.aspect2d.attachNewNode(cm.generate())  
        self.card1.setColor(bgcolor)  #make this an add mode

        #Transform the model(s)
        self.card1.setScale(np.sqrt(8))
        self.card1.setR(stim_params[self.stim_values[self.stim_num]]['angle'])
        
        #Add task to taskmgr to translate texture 
        self.taskMgr.add(self.moveTextureTask, "moveTextureTask")
        
    def set_title(self, title):
        self.windowProps.setTitle(title)
        ShowBaseGlobal.base.win.requestProperties(self.windowProps)  #base is a panda3d global
        
    #Procedure to handle changes on each frame, if needed
    def moveTextureTask(self, task):
        if task.time >= event_change_times[self.event_change_num]:
            #If changing to baseline, turn off texture.
            #Otherwise turn it on and set angle
            if self.event_change_num < num_event_changes-1:
                if self.baseline_stim_on:
                    self.stim_num += 1  #bring to correct index
                    self.set_title("FFDE {0}: {1}".format(self.stim_num, self.stim_values[self.stim_num]))
                    self.card1.setColor((1, 1, 1, 1))  #make this an add mode
                    self.card1.setTexture(self.texture_stage, self.texture) 
                    self.card1.setR(stim_params[self.stim_values[self.stim_num]]['angle']) 
                    print("\nstim_num: ", self.stim_num)
                else:  #have been showing stim so turn it off
                    self.card1.setColor(bgcolor)  
                    self.card1.clearTexture(self.texture_stage)  #turn off stage
                self.baseline_stim_on = not self.baseline_stim_on   #toggle whether baseline or stim 
                self.event_change_num += 1
            print("event_change_num: ", self.event_change_num)
        if not self.baseline_stim_on:
            shiftMag = task.time*stim_params[self.stim_values[self.stim_num]]['velocity']
            self.card1.setTexPos(self.texture_stage, shiftMag, 0, 0) #u, v, w

        if task.time <= event_change_times[-2]:
            return task.cont #taskMgr will continue to call task
        else:
            print("Last stimulus has been shown")
            self.setTitle("Experiment done")
            #Put text into arena
            return task.done  #taskMgr will not call task
 
if __name__ == '__main__':
    window_size = 1024
    texture_size = window_size 
    #Stimulus parameters
    stim_params = [{'angle': -20, 'velocity':-0.10, 'spatial_freq': 15},
                   {'angle':  20, 'velocity':  .15, 'spatial_freq': 10},
                   {'angle':  90, 'velocity': 0.05, 'spatial_freq': 5}]
    stim_values = [2, 1, 0, 1, 0, 2, ]
    texture_function = textures.sin_texture;
    #texture_kwargs = {'texture_size': texture_size, 'spatial_frequency': stim_params[0] }
    #texture = texture_function(**texture_kwargs)
    
    #Experimental paramters
    initial_baseline_duration = [7] #time before first stimulus to show baseline
    stim_durations = [4, 4, 6, 5, 3, 2, ]
    delay_durations = [4, 2, 3, 2, 1, 2, ]  #time after each stimulus to show baseline
    baseline_durations = initial_baseline_duration + delay_durations
    num_stim = len(stim_durations)    
    num_baselines = len(baseline_durations)
    #Create list of all events, including baseline as -1
    all_events = [y for x in zip_longest(-1*np.ones(num_baselines), stim_values) for y in x if y is not None]
    
    #Derive event structure
    event_durations =  [y for x in zip_longest(baseline_durations, stim_durations) for y in x if y is not None]
    event_change_times = np.cumsum(event_durations)   #-1 because final baseline never ends
    num_event_changes = len(event_change_times)
    num_events = num_event_changes
    baseline_events = np.ones(num_events)
    baseline_events[::2] = 0
    experiment_structure = {'stimulus_values': stim_values, #reduntant, contained in event values
                            'event_values': all_events,  
                            'event_durations': event_durations, 
                            'event_change_times': event_change_times}   #redundant, contained in event_durs
    
    #quick tests
    assert(len(baseline_durations) == num_stim+1)
    assert(num_event_changes == num_stim*2+1)
    
    #%%
    #Create step plot of stimuli versus time
    full_time = np.arange(0, event_change_times[-1], 0.5)
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
    bgcolor = (0.5, 0.5, 0.5, 1)   
    app = FullFieldDriftExperiment(texture_function, stim_params, experiment_structure)
    app.run()
