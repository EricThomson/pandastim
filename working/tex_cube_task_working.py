#On filtering: https://www.panda3d.org/manual/?title=Texture_Filter_Types
import numpy as np 
import matplotlib.pyplot as plt
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage, SamplerState
from direct.task import Task
from panda3d.core import TransformState
from direct.showbase import ShowBaseGlobal  #global vars defined by p3d


num_slices = 20
image_dims = 32
rand_cube = np.zeros(shape = (num_slices, image_dims, image_dims), dtype = np.uint8)
for slice_num in range(num_slices):
    rand_cube[slice_num, :, :] = np.random.randint(0, 255, size = (image_dims, image_dims))

#cube_ind = 10
#randi = rand_cube[cube_ind, :, :] #[:, :, cube_ind]
#plt.imshow(randi, cmap = 'Greys')
#plt.show()


  
#%%
class CubeShow(ShowBase):
    def __init__(self, texture_cube, window_size = 512, texture_size = 512):
        super().__init__() 
        self.cube_ind = 0
        self.num_slices = texture_cube.shape[0]
      
        #Create texture stage
        self.texture = Texture("Stimulus")
        self.texture.setMagfilter(SamplerState.FT_nearest)
        self.texture.setMinfilter(SamplerState.FT_nearest)
        self.texture.setup2dTexture(texture_size, texture_size, 
                               Texture.T_unsigned_byte, Texture.F_luminance)  
        self.texture.setRamImageAs(texture_cube[0, :, :], "L")        
        self.textureStage = TextureStage("Stimulus")
                                                                    
        #Create scenegraph
        cm = CardMaker('card1')
        cm.setFrameFullscreenQuad()
        self.card1 = self.aspect2d.attachNewNode(cm.generate())  
        self.card1.setTexture(self.textureStage, self.texture)  #ts, tx
        ShowBaseGlobal.base.setFrameRateMeter(True) 


        self.taskMgr.add(self.setTextureTask, "setTextureTask")
        
    #Scale the texture
    def setTextureTask(self, task):
        if  task.time > 1:
            #self.texture.clearSimpleRamImage()  #? do I need this to clear between frames
            self.texture.setRamImageAs(rand_cube[self.cube_ind, :, :], "L")
            #self.textureStage = TextureStage("Stimulus")
            self.card1.setTexture(self.textureStage, self.texture)
            self.cube_ind += 1
            if self.cube_ind == self.num_slices-1:
                self.cube_ind = 0
            
        return Task.cont       
           
if __name__ == '__main__':
    cube_runner = CubeShow(rand_cube, texture_size = image_dims)
    cube_runner.run()



