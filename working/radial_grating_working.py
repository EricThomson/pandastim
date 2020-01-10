#On filtering: https://www.panda3d.org/manual/?title=Texture_Filter_Types
import numpy as np 
import cv2
import matplotlib.pyplot as plt
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage, SamplerState
from direct.task import Task
from panda3d.core import TransformState
from direct.showbase import ShowBaseGlobal  #global vars defined by p3d


#%%
def concentric_circles(tex_size = 512, circ_center = (512//2, 512//2), 
                       bg_color = 0, circ_color = 255, circ_thickness = 25,
                       period = 50, phase = 0):
    concentric_grating = bg_color*np.ones((tex_size, tex_size), dtype = np.uint8)
    circ_radii = np.arange(phase, tex_size, period)
    #print(circ_radii)
    num_circles = len(circ_radii)
    for circ_ind in range(num_circles):
        cv2.circle(concentric_grating, circ_center, circ_radii[circ_ind], 
                   (circ_color, circ_color, circ_color), circ_thickness, lineType = cv2.LINE_AA);
    return concentric_grating
               
tex_size   = 512
period = 50
phase = 25
circ_center = (tex_size//2, tex_size//2)
bg_color = 0
circ_color = 255
circ_thickness = 25
cc_tex = concentric_circles(tex_size = tex_size, circ_center = circ_center, 
                       bg_color = bg_color, circ_color = circ_color, circ_thickness = circ_thickness,
                       period = period, phase = phase)
plt.imshow(cc_tex, cmap = 'gray')

#%%
image_dims = 512
phase_shift = 2
phase_vals = np.arange(5, 500, phase_shift); 
num_phases = len(phase_vals)
num_slices = num_phases
grating_cube = np.zeros(shape = (num_slices, image_dims, image_dims), dtype = np.uint8)
for phase_ind in range(num_phases):
    grating_cube[phase_ind,:, :] = concentric_circles(tex_size = tex_size, circ_center = circ_center, 
                       bg_color = bg_color, circ_color = circ_color, circ_thickness = circ_thickness,
                       period = period, phase = phase_vals[phase_ind])
  
#%%
#to_show = 10
#plt.imshow(grating_cube[to_show], cmap = 'gray')
    
#%%
class CubeShow(ShowBase):
    def __init__(self, texture_cube, window_size = 512, texture_size = 512):
        super().__init__() 
        self.cube_ind = 0
        self.num_slices = texture_cube.shape[0]
        self.cube = texture_cube
      
        #Create texture stage
        self.texture = Texture("Stimulus")
#        self.texture.setMagfilter(SamplerState.FT_nearest)
#        self.texture.setMinfilter(SamplerState.FT_nearest)
        self.texture.setup2dTexture(texture_size, texture_size, 
                               Texture.T_unsigned_byte, Texture.F_luminance)  
        self.texture.setRamImageAs(self.cube[0, :, :], "L")        
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
            self.texture.setRamImageAs(self.cube[self.cube_ind, :, :], "L")
            #self.textureStage = TextureStage("Stimulus")
            self.card1.setTexture(self.textureStage, self.texture)
            self.cube_ind += 1
            if self.cube_ind == self.num_slices-1:
                self.cube_ind = 0
            
        return Task.cont       
           
if __name__ == '__main__':
    cube_runner = CubeShow(grating_cube, texture_size = image_dims)
    cube_runner.run()



