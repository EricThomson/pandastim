"""
drifting_sinusoid(): pandastim package
Single full-field drifting sinusoid.


"""
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage, WindowProperties
import numpy as np 
from direct.task import Task


#Create sin
texSize = 256
spatial_freq = 6
shift_velocity = -0.25
rotation = 30

def sin3d(X, freq = 1):
    return np.sin(X*freq)
def sin8bit(X, freq = 1):
    sin_float = sin3d(X, freq=freq)
    sin_pos = (sin_float+1)*127.5; #from 0-255
    return np.asarray(sin_pos, dtype = np.uint8)
x = np.linspace(0, 2*np.pi, texSize+1)
y = np.linspace(0, 2*np.pi, texSize+1)
X, Y = np.meshgrid(x[:texSize],y[:texSize])
sinTex = sin8bit(X, freq = spatial_freq);


durations = [3, 5, 3, 4]
stim_change_times = np.cumsum(durations)
num_stim = len(durations)
stim_continue = [True]*4  
angles = [-20, 20, 45, 90]
#spatial_freqs = 
#

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.stim_num = 0
        self.experiment_duration = np.sum(durations)
        self.num_stim = len(durations)
        
        #Set window title (need to update with each stim)
        self.windowProps = WindowProperties()
        self.windowProps.setTitle("Drifting sinusoid stim num: " + str(self.stim_num))
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
        self.card1.setTexture(self.sinTextureStage, self.sinTexture)  #ts, tx
        
        #Transform the model(s)
        self.card1.setScale(np.sqrt(2))
        self.card1.setR(angles[self.stim_num])
        
        #Add task to taskmgr to translate texture 
        self.taskMgr.add(self.moveTextureTask, "moveTextureTask")
        
    #Procedure to move the camera
    def moveTextureTask(self, task):
        shiftMag = task.time*shift_velocity
        if task.time >= stim_change_times[self.stim_num] and stim_continue[self.stim_num]:
            stim_continue[self.stim_num] = False
            self.stim_num += 1
            self.card1.setR(angles[self.stim_num]) 
        self.card1.setTexPos(self.sinTextureStage, shiftMag, 0, 0) #u, v, w
        return Task.cont #as long as this is returned, the taskMgr will continue to call it
 

if __name__ == '__main__':
    app = MyApp()
    app.run()
