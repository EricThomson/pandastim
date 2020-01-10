"""
TransformState is the under-the-hood class that Panda uses for storing any kind of transformation.

When you use nodepath.setPos(...) what Panda is actually doing is putting a TransformState on 
the underlying node with the given position.

The same goes for setTexPos/setTexRotate etc.

Though, when you use both setTexPos and setTexRotate, it composes the pos and rotation in the 
wrong order: it first applies the rotation, then the position, whereas you want it to be the other way around.

So, using the underlying TransformState API directly means you can compose the transform components in 
whatever order you want to.


To do:
    First write up:
     What is the origin?
     What is the uv range?
     How does it map to xy range of card?
    
    Set rotation to 0 (add that rotation method that rdb wrote to test all of these 
    always, at every x,y position) 
        check on x position
            +, scale, spin around the x
            
            -, scale, spin around the x
        check on y position (+/- values)
            +, scale
            -, scale
        x and y togeter with scaling
        try to figure out how to fucking handle scaling AAARGH
        
    Set position to 0
        check on rotation (+/- values)
        how to handle scaling?
    
    Set postion/rotation to arbitrary values
        +/-/scaling
        
For more detailed analysis of transforms:
    @neuronet also getTexTransform(ts) returns the TransformState on which you can 
    call getRotate2d(), getPos2d(), etc.
"""
import numpy as np 
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage, TransformState
from direct.gui.OnscreenText import OnscreenText   #for binocular stim
import matplotlib.pyplot as plt
    
class CombineStages(ShowBase):
    """Trying to draw a mask stage over a stim stage and combine them (modulate)
    Note debug variable is 1 to print vars, 2 to print vars and display mask from 
    matplotlib"""
    def __init__(self, texture_array, mask_angle, mask_position, debug):
        super().__init__()

        texture_size = 1024
        self.texture_array = texture_array
        self.mask_angle = mask_angle
        self.mask_position_ndc = mask_position
        #print(self.mask_position[0], self.mask_position[1])
        #print(self.ndc2uv(self.mask_position[0]), self.mask_position[1])
        self.mask_position_uv = (self.ndc2uv(self.mask_position_ndc[0]), self.ndc2uv(self.mask_position_ndc[1]))

        #CREATE MASK (zeros on left, 255s on right)
        self.right_mask = 255*np.ones((texture_size,texture_size), dtype=np.uint8)  #should set to 0/1 not 255?
        self.right_mask[:, texture_size//2: ] = 0   
        self.right_mask[texture_size//2 - 400:texture_size//2-300, -40:] = 120 #gray notch in RHS of zeros
        self.right_mask[texture_size//2 - 50:texture_size//2+50, 
                        texture_size//2: texture_size//2+80] = 180 #light notch in LHS of zeros
        
        if debug >= 2:
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

        #Set up grating texture stage and rotate it
        self.left_card.setTexture(self.left_texture_stage, self.grating_texture)  

        #Set up mask texture stage, rotate it and reposition it
        self.left_card.setTexture(self.right_mask_stage, self.right_mask_texture)
        
        #Text mark the origin in green
        self.title = OnscreenText("x", style = 1, fg = (1,0,0,1), bg = (0,1,0,1),
                          pos = (0,0), scale = 0.05)
        #Text mark the desired location in white x
        self.title = OnscreenText("x", style = 1, fg = (1,1,1,1), bg = (0,0,0,1),
                                  pos = self.mask_position_ndc, scale = 0.1)

        rot_shift_transform = self.ts_rot_shift_transform(self.mask_angle, 
                                                        self.mask_position_uv)
        
        if debug >= 1:
            print("\nMask before transform:")
            self.print_ts_info(self.left_card, self.right_mask_stage)
            
        self.left_card.setTexTransform(self.right_mask_stage, rot_shift_transform)

        if debug >= 1:
            print("\nMask after transform:")
            self.print_ts_info(self.left_card, self.right_mask_stage)
            
        #self.left_card.setTexOffset(self.right_mask_stage, -self.mask_position_uv[0], -self.mask_position_uv[1])
        #self.left_card.setScale(np.sqrt(8))  #to handle rotations and shifts  
        #print(self.left_card.getTexTransforms(self.right_mask_stage))
        
    def ts_rot_shift_transform(self, angle, newpos):
        center_shift = TransformState.make_pos2d((-0.5, -0.5))
        scale = TransformState.make_scale2d(1/np.sqrt(8))
        rotation = TransformState.make_rotate2d(angle)
        reposition = TransformState.make_pos2d((-0.5-newpos[0]/np.sqrt(8), -0.5-newpos[1]))

        return reposition.compose(rotation.compose(scale.compose(center_shift)))

    def print_ts_info(self, model, ts):
            print("offset: ", model.getTexOffset(ts))
            print("rot: ", model.getTexRotate(ts))
            return
            
    def ndc2uv(self, val):
        return 0.5*val # + 0.5
    
    def uv2nds(self, val):
        return 2*val
        
#%%
if __name__ == '__main__':
    debug = 1
    texture = np.array(np.random.rand(1024, 1024) * 255, dtype=np.uint8)  
    mask_position = (.20, .10)
    mask_angle = -20
    binocular_drifting = CombineStages(texture, mask_angle, mask_position, debug)
    binocular_drifting.run()
