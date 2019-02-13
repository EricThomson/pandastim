"""
blah blah bglah

"""
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage
from panda3d.core import ColorBlendAttrib, WindowProperties
import numpy as np 
from scipy import signal
from direct.gui.OnscreenText import OnscreenText 
from direct.task import Task

#General parameters
window_size = 500
bgcolor = (0, 0, 0, 1)

#Stim features
texSize = 1024
bandRadius = 3  #pixels in original image: this will be scaled
frequency = 15
rotation = -40
position = (-0.2, 0, 0.1)  #x,y,z
if abs(position[0]) > 1 or abs(position[2]) > 1:
    raise ValueError('Position shift must remain within NDC [-1, 1]')
    
print("Position: ", position)

#Grating
spatial_freq = 20
def squareWave(X, freq = 1):
    return signal.square(X*freq)
def square8bit(X, freq = 1):
    square_float = squareWave(X, freq = freq)
    square_pos = (square_float+1)*127.5; #from 0-255
    return np.asarray(square_pos, dtype = np.uint8)
x = np.linspace(0, 2*np.pi, texSize+1)
y = np.linspace(0, 2*np.pi, texSize+1)
X, Y = np.meshgrid(x[:texSize], y[:texSize])
sinTex = square8bit(X, spatial_freq)


#%% try plotting it
#import matplotlib.pyplot as plt
#plt.plot(sinTex[1,:])

#%%
#Create masks
leftMask = 255*np.ones((texSize,texSize), dtype=np.uint8)      #127.5
leftMask[:, :texSize//2 + bandRadius] = 0
rightMask = 255*np.ones((texSize,texSize), dtype=np.uint8)      #127.5
rightMask[:, texSize//2 - bandRadius:] = 0  #Check index on this

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        #Set window title and size
        self.windowProps = WindowProperties()
        self.windowProps.setSize(window_size, window_size)
        self.windowProps.setTitle("Drifting grating")
        base.win.requestProperties(self.windowProps)  #base is a panda3d global
        
        #CREATE TEXTURE STAGES
        #Sine
        self.sinTexture = Texture("sin")  #T_unsigned_byte
        self.sinTexture.setup2dTexture(texSize, texSize, Texture.T_unsigned_byte, Texture.F_luminance) 
        self.sinTexture.setRamImage(sinTex)   
        self.sinTextureStage = TextureStage('sin')
        #Mask left (with card 1)
        self.leftMaskTex = Texture("left_mask")
        self.leftMaskTex.setup2dTexture(texSize, texSize, Texture.T_unsigned_byte, Texture.F_luminance) 
        self.leftMaskTex.setRamImage(leftMask)  
        self.leftMaskTexStage = TextureStage('left_mask')
        #Mask right (with card 2)
        self.rightMaskTex = Texture("right_mask")
        self.rightMaskTex.setup2dTexture(texSize, texSize, Texture.T_unsigned_byte, Texture.F_luminance) 
        self.rightMaskTex.setRamImage(rightMask)  
        self.rightMaskTexStage = TextureStage('right_mask')
                                                                           
        #CREATE CARDS/SCENEGRAPH
        cm = CardMaker('card1')
        cm.setFrameFullscreenQuad()
        self.card1 = self.aspect2d.attachNewNode(cm.generate())
        self.card2 = self.aspect2d.attachNewNode(cm.generate())
        
        #SET TEXTURE STAGES
        self.card1.setTexture(self.sinTextureStage, self.sinTexture)  #ts, tx
        self.card1.setTexture(self.leftMaskTexStage, self.leftMaskTex)
        self.card2.setTexture(self.sinTextureStage, self.sinTexture)  #ts, tx
        self.card2.setTexture(self.rightMaskTexStage, self.rightMaskTex)

        #Set attributes so both show brightly (do not use transparency attrib that's a trap)
        self.setBackgroundColor(bgcolor)  #set above
        self.card1.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
        self.card2.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
        
               
        #BASIC TRANSFORMS
        self.card1.setScale(np.sqrt(8))  #to handle shifts to +/-1
        self.card1.setR(rotation) 
        self.card1.setPos(position[0], position[1], position[2])
        
        self.card2.setScale(np.sqrt(8))
        self.card2.setR(rotation) 
        self.card2.setPos(position[0], position[1], position[2])
        
        self.title = OnscreenText("x",
                                  style = 1,
                                  fg = (1,1,1,1),
                                  bg = bgcolor,
                                  pos = (position[0], position[2]), 
                                  scale = 0.02)
        
        #Add texture move procedure to the task manager
        self.taskMgr.add(self.moveTextureTask, "moveTextureTask")
        
    #Procedure to move the camera
    def moveTextureTask(self, task):
        shiftMag = task.time*0.1
        self.card1.setTexPos(self.sinTextureStage, shiftMag, 0, 0) #u, v, w
        self.card2.setTexPos(self.sinTextureStage, -shiftMag, 0, 0) #u, v, w
        return Task.cont #as long as this is returned, the taskMgr will continue to call it
 

if __name__ == '__main__':
    app = MyApp()
    app.run()
