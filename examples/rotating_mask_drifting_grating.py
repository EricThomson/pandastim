"""
this is just some crazy stuff not documented but keeping it on hand to show what you can do
"""
import numpy as np 
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage
from panda3d.core import WindowProperties, ColorBlendAttrib, TransformState
from direct.showbase import ShowBaseGlobal  #global vars defined by p3d
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText   #for binocular stim
      
import sys
sys.path.append('..')  #put parent directory in python path
import textures  

def ndc2uv(val):
    """ from model-based normalized device coordinates to texture-based uv-coordinates"""
    return 0.5*val

def uv2ndc(val):
    """ from texture-based uv-coordinates to model-based normalized device coordinates"""
    return 2*val
       
class BinocularDrift(ShowBase):
    """
    Show binocular drifting textures forever.
    Takes in texture array and other parameters, and shows texture drifting indefinitely.
    Texture array can be grayscale or rgb, uint8 or uint16.
    
    Usage:
        BinocularDrift(texture_array, 
                        stim_angles = (0, 0), 
                        mask_angle = 0, 
                        position = (0,0),
                        velocity = 0.1,
                        band_radius = 3,
                        window_size = 512, 
                        texture_size = 512,
                        bgcolor = (0,0,0,1))
        
    Note(s): 
        angles are (left_texture_angle, right_texture_angle): >  is cw, < 0 cc2
        Velocity is in NDC, so 1.0 is the entire window width (i.e., super-fast).
        Make texture_size a power of 2: this makes the GPU happier.
        position is x,y in NDC (from [-1 1]), so (.5, .5) will be in top right quadrant of window.
        band_radius is just the half-width of the band in the middle. It can be 0.
        The texture array can be 2d (gray) or NxNx3 (rgb)
    """
    def __init__(self, texture_array, stim_angles = (0, 0), mask_angle = 0, position = (0, 0), velocity = 0,
                 band_radius = 3, window_size = 512, texture_size = 512, bgcolor = (0, 0, 0, 1)):
        super().__init__()

        self.mask_position_ndc = position
        self.mask_position_uv = (ndc2uv(self.mask_position_ndc[0]), 
                                 ndc2uv(self.mask_position_ndc[1]))
        self.mask_scale = np.sqrt(8)
        self.texture_array = texture_array
        self.texture_dtype = type(self.texture_array.flat[0])
        self.ndims = self.texture_array.ndim
        self.left_texture_angle = stim_angles[0]
        self.right_texture_angle = stim_angles[1]
        self.velocity = velocity
        self.mask_angle = mask_angle #this will change fairly frequently
        
        #Set window title and size
        self.window_properties = WindowProperties()
        self.window_properties.setSize(window_size, window_size)
        self.window_properties.setTitle("BinocularStatic")
        ShowBaseGlobal.base.win.requestProperties(self.window_properties)  #base is a panda3d global
        
        #CREATE MASKS (right mask for left stim, and vice-versa)
        self.right_mask = 255*np.ones((texture_size,texture_size), dtype=np.uint8)    
        self.right_mask[:, texture_size//2 - band_radius:] = 0  
    
        #CREATE TEXTURE STAGES
        #Grating texture 
        self.grating_texture = Texture("Grating")  #T_unsigned_byte
        self.grating_texture.setup2dTexture(texture_size, texture_size, 
                                            Texture.T_unsigned_byte, Texture.F_luminance) 
        self.grating_texture.setRamImage(self.texture_array)   
        self.left_texture_stage = TextureStage('grating')
        #Mask
        self.right_mask_texture = Texture("right_mask")
        self.right_mask_texture.setup2dTexture(texture_size, texture_size, 
                                               Texture.T_unsigned_byte, Texture.F_luminance) 
        self.right_mask_texture.setRamImage(self.right_mask)  
        self.right_mask_stage = TextureStage('right_mask')
        #Multiply the texture stages together
        self.right_mask_stage.setCombineRgb(TextureStage.CMModulate, 
                                    TextureStage.CSTexture, 
                                    TextureStage.COSrcColor,
                                    TextureStage.CSPrevious, 
                                    TextureStage.COSrcColor)    
                                                                           
        #CREATE CARDS/SCENEGRAPH
        cm = CardMaker('stimcard')
        cm.setFrameFullscreenQuad()
        self.left_card = self.aspect2d.attachNewNode(cm.generate())
        
        #SET TEXTURE STAGES
        self.left_card.setTexture(self.left_texture_stage, self.grating_texture)  
        self.left_card.setTexture(self.right_mask_stage, self.right_mask_texture)

        #Add texture move procedure to the task manager, if needed
        if self.velocity != 0:
            self.taskMgr.add(self.update_trs, "moveTextureTask")


        self.title = OnscreenText("x",
                                  style = 1,
                                  fg = (1,1,1,1),
                                  bg = (0,0,0,.8),
                                  pos = self.mask_position_ndc, 
                                  scale = 0.05)
        
    #Procedure to move the camera
    def update_trs(self, task):
        #Move texture in whatever direction
        new_texture_position = -task.time*self.velocity #negative b/c texture stage
        self.left_card.setTexPos(self.left_texture_stage, new_texture_position, 0, 0) 
        #Transform the mask so we only see some of the texture
        self.left_card.setTexTransform(self.right_mask_stage, self.trs_transform(task.time))
        return task.cont
    

    def trs_transform(self, elapsed_time):
        """ trs = translate rotate scale: transform for mask stage """        
        pos = 0.5 + self.mask_position_uv[0], 0.5 + self.mask_position_uv[1]
        center_shift = TransformState.make_pos2d((-pos[0], -pos[1]))
        scale = TransformState.make_scale2d(1/self.mask_scale)
        rotate = TransformState.make_rotate2d(np.mod(elapsed_time*40, 360))
        translate = TransformState.make_pos2d((0.5, 0.5))
        return translate.compose(rotate.compose(scale.compose(center_shift)))
    

    
#%%
if __name__ == '__main__':
    stim_params = {'spatial_freq': 15, 'stim_angles': (45, 30), 'velocity': .03, 
                   'position': (0, 0), 'band_radius': 4}
    mask_angle = -20
    texture_size = 512
    window_size = 512  
    bgcolor = (0, 0, 0, 1)
    grating_texture = textures.grating_texture(texture_size, 
                                               stim_params['spatial_freq'])

    binocular_drifting = BinocularDrift(grating_texture, 
                                       stim_angles = stim_params["stim_angles"],
                                       mask_angle = mask_angle,
                                       position = stim_params["position"], 
                                       velocity = stim_params["velocity"],
                                       band_radius = stim_params['band_radius'],
                                       window_size = window_size,
                                       texture_size = texture_size, 
                                       bgcolor = bgcolor)
    binocular_drifting.run()


