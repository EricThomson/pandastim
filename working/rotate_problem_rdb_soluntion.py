"""
TransformState is the under-the-hood class that Panda uses for storing any kind of transformation.

When you use nodepath.setPos(...) what Panda is actually doing is putting a TransformState on 
the underlying node with the given position.

The same goes for setTexPos/setTexRotate etc.

Though, when you use both setTexPos and setTexRotate, it composes the pos and rotation in the 
wrong order: it first applies the rotation, then the position, whereas you want it to be the other way around.

So, using the underlying TransformState API directly means you can compose the transform components in 
whatever order you want to.
"""
import numpy as np 
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage, TransformState
from direct.gui.OnscreenText import OnscreenText   #for binocular stim
    
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
        #plt.imshow(self.right_mask, cmap = 'gray')
        #plt.show()

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
        #self.left_card.setScale(np.sqrt(8))  #to handle rotations and shifts  
        #Set up grating texture stage and rotate it
        self.left_card.setTexture(self.left_texture_stage, self.grating_texture)  

        #Set up mask texture stage, rotate it and reposition it
        self.left_card.setTexture(self.right_mask_stage, self.right_mask_texture)
        
        #To show where I want the mask centered
        self.title = OnscreenText("x", style = 1, fg = (1,1,1,1), bg = (0,0,0,1),
                                  pos = (0, 0), scale = 0.1)

        taskMgr.add(self.update)

    def update(self, task):
        pos = TransformState.make_pos2d((-0.5, -0.5))
        rot = TransformState.make_rotate2d(task.time * 90)
        self.left_card.setTexTransform(self.right_mask_stage, rot.compose(pos))

        return task.cont
        
#%%
if __name__ == '__main__':
    texture = np.array(np.random.rand(1024, 1024) * 255, dtype=np.uint8)  
    binocular_drifting = CombineStages(texture)
    binocular_drifting.run()