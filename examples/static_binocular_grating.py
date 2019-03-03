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
from textures import grating_texture_byte


class BinocularDrifting(ShowBase):
    def __init__(self, texture_array, angle = 0, position = (0, 0), velocity = 0,
                 band_radius = 3, window_size = 512, texture_size = 512, bgcolor = (0, 0, 0, 1)):
        super().__init__()

        self.texture_array = texture_array
        self.texture_dtype = type(self.texture_array.flat[0])
        self.ndims = self.texture_array.ndim
        self.angle = angle
        self.velocity = velocity
        
        #Set window title and size
        self.windowProps = WindowProperties()
        self.windowProps.setSize(window_size, window_size)
        self.windowProps.setTitle("BinocularStatic")
        ShowBaseGlobal.base.win.requestProperties(self.windowProps)  #base is a panda3d global
        
        #CREATE MASKS
        self.leftMask = 255*np.ones((texture_size,texture_size), dtype=np.uint8) 
        self.leftMask[:, :texture_size//2 + band_radius] = 0
        self.rightMask = 255*np.ones((texture_size,texture_size), dtype=np.uint8)    
        self.rightMask[:, texture_size//2 - band_radius:] = 0  
    
        #CREATE TEXTURE STAGES
        #Grating
        self.grating_texture = Texture("Grating")  #T_unsigned_byte
        self.grating_texture.setup2dTexture(texture_size, texture_size, Texture.T_unsigned_byte, Texture.F_luminance) 
        self.grating_texture.setRamImage(self.texture_array)   
        self.grating_texture_stage = TextureStage('sin')
        #Mask left (with card 1)
        self.leftMaskTex = Texture("left_mask")
        self.leftMaskTex.setup2dTexture(texture_size, texture_size, Texture.T_unsigned_byte, Texture.F_luminance) 
        self.leftMaskTex.setRamImage(self.leftMask)  
        self.leftMaskTexStage = TextureStage('left_mask')
        #Mask right (with card 2)
        self.rightMaskTex = Texture("right_mask")
        self.rightMaskTex.setup2dTexture(texture_size, texture_size, Texture.T_unsigned_byte, Texture.F_luminance) 
        self.rightMaskTex.setRamImage(self.rightMask)  
        self.rightMaskTexStage = TextureStage('right_mask')
                                                                           
        #CREATE CARDS/SCENEGRAPH
        cm = CardMaker('card1')
        cm.setFrameFullscreenQuad()
        self.card1 = self.aspect2d.attachNewNode(cm.generate())
        self.card2 = self.aspect2d.attachNewNode(cm.generate())
        
        #SET TEXTURE STAGES
        self.card1.setTexture(self.grating_texture_stage, self.grating_texture)  #ts, tx
        self.card1.setTexture(self.leftMaskTexStage, self.leftMaskTex)
        self.card2.setTexture(self.grating_texture_stage, self.grating_texture)  #ts, tx
        self.card2.setTexture(self.rightMaskTexStage, self.rightMaskTex)

        #Set attributes so both show brightly (do not use transparency attrib that's a trap)
        self.setBackgroundColor(bgcolor)  #set above
        self.card1.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
        self.card2.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
        
        #BASIC TRANSFORMS
        self.card1.setScale(np.sqrt(8))  #to handle shifts to +/-1
        self.card1.setR(self.angle) 
        self.card1.setPos(position[0], position[1], position[2])
        
        self.card2.setScale(np.sqrt(8))
        self.card2.setR(self.angle) 
        self.card2.setPos(position[0], position[1], position[2])
        
        self.title = OnscreenText("x",
                                  style = 1,
                                  fg = (1,1,1,1),
                                  bg = bgcolor,
                                  pos = (position[0], position[2]), 
                                  scale = 0.02)
        
        #Add texture move procedure to the task manager
        if self.velocity != 0:
            self.taskMgr.add(self.moveTextureTask, "moveTextureTask")
        
    #Procedure to move the camera
    def moveTextureTask(self, task):
        shiftMag = task.time*self.velocity
        self.card1.setTexPos(self.grating_texture_stage, shiftMag, 0, 0) #u, v, w
        self.card2.setTexPos(self.grating_texture_stage, -shiftMag, 0, 0) #u, v, w
        return Task.cont #as long as this is returned, the taskMgr will continue to call it
 

if __name__ == '__main__':
    stim_params = {'spatial_freq': 20, 'angle': 30, 'velocity': 0, 
                   'position': (0, 0, 0), 'band_radius': 4}
    texture_size = 512
    window_size = 512  
    bgcolor = (0, 0, 0, 1)
    grating_texture = grating_texture_byte(texture_size, stim_params['spatial_freq'])

    binocular_static = BinocularDrifting(grating_texture, 
                                       angle = stim_params["angle"],
                                       position = stim_params["position"], 
                                       velocity = stim_params["velocity"],
                                       band_radius = stim_params['band_radius'],
                                       window_size = window_size,
                                       texture_size = texture_size, 
                                       bgcolor = bgcolor)
    binocular_static.run()