"""
drifting_sinusoid_stimulus(): pandastim package
Single full-field drifting sinusoid.

To do:
    Functionalize app stop using globals
    
    
    
"""
import numpy as np 
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import Texture, CardMaker, TextureStage
from panda3d.core import WindowProperties
import stimuli


#%%
class MyApp(ShowBase):
    def __init__(self, texture_array, angle, velocity, 
                 window_size = 512, texture_size = 512):
        super().__init__()
        
        self.texture_array = texture_array
        self.angle = angle
        self.velocity = velocity
        
        #Set window title (need to update with each stim) and size
        self.windowProps = WindowProperties()
        self.windowProps.setSize(window_size, window_size)
        self.windowProps.setTitle("Full field: running")
        base.win.requestProperties(self.windowProps)  #base is a panda3d global
        
        #Create texture stage
        self.texture = Texture("sin")
               
        self.texture.setup2dTexture(texture_size, texture_size, 
                               Texture.T_unsigned_byte, Texture.F_luminance) 
        
        self.texture.setRamImage(self.texture_array)   
        self.textureStage = TextureStage("sin")
                                                                    
        #Create scenegraph
        cm = CardMaker('card1')
        cm.setFrameFullscreenQuad()
        self.card1 = self.aspect2d.attachNewNode(cm.generate())  
        self.card1.setTexture(self.textureStage, self.texture)  #ts, tx
       
        #Transform the model(s)
        self.card1.setScale(np.sqrt(2))
        self.card1.setR(self.angle)
        
        #Add task to taskmgr to translate texture 
        self.taskMgr.add(self.moveTextureTask, "moveTextureTask")
        
    def moveTextureTask(self, task):
        new_position = task.time*self.velocity
        self.card1.setTexPos(self.textureStage, new_position, 0, 0) #u, v, w
        return Task.cont 
 
if __name__ == '__main__':
    
    #Stim params
    stim_params = {'velocity': 0.1, 'spatial_freq': 30, 'angle': 90}
    #Windows
    texture_size = 512
    window_size = 512
    #Create texture
    tex_array = stimuli.grating_texture_byte(texture_size, stim_params['spatial_freq'])
    app = MyApp(tex_array, stim_params["angle"], stim_params["velocity"], 
                window_size = window_size, texture_size = texture_size)
    app.run()
