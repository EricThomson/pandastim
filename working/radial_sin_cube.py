"""
cube of concentric sinusoids: one shown in matplotlib, then in panda3d statically, then
in task manager in sequence when they turn dark.
"""
import numpy as np
import matplotlib.pyplot as plt
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage, SamplerState
from direct.task import Task
from direct.showbase import ShowBaseGlobal  #global vars defined by p3d

def radial_sin(texture_size = 512, phase = 0, period = 8):
    x = np.linspace(-8*np.pi, 8*np.pi, texture_size)
    y = np.linspace(-8*np.pi, 8*np.pi, texture_size)
    return np.round((2*np.pi/period)*np.sin(np.sqrt(x[None, :]**2 +  y[:, None]**2)+phase)*127+127).astype(np.uint8)

num_slices = 190 #190 makes it periodic
radial_cube = np.zeros(shape = (num_slices, 512, 512), dtype = np.uint8)
phase = 0
phase_change = 0.1
for slice_num in range(num_slices):
    rad_slice_i = radial_sin(period = 8, phase = phase)
    phase += phase_change
    radial_cube[slice_num,:,:] = rad_slice_i

#%% plot a random slice from the cube: it looks pretty bright and awesome
#cube_ind = 10
#rad_sin_i = radial_cube[cube_ind, :, :]
#plt.imshow(rad_sin_i, cmap = 'Greys')
#plt.title(f"Matplotlib slice {cube_ind}")
#plt.show()
# 
#%%
class TexCube(ShowBase):
    def __init__(self, texture_cube, window_size = 512, texture_size = 512):
        super().__init__()
        self.num_slices = texture_cube.shape[0]
        self.texture_cube = texture_cube
        self.cube_ind = 0
        #Create texture stage
        self.texture = Texture("Stimulus")
        
        self.texture.setMagfilter(SamplerState.FT_linear)
        #self.texture.setMinfilter(SamplerState.FT_nearest)
        self.texture.setMinfilter(SamplerState.FT_linear_mipmap_linear)
        
        self.texture.setup2dTexture(texture_size, texture_size,
                               Texture.T_unsigned_byte, Texture.F_luminance) 
        self.texture.setRamImageAs(self.texture_cube[0, :, :], "L")       
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
        if  task.time > 0.5:
            #self.texture.clearSimpleRamImage()
            self.texture.setRamImageAs(self.texture_cube[self.cube_ind, :, :], "L")
            #self.textureStage = TextureStage("Stimulus")
            self.card1.setTexture(self.textureStage, self.texture)
            self.cube_ind += 1
            if self.cube_ind == self.num_slices:
                self.cube_ind = 0
        return Task.cont      
          
if __name__ == '__main__':
    wave_cube = TexCube(radial_cube)
    wave_cube.run()