"""
pandastim/stimulus_classes.py
Classes to present visual stimuli in pandastim: subclasses of Showbase.
Two main classes: 
    FullFieldStatic() -- show nonmoving textures
    FullFieldDrift() -- show textures that translate on each frame refresh

Part of pandastim package: https://github.com/EricThomson/pandastim 

Component types:
https://www.panda3d.org/reference/python/classpanda3d_1_1core_1_1Texture.html#a81f78fc173dedefe5a049c0aa3eed2c0
    T_unsigned_byte 	(1byte = 8 bits: 0 to 255)
    T_unsigned_short (2 bytes (16 bits): 0 to 65535, but this is platform dependent)
    T_float 	 (floats: not sure if single (32 bit) or double (64 bit))
    T_unsigned_int_24_8 	 (packed: one 24 bit for depth, one 8 bit for stencil)
    T_int 	(signed int)
    T_byte 	(signed byte: from -128 to 127)
    T_short 	(signed short: 2 bytes from -32768 to 32767)
    T_half_float (2 bytes: may sometimes be good if you are inside the 0-1 range)
    T_unsigned_int (4 bytes (32 bits): from 0 to ~4 billion)   

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
    Presents static (non-moving) texture arrray (numpy array), either grayscale (NxN array)
    or rgb (NxNx3 array).  Arrays are either one or two byte unsigned ints. 
    """
    def __init__(self, texture_array, angle = 0, window_size = 512, texture_size = 512):
        super().__init__()

        self.texture_array = texture_array
        self.texture_dtype = type(self.texture_array.flat[0])
        self.ndims = self.texture_array.ndim
        self.angle = angle
        
        #Set window title (need to update with each stim) and size
        self.windowProps = WindowProperties()
        self.windowProps.setSize(window_size, window_size)
        self.windowProps.setTitle("FullFieldStatic( )")
        ShowBaseGlobal.base.win.requestProperties(self.windowProps)  #base is a panda3d global
        
        #Create texture stage
        self.texture = Texture("static")
               
        #Select Texture ComponentType (e.g., uint8 or whatever)
        if self.texture_dtype == np.uint8:
            self.texture_component_type = Texture.T_unsigned_byte
        elif self.texture_dtype == np.uint16:
            self.texture_component_type = Texture.T_unsigned_short
        
        #Select Texture Format (color or b/w etc)
        if self.ndims == 2:
            self.texture_format = Texture.F_luminance #grayscale
            self.texture.setup2dTexture(texture_size, texture_size, 
                                   self.texture_component_type, self.texture_format)  
            self.texture.setRamImageAs(self.texture_array, "L") 
        elif self.ndims == 3:
            self.texture_format = Texture.F_rgb8
            self.texture.setup2dTexture(texture_size, texture_size, 
                                   self.texture_component_type, self.texture_format)  
            self.texture.setRamImageAs(self.texture_array, "RGB") 
        else:
            raise ValueError("Texture needs to be 2d or 3d")
       
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
        self.texture_dtype = type(self.texture_array.flat[0])
        self.ndims = self.texture_array.ndim
        self.angle = angle
        self.velocity = velocity
        
        #Set window title (need to update with each stim) and size
        self.windowProps = WindowProperties()
        self.windowProps.setSize(window_size, window_size)
        self.windowProps.setTitle("FullFieldDrift: running")
        ShowBaseGlobal.base.win.requestProperties(self.windowProps)  #base is a panda3d global
        
        #Create texture stage
        self.texture = Texture("drifting")
               
        #Select Texture ComponentType (e.g., uint8 or whatever)
        if self.texture_dtype == np.uint8:
            self.texture_component_type = Texture.T_unsigned_byte
        elif self.texture_dtype == np.uint16:
            self.texture_component_type = Texture.T_unsigned_short
        
        #Select Texture Format (color or b/w etc)
        if self.ndims == 2:
            self.texture_format = Texture.F_luminance #grayscale
            self.texture.setup2dTexture(texture_size, texture_size, 
                                   self.texture_component_type, self.texture_format)  
            self.texture.setRamImageAs(self.texture_array, "L") 
        elif self.ndims == 3:
            self.texture_format = Texture.F_rgb8
            self.texture.setup2dTexture(texture_size, texture_size, 
                                   self.texture_component_type, self.texture_format)  
            self.texture.setRamImageAs(self.texture_array, "RGB") 
        else:
            raise ValueError("Texture needs to be 2d or 3d")
       
        self.textureStage = TextureStage("drifting")
                                                                    
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
        print(sys.argv[0], ": at command line enter 1 to test Static Grating [default], 2 Drifting Sin.")
        test_case = '1'
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


