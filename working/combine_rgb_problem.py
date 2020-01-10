"""
Combining rgb:
https://discourse.panda3d.org/t/ground-multitexturing-combine-textures-of-different-stages/2548/22
http://codepad.org/agsXeq6y


setSort:
https://www.panda3d.org/reference/python/classpanda3d_1_1core_1_1TextureStage.html#a1d878b27d5d0e934037e0943ab2fd881
Changes the order in which the texture associated with this stage is rendered relative to 
the other texture stages. When geometry is rendered with multiple textures, the textures 
are rendered in order from the lowest sort number to the highest sort number. 

Also see set_priority(), which is used to select the most important textures for 
rendering when some must be omitted because of hardware limitations


setPriority:
https://www.panda3d.org/reference/python/classpanda3d_1_1core_1_1TextureStage.html#a7a16b2f1541010eed0ce76b5daba7e89

Changes the relative importance of the texture associated with this stage relative to 
the other texture stages that are applied simultaneously. This is unrelated to set_sort(), 
which controls the order in which multiple textures are applied. 

The priority number is used to decide which of the requested textures are to be selected for rendering 
when more textures are requested than the hardware will support. The highest-priority n textures are 
selected for rendering, and then rendered in order by their sort factor.

"""
import numpy as np 
from scipy import signal  #for grating (square wave)

from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage
from panda3d.core import TransparencyAttrib
   
#Define texture (simple grating)
def grating_byte(X, freq = 1):
    grating_float = signal.square(X*freq)
    grating_transformed = (grating_float+1)*127.5; #from 0-255
    return np.uint8(grating_transformed)

def grating_texture(texture_size = 512, spatial_frequency = 10):
    x = np.linspace(0, 2*np.pi, texture_size+1)
    y = np.linspace(0, 2*np.pi, texture_size+1)
    X, Y = np.meshgrid(x[:texture_size],y[:texture_size])
    return grating_byte(X, freq = spatial_frequency)
        

class CombineCards(ShowBase):
    """Trying to draw a mask card over a texture card and combine them (modulate)"""
    def __init__(self, texture_array, texture_angle = 0, mask_angle = 0, 
                 window_size = 512, texture_size = 512):
        super().__init__()

        self.texture_array = texture_array
        self.left_angle = texture_angle
        self.mask_angle = mask_angle #this will change fairly frequently
        #self.setBackgroundColor((0,0,0,1))  #set above

        #CREATE MASK
        self.right_mask = 255*np.ones((texture_size,texture_size), dtype=np.uint8)  #should set to 0/1 not 255
        self.right_mask[:, texture_size//2: ] = 0   #texture_size//2:] = 0  
        #print(self.right_mask)

        #CREATE TEXTURE STAGES
        #Texture
        self.grating_texture = Texture("Grating")  #T_unsigned_byte
        self.grating_texture.setup2dTexture(texture_size, texture_size, 
                                            Texture.T_unsigned_byte, Texture.F_luminance) 
        self.grating_texture.setRamImage(self.texture_array)   
        self.left_texture_stage = TextureStage('grating')
        self.left_texture_stage.setSort(0)
        
        #Mask
        self.right_mask_texture = Texture("right_mask")
        self.right_mask_texture.setup2dTexture(texture_size, texture_size, 
                                               Texture.T_unsigned_byte, Texture.F_luminance) 
        self.right_mask_texture.setRamImage(self.right_mask)  
        self.right_mask_stage = TextureStage('right_mask')
        self.right_mask_stage.setSort(1)
        
                                                                           
        #CREATE CARDS/SCENEGRAPH
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        
        #Set up left texture card
        self.left_texture_card = self.aspect2d.attachNewNode(cm.generate())
        self.left_texture_card.setTexture(self.left_texture_stage, self.grating_texture)  
        self.left_texture_card.setScale(np.sqrt(8))  #so it can handle arbitrary rotations and shifts    
        self.left_texture_card.setR(self.left_angle) 
        self.left_texture_card.setTransparency(TransparencyAttrib.MAlpha)
        print(self.left_texture_card.getColor())
        self.left_texture_card.setColor(1,1,1,0)
       
        #Set up right mask card
        self.right_mask_card = self.aspect2d.attachNewNode(cm.generate())
        self.right_mask_card.setTexture(self.right_mask_stage, self.right_mask_texture)
        self.right_mask_card.setScale(np.sqrt(8))
        self.right_mask_card.setR(self.mask_angle)
        self.right_mask_card.setTransparency(TransparencyAttrib.MAlpha)  
        self.right_mask_card.setColor(1,1,1,0)
        
        #The following yields error
        self.right_mask_stage.setCombineRgb(TextureStage.CMModulate, 
                                    TextureStage.CSTexture, 
                                    TextureStage.COSrcColor,
                                    TextureStage.CSPrevious, 
                                    TextureStage.COSrcColor) 


#%%
if __name__ == '__main__':
    mask_orientation = 0
    texture_orientation = 90
    stim_params = {'spatial_freq': 20, 'stim_angle': texture_orientation}
    animal_angle = mask_orientation
    texture_size = 512
    window_size = 512  
    bgcolor = (0, 0, 0, 1)
    grating_texture = grating_texture(texture_size, stim_params['spatial_freq'])

    binocular_drifting = CombineCards(grating_texture, 
                                       texture_angle = stim_params["stim_angle"],
                                       mask_angle = mask_orientation,
                                       window_size = window_size,
                                       texture_size = texture_size)
    binocular_drifting.run()


