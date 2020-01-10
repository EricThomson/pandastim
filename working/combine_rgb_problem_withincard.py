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
import sys
import numpy as np 
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage
from direct.gui.OnscreenText import OnscreenText   #for binocular stim
import matplotlib.pyplot as plt

        
def ndc2uv(val):
    """convert normalized d coords [-1, 1] to uv coordinates [0 1]"""
    return 0.5*val + 0.5

    
class CombineStages(ShowBase):
    """Trying to draw a mask stage over a stim stage and combine them (modulate)"""
    def __init__(self, texture_array, texture_angle = 0, mask_angle = 0, mask_position = (0,0),
                 window_size = 512, texture_size = 512):
        super().__init__()

        self.texture_array = texture_array
        self.left_angle = texture_angle
        self.mask_angle = mask_angle #this will change fairly frequently
        self.mask_position = (ndc2uv(mask_position[0]), ndc2uv(mask_position[1]))
        #self.setBackgroundColor((0,0,0,1))  #set above

        #CREATE MASK
        self.right_mask = 255*np.ones((texture_size,texture_size), dtype=np.uint8)  #should set to 0/1 not 255
        self.right_mask[:, texture_size//2: ] = 0   #texture_size//2:] = 0  
        plt.imshow(self.right_mask, cmap = 'gray')
        plt.show()

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
        
                                                                           
        #Create card
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        self.left_card = self.aspect2d.attachNewNode(cm.generate())
        self.left_card.setScale(np.sqrt(8))  #to handle rotations and shifts  
        
        #Set up grating texture stage and rotate it
        self.left_card.setTexture(self.left_texture_stage, self.grating_texture)  
        self.left_card.setTexRotate(self.left_texture_stage, self.left_angle) 

        #Set up mask texture stage, rotate it and reposition it
        self.left_card.setTexture(self.right_mask_stage, self.right_mask_texture)
        self.left_card.setTexRotate(self.right_mask_stage, self.mask_angle)
        self.left_card.setTexOffset(self.right_mask_stage, 
                                    self.mask_position[0], self.mask_position[1])
        
        #Best way to combine them
        self.right_mask_stage.setCombineRgb(TextureStage.CMModulate, 
                                    TextureStage.CSTexture, 
                                    TextureStage.COSrcColor,
                                    TextureStage.CSPrevious, 
                                    TextureStage.COSrcColor) 
        #To show where the mask should be starting
        self.title = OnscreenText("x",
                                  style = 1,
                                  fg = (1,1,1,1),
                                  bg = (0,0,0,1),
                                  pos = (-mask_position[0], -mask_position[1]), 
                                  scale = 0.1)

        
#%%
if __name__ == '__main__':
    
    
    
    usage_note = "1 for mask not rotated/shifted [default]\n2: mask rotated 20 degrees"
    usage_note += "\n3: mask shifted (.2, .2)\n4: rotated and shifted.\n"
    if len(sys.argv) == 1:
        print(sys.argv[0], ": ", usage_note)
        test_case = '1'
    else:
        test_case = sys.argv[1]
    
    position_val = -0.3
    if test_case == '1':
        mask_orientation = 0
        texture_orientation = 90
        mask_position = (0,0)
    elif test_case == '2':
        mask_orientation = 20
        texture_orientation = 90
        mask_position = (0,0)
    elif test_case == '3':
        mask_orientation = 0
        texture_orientation = 90
        mask_position = (position_val, position_val)
    elif test_case == '4':
        mask_orientation = 20
        texture_orientation = 90
        mask_position = (position_val, position_val)
      
    texture_size = 1024
    window_size = 1024
    stim_params = {'spatial_freq': 30, 'stim_angle': texture_orientation}
    texture = np.array(np.random.rand(texture_size, texture_size) * 255, dtype=np.uint8)  
    binocular_drifting = CombineStages(texture,
                                       texture_angle = stim_params["stim_angle"],
                                       mask_angle = mask_orientation,
                                       mask_position = mask_position,
                                       window_size = window_size,
                                       texture_size = texture_size)
    binocular_drifting.run()


