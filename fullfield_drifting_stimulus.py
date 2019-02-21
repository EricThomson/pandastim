"""
fullfield_drifting_stimulus.py part of pandastim package
Contains FullFieldDrift class to present full field drifting stimulus of any type.

Created using panda3d.  
https://github.com/EricThomson/pandastim  
"""
import numpy as np 
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import Texture, CardMaker, TextureStage
from panda3d.core import WindowProperties
import stimuli

class FullFieldDrift(ShowBase):
    """
    Takes in texture array
    Generates drifting texture.
    """
    def __init__(self, texture_array, angle = 0, velocity = 0.1, 
                 window_size = 512, texture_size = 512):
        super().__init__()
        
        self.texture_array = texture_array
        self.angle = angle
        self.velocity = velocity
        
        #Set window title (need to update with each stim) and size
        self.windowProps = WindowProperties()
        self.windowProps.setSize(window_size, window_size)
        self.windowProps.setTitle("FullFieldDrift: running")
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
        new_position = -task.time*self.velocity
        self.card1.setTexPos(self.textureStage, new_position, 0, 0) #u, v, w
        return Task.cont 
 
if __name__ == '__main__':
    #Test with grating
    stim_params = {'velocity': 0.1, 'spatial_freq': 15, 'angle': 45}
    texture_size = 512
    window_size = 512
    tex_array = stimuli.grating_texture_byte(texture_size, stim_params['spatial_freq'])
    pandastim_drifter = FullFieldDrift(tex_array, angle = stim_params["angle"], 
                                       velocity = stim_params["velocity"], window_size = window_size, 
                                       texture_size = texture_size)
    pandastim_drifter.run()
