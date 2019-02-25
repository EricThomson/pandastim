"""
pandastim/stimulus_classes.py
Classes to generate stimuli in pandastim: subclasses of Showbase.

Part of pandastim package: https://github.com/EricThomson/pandastim 

To do: 
    - fix up component selection currently just picks unsigned byte.
    - Write better docs so people can actually call this (stimulus_classes.py 2 or whtaewver)
    - consider renaming this module?
"""
import sys
import numpy as np 
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage
from panda3d.core import WindowProperties
from direct.showbase import ShowBaseGlobal  #global vars defined by p3d
from direct.task import Task
import textures

#%%
class FullFieldStatic(ShowBase):
    """
    Presents given texture array at given angle
    """
    def __init__(self, texture_array, angle = 0, window_size = 512, texture_size = 512):
        super().__init__()

        self.texture_array = texture_array
        self.ndims = self.texture_array.ndim
        self.angle = angle
        
        #Set window title (need to update with each stim) and size
        self.windowProps = WindowProperties()
        self.windowProps.setSize(window_size, window_size)
        self.windowProps.setTitle("FullFieldStatic( )")
        ShowBaseGlobal.base.win.requestProperties(self.windowProps)  #base is a panda3d global
        
        #Create texture stage
        self.texture = Texture("static")
               
        #Select Texture Format (color or b/w etc)
        #https://www.panda3d.org/reference/python/classpanda3d_1_1core_1_1Texture.html#ab4e88c89b3b7ea1735996cc4def22d58
        if self.ndims == 2:
            self.data_format = Texture.F_luminance #grayscale
        elif self.ndims == 3:
            self.data_format = Texture.F_rgb8
        else:
            raise ValueError("Texture needs to be 2d or 3d")

        #Select Texture ComponentType (e.g., uint8 or whatever)
        #https://www.panda3d.org/reference/python/classpanda3d_1_1core_1_1Texture.html#a81f78fc173dedefe5a049c0aa3eed2c0
        self.data_type = Texture.T_unsigned_byte
        
        self.texture.setup2dTexture(texture_size, texture_size, 
                               self.data_type, self.data_format) 
        
        self.texture.setRamImage(self.texture_array)   
        self.textureStage = TextureStage("static")
                                                                    
        #Create scenegraph
        cm = CardMaker('card1')
        cm.setFrameFullscreenQuad()
        self.card1 = self.aspect2d.attachNewNode(cm.generate())  
        self.card1.setTexture(self.textureStage, self.texture)  #ts, tx
       
        #Transform the model(s)
        self.card1.setScale(np.sqrt(2))
        self.card1.setR(self.angle)
        
#%%
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
        ShowBaseGlobal.base.win.requestProperties(self.windowProps)  #base is a panda3d global
        
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

#%%
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print(sys.argv[0], ": at command line enter 1 to test Static Grating, 2 Drifting Sin")
    else:
        test_case = sys.argv[1]
        
    if test_case == '1':
        #Test FullFieldStatic()
        stim_params = {'spatial_freq': 15, 'angle': -45}
        texture_size = 512
        window_size = 512
        grating_texture = textures.grating_texture_byte(texture_size, stim_params['spatial_freq'])
        pandastim_static = FullFieldStatic(grating_texture, angle = stim_params["angle"], 
                                            window_size = window_size, texture_size = texture_size)
        pandastim_static.run()
    elif test_case == '2':
        #Test FullFieldDrift()
        stim_params = {'velocity': 0.125, 'spatial_freq': 15, 'angle': 45}
        texture_size = 512
        window_size = 512
        tex_array = textures.grating_texture_byte(texture_size, stim_params['spatial_freq'])
        pandastim_drifter = FullFieldDrift(tex_array, angle = stim_params["angle"], 
                                           velocity = stim_params["velocity"], window_size = window_size, 
                                           texture_size = texture_size)
        pandastim_drifter.run()
        
    else:
        print("1 for FullFieldStatic(), 2 for FullFieldDrift()")


