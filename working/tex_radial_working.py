import numpy as np 
import matplotlib.pyplot as plt
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage
from direct.task import Task
from panda3d.core import TransformState
from direct.showbase import ShowBaseGlobal  #global vars defined by p3d


#def radial_sin(texture_size = 512, phase = 0, period = 8):
#    x = np.linspace(-8*np.pi, 8*np.pi, texture_size)
#    y = np.linspace(-8*np.pi, 8*np.pi, texture_size)
#    #X, Y = np.meshgrid(x, y)
#    #pd_gain = 2*np.pi/period
#    radial_sin_init = np.round((2*np.pi/period)*np.sin(np.sqrt(x[None, :]**2 +  y[:, None]**2)))  #*127+127
#    #trans_rad = ((radial_sin_init+1)/2)*127.5
#    trans_rad = radial_sin_init*127+127
#    return np.uint8(trans_rad+phase)
def radial_sin(texture_size = 512, phase = 0, period = 8):
    x = np.linspace(-8*np.pi, 8*np.pi, texture_size)
    y = np.linspace(-8*np.pi, 8*np.pi, texture_size)
    #X, Y = np.meshgrid(x, y)
    #pd_gain = 2*np.pi/period
    return np.round((2*np.pi/period)*np.sin(np.sqrt(x[None, :]**2 +  y[:, None]**2)+phase)*127+127).astype(np.uint8)
 
rad_sin = radial_sin(period = 8, phase = 18)
plt.imshow(rad_sin, cmap = 'Greys')    

#%%

# Make a texture with concentric circles
#Try out all of the following and pick the most efficient (and make a post):
#     https://stackoverflow.com/questions/10031580/how-to-write-simple-geometric-shapes-into-numpy-arrays
#Do both black and white and red/black just for fun
    

# Cairo is written in C and has python bindings:
    #
    #https://stackoverflow.com/questions/27633985/plotting-wave-equation
    # also look at Eva's code for this.
    #https://www.nodebox.net/code/index.php/Mark_Meyer_%7c_Parametric_surfaces_%7c_radial_wave
    

class TexRadialSin(ShowBase):
    """
    Show a single full-field texture that scales up or down in time, starting after 1 second.
    """
    def __init__(self, texture_array, window_size = 512, texture_size = 512, phase_shift = 0.05, initial_phase = 0, period = 8):
        super().__init__() 
        self.current_scale = 1
        self.phase_shift = phase_shift
        self.phase = initial_phase
        self.period = period
        self.texture_array = texture_array
        self.cube_ind = 0
        self.texture_dtype = type(self.texture_array.flat[0])
       
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
        ShowBaseGlobal.base.setFrameRateMeter(True) 

        self.taskMgr.add(self.setTextureTask, "setTextureTask")
        
    #Scale the texture
    def setTextureTask(self, task):
        if  task.time > 1:
            #self.texture.clearRamImage()
            self.phase += self.phase_shift
            new_texture = radial_sin(phase = self.phase)
            self.texture.setRamImageAs(new_texture, "L")
            #self.textureStage = TextureStage("Stimulus")
            self.card1.setTexture(self.textureStage, self.texture)
           
        return Task.cont       
           
if __name__ == '__main__':
    initial_phase = 0
    period = 10
    initial_texture = radial_sin(phase = initial_phase, period = period)
    radial_texture = TexRadialSin(initial_texture, phase_shift = 0.1, initial_phase = initial_phase, period = period)
    radial_texture.run()



