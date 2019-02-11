"""
drifting_sinusoid(): pandastim package
Single full-field drifting sinusoid.

To do:
    Add print statements to every motherfucking bit here.
    Change window title with each stimulus?
    Add something to plot stimulus versus time
    
"""
import numpy as np 
from itertools import zip_longest
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage
from panda3d.core import WindowProperties
from direct.task import Task

#Sinusoid
texSize = 256
spatial_freq = 10
def sin3d(X, freq = 1):
    return np.sin(X*freq)
def sin8bit(X, freq = 1):
    sin_float = sin3d(X, freq=freq)
    sin_pos = (sin_float+1)*127.5; #from 0-255
    return np.asarray(sin_pos, dtype = np.uint8)
x = np.linspace(0, 2*np.pi, texSize+1)
y = np.linspace(0, 2*np.pi, texSize+1)
X, Y = np.meshgrid(x[:texSize],y[:texSize])
sinTex = sin8bit(X, freq = spatial_freq)

#Experimental parameters
stim_durations = (4, 4, 6, 5)
angles = (-20, 20, 45, 90)
shift_velocities = (-0.25, 0.4, 0.2, -0.4)
inter_stimulus_times = (4, 3, 3, 2.5, 5) #baseline to start before, all the way to end
bgcolor = (0.5, 0.5, 0.5, 1)

num_stim = len(stim_durations)
event_durations =  [y for x in zip_longest(inter_stimulus_times, stim_durations) for y in x if y is not None]
event_change_times = np.cumsum(event_durations)[:-1]
num_event_changes = len(event_change_times)

#quick tests
assert(len(inter_stimulus_times) == num_stim+1)
assert(num_event_changes == num_stim*2)

#%%
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.event_change_num = 0
        self.stim_num = -1  #increments to 0 when we hit stimulus time
        self.baseline_stim = True #when stim is baseline vs texture
        
        #Set window title (need to update with each stim)
        self.windowProps = WindowProperties()
        self.windowProps.setTitle("Full field: running")
        base.win.requestProperties(self.windowProps)  #base is a panda3d global
        
        #Create texture stage
        self.sinTexture = Texture("sin")
        self.sinTexture.setup2dTexture(texSize, texSize, Texture.T_unsigned_byte, Texture.F_luminance) 
        self.sinTexture.setRamImage(sinTex)   
        self.sinTextureStage = TextureStage('sin')
                                                                    
        #Create scenegraph
        cm = CardMaker('card1')
        cm.setFrameFullscreenQuad()
        self.card1 = self.aspect2d.attachNewNode(cm.generate())  
        self.card1.setColor(bgcolor)  #make this an add mode

        #Transform the model(s)
        self.card1.setScale(np.sqrt(2))
        self.card1.setR(angles[self.stim_num])
        
        #Add task to taskmgr to translate texture 
        self.taskMgr.add(self.moveTextureTask, "moveTextureTask")
        
    #Procedure to handle changes on each frame, if needed
    def moveTextureTask(self, task):
        if task.time >= event_change_times[self.event_change_num]:
            #If changing to baseline event, turn off texture else turn it on and set angle
            if self.event_change_num < num_event_changes:
                if self.baseline_stim:
                    self.stim_num += 1  #bring to correct index
                    self.card1.setColor((1, 1, 1, 1))  #make this an add mode
                    self.card1.setTexture(self.sinTextureStage, self.sinTexture) 
                    self.card1.setR(angles[self.stim_num]) 
                    print("\nstim_num: ", self.stim_num)
                else:  #have been showing stim so turn it off
                    self.card1.setColor(bgcolor)  
                    self.card1.clearTexture(self.sinTextureStage)  #turn off stage
                self.baseline_stim = not self.baseline_stim   #toggle whether baseline or stim 
                self.event_change_num += 1
            print("event_change_num: ", self.event_change_num)
        if not self.baseline_stim:
            shiftMag = task.time*shift_velocities[self.stim_num]
            self.card1.setTexPos(self.sinTextureStage, shiftMag, 0, 0) #u, v, w

        if task.time <= event_change_times[-1]:
            return Task.cont #taskMgr will continue to call task
        else:
            print("Last stimulus has been shown")
            self.windowProps.setTitle("Full field: done")
            base.win.requestProperties(self.windowProps)
            return Task.done  #taskMgr will not call task
 
if __name__ == '__main__':
    app = MyApp()
    app.run()
