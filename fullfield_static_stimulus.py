"""
pandastim/examples/fullfield_static_stimulus.py
Implements FullFieldStatic, class to present full field drifting stimulus of any type.

Part of pandastim package: https://github.com/EricThomson/pandastim 

To do: add ComponentType and texture Format.
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
import numpy as np 
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage
from panda3d.core import WindowProperties
from direct.showbase import ShowBaseGlobal  #global vars defined by p3d
import stimuli

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
              

 
if __name__ == '__main__':
    #Test with grating
    stim_params = {'spatial_freq': 15, 'angle': -45}
    texture_size = 512
    window_size = 512
    tex_array = stimuli.grating_texture_byte(texture_size, stim_params['spatial_freq'])
    pandastim_static = FullFieldStatic(tex_array, angle = stim_params["angle"], 
                                        window_size = window_size, texture_size = texture_size)
    pandastim_static.run()
