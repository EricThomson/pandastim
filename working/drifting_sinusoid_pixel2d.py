"""
static_sinusoid_pixel2d(): pandastim package
Single static sinusoid


On setting it uP:
1 pixel is 1 unit, so if you have a card with the default frame of 0-1 set 
then it will show up one pixel large. Alternatively you can use setFrame on 
the CardMaker to set a proper frame

Note the origin of the card is the top right corner by convention, so it will not 
appear on screen.

"""
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage, WindowProperties
import numpy as np 
from direct.task import Task

#Basic properties
window_size = 512

#Create sin
texture_size = 512
spatial_freq = 6
speed = .2

def sin3d(X, freq = 1):
    return np.sin(X*freq)
def sin8bit(X, freq = 1):
    sin_float = sin3d(X, freq=freq)
    sin_pos = (sin_float+1)*127.5; #from 0-255
    return np.asarray(sin_pos, dtype = np.uint8)
x = np.linspace(0, 2*np.pi, texture_size+1)
y = np.linspace(0, 2*np.pi, texture_size+1)
X, Y = np.meshgrid(x[:texture_size],y[:texture_size])
sin_texture = sin8bit(X, freq = spatial_freq);


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        #Set window title (need to update with each stim)
        self.windowProps = WindowProperties()
        self.windowProps.setSize(window_size, window_size)
        self.windowProps.setTitle("Full field static sine")
        base.win.requestProperties(self.windowProps)  #base is a panda3d global
        
        #Create texture stage
        self.sinTexture = Texture("sin")
        self.sinTexture.setup2dTexture(texture_size, texture_size, Texture.T_unsigned_byte, Texture.F_luminance) 
        self.sinTexture.setRamImage(sin_texture)   
        self.sinTextureStage = TextureStage('sin')
                                                                    
        #Create scenegraph
        cm = CardMaker('card1')
        #Initialize card at origin (top left of window)
        cm.setFrame(-texture_size//2, texture_size//2, -texture_size//2, texture_size//2)  #left right bottom top
        #cm.setFrame(0, texture_size, 0, -texture_size)  #left right bottom top        
        
        self.card1 = self.pixel2d.attachNewNode(cm.generate())
        self.card1.setTexture(self.sinTextureStage, self.sinTexture)  #ts, tx
        
        #self.card1.setScale(texture_size,1,texture_size)
        print(self.card1.getScale()) #default 1,1,1
        print(self.card1.getHpr()) #def 0,0,0
        print(self.card1.getPos()) #def 0,0,0
        
        
        #self.card1.setPos(texture_size,0,-texture_size)
        #self.card1.setPos(texture_size, 0, 0) #x,y, z
        
        #Add task to taskmgr to translate texture 
        self.taskMgr.add(self.moveTextureTask, "moveTextureTask")
        
        
    #Procedure to handle changes on each frame, if needed
    def moveTextureTask(self, task):
        shiftMag = task.time*speed
        self.card1.setTexPos(self.sinTextureStage, shiftMag, 0, 0) #u, v, w
        return Task.cont #taskMgr will continue to call task


if __name__ == '__main__':
    app = MyApp()
    app.run()
