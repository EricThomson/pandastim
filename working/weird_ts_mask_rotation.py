"""
try8ing to version 2 of binocular drift working with arbityrary fish angle and 
stimulus angles in each side.

Why does the transforms look so different when I apply it for one versus the other?
(I have taken the negative values)

Note standard texture coordinates are [-1,1] while
the uv coordintaes for texture stages are [0,1] so you 
have to translate unfortunateluy (e.g., -.5, -.5 = .5, .5)

Also, the rotation in standard texture is wrt 0 (i.e., center) while
in uv coordinates it is also , but that means wrt lower left.

Isn't it possible to just tell panda3d to set uv as -1,1? Because this shit will also
throw off the scale significantly.

What I expect: 90 degree grating on the left hand side masked out on the right-hand side,
but with a mask that is tilted by 45 degrees.

Why with mask rotation 0 is the actual texture and mask reversed, even for 0,0?
"""
import numpy as np 
from scipy import signal  #for grating (square wave)
import matplotlib.pyplot as plt

from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage
from panda3d.core import WindowProperties, ColorBlendAttrib, TransparencyAttrib
from direct.showbase import ShowBaseGlobal  #global vars defined by p3d
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText   #for binocular stim

   
#Define texture
def grating_byte(X, freq = 1):
    grating_float = signal.square(X*freq)
    grating_transformed = (grating_float+1)*127.5; #from 0-255
    return np.uint8(grating_transformed)


def grating_texture(texture_size = 512, spatial_frequency = 10):
    x = np.linspace(0, 2*np.pi, texture_size+1)
    y = np.linspace(0, 2*np.pi, texture_size+1)
    X, Y = np.meshgrid(x[:texture_size],y[:texture_size])
    return grating_byte(X, freq = spatial_frequency)

def ndc2uv(val):
    return -(0.5*val + 0.5)

        
class LeftDrift(ShowBase):
    """
    Show drifting textures forever to left eye.
    """
    def __init__(self, texture_array, texture_angle = 0, mask_angle = 0, position = (0, 0), velocity = 0,
                 window_size = 512, texture_size = 512, bgcolor = (0, 0, 0, 1)):
        super().__init__()

        self.texture_array = texture_array
        self.texture_dtype = type(self.texture_array.flat[0])
        self.left_angle = texture_angle
        self.velocity = velocity
        self.mask_angle = mask_angle #this will change fairly frequently
        
        #Set window title and size
        self.window_properties = WindowProperties()
        self.window_properties.setSize(window_size, window_size)
        self.window_properties.setTitle("LeftDrift")
        ShowBaseGlobal.base.win.requestProperties(self.window_properties)  #base is a panda3d global
        
        #CREATE MASKS (right mask for left stim, and vice-versa)
        self.right_mask = np.ones((texture_size,texture_size), dtype=np.uint8)    #was 255* this but for modulate 
        self.right_mask[:, texture_size//2: ] = 0   #texture_size//2:] = 0  
        #print(self.right_mask)

        #CREATE TEXTURE STAGES
        #Stimuli
        self.grating_texture = Texture("Grating")  #T_unsigned_byte
        self.grating_texture.setup2dTexture(texture_size, texture_size, 
                                            Texture.T_unsigned_byte, Texture.F_luminance) 
        self.grating_texture.setRamImage(self.texture_array)   
        self.left_texture_stage = TextureStage('grating')
        #Mask to restrict stimulus to LHS
        self.right_mask_texture = Texture("right_mask")
        self.right_mask_texture.setup2dTexture(texture_size, texture_size, 
                                               Texture.T_unsigned_byte, Texture.F_luminance) 
        self.right_mask_texture.setRamImage(self.right_mask)  
        self.right_mask_stage = TextureStage('right_mask')
                                                                           
        #CREATE CARDS/SCENEGRAPH
        cm = CardMaker('left_stim_card')
        cm.setFrameFullscreenQuad()
        self.left_texture_card = self.aspect2d.attachNewNode(cm.generate())
        self.right_mask_card = self.aspect2d.attachNewNode(cm.generate())
        
        #SET TEXTURE STAGES
        self.left_texture_card.setTexture(self.left_texture_stage, self.grating_texture)  
        self.right_mask_card.setTexture(self.right_mask_stage, self.right_mask_texture)

        
        #BASIC TRANSFORMS to set up angles and position 
        #TEXTURE
        self.left_texture_card.setScale(np.sqrt(8))  #so it can handle arbitrary rotations and shifts    
        self.left_texture_card.setR(self.left_angle) 
        
        #MASK
        #self.right_card.setPos(position[0], 0, position[1])
        self.right_mask_card.setScale(np.sqrt(8))
        self.right_mask_card.setR(self.mask_angle)
        self.right_mask_card.setPos(position[0], 0, position[1] ) # ndc2uv(position[0]), ndc2uv(position[1]))

        self.right_mask_card.setTransparency(TransparencyAttrib.MAlpha)  #enable transparency
        #Combine the two cards (take product of mask and texture)
        operand = TextureStage.COSrcColor
        source0 = self.right_mask_stage
        source1 = self.left_texture_stage
        self.right_mask_stage.setCombineRgb(TextureStage.CMModulate, source0, operand, source1, operand)
        #self.left_texture_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
        #self.left_texture_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
        
        #This puts a marker where the stimulus should end
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
        self.left_texture_card.setTexPos(self.left_texture_stage, new_position, 0, 0) #u, v, w
        return Task.cont #as long as this is returned, the taskMgr will continue to call it
 
        
#%%
if __name__ == '__main__':
    mask_orientation = 20
    texture_orientation = 90
    stim_params = {'spatial_freq': 20, 'stim_angle': texture_orientation, 'velocity': .04, 
                   'position': (.25, 0.5)}
    animal_angle = mask_orientation
    texture_size = 512
    window_size = 512  
    bgcolor = (0, 0, 0, 1)
    grating_texture = grating_texture(texture_size, stim_params['spatial_freq'])

    binocular_drifting = LeftDrift(grating_texture, 
                                       texture_angle = stim_params["stim_angle"],
                                       mask_angle = mask_orientation,
                                       position = stim_params["position"], 
                                       velocity = stim_params["velocity"],
                                       window_size = window_size,
                                       texture_size = texture_size, 
                                       bgcolor = bgcolor)
    binocular_drifting.run()


