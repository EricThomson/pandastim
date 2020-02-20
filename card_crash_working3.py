import numpy as np
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage
from panda3d.core import WindowProperties, ColorBlendAttrib, TransformState
from direct.showbase import ShowBaseGlobal  

def sin_byte(X, freq = 1):
    """
    Creates unsigned 8 bit representation of sin (T_unsigned_Byte). 
    """
    sin_float = np.sin(freq*X)
    sin_transformed = (sin_float + 1)*127.5; #from 0-255
    return np.uint8(sin_transformed)

class SinRgbTex:
    """
    RGB sinusoidal grating tex class, used by ShowBase.
    """
    def __init__(self, texture_size = 512, texture_name = "sin_rgb", 
                 spatial_frequency = 10, rgb = (255, 0, 0)):
        self.frequency = spatial_frequency
        self.rgb = rgb
        self.texture_size = texture_size
        self.texture_name = texture_name
        self.texture_array = self.create_texture()
        self.texture = Texture(self.texture_name)
        self.texture.setup2dTexture(self.texture_size, self.texture_size,
                                    Texture.T_unsigned_byte, 
                                    Texture.F_rgb8)
        self.texture.setRamImageAs(self.texture_array, "RGB")
            
    def create_texture(self):
        """ 
        Sinusoid that goes from black to the given rgb value. 
        """
        if not (all([x >= 0 for x in self.rgb]) and all([x <= 255 for x in self.rgb])):
            raise ValueError("SinRgbTex.sin_texture_rgb(): rgb values must lie in [0,255]")
        x = np.linspace(0, 2*np.pi, self.texture_size+1)
        y = np.linspace(0, 2*np.pi, self.texture_size+1)
        array, Y = np.meshgrid(x[: self.texture_size],y[: self.texture_size])
        R = np.uint8((self.rgb[0]/255)*sin_byte(array, freq = self.frequency))
        G = np.uint8((self.rgb[1]/255)*sin_byte(array, freq = self.frequency))
        B = np.uint8((self.rgb[2]/255)*sin_byte(array, freq = self.frequency))
        rgb_sin = np.zeros((self.texture_size, self.texture_size, 3), dtype = np.uint8)
        rgb_sin[...,0] = R
        rgb_sin[...,1] = G
        rgb_sin[...,2] = B
        return rgb_sin
    
    

class KeyboardToggleStim(ShowBase):
    """
    toggles between different stim based on keyboard inputs (0/1)
    
    Useful for testing things out quickly before pushing to the ClostLoopStim classes.
    """
    def __init__(self, stim_classes, stim_params):
        super().__init__()

        self.stim_classes = stim_classes
        self.current_stim_num = 0
        self.stim_params = stim_params
        self.texture_size = 512
        self.window_size = 512
        self.stimulus_initialized = False  #to handle case from -1 (uninitalize) to 0 (first stim)
        self.scale = np.sqrt(8)

        #Window properties
        self.windowProps = WindowProperties()
        self.windowProps.setSize(self.window_size, self.window_size)
        ShowBaseGlobal.base.win.requestProperties(self.windowProps)  #base is a panda3d global
        
        
        # Create cards and texture stages
        """ singleton"""
        cm1 = CardMaker('card')
        cm1.setFrameFullscreenQuad()
        self.card = self.aspect2d.attachNewNode(cm1.generate())
        self.card.setScale(np.sqrt(8))
        self.texture_stage = TextureStage("texture_stage") 
        
        """ masked """
        self.masked_texture_stage = TextureStage('masked_texture_stage')
        # Mask
        self.mask = Texture("mask_texture")
        self.mask.setup2dTexture(self.texture_size, self.texture_size,
                                      Texture.T_unsigned_byte, Texture.F_luminance)
        self.mask_stage = TextureStage('mask_array')
        cm2 = CardMaker('maskcard')
        cm2.setFrameFullscreenQuad()
        # self.mask_card = self.aspect2d.attachNewNode(cm2.generate())
        # self.mask_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
        
        #Set initial texture
        self.set_stimulus(str(self.current_stim_num))
        
        # Set up event handlers and task managers
        self.accept('0', self.set_stimulus, ['0']) #event handler
        self.accept('1', self.set_stimulus, ['1'])

    @property
    def current_stim_params(self):
        return self.stim_params[self.current_stim_num]
    
    def set_stimulus(self, data):
        # if there is currently a stim, clear it
        if not self.stimulus_initialized:
            self.stimulus_initialized = True
        else:
            if self.current_stim_params['type'] == 'single':
                #self.card.clearTexture(self.texture_stage)  #turn off stage  
                pass
            else:
                #self.mask_card.clearTexture(self.masked_texture_stage)  #turn off stage
                #self.mask_card.clearTexture(self.mask_stage)
                pass


        if data == '0':
            self.current_stim_num = 0            
        elif data == '1':
            self.current_stim_num = 1

        print(self.current_stim_num, self.current_stim_params)
        self.stim = self.stim_classes[self.current_stim_num]
        #print(self.stim)

        if self.current_stim_params['type'] == 'single':

            #self.card.setColor((1, 1, 1, 1))
            #print(self.stim.texture)
            self.card.setTexture(self.texture_stage, self.stim.texture)
            self.card.setR(45)  #set full-field at angle
        else:
            self.create_masked_stim()

        return
       

    def create_masked_stim(self):
        """
        This creates a masked stim using texture stages
        """
        #CREATE MASK
        self.mask_array = 255*np.ones((self.texture_size, 
                                       self.texture_size), dtype=np.uint8)
        self.mask_array[:, self.texture_size//2 :] = 0

        #ADD TEXTURE STAGES TO CARDS
        self.mask.setRamImage(self.mask_array)
        self.mask_card.setTexture(self.mask_stage, self.mask)
        self.mask_card.setTexture(self.masked_texture_stage, self.stim.texture)        
        
        #Multiply the texture stages together
        self.mask_stage.setCombineRgb(TextureStage.CMModulate,
                                      TextureStage.CSTexture,
                                      TextureStage.COSrcColor,
                                      TextureStage.CSPrevious,
                                      TextureStage.COSrcColor)
        

        self.mask_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
                
        return
        



#%%
if __name__ == '__main__':
    stim1 = SinRgbTex(rgb = (50, 255, 255))
    stim2 = SinRgbTex()
    stim_classes = [stim1, stim2]
    stim_params = [{'type': 'single'},
                   {'type': 'double'}]
    toggle_show = KeyboardToggleStim(stim_classes, stim_params)
    toggle_show.run()

    
