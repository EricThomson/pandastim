"""
pandastim/stimulus_classes.py
Classes to present visual stimuli in pandastim
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
from panda3d.core import WindowProperties, ColorBlendAttrib
from direct.showbase import ShowBaseGlobal  #global vars defined by p3d
from direct.task import Task
import textures
from direct.gui.OnscreenText import OnscreenText   #for binocular stim
        
class FullFieldDrift(ShowBase):
    """
    Show drifting texture forever.
    Takes in texture array and other parameters, and shows texture drifting indefinitely.
    Texture array can be grayscale or rgb.
    
    Usage:
        FullFieldStatic(texture_array, 
                        angle = 0, 
                        velocity = 0.1,
                        window_size = 512, 
                        texture_size = 512)
        
    Note(s): 
        Positive angles are clockwise, negative ccw.
        Velocity is in NDC, so 1.0 is the entire window width (i.e., super-fast).
        Make texture_size a power of 2: this makes the GPU happier.
        Textures are automatically scaled to fit window_size.
        The texture array can be np.uint8 or np.uint16, and 2d (gray) or NxNx3 (rgb)
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
        self.window_properties = WindowProperties()
        self.window_properties.setSize(window_size, window_size)
        self.window_properties.setTitle("FullFieldDrift: running")
        ShowBaseGlobal.base.win.requestProperties(self.window_properties)  #base is a panda3d global
        
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
        
        if self.velocity != 0:
            #Add task to taskmgr to translate texture 
            self.taskMgr.add(self.moveTextureTask, "moveTextureTask")
        
    #Move the texture
    def moveTextureTask(self, task):
        new_position = -task.time*self.velocity
        self.card1.setTexPos(self.textureStage, new_position, 0, 0) #u, v, w
        return Task.cont          

class FullFieldStatic(FullFieldDrift):
    """
    Show a single full-field texture.
    Child of FullFieldDrift, with velocity fixed at 0.
    
    FullFieldStatic(texture_array, 
                    angle = 0, 
                    window_size = 512, 
                    texture_size = 512)
    """
    def __init__(self, texture_array, angle = 0, window_size = 512, texture_size = 512):
        self.velocity = 0
        super().__init__(texture_array, angle, self.velocity, window_size, texture_size)
        
        
