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
        self.window_size = 512
        self.bgcolor = (0.5, 0.5, 0.5, 1)
        self.stimulus_initialized = False  #to handle case from -1 (uninitalize) to 0 (first stim)
        self.scale = np.sqrt(8)

        #Window properties
        self.windowProps = WindowProperties()
        self.windowProps.setSize(self.window_size, self.window_size)
        ShowBaseGlobal.base.win.requestProperties(self.windowProps)  #base is a panda3d global
        
        #Set initial texture
        self.set_stimulus(str(self.current_stim_num))
        
        # Set up event handlers and task managers
        self.accept('0', self.set_stimulus, ['0']) #event handler
        self.accept('1', self.set_stimulus, ['1'])
        self.taskMgr.add(self.move_texture_task, "move_textures") #task


    @property
    def current_stim_params(self):
        """ 
        returns actual value of current stimulus 
        """
        return self.stim_params[self.current_stim_num]
    
    
    def set_stimulus(self, data):
        """ 
        Called with relevant keyboard events
        """
        if not self.stimulus_initialized:
            self.stimulus_initialized = True
        else:
            if self.current_stim_params['type'] == 'single':
                self.card.clearTexture(self.texture_stage)  #turn off stage
                self.card.removeNode()
            else:
                self.left_card.clearTexture(self.left_texture_stage)  #turn off stage
                self.left_card.clearTexture(self.left_mask_stage)
                self.right_card.clearTexture(self.right_texture_stage)
                self.right_card.clearTexture(self.right_mask_stage)
                self.left_card.removeNode()
                self.right_card.removeNode()

        if data == '0':
            self.current_stim_num = 0            
        elif data == '1':
            self.current_stim_num = 1

        print(self.current_stim_num, self.current_stim_params)
        self.stim = self.stim_classes[self.current_stim_num]

        if self.current_stim_params['type'] == 'single':
            #Create scenegraph
            cm = CardMaker('card')
            cm.setFrameFullscreenQuad()
            self.card = self.aspect2d.attachNewNode(cm.generate())
            self.card.setScale(np.sqrt(8))
            self.texture_stage = TextureStage("texture_stage") 
            self.card.setColor((1, 1, 1, 1))
            self.card.setTexture(self.texture_stage, self.stim.texture)
            self.card.setR(self.current_stim_params['angle'])
        else:
            # Following creates two cards (left/right) and two textures for each 
            # (stimulus and mask)
            self.create_dual_stim()

        return
       
        
    def move_texture_task(self, task):
        """
        The stimulus (texture) is set: now move it if needed.
        """
        if self.current_stim_params['type'] == 'single':

            new_position = -task.time*self.current_stim_params['velocity']
            self.card.setTexPos(self.texture_stage, new_position, 0, 0) #u, v, w
        else:
            left_tex_position =  -task.time*self.current_stim_params['velocities'][0] #negative b/c texture stage
            right_tex_position = -task.time*self.current_stim_params['velocities'][1]
            self.left_card.setTexPos(self.left_texture_stage, left_tex_position, 0, 0)
            self.right_card.setTexPos(self.right_texture_stage, right_tex_position, 0, 0)
        return task.cont 

    def create_dual_stim(self):
        """
        This creates two textures that each cover half the card, and move at 
        artibrary velocities.
        """
        #CREATE MASK ARRAYS
        self.left_mask_array = 255*np.ones((self.stim.texture_size, self.stim.texture_size), dtype=np.uint8)
        self.left_mask_array[:, self.stim.texture_size//2 - 3 :] = 0
        self.right_mask_array = 255*np.ones((self.stim.texture_size, self.stim.texture_size), dtype=np.uint8)
        self.right_mask_array[:, : self.stim.texture_size//2 + 3] = 0

        #TEXTURE STAGES FOR LEFT CARD
        self.left_texture_stage = TextureStage('left_texture_stage')
        #Mask
        self.left_mask = Texture("left_mask_texture")
        self.left_mask.setup2dTexture(self.stim.texture_size, self.stim.texture_size,
                                               Texture.T_unsigned_byte, Texture.F_luminance)
        self.left_mask.setRamImage(self.left_mask_array)
        self.left_mask_stage = TextureStage('left_mask_array')
        #Multiply the texture stages together
        self.left_mask_stage.setCombineRgb(TextureStage.CMModulate,
                                    TextureStage.CSTexture,
                                    TextureStage.COSrcColor,
                                    TextureStage.CSPrevious,
                                    TextureStage.COSrcColor)

        #TEXTURE STAGES FOR RIGHT CARD
        self.right_texture_stage = TextureStage('right_texture_stage')
        #Mask
        self.right_mask = Texture("right_mask_texture")
        self.right_mask.setup2dTexture(self.stim.texture_size, self.stim.texture_size,
                                               Texture.T_unsigned_byte, Texture.F_luminance)
        self.right_mask.setRamImage(self.right_mask_array)
        self.right_mask_stage = TextureStage('right_mask_stage')
        #Multiply the texture stages together
        self.right_mask_stage.setCombineRgb(TextureStage.CMModulate,
                                    TextureStage.CSTexture,
                                    TextureStage.COSrcColor,
                                    TextureStage.CSPrevious,
                                    TextureStage.COSrcColor)

        #CREATE CARDS/SCENEGRAPH
        cm = CardMaker('stimcard')
        cm.setFrameFullscreenQuad()
        self.setBackgroundColor((0,0,0,1))
        self.left_card = self.aspect2d.attachNewNode(cm.generate())
        self.right_card = self.aspect2d.attachNewNode(cm.generate())
        self.left_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
        self.right_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))

        #ADD TEXTURE STAGES TO CARDS
        self.left_card.setTexture(self.left_texture_stage, self.stim.texture)
        self.left_card.setTexture(self.left_mask_stage, self.left_mask)
        self.right_card.setTexture(self.right_texture_stage, self.stim.texture)
        self.right_card.setTexture(self.right_mask_stage, self.right_mask)

        #TRANSFORMS
        #Masks
        self.mask_transform = self.trs_transform()
        self.left_card.setTexTransform(self.left_mask_stage, self.mask_transform)
        self.right_card.setTexTransform(self.right_mask_stage, self.mask_transform)
        #Left texture
        self.left_card.setTexScale(self.left_texture_stage, 1/self.scale)
        self.left_card.setTexRotate(self.left_texture_stage, self.current_stim_params['angle'])
        #Right texture
        self.right_card.setTexScale(self.right_texture_stage, 1/self.scale)
        self.right_card.setTexRotate(self.right_texture_stage, self.current_stim_params['angle'])
        
    def trs_transform(self):
        """ 
        trs = translate rotate scale transform for mask stage
        rdb-inspired code
        """
        pos = 0.5, 0.5
        center_shift = TransformState.make_pos2d((-pos[0], -pos[1]))
        scale = TransformState.make_scale2d(1/self.scale)
        rotate = TransformState.make_rotate2d(self.current_stim_params['angle'])
        translate = TransformState.make_pos2d((0.5, 0.5))
        return translate.compose(rotate.compose(scale.compose(center_shift)))



#%
if __name__ == '__main__':

    stim1 = SinRgbTex(rgb = (50, 255, 255))
    stim2 = SinRgbTex()
    stim_classes = [stim1, stim2]
    stim_params = [{'type': 'single', 'angle': 45, 'velocity': 0.1},
                   {'type': 'double', 'angle': -45, 'velocities': (-0.05, 0.05)}]
    toggle_show = KeyboardToggleStim(stim_classes, stim_params)
    toggle_show.run()

    
