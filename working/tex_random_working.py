import numpy as np 
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage
from direct.task import Task
from panda3d.core import TransformState

def make_circle_tex(texture_size = 512, circle_center = (0, 0), circle_radius = 100):
    x = np.linspace(-texture_size/2, texture_size/2, texture_size)
    y = np.linspace(-texture_size/2, texture_size/2, texture_size)
    X, Y = np.meshgrid(x, y)
    circle_texture = np.zeros((texture_size, texture_size), dtype = np.uint8)
    circle_mask = (X - circle_center[0])**2 + (Y - circle_center[1])**2 <= circle_radius**2
    circle_texture[circle_mask] = 255
    return np.uint8(circle_texture)


# Make a texture with concentric circles
#Try out all of the following and pick the most efficient (and make a post):
#     https://stackoverflow.com/questions/10031580/how-to-write-simple-geometric-shapes-into-numpy-arrays
#Do both black and white and red/black just for fun
    

# Cairo is written in C and has python bindings:
    

class TexRand(ShowBase):
    """
    Show a single full-field texture that scales up or down in time, starting after 1 second.
    """
    def __init__(self, texture_array, window_size = 512, texture_size = 512):
        super().__init__() 
        self.current_scale = 1
        self.texture_array = texture_array
        self.texture_dtype = type(self.texture_array.flat[0])
        self.ndims = self.texture_array.ndim
        self.center_shift = TransformState.make_pos2d((-0.5, -0.5))
        self.shift_back = TransformState.make_pos2d((0.5, 0.5))
       
        #Create texture stage
        self.texture = Texture("Stimulus")
        self.texture.setup2dTexture(texture_size, texture_size, 
                               Texture.T_unsigned_byte, Texture.F_luminance)  
        self.texture.setWrapU(Texture.WM_clamp)
        self.texture.setWrapV(Texture.WM_clamp)
        self.texture.setRamImageAs(self.texture_array, "L")        
        self.textureStage = TextureStage("Stimulus")
                                                                    
        #Create scenegraph
        cm = CardMaker('card1')
        cm.setFrameFullscreenQuad()
        self.card1 = self.aspect2d.attachNewNode(cm.generate())  
        self.card1.setTexture(self.textureStage, self.texture)  #ts, tx
              

        self.taskMgr.add(self.setTextureTask, "setTextureTask")
        
    #Scale the texture
    def setTextureTask(self, task):
        if task.time > 1:
            self.pos = np.random.randint(-200, 200, size = 2, dtype = np.int16)
            #self.texture.clearRamImage()
            new_texture = make_circle_tex(texture_size = 512, circle_center = (self.pos[0], self.pos[1]))
            self.texture_array = new_texture
            self.texture.setRamImageAs(self.texture_array, "L")
            #self.textureStage = TextureStage("Stimulus")
            self.card1.setTexture(self.textureStage, self.texture)
            
        return Task.cont       
           
if __name__ == '__main__':
    circle_texture = make_circle_tex()
    circle_rand = TexRand(circle_texture)
    circle_rand.run()