class BinocularDrift(ShowBase):
    """
    Show binocular drifting textures forever.
    Takes in texture array and other parameters, and shows texture drifting indefinitely.
    Texture array can be grayscale or rgb, uint8 or uint16.
    
    Usage:
        BinocularDrift(texture_array, 
                        stim_angles = (0, 0), 
                        animal_angle = 0, 
                        position = (0,0),
                        velocity = 0.1,
                        band_radius = 3,
                        window_size = 512, 
                        texture_size = 512,
                        bgcolor = (0,0,0,1))
        
    Note(s): 
        angles are (left_angle, right_angle): > 0 is cw, < 0 cc2
        Velocity is in NDC, so 1.0 is the entire window width (i.e., super-fast).
        Make texture_size a power of 2: this makes the GPU happier.
        position is x,y in NDC (from [-1 1]), so (.5, .5) will be in top right quadrant of window.
        band_radius is just the half-width of the band in the middle. It can be 0.
        The texture array can be 2d (gray) or NxNx3 (rgb)
    """
    def __init__(self, texture_array, stim_angles = (0, 0), animal_angle = 0, position = (0, 0), velocity = 0,
                 band_radius = 3, window_size = 512, texture_size = 512, bgcolor = (0, 0, 0, 1)):
        super().__init__()

        self.texture_array = texture_array
        self.texture_dtype = type(self.texture_array.flat[0])
        self.ndims = self.texture_array.ndim
        self.left_angle = stim_angles[0]
        self.right_angle = stim_angles[1]
        self.velocity = velocity
        self.animal_angle = animal_angle #this will change fairly frequently
        
        #Set window title and size
        self.window_properties = WindowProperties()
        self.window_properties.setSize(window_size, window_size)
        self.window_properties.setTitle("BinocularDrift")
        ShowBaseGlobal.base.win.requestProperties(self.window_properties)  #base is a panda3d global
        
        #CREATE MASKS (right mask for left stim, and vice-versa)
        self.right_mask = 255*np.ones((texture_size,texture_size), dtype=np.uint8)    
        self.right_mask[:, texture_size//2 - band_radius:] = 0  
        self.left_mask = 255*np.ones((texture_size,texture_size), dtype=np.uint8) 
        self.left_mask[:, :texture_size//2 + band_radius] = 0

    
        #CREATE TEXTURE STAGES
        #Stimuli
        self.grating_texture = Texture("Grating")  #T_unsigned_byte
        self.grating_texture.setup2dTexture(texture_size, texture_size, Texture.T_unsigned_byte, Texture.F_luminance) 
        self.grating_texture.setRamImage(self.texture_array)   
        self.grating_texture_stage = TextureStage('sin')
        #Left mask for right texture
        self.left_mask_texture = Texture("left_mask")
        self.left_mask_texture.setup2dTexture(texture_size, texture_size, Texture.T_unsigned_byte, Texture.F_luminance) 
        self.left_mask_texture.setRamImage(self.left_mask)  
        self.left_mask_stage = TextureStage('left_mask')
        #Right mask for left texture
        self.right_mask_texture = Texture("right_mask")
        self.right_mask_texture.setup2dTexture(texture_size, texture_size, Texture.T_unsigned_byte, Texture.F_luminance) 
        self.right_mask_texture.setRamImage(self.right_mask)  
        self.right_mask_stage = TextureStage('right_mask')
                                                                           
        #CREATE CARDS/SCENEGRAPH
        cm = CardMaker('stim_card')
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
        
        #BASIC TRANSFORMS to set up stimulus and animal angles
        self.right_card.setScale(np.sqrt(8))  #sqrt8 to handle shifts to +/-1
        #self.right_card.setR(self.right_angle) 
        #self.right_card.setPos(position[0], 0, position[1])
        
        #Set up stimulus angle
        self.left_card.setScale(np.sqrt(8))
        #Mask
        self.left_card.setTexRotate(self.right_mask_stage, self.animal_angle)
        self.left_card.setTexOffset(self.right_mask_stage, -.05, 0)  #position[0], position[1])
        #Texture
        self.left_card.setTexRotate(self.grating_texture_stage, self.left_angle)
        
        #Previous when both angles were same
        #self.left_card.setR(self.left_angle) 
        #self.left_card.setPos(position[0], 0, position[1])
        
        self.title = OnscreenText("x",
                                  style = 1,
                                  fg = (1,1,1,1),
                                  bg = bgcolor,
                                  pos = (position[0], position[1]), 
                                  scale = 0.02)
        
        #Add texture move procedure to the task manager, if needed
        if self.velocity != 0:
            self.taskMgr.add(self.moveTextureTask, "moveTextureTask")
        
    #Procedure to move the texture
    def moveTextureTask(self, task):
        new_position = -task.time*self.velocity #not sure why negative
        #self.right_card.setTexPos(self.grating_texture_stage, new_position, 0, 0) #u, v, w
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
        
        
#%%
if __name__ == '__main__':
    
    usage_note = "\nCommand line arguments:\n1: To test FullFieldStatic() [default]\n2: FullfieldDrift()\n"
    usage_note += "3: BinocularStatic()\n4: BinocularDrift()\n"
    
    if len(sys.argv) == 1:
        print(sys.argv[0], ": ", usage_note)
        test_case = '1'
        
    else:
        test_case = sys.argv[1]
        
    if test_case == '1':
        #Test FullFieldStatic()
        stim_params = {'spatial_freq': 15, 'angle': -45}
        texture_size = 512
        window_size = 512
        grating_texture = textures.grating_texture(texture_size, stim_params['spatial_freq'])
        pandastim_static = FullFieldStatic(grating_texture, angle = stim_params["angle"], 
                                            window_size = window_size, texture_size = texture_size)
        pandastim_static.run()
        
    elif test_case == '2':
        #Test FullFieldDrift()
        stim_params = {'velocity': 0.125, 'spatial_freq': 10, 'angle': 40}
        texture_size = 512
        window_size = 512
        tex_array = textures.sin_texture(texture_size, stim_params['spatial_freq'])
        pandastim_drifter = FullFieldDrift(tex_array, angle = stim_params["angle"], 
                                           velocity = stim_params["velocity"], window_size = window_size, 
                                           texture_size = texture_size)
        pandastim_drifter.run()
        
    elif test_case == '3':
        stim_params = {'spatial_freq': 20, 'angle': 30, 
                       'position': (0, 0), 'band_radius': 4}
        texture_size = 512
        window_size = 512  
        bgcolor = (0, 0, 0, 1)
        grating_texture = textures.grating_texture(texture_size, stim_params['spatial_freq'])
    
        binocular_static = BinocularStatic(grating_texture, 
                                           angle = stim_params["angle"],
                                           position = stim_params["position"], 
                                           band_radius = stim_params['band_radius'],
                                           window_size = window_size,
                                           texture_size = texture_size, 
                                           bgcolor = bgcolor)
        binocular_static.run()
        
    elif test_case == '4':
        stim_params = {'spatial_freq': 30, 'stim_angles': (90, 30), 'velocity': 0, 
                       'position': (0, 0), 'band_radius': 4}
        animal_angle = -20
        texture_size = 512
        window_size = 512  
        bgcolor = (0, 0, 0, 1)
        grating_texture = textures.grating_texture(texture_size, stim_params['spatial_freq'])
    
        binocular_drifting = BinocularDrift(grating_texture, 
                                           stim_angles = stim_params["stim_angles"],
                                           animal_angle = animal_angle,
                                           position = stim_params["position"], 
                                           velocity = stim_params["velocity"],
                                           band_radius = stim_params['band_radius'],
                                           window_size = window_size,
                                           texture_size = texture_size, 
                                           bgcolor = bgcolor)
        binocular_drifting.run()
        
    else:
        print(usage_note)


