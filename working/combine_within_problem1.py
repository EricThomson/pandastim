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
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage, TransformState
from direct.gui.OnscreenText import OnscreenText   #for binocular stim
import matplotlib.pyplot as plt
    
class CombineStages(ShowBase):
    """Trying to draw a mask stage over a stim stage and combine them (modulate)"""
    def __init__(self, texture_array):
        super().__init__()

        texture_size = 1024
        self.texture_array = texture_array
        self.mask_angle = 10
        self.mask_position = (0,0)

        #CREATE MASK (zeros on left, 255s on right)
        self.right_mask = 255*np.ones((texture_size,texture_size), dtype=np.uint8)  #should set to 0/1 not 255
        self.right_mask[:, texture_size//2: ] = 0   

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
                                     
        #CREATE SCENE GRAPH
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        self.left_card = self.aspect2d.attachNewNode(cm.generate())
        self.left_card.setTexture(self.left_texture_stage, self.grating_texture)  
        self.left_card.setTexture(self.right_mask_stage, self.right_mask_texture)
        self.left_card.setScale(np.sqrt(8))  #to handle rotations and shifts  
        
        #Transforms: following from rdb@discord
        #self.left_card.setTexRotate(self.right_mask_stage, self.mask_angle)
        position_transform = TransformState.make_pos2d((-0.5, -0.5))
        rotation_transform = TransformState.make_rotate2d(self.mask_angle)
        self.left_card.setTexTransform(self.right_mask_stage, rotation_transform.compose(position_transform))
        
        #To show where I want the mask
        self.title = OnscreenText("x", style = 1, fg = (1,1,1,1), bg = (0,0,0,1),
                                  pos = (0, 0), scale = 0.1)
        
#        taskMgr.add(self.update)
#
#    def update(self, task):
#        pos = TransformState.make_pos2d((-0.5, -0.5))
#        rot = TransformState.make_rotate2d(task.time * 90)
#        self.left_card.setTexTransform(self.right_mask_stage, rot.compose(pos))
#


#%%
if __name__ == '__main__':
    texture = np.array(np.random.rand(1024, 1024) * 255, dtype=np.uint8)  
    binocular_drifting = CombineStages(texture)
    binocular_drifting.run()


