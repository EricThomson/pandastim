"""
Figuring out how to show sequences of stimuli in a modular way.
"""
import numpy as np 
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage
from panda3d.core import WindowProperties
from panda3d.core import PStatClient

# numpy array
def rgb_texture(texture_size = 512, rgb = (0, 0, 0)):
    x = np.linspace(-texture_size/2, texture_size/2, texture_size)
    y = np.linspace(-texture_size/2, texture_size/2, texture_size)
    X, Y = np.meshgrid(x, y)
    rgb_texture = np.zeros((texture_size, texture_size, 3), dtype = np.uint8)
    rgb_texture[..., 0] = rgb[0]
    rgb_texture[..., 1] = rgb[1]
    rgb_texture[..., 2] = rgb[2]
    return rgb_texture
        
# class with p3 properties for consumption by ShowBase    
class RgbTex:
    def __init__(self, rgb = (0,0,0), tex_name = "rgb"):
        self.rgb = rgb
        self.texture_array = rgb_texture(rgb = self.rgb)
        self.texture = Texture(tex_name)
        self.texture.setup2dTexture(512, 512, Texture.T_unsigned_byte, Texture.F_rgb8)  
        self.texture.setRamImageAs(self.texture_array, "RGB")       
        self.texture_stage = TextureStage(tex_name)
       
     
class RgbShow(ShowBase):
    def __init__(self, stim):
        super().__init__()
        self.stim = stim
        self.bgcolor = (1, 1, 1, 1)
        #Window properties
        self.windowProps = WindowProperties()
        self.windowProps.setSize(512, 512)
        #Create scenegraph
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        self.card = self.aspect2d.attachNewNode(cm.generate())
        self.card.setScale(np.sqrt(8))
        self.card.setColor(self.bgcolor)  #make this an add mode
        self.card.setTexture(self.stim.texture_stage, self.stim.texture)

        
    
class SequenceShow(ShowBase):
    def __init__(self, experiment_structure, profile_on = False):
        super().__init__()
        self.current_stim_num = 0
        self.stim_classes = experiment_structure['stim_classes']
        self.stim_values = experiment_structure['stim_values']
        self.stim_durations = experiment_structure['stim_durations']
        self.stim_change_times = np.cumsum(self.stim_durations)  #times to switch
        self.bgcolor = (1, 1, 1, 1)

        #Set up profiling if desired
        if profile_on:
            PStatClient.connect()
            
        #Window properties
        self.windowProps = WindowProperties()
        self.windowProps.setSize(512, 512)

        #Create scenegraph
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        self.card = self.aspect2d.attachNewNode(cm.generate())
        self.card.setScale(np.sqrt(8))
        self.card.setColor(self.bgcolor)  #make this an add mode

        #Set initial texture
        self.taskMgr.add(self.set_stim_task, "set_stimulus_class")  

    @property
    def current_stim_ind(self):
        """
        returns index, from stim list, of current stimulus
        typical events = [3 1 3 0 3 3 1 3 2] so self.current_stim_ind[2] = 3
        """
        return self.stim_values[self.current_stim_num]

    @property
    def current_stim_class(self):
        """ 
        returns actual value of current stimulus 
        """
        return self.stim_classes[self.current_stim_ind]
    
    @property
    def next_change_time(self):
        """
        returns time of next stimulus toggle
        """
        return self.stim_change_times[self.current_stim_num]


    def set_stim_task(self, task):
        if task.time <= self.stim_change_times[-1]:
            if task.time >= self.next_change_time:
                self.card.clearTexture(self.current_stim_class.texture_stage)  #turn off stage
                self.current_stim_num += 1
                #print(type(self.current_stim_class))
                self.card.setTexture(self.current_stim_class.texture_stage, 
                                     self.current_stim_class.texture)
            return task.cont
        else:
            return task.done

#%%
if __name__ == "__main__":
    example = 'seq'  
    red_tex = RgbTex(rgb = (255,0,0)) 
    green_tex = RgbTex(rgb=(0,255,0))    
    if example == 'red':
        red_screen = RgbShow(red_tex)
        red_screen.run()
    elif example == 'green':
        green_screen = RgbShow(green_tex)
        green_screen.run()
    elif example == 'seq':
        stim_classes = {0: red_tex, 1: green_tex}
        stim_values = [0, 1, 0, 1, 0]
        stim_durations = [1, 2, 3, 1, 2]
        profile = True
        experiment_structure = {'stim_classes': stim_classes,
                            'stim_values': stim_values,
                            'stim_durations': stim_durations}
        stim_seq = SequenceShow(experiment_structure, profile_on = profile)
        stim_seq.run()
        
        
        
