"""
pandastim/examples/static_binocular_grating.py
How to show different gratings to the left and right side of window.

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""
import sys
sys.path.append('..')  #put parent directory in python path


import numpy as np 
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage
from panda3d.core import ColorBlendAttrib, WindowProperties
from direct.gui.OnscreenText import OnscreenText 
from direct.showbase import ShowBaseGlobal  #global vars defined by p3d
from direct.task import Task
from textures import grating_texture


class BinocularDrift(ShowBase):
    """
    Show binocular drifting textures forever.
    Takes in texture array and other parameters, and shows texture drifting indefinitely.
    Texture array can be grayscale or rgb, uint8 or uint16.
    
    Usage:
        BinocularDrift(texture_array, 
                        angle = 0, 
                        position = (0,0),
                        velocity = 0.1,
                        band_radius = 3,
                        window_size = 512, 
                        texture_size = 512,
                        bgcolor = (0,0,0,1))
        
    Note(s): 
        Positive angles are clockwise, negative ccw.
        Velocity is in NDC, so 1.0 is the entire window width (i.e., super-fast).
        Make texture_size a power of 2: this makes the GPU happier.
        position is x,y in NDC (.5, .5) will be in top right quadrant of window.
        band_radius is just the half-width of the band in the middle. It can be 0.
        The texture array can be 2d (gray) or NxNx3 (rgb)
    """
    def __init__(self, texture_array, angle = 0, position = (0, 0), velocity = 0,
                 band_radius = 3, window_size = 512, texture_size = 512, bgcolor = (0, 0, 0, 1)):
        super().__init__()

        self.texture_array = texture_array
        self.texture_dtype = type(self.texture_array.flat[0])
        self.ndims = self.texture_array.ndim
        self.angle = angle
        self.velocity = velocity
        
        #Set window title and size
        self.window_properties = WindowProperties()
        self.window_properties.setSize(window_size, window_size)
        self.window_properties.setTitle("BinocularStatic")
        ShowBaseGlobal.base.win.requestProperties(self.window_properties)  #base is a panda3d global
        
        #CREATE MASKS
        self.left_mask = 255*np.ones((texture_size,texture_size), dtype=np.uint8) 
        self.left_mask[:, :texture_size//2 + band_radius] = 0
        self.right_mask = 255*np.ones((texture_size,texture_size), dtype=np.uint8)    
        self.right_mask[:, texture_size//2 - band_radius:] = 0  
    
        #CREATE TEXTURE STAGES
        #Grating
        self.grating_texture = Texture("Grating")  #T_unsigned_byte
        self.grating_texture.setup2dTexture(texture_size, texture_size, Texture.T_unsigned_byte, Texture.F_luminance) 
        self.grating_texture.setRamImage(self.texture_array)   
        self.grating_texture_stage = TextureStage('sin')
        #Mask left (with card 1)
        self.left_mask_texture = Texture("left_mask")
        self.left_mask_texture.setup2dTexture(texture_size, texture_size, Texture.T_unsigned_byte, Texture.F_luminance) 
        self.left_mask_texture.setRamImage(self.left_mask)  
        self.left_mask_stage = TextureStage('left_mask')
        #Mask right (with card 2)
        self.right_mask_texture = Texture("right_mask")
        self.right_mask_texture.setup2dTexture(texture_size, texture_size, Texture.T_unsigned_byte, Texture.F_luminance) 
        self.right_mask_texture.setRamImage(self.right_mask)  
        self.right_mask_stage = TextureStage('right_mask')
                                                                           
        #CREATE CARDS/SCENEGRAPH
        cm = CardMaker('right_card')
        cm.setFrameFullscreenQuad()
        self.right_card = self.aspect2d.attachNewNode(cm.generate())
        self.left_card = self.aspect2d.attachNewNode(cm.generate())
        
        #SET TEXTURE STAGES
        self.right_card.setTexture(self.grating_texture_stage, self.grating_texture)  
        self.right_card.setTexture(self.left_mask_stage, self.left_mask_texture)
        self.left_card.setTexture(self.grating_texture_stage, self.grating_texture)  
        self.left_card.setTexture(self.right_mask_stage, self.right_mask_texture)

        #Set attributes so both show brightly (do not use transparency attrib that's a trap)
        self.setBackgroundColor(bgcolor)  #set above
        self.right_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
        self.left_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
        
        #BASIC TRANSFORMS
        self.right_card.setScale(np.sqrt(8))  #sqrt8 to handle shifts to +/-1
        self.right_card.setR(self.angle) 
        self.right_card.setPos(position[0], position[1], position[2])
        
        self.left_card.setScale(np.sqrt(8))
        self.left_card.setR(self.angle) 
        self.left_card.setPos(position[0], position[1], position[2])
        
        self.title = OnscreenText("x",
                                  style = 1,
                                  fg = (1,1,1,1),
                                  bg = bgcolor,
                                  pos = (position[0], position[2]), 
                                  scale = 0.02)
        
        #Add texture move procedure to the task manager, if needed
        if self.velocity != 0:
            self.taskMgr.add(self.moveTextureTask, "moveTextureTask")
        
    #Procedure to move the camera
    def moveTextureTask(self, task):
        new_position = -task.time*self.velocity #not sure why negative
        self.right_card.setTexPos(self.grating_texture_stage, new_position, 0, 0) #u, v, w
        self.left_card.setTexPos(self.grating_texture_stage, new_position, 0, 0) #u, v, w
        return Task.cont #as long as this is returned, the taskMgr will continue to call it
 
class BinocularStatic(BinocularDrift):
    """
    Show static  binocular drifting textures forever.
    Child of BinocularDrift, with velocity automatically set to 0.
    
        BinocularDrift(texture_array, 
                        angle = 0, 
                        position = (0,0),
                        band_radius = 3,
                        window_size = 512, 
                        texture_size = 512,
                        bgcolor = (0,0,0,1))
    """
    def __init__(self, texture_array, angle = 0, position = (0, 0), band_radius = 3, 
                 window_size = 512, texture_size = 512, bgcolor = (0, 0, 0, 1)):
        self.velocity = 0
        super().__init__(texture_array, angle, position, self.velocity, 
                         band_radius, window_size, texture_size, bgcolor)

            
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print(sys.argv[0], ": at command line enter 1 to test Static binoc grating [default], 2 Drifting.")
        test_case = '1'
    else:
        test_case = sys.argv[1]
        
    if test_case == '1':
        stim_params = {'spatial_freq': 20, 'angle': 30, 
                       'position': (0, 0, 0), 'band_radius': 4}
        texture_size = 512
        window_size = 512  
        bgcolor = (0, 0, 0, 1)
        grating_texture = grating_texture(texture_size, stim_params['spatial_freq'])
    
        binocular_static = BinocularStatic(grating_texture, 
                                           angle = stim_params["angle"],
                                           position = stim_params["position"], 
                                           band_radius = stim_params['band_radius'],
                                           window_size = window_size,
                                           texture_size = texture_size, 
                                           bgcolor = bgcolor)
        binocular_static.run()
        
    elif test_case == '2':
        stim_params = {'spatial_freq': 30, 'angle': 30, 'velocity': 0.02, 
                       'position': (0, 0, 0), 'band_radius': 4}
        texture_size = 512
        window_size = 512  
        bgcolor = (0, 0, 0, 1)
        grating_texture = grating_texture(texture_size, stim_params['spatial_freq'])
    
        binocular_drifting = BinocularDrift(grating_texture, 
                                           angle = stim_params["angle"],
                                           position = stim_params["position"], 
                                           velocity = stim_params["velocity"],
                                           band_radius = stim_params['band_radius'],
                                           window_size = window_size,
                                           texture_size = texture_size, 
                                           bgcolor = bgcolor)
        binocular_drifting.run()
               
    else:
        print("1 for BinocularStatic(), 2 for BinocularDrift()")
    
    
    #hi