import sys
import numpy as np

from direct.showbase.ShowBase import ShowBase
from direct.showbase import ShowBaseGlobal  #global vars defined by p3d
from panda3d.core import Texture, CardMaker, TextureStage, KeyboardButton
from panda3d.core import WindowProperties
from direct.task import Task


class SinGreyTex:
    """
    RGB sinusoidal grating stimulus class, used by ShowBase.
    """
    def __init__(self, texture_size = 512, texture_name = "sin_grey", spatial_frequency = 10):
        self.frequency = spatial_frequency
        self.texture_size = texture_size
        self.texture_name = texture_name
        # Create texture stage
        self.texture_array = self.create_texture()
        self.texture = Texture(self.texture_name)
        self.texture.setup2dTexture(self.texture_size, self.texture_size,
                                    Texture.T_unsigned_byte, 
                                    Texture.F_luminance)
        self.texture.setRamImageAs(self.texture_array, "L")

    
    def create_texture(self):
        x = np.linspace(0, 2*np.pi, self.texture_size + 1)
        y = np.linspace(0, 2*np.pi, self.texture_size + 1)
        array, Y = np.meshgrid(x[: self.texture_size],y[: self.texture_size])
        sin_float = np.sin(self.frequency*array)
        sin_transformed = (sin_float + 1)*127.5; #from 0-255
        return np.uint8(sin_transformed)
  

class KeyboardToggleStim(ShowBase):
    """
    toggles between different stim: enter 0 for one, 1 for the other
    """
    def __init__(self, stim_classes, stim_params, window_size = 512):
        super().__init__()
        self.stage_name = "stage_left"
        self.stim_classes = stim_classes
        self.current_stim_num = 0
        self.stim_params = stim_params
        self.window_size = window_size
        self.bgcolor = (1, 1, 1, 1)
        self.stimulus_initialized = False  
        
        #Set up key control mechanism
        self.zero_button = KeyboardButton.ascii_key('0')
        self.one_button = KeyboardButton.ascii_key('1')

        #Window properties
        self.window_props = WindowProperties()
        self.window_props.setSize(self.window_size, self.window_size)

        #Create scenegraph
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        self.card = self.aspect2d.attachNewNode(cm.generate())
        self.card.setScale(np.sqrt(2))  #so it can handle arbitrary rotations
        self.card.setColor(self.bgcolor)  
        
        # Create texture stage
        self.texture_stage = TextureStage(self.stage_name) 
            
        #Set initial texture
        self.set_stimulus(str(self.current_stim_num)) 
        
        # Set up event handlers and tasks
        self.accept('0', self.set_stimulus, ['0']) #event handler
        self.accept('1', self.set_stimulus, ['1'])
        self.taskMgr.add(self.move_texture_task, "move_texture") #task

    @property
    def current_stim_params(self):
        """ 
        returns actual value of current stimulus 
        """
        return self.stim_params[self.current_stim_num]
    
    def set_stimulus(self, data):
        # If first texture hasn't been shown, don't clear previous texture 
        if not self.stimulus_initialized:
            self.self_initialized = True
        else:
            self.card.clearTexture(self.texture_stage)  #turn off stage
        self.window_props.setTitle(data)
        ShowBaseGlobal.base.win.requestProperties(self.window_props)  #base is a panda3d global
        
        if data == '0':
            self.current_stim_num = 0
        elif data == '1':
            self.current_stim_num = 1
        self.stim = self.stim_classes[self.current_stim_num]
        self.card.setColor(self.bgcolor)
        self.card.setTexture(self.texture_stage, self.stim.texture)
        self.card.setR(self.current_stim_params['angle']) #set angle

        return
               
    def move_texture_task(self, task):
        if self.current_stim_params['velocity'] == 0:
            pass
        else:
            new_position = -task.time*self.current_stim_params['velocity']
            self.card.setTexPos(self.texture_stage, new_position, 0, 0) #u, v, w
        return task.cont 


if __name__ == '__main__':
    stim1 = SinGreyTex(spatial_frequency = 10)
    stim2 = SinGreyTex(spatial_frequency = 5)
    stim_classes = [stim1, stim2]
    stim_params = [{'angle': 45, 'velocity': 0.1},
                   {'angle': -45, 'velocity': -0.1}]
    toggle_show = KeyboardToggleStim(stim_classes, stim_params)
    toggle_show.run()
    
    
    