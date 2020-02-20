"""
pandastim/stimuli.py
Classes to present visual stimuli in pandastim (subclasses of ShowBase, which 
implements the main event loop in panda3d).

Part of pandastim package: https://github.com/EricThomson/pandastim

Component types (texture data types in panda3d):
https://www.panda3d.org/reference/python/classpanda3d_1_1core_1_1Texture.html#a81f78fc173dedefe5a049c0aa3eed2c0

To do:
    You could make texture size x/y different. Currently constrained to be a square (setup2dTexture method)
"""
import sys
import numpy as np
from datetime import datetime

from direct.showbase.ShowBase import ShowBase
from direct.showbase import ShowBaseGlobal  #global vars defined by p3d
from panda3d.core import Texture, CardMaker, TextureStage, KeyboardButton
from panda3d.core import WindowProperties, ColorBlendAttrib, TransformState, ClockObject
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText   #for binocular stim
from panda3d.core import PStatClient

 

class ShowTexMoving(ShowBase):
    """
    Consumes single texture class and shows it drifting across the window at the
    specified velocity and angle.
    
    Usage:
        stim = SinGreyTex()
        stim_show = ShowTexMoving(stim, angle = 30, velocity = 0.1, fps = 40, profile_on = True)
        stim_show.run()
        
    Note(s):
        Positive angles are clockwise, negative ccw.
        Velocity is normalized to window size, so 1.0 is the entire window width (i.e., super-fast).
    """
    def __init__(self, stim, angle = 0, velocity = 0.1, 
                 fps = 30, window_size = None, profile_on = False):
        super().__init__()
        if window_size is None:
            self.window_size = stim.texture_size
        else:
            self.window_size = window_size
        self.stim = stim
        self.angle = angle
        self.velocity = velocity
        self.bgcolor = (1, 1, 1, 1)
        self.texture_stage = TextureStage("texture_stage") 
        
        # Set frame rate (fps)
        ShowBaseGlobal.globalClock.setMode(ClockObject.MLimited)
        ShowBaseGlobal.globalClock.setFrameRate(fps) 
        
        #Set up profiling if desired
        if profile_on:
            PStatClient.connect()
            ShowBaseGlobal.base.setFrameRateMeter(True)  #Show frame rate
            
        #Window properties set up 
        self.window_properties = WindowProperties()
        self.window_properties.setSize(self.window_size, self.window_size)
        self.window_properties.setTitle("ShowTexMoving")
        ShowBaseGlobal.base.win.requestProperties(self.window_properties)
        
        #Create scenegraph, attach stimulus to card.
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        self.card = self.aspect2d.attachNewNode(cm.generate())
        # Scale is so it can handle arbitrary rotations and shifts in binocular case
        self.card.setScale(np.sqrt(8))
        self.card.setColor(self.bgcolor)  
        self.card.setTexture(self.texture_stage, self.stim.texture)
       
        #Transform the card
        self.card.setR(self.angle)
        
        if self.velocity != 0:
            #Add task to taskmgr to translate texture
            self.taskMgr.add(self.moveTextureTask, "moveTextureTask")
        
    #Task for moving the texture
    def moveTextureTask(self, task):
        new_position = -task.time*self.velocity
        self.card.setTexPos(self.texture_stage, new_position, 0, 0) #u, v, w
        return Task.cont
                
class ShowTexStatic(ShowTexMoving):
    """
    Consumes single stimulus class and presents it, without any motion.
    Most useful for testing stimuli. Obviously no need to set fps high.
    
    Usage:
        stim = SinGreyTex()
        stim_show = ShowTexStatic(stim, fps = 10, profile_on = True)
        stim_show.run()
    """
    def __init__(self, stim, angle = 0,  fps = 30, window_size = None, profile_on = False):     
        super().__init__(stim, angle = angle, velocity = 0, 
                         fps = fps, window_size = window_size, 
                         profile_on = profile_on )
        self.window_properties.setTitle("ShowTexStatic")
        ShowBaseGlobal.base.win.requestProperties(self.window_properties)


class BinocularDrift(ShowBase):
    """
    Show binocular drifting textures forever.
    Takes in texture object and other parameters, and shows texture drifting indefinitely.

    Usage:
        BinocularDrift(texture_object,
                        stim_angles = (0, 0),
                        strip_angle = 0,
                        position = (0,0),
                        velocities = (0,0),
                        strip_width = 2,
                        window_size = 512,
                        texture_size = 512)

    Note(s):
        - angles are (left_texture_angle, right_texture_angle): >0 is cw, <0 ccw
        - Velocity is in NDC, so 1.0 is the entire window width (i.e., super-fast).
        - Make texture_size a power of 2: this makes the GPU happier.
        - position is x,y in NDC (from [-1 1]), so (.5, .5) will be in middle of top right quadrant
        - strip_width is just the width of the strip down the middle. It can be 0. Even is better.
        - The texture array can be 2d (gray) or NxNx3 (rgb) with unit8 or uint16 elements.
    """
    def __init__(self, stim, stim_angles = (0, 0), strip_angle = 0, position = (0,0),
                 velocities = (0,0), strip_width = 4, fps = 30, window_size = None,
                 profile_on = False):
        super().__init__()
        self.stim = stim
        if window_size == None:
            self.window_size = stim.texture_size
        else:
            self.window_size = window_size
        self.mask_position_ndc = position
        self.mask_position_uv = (self.ndc2uv(self.mask_position_ndc[0]),
                                 self.ndc2uv(self.mask_position_ndc[1]))
        self.scale = np.sqrt(8)  #so it can handle arbitrary rotations and shifts
        self.left_texture_angle = stim_angles[0]
        self.right_texture_angle = stim_angles[1]
        self.left_velocity = velocities[0]
        self.right_velocity = velocities[1]
        self.strip_angle = strip_angle #this will change fairly frequently
        self.fps = fps

        #Set window title and size
        self.window_properties = WindowProperties()
        self.window_properties.setSize(self.window_size, self.window_size)
        self.window_properties.setTitle("BinocularDrift")
        ShowBaseGlobal.base.win.requestProperties(self.window_properties)  #base is a panda3d global

        #CREATE MASK ARRAYS
        self.left_mask_array = 255*np.ones((self.stim.texture_size, self.stim.texture_size), dtype=np.uint8)
        self.left_mask_array[:, self.stim.texture_size//2 - strip_width//2 :] = 0
        self.right_mask_array = 255*np.ones((self.stim.texture_size, self.stim.texture_size), dtype=np.uint8)
        self.right_mask_array[:, : self.stim.texture_size//2 + strip_width//2] = 0

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
        self.left_card.setTexRotate(self.left_texture_stage, self.left_texture_angle)
        #Right texture
        self.right_card.setTexScale(self.right_texture_stage, 1/self.scale)
        self.right_card.setTexRotate(self.right_texture_stage, self.right_texture_angle)

        #Set dynamic transforms
        if self.left_velocity != 0 and self.right_velocity != 0:
            print("Moving both textures")
            self.taskMgr.add(self.textures_update, "move_both")
        elif self.left_velocity != 0 and self.right_velocity == 0:
            print("Moving left texture")
            self.taskMgr.add(self.left_texture_update, "move_left")
        elif self.left_velocity == 0 and self.right_velocity != 0:
            print("Moving right texture")
            self.taskMgr.add(self.right_texture_update, "move_right")

        # Set frame rate
        ShowBaseGlobal.globalClock.setMode(ClockObject.MLimited)
        ShowBaseGlobal.globalClock.setFrameRate(self.fps)  #can lock this at whatever
        
        #Set up profiling if desired
        if profile_on:
            PStatClient.connect()
            ShowBaseGlobal.base.setFrameRateMeter(True)  #Show frame rate

        # Following will show a small x at the center
        self.title = OnscreenText("x",
                                  style = 1,
                                  fg = (1,1,1,1),
                                  bg = (0,0,0,.8),
                                  pos = self.mask_position_ndc,
                                  scale = 0.05)

    #Move both textures
    def textures_update(self, task):
        left_tex_position = -task.time*self.left_velocity #negative b/c texture stage
        right_tex_position = -task.time*self.right_velocity
        self.left_card.setTexPos(self.left_texture_stage, left_tex_position, 0, 0)
        self.right_card.setTexPos(self.right_texture_stage, right_tex_position, 0, 0)
        return task.cont

    def left_texture_update(self, task):
        left_tex_position = -task.time*self.left_velocity #negative b/c texture stage
        self.left_card.setTexPos(self.left_texture_stage, left_tex_position, 0, 0)
        return task.cont

    def right_texture_update(self, task):
        right_tex_position = -task.time*self.right_velocity
        self.right_card.setTexPos(self.right_texture_stage, right_tex_position, 0, 0)
        return task.cont

    def trs_transform(self):
        """ 
        trs = translate rotate scale transform for mask stage
        rdb contributed to this code
        """
        pos = 0.5 + self.mask_position_uv[0], 0.5 + self.mask_position_uv[1]
        center_shift = TransformState.make_pos2d((-pos[0], -pos[1]))
        scale = TransformState.make_scale2d(1/self.scale)
        rotate = TransformState.make_rotate2d(self.strip_angle)
        translate = TransformState.make_pos2d((0.5, 0.5))
        return translate.compose(rotate.compose(scale.compose(center_shift)))

    def ndc2uv(self, val):
        """ from model-based normalized device coordinates to texture-based uv-coordinates"""
        return 0.5*val

    def uv2ndc(self, val):
        """ from texture-based uv-coordinates to model-based normalized device coordinates"""
        return 2*val
    
        
        
class BinocularStatic(BinocularDrift):
    """
    Presents binocular stim class without any motion.
    Most useful for testing stimuli. Obviously no need to set fps high.
    """
    def __init__(self, stim, stim_angles = (0,0), strip_angle = 0,
                 position = (0, 0), strip_width = 4, fps = 30, 
                 window_size = None, profile_on = False):     
        super().__init__(stim, stim_angles = stim_angles, velocities = (0, 0),
                         strip_angle = strip_angle, strip_width = strip_width,
                         position = position, fps = fps, window_size = window_size, 
                         profile_on = profile_on )
        self.window_properties.setTitle("BinocularStatic")
        ShowBaseGlobal.base.win.requestProperties(self.window_properties)


class OpenLoopStim(ShowBase):
    """
    Takes in list of stimuli, and params, as well as list of values/durations to show
    different stimuli. 
    
    Should be useful for testing. 
    
    Model on working/seq_stim_play.py as well as ClosedLoop
    """      
    pass


class ClosedLoop(ShowBase):
    """
    Generic closed loop class takes in list of texture classes, and stimulus parameters (angles),
    and presents them in closed loop with zmq signals. 
    """
    def __init__(self, tex_classes, stim_params, initial_stim_ind = 0, window_size = 512, 
                 profile_on = False, fps = 30, save_path = None):
        super().__init__()

        self.current_stim_num = initial_stim_ind
        self.tex_classes = tex_classes
        self.stim_params = stim_params
        self.window_size = window_size
        self.bgcolor = (0.5, 0.5, 0.5, 1)
        self.stimulus_initialized = False  #to handle case from -1 (uninitalize) to 0 (first stim)
        self.fps = fps
        self.save_path = save_path
        if self.save_path:
            self.filestream = open(self.save_path, "a")
        else:
            self.filestream = None 
        self.scale = np.sqrt(8)  #so it can handle arbitrary rotations and shifts
        
        #Window properties
        self.windowProps = WindowProperties()
        self.windowProps.setSize(self.window_size, self.window_size)
        self.set_title("Initializing")

        # Set frame rate
        ShowBaseGlobal.globalClock.setMode(ClockObject.MLimited)
        ShowBaseGlobal.globalClock.setFrameRate(self.fps)  
        
        # Profile the unsub
        if profile_on:
            PStatClient.connect()
            ShowBaseGlobal.base.setFrameRateMeter(True) 
            
        #Set initial texture(s)
        self.set_stimulus(str(self.current_stim_num))
        
        # Set up event handlers (accept) and tasks (taskMgr) for dynamics
        self.accept('stim0', self.set_stimulus, ['0']) 
        self.accept('stim1', self.set_stimulus, ['1'])
        self.accept('stim2', self.set_stimulus, ['2'])
        # Wrinkle: should we set this here or there?
        self.taskMgr.add(self.move_textures, "move textures")

    def set_tasks(self):
        if self.current_stim_params['stim_type'] == 'b':
            self.taskMgr.add(self.textures_update, "move_both")
            
    #Move textures
    def move_textures(self, task):
        if self.current_stim_params['stim_type'] == 'b':
            left_tex_position =  -task.time*self.current_stim_params['velocities'][0] #negative b/c texture stage
            right_tex_position = -task.time*self.current_stim_params['velocities'][1]
            self.left_card.setTexPos(self.left_texture_stage, left_tex_position, 0, 0)
            self.right_card.setTexPos(self.right_texture_stage, right_tex_position, 0, 0)
        elif self.current_stim_params['stim_type'] == 's':
            if self.current_stim_params['velocity'] == 0:
                pass
            else:
                new_position = -task.time*self.current_stim_params['velocity']
                self.card.setTexPos(self.texture_stage, new_position, 0, 0) #u, v, w
        return task.cont
    
    @property
    def texture_size(self):
        return self.tex_classes[self.current_stim_num].texture_size

    @property
    def current_stim_params(self):
        """ 
        returns actual value of current stimulus 
        """
        return self.stim_params[self.current_stim_num]
    
    def create_cards(self):
        """ 
        Create cards: these are panda3d objects that are required for displaying textures.
        You can't just have a disembodied texture. In pandastim (at least for now) we are
        only showing 2d projections of textures, so we use cards.
        """
        if self.current_stim_params['stim_type'] == 'b':
            #CREATE CARDS/SCENEGRAPH
            cm = CardMaker('stimcard')
            cm.setFrameFullscreenQuad()
            self.setBackgroundColor((0,0,0,1))
            self.left_card = self.aspect2d.attachNewNode(cm.generate())
            self.left_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
    
            self.right_card = self.aspect2d.attachNewNode(cm.generate())
            self.right_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
        elif self.current_stim_params['stim_type'] == 's':
            cm = CardMaker('card')
            cm.setFrameFullscreenQuad()
            self.card = self.aspect2d.attachNewNode(cm.generate())
            self.card.setScale(self.scale)
            self.card.setColor((0.5, 0.5, 0.5, 1))
        return
        
    def create_texture_stages(self):
        """
        Create the texture stages: these are basically textures that you can apply
        to cards at the same time, which is useful when you need to combine textures
        to create the final visual appearance of a card.
        
        For more on texture stages:
        https://docs.panda3d.org/1.10/python/programming/texturing/multitexture-introduction
        
        """
        if self.current_stim_params['stim_type'] == 'b':
            #TEXTURE STAGES FOR LEFT CARD
            # Texture itself
            self.left_texture_stage = TextureStage('left_texture_stage')
            # Mask
            self.left_mask = Texture("left_mask_texture")
            self.left_mask.setup2dTexture(self.texture_size, self.texture_size,
                                          Texture.T_unsigned_byte, Texture.F_luminance)
            self.left_mask_stage = TextureStage('left_mask_array')
    
    
            #TEXTURE STAGES FOR RIGHT CARD
            self.right_texture_stage = TextureStage('right_texture_stage')
            #Mask
            self.right_mask = Texture("right_mask_texture")
            self.right_mask.setup2dTexture(self.texture_size, self.texture_size,
                                           Texture.T_unsigned_byte, Texture.F_luminance)
            self.right_mask_stage = TextureStage('right_mask_stage')
        elif self.current_stim_params['stim_type'] == 's':
            self.texture_stage = TextureStage("texture_stage") 
        return
    
    def set_stimulus(self, data):
        """ 
        Uses events from zmq to set the stimulus value. 
        
        Matt: this should be more general. Right now it is set up to consume 3
        different inputs.
        """
            
        if not self.stimulus_initialized:
            # If this is first stim, then toggle initialization to on, and
            # do not clear previous texture (there is no previous texture).
            self.stimulus_initialized = True
        else:
            self.clear_cards() #clear the textures before adding new ones

        if data == '0':
            self.current_stim_num = 0
        elif data == '1':
            self.current_stim_num = 1
        elif data == '2':
            self.current_stim_num = 2
            
        #Save stim to file
        if self.filestream:
            current_datetime = str(datetime.now())
            self.filestream.write(f"{current_datetime}\t{data}\n")
            self.filestream.flush()
            
        print(self.current_stim_num, self.current_stim_params) #for debugging
        self.stim = self.tex_classes[self.current_stim_num]
        self.create_texture_stages()
        self.create_cards()
        self.set_texture_stages()
        self.set_transforms()
                          
        return

    def set_transforms(self):
        """ 
        Set up the transforms to apply to textures/cards (e.g., rotations/scales)
        This is different from the framewise movement handled by the task manager
        """
        if self.current_stim_params['stim_type'] == 'b':
            #masks
            self.mask_transform = self.trs_transform()
            self.left_card.setTexTransform(self.left_mask_stage, self.mask_transform)
            self.right_card.setTexTransform(self.right_mask_stage, self.mask_transform)
            #Left texture
            self.left_card.setTexScale(self.left_texture_stage, 1/self.scale)
            self.left_card.setTexRotate(self.left_texture_stage, self.current_stim_params['angles'][0])
            self.left_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
            #Right texture
            self.right_card.setTexScale(self.right_texture_stage, 1/self.scale)
            self.right_card.setTexRotate(self.right_texture_stage, self.current_stim_params['angles'][1])
            self.right_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))      
        if self.current_stim_params['stim_type'] == 's':
            self.card.setR(self.current_stim_params['angle'])
        return
          
    def set_texture_stages(self):
        """ 
        Add texture stages to cards
        """
        if self.current_stim_params['stim_type'] == 'b':
            self.mask_position_ndc = self.current_stim_params['position']
            self.mask_position_uv = (self.ndc2uv(self.mask_position_ndc[0]),
                                      self.ndc2uv(self.mask_position_ndc[1]))
            
            #CREATE MASK ARRAYS
            self.left_mask_array = 255*np.ones((self.texture_size, 
                                                self.texture_size), dtype=np.uint8)
            self.left_mask_array[:, self.texture_size//2 - self.current_stim_params['strip_width']//2 :] = 0
            self.right_mask_array = 255*np.ones((self.texture_size, 
                                                  self.texture_size), dtype=np.uint8)
            self.right_mask_array[:, : self.texture_size//2 + self.current_stim_params['strip_width']//2] = 0
    
            #ADD TEXTURE STAGES TO CARDS
            self.left_mask.setRamImage(self.left_mask_array)
            self.left_card.setTexture(self.left_texture_stage, self.stim.texture)
            self.left_card.setTexture(self.left_mask_stage, self.left_mask)
            #Multiply the texture stages together
            self.left_mask_stage.setCombineRgb(TextureStage.CMModulate,
                                        TextureStage.CSTexture,
                                        TextureStage.COSrcColor,
                                        TextureStage.CSPrevious,
                                        TextureStage.COSrcColor)
            self.right_mask.setRamImage(self.right_mask_array)
            self.right_card.setTexture(self.right_texture_stage, self.stim.texture)
            self.right_card.setTexture(self.right_mask_stage, self.right_mask)
            #Multiply the texture stages together
            self.right_mask_stage.setCombineRgb(TextureStage.CMModulate,
                                        TextureStage.CSTexture,
                                        TextureStage.COSrcColor,
                                        TextureStage.CSPrevious,
                                        TextureStage.COSrcColor)
        elif self.current_stim_params['stim_type'] == 's':
            self.card.setColor((1, 1, 1, 1))
            self.card.setTexture(self.texture_stage, self.stim.texture)
        return
        
    def clear_cards(self):
        """ 
        Clear cards when new stimulus: stim-class sensitive
        """
        if self.current_stim_params['stim_type'] == 'b':
            self.left_card.clearTexture(self.left_texture_stage)  #turn off stage
            self.left_card.clearTexture(self.left_mask_stage)
            self.right_card.clearTexture(self.right_texture_stage)
            self.right_card.clearTexture(self.right_mask_stage)
            self.left_card.removeNode()
            self.right_card.removeNode()
        elif self.current_stim_params['stim_type'] == 's':
            self.card.clearTexture(self.texture_stage)  #turn off stage
            self.card.removeNode()
        return
        
    def trs_transform(self):
        """ 
        trs = translate-rotate-scale transform for mask stage
        panda3d developer rdb contributed to this code
        """
        pos = 0.5 + self.mask_position_uv[0], 0.5 + self.mask_position_uv[1]
        center_shift = TransformState.make_pos2d((-pos[0], -pos[1]))
        scale = TransformState.make_scale2d(1/self.scale)
        rotate = TransformState.make_rotate2d(self.current_stim_params['strip_angle'])
        translate = TransformState.make_pos2d((0.5, 0.5))
        return translate.compose(rotate.compose(scale.compose(center_shift)))

    def ndc2uv(self, val):
        """ from model-based normalized device coordinates to texture-based uv-coordinates"""
        return 0.5*val

    def uv2ndc(self, val):
        """ from texture-based uv-coordinates to model-based normalized device coordinates"""
        return 2*val
    
    def set_title(self, title):
        self.windowProps.setTitle(title)
        ShowBaseGlobal.base.win.requestProperties(self.windowProps)  #base is a panda3d global
    
   
class ClosedLoopBinocular(ShowBase):
    """
    toggles between different stim depending on messages produced by ZmqHandler
    
    """
    def __init__(self, tex_classes, stim_params, window_size = 512, 
                 profile_on = False, fps = 30, save_path = None):
        super().__init__()

        self.current_stim_num = 0
        self.tex_classes = tex_classes
        self.stim_params = stim_params
        self.window_size = window_size
        self.bgcolor = (0.5, 0.5, 0.5, 1)
        self.stimulus_initialized = False  #to handle case from -1 (uninitalize) to 0 (first stim)
        self.fps = fps
        self.save_path = save_path
        if self.save_path:
            self.filestream = open(self.save_path, "a")
        else:
            self.filestream = None 
        self.scale = np.sqrt(8)  #so it can handle arbitrary rotations and shifts
        
        #Window properties
        self.windowProps = WindowProperties()
        self.windowProps.setSize(self.window_size, self.window_size)
        self.set_title("Initializing")

        # Set frame rate
        ShowBaseGlobal.globalClock.setMode(ClockObject.MLimited)
        ShowBaseGlobal.globalClock.setFrameRate(self.fps)  
        
        # Profile the unsub
        if profile_on:
            PStatClient.connect()
            ShowBaseGlobal.base.setFrameRateMeter(True) 
            
        #TEXTURE STAGES FOR LEFT CARD
        # Texture itself
        self.left_texture_stage = TextureStage('left_texture_stage')
        # Mask
        self.left_mask = Texture("left_mask_texture")
        self.left_mask.setup2dTexture(self.texture_size, self.texture_size,
                                      Texture.T_unsigned_byte, Texture.F_luminance)
        self.left_mask_stage = TextureStage('left_mask_array')


        #TEXTURE STAGES FOR RIGHT CARD
        self.right_texture_stage = TextureStage('right_texture_stage')
        #Mask
        self.right_mask = Texture("right_mask_texture")
        self.right_mask.setup2dTexture(self.texture_size, self.texture_size,
                                       Texture.T_unsigned_byte, Texture.F_luminance)
        self.right_mask_stage = TextureStage('right_mask_stage')

        #CREATE CARDS/SCENEGRAPH
        cm = CardMaker('stimcard')
        cm.setFrameFullscreenQuad()
        self.setBackgroundColor((0,0,0,1))
        self.left_card = self.aspect2d.attachNewNode(cm.generate())
        self.left_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))

        self.right_card = self.aspect2d.attachNewNode(cm.generate())
        self.right_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
             
        #Set initial texture
        self.set_stimulus(str(self.current_stim_num))
        
        # Set up event handlers and tasks
        self.accept('stim0', self.set_stimulus, ['0']) #event handler
        self.accept('stim1', self.set_stimulus, ['1'])
        #Set dynamic transforms
        if self.current_stim_params['velocities'][0] != 0 and self.current_stim_params['velocities'][1] != 0:
            print("Moving textures")
            self.taskMgr.add(self.textures_update, "move_both")
              
    @property
    def texture_size(self):
        return self.tex_classes[self.current_stim_num].texture_size

    @property
    def current_stim_params(self):
        """ 
        returns actual value of current stimulus 
        """
        return self.stim_params[self.current_stim_num]
      
    def set_stimulus(self, data):
        """ 
        Invoked with different 
        """
        if not self.stimulus_initialized:
            """
            If the first texture has not yet been shown, then toggle initialization to on
            and do not clear previous texture (there is no previous texture). Otherwise
            clear previous texture otherwise it will cover new textures."""
            self.self_initialized = True
        else:
            self.left_card.clearTexture(self.left_texture_stage)  #turn off stage
            self.left_card.clearTexture(self.left_mask_stage)
            self.right_card.clearTexture(self.right_texture_stage)
            self.right_card.clearTexture(self.right_mask_stage)
        
        #Save stim to file
        if self.filestream:
            current_datetime = str(datetime.now())
            self.filestream.write(f"{current_datetime}\t{data}\n")
            self.filestream.flush()
            
        if data == '0':
            self.current_stim_num = 0
            
        elif data == '1':
            self.current_stim_num = 1

        print(self.current_stim_num, self.current_stim_params)
        self.stim = self.tex_classes[self.current_stim_num]

        self.mask_position_ndc = self.current_stim_params['position']
        self.mask_position_uv = (self.ndc2uv(self.mask_position_ndc[0]),
                                 self.ndc2uv(self.mask_position_ndc[1]))
        
        #CREATE MASK ARRAYS
        self.left_mask_array = 255*np.ones((self.texture_size, 
                                            self.texture_size), dtype=np.uint8)
        self.left_mask_array[:, self.texture_size//2 - self.current_stim_params['strip_width']//2 :] = 0
        self.right_mask_array = 255*np.ones((self.texture_size, 
                                              self.texture_size), dtype=np.uint8)
        self.right_mask_array[:, : self.texture_size//2 + self.current_stim_params['strip_width']//2] = 0
       
        #ADD TEXTURE STAGES TO CARDS
        self.left_mask.setRamImage(self.left_mask_array)
        self.left_card.setTexture(self.left_texture_stage, self.stim.texture)
        self.left_card.setTexture(self.left_mask_stage, self.left_mask)
        self.left_mask_stage.setCombineRgb(TextureStage.CMModulate,
                                    TextureStage.CSTexture,
                                    TextureStage.COSrcColor,
                                    TextureStage.CSPrevious,
                                    TextureStage.COSrcColor)
        
        self.right_mask.setRamImage(self.right_mask_array)
        self.right_card.setTexture(self.right_texture_stage, self.stim.texture)
        self.right_card.setTexture(self.right_mask_stage, self.right_mask)
        #Multiply the texture stages together
        self.right_mask_stage.setCombineRgb(TextureStage.CMModulate,
                                    TextureStage.CSTexture,
                                    TextureStage.COSrcColor,
                                    TextureStage.CSPrevious,
                                    TextureStage.COSrcColor)
        
        #SET TRANSFORMS
        #Masks
        self.mask_transform = self.trs_transform()
        self.left_card.setTexTransform(self.left_mask_stage, self.mask_transform)
        self.right_card.setTexTransform(self.right_mask_stage, self.mask_transform)
        #Left texture
        self.left_card.setTexScale(self.left_texture_stage, 1/self.scale)
        self.left_card.setTexRotate(self.left_texture_stage, self.current_stim_params['angles'][0])
        self.left_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
                
        #Right texture
        self.right_card.setTexScale(self.right_texture_stage, 1/self.scale)
        self.right_card.setTexRotate(self.right_texture_stage, self.current_stim_params['angles'][1])
        self.right_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))        
        
        return
               
    #Move textures
    def textures_update(self, task):
        left_tex_position =  -task.time*self.current_stim_params['velocities'][0] #negative b/c texture stage
        right_tex_position = -task.time*self.current_stim_params['velocities'][1]
        self.left_card.setTexPos(self.left_texture_stage, left_tex_position, 0, 0)
        self.right_card.setTexPos(self.right_texture_stage, right_tex_position, 0, 0)
        return task.cont

    def left_texture_update(self, task):
        left_tex_position = -task.time*self.left_velocity #negative b/c texture stage
        self.left_card.setTexPos(self.left_texture_stage, left_tex_position, 0, 0)
        return task.cont

    def right_texture_update(self, task):
        right_tex_position = -task.time*self.right_velocity
        self.right_card.setTexPos(self.right_texture_stage, right_tex_position, 0, 0)
        return task.cont

    def trs_transform(self):
        """ 
        trs = translate-rotate-scale transform for mask stage
        rdb contributed to this code
        """
        pos = 0.5 + self.mask_position_uv[0], 0.5 + self.mask_position_uv[1]
        center_shift = TransformState.make_pos2d((-pos[0], -pos[1]))
        scale = TransformState.make_scale2d(1/self.scale)
        rotate = TransformState.make_rotate2d(self.current_stim_params['strip_angle'])
        translate = TransformState.make_pos2d((0.5, 0.5))
        return translate.compose(rotate.compose(scale.compose(center_shift)))

    def ndc2uv(self, val):
        """ from model-based normalized device coordinates to texture-based uv-coordinates"""
        return 0.5*val

    def uv2ndc(self, val):
        """ from texture-based uv-coordinates to model-based normalized device coordinates"""
        return 2*val
    
    def set_title(self, title):
        self.windowProps.setTitle(title)
        ShowBaseGlobal.base.win.requestProperties(self.windowProps)  #base is a panda3d global




    
class ClosedLoopStim(ShowBase):
    """
    toggles between different textures depending on messages produced by ZmqHandler
    
    Note:
        I toyed with combining tex_classes/stim_params into one list:
            list(zip(tex_classes, stim_params))
        While that is more compact, to make the code more readable I just end up 
        separating them in the class. Something to think about though.
    """
    def __init__(self, tex_classes, stim_params, window_size = 512, 
                 profile_on = False, fps = 30, save_path = None):
        super().__init__()

        self.tex_classes = tex_classes
        self.current_stim_num = 0
        self.stim_params = stim_params
        self.window_size = window_size
        self.scale = np.sqrt(8)
        self.stimulus_initialized = False  #to handle case from -1 (uninitalize) to 0 (first stim)
        self.fps = fps
        self.save_path = save_path
        if self.save_path:
            self.filestream = open(self.save_path, "a")
        else:
            self.filestream = None 
        
        # Set frame rate
        ShowBaseGlobal.globalClock.setMode(ClockObject.MLimited)
        ShowBaseGlobal.globalClock.setFrameRate(self.fps)  #can lock this at whatever
        
        if profile_on:
            PStatClient.connect()
            ShowBaseGlobal.base.setFrameRateMeter(True) 
            
        #Window properties
        self.windowProps = WindowProperties()
        self.windowProps.setSize(self.window_size, self.window_size)
        self.set_title("Initializing")

        # Create initial card and texture stage
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        self.card = self.aspect2d.attachNewNode(cm.generate())
        self.card.setScale(self.scale)
        self.card.setColor((0.5, 0.5, 0.5, 1))
        self.texture_stage = TextureStage("texture_stage") 
                   
        #Set initial texture
        self.set_stimulus(str(self.current_stim_num))
        
        # Set up event handlers and tasks
        self.accept('stim0', self.set_stimulus, ['0']) #event handler
        self.accept('stim1', self.set_stimulus, ['1'])
        self.taskMgr.add(self.move_texture_task, "move_texture") #task


    @property
    def current_stim_params(self):
        """ 
        returns actual value of current stimulus 
        """
        return self.stim_params[self.current_stim_num]
    
    
    def set_stimulus(self, data):
        """ 
        Invoked with different 
        """
        if not self.stimulus_initialized:
            """
            If the first texture has not yet been shown, then toggle initialization to on
            and do not clear previous texture (there is no previous texture). Otherwise
            clear previous texture otherwise it will cover new textures."""
            self.self_initialized = True
        else:
            self.card.clearTexture(self.texture_stage)  #turn off stage
        
        #Save stim to file
        if self.filestream:
            current_datetime = str(datetime.now())
            self.filestream.write(f"{current_datetime}\t{data}\n")
            self.filestream.flush()
            
        if data == '0':
            self.current_stim_num = 0
            
        elif data == '1':
            self.current_stim_num = 1

        print(self.current_stim_num, self.current_stim_params)
        self.stim = self.tex_classes[self.current_stim_num]

        self.card.setColor((1, 1, 1, 1))
        self.card.setTexture(self.texture_stage, self.stim.texture)
        self.card.setR(self.current_stim_params['angle'])
        self.set_title(f"{self.current_stim_num}")

        return
               
    def move_texture_task(self, task):
        """
        The stimulus (texture) is set: now move it if needed.
        """
        if self.current_stim_params['velocity'] == 0:
            pass
        else:
            new_position = -task.time*self.current_stim_params['velocity']
            self.card.setTexPos(self.texture_stage, new_position, 0, 0) #u, v, w
        return task.cont 

    def set_title(self, title):
        self.windowProps.setTitle(title)
        ShowBaseGlobal.base.win.requestProperties(self.windowProps)  #base is a panda3d global


class KeyboardToggleStim(ShowBase):
    """
    toggles between different stim based on keyboard inputs (0/1)
    
    Useful for testing things out quickly before pushing to the ClostLoopStim classes.
    """
    def __init__(self, tex_classes, stim_params, window_size = 512, 
                 profile_on = False, fps = 30, save_path = None):
        super().__init__()

        self.tex_classes = tex_classes
        self.current_stim_num = 0
        self.stim_params = stim_params
        self.window_size = window_size
        self.bgcolor = (0.5, 0.5, 0.5, 1)
        self.stimulus_initialized = False  #to handle case from -1 (uninitalize) to 0 (first stim)
        self.fps = fps
        self.save_path = save_path
        if self.save_path:
            self.filestream = open(self.save_path, "a")
        else:
            self.filestream = None
        
        #Set up key control mechanism
        self.zero_button = KeyboardButton.ascii_key('0')
        self.one_button = KeyboardButton.ascii_key('1')
        self.is_down = ShowBaseGlobal.base.mouseWatcherNode.is_button_down

        #Window properties
        self.windowProps = WindowProperties()
        self.windowProps.setSize(self.window_size, self.window_size)
        self.set_title("Initializing")

        #Create scenegraph
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        self.card = self.aspect2d.attachNewNode(cm.generate())
        self.card.setScale(np.sqrt(8))
        self.card.setColor(self.bgcolor)  #make this an add mode
        self.texture_stage = TextureStage("texture_stage") 
        
        # Set frame rate
        ShowBaseGlobal.globalClock.setMode(ClockObject.MLimited)
        ShowBaseGlobal.globalClock.setFrameRate(self.fps)  #can lock this at whatever
        
        if profile_on:
            PStatClient.connect()
            ShowBaseGlobal.base.setFrameRateMeter(True) 
            
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
        """ 
        Called with relevant keyboard events
        """
        if not self.stimulus_initialized:
            """
            If the first texture has not yet been shown, then toggle initialization
            and do not clear previous texture (there is no previous texture). 
            Otherwise clear previous texture so they do not overlap."""
            self.self_initialized = True
        else:
            self.card.clearTexture(self.texture_stage)  #turn off stage


        if data == '0':
            self.current_stim_num = 0
            
        elif data == '1':
            self.current_stim_num = 1

        if self.filestream:
            current_datetime = str(datetime.now())
            data_to_save = f"{current_datetime}\t{data}"
            print(data_to_save)
            self.filestream.write(f"{current_datetime}\t{data}\n")
            self.filestream.flush()
        print(self.current_stim_num, self.current_stim_params)
        self.stim = self.tex_classes[self.current_stim_num]

        self.card.setColor((1, 1, 1, 1))
        self.card.setTexture(self.texture_stage, self.stim.texture)
        self.card.setR(self.current_stim_params['angle'])
        self.set_title(f"{self.current_stim_num}")

        return
       
        
    def move_texture_task(self, task):
        """
        The stimulus (texture) is set: now move it if needed.
        """
        if self.current_stim_params['velocity'] == 0:
            pass
        else:
            new_position = -task.time*self.current_stim_params['velocity']
            self.card.setTexPos(self.texture_stage, new_position, 0, 0) #u, v, w
        return task.cont 


    def set_title(self, title):
        self.windowProps.setTitle(title)
        ShowBaseGlobal.base.win.requestProperties(self.windowProps)  #base is a panda3d global






#%%  below stuff has NOT been refactored


class Scaling(ShowBase):
    """
    Show a single full-field texture that scales up or down in time, repeating.
    
    Matt: this has not been rewritten for the refactor it will not work.
    """
    def __init__(self, texture_array, scale = 0.2, window_size = 512, texture_size = 512):
        super().__init__()
        self.scale = scale
        self.texture_array = texture_array
        self.texture_dtype = type(self.texture_array.flat[0])
        self.ndims = self.texture_array.ndim

        #Set window title
        self.window_properties = WindowProperties()
        self.window_properties.setSize(window_size, window_size)
        self.window_properties.setTitle("FullFieldDrift")
        ShowBaseGlobal.base.win.requestProperties(self.window_properties)

        #Create texture stage
        self.texture = Texture("Stimulus")

        #Select Texture ComponentType (e.g., uint8 or whatever)
        if self.texture_dtype == np.uint8:
            self.texture_component_type = Texture.T_unsigned_byte
        elif self.texture_dtype == np.uint16:
            self.texture_component_type = Texture.T_unsigned_short

        #Select Texture Format (color or b/w etc)
        if self.ndims == 2:
            self.texture_format = Texture.F_luminance #grayscale
            self.texture.setup2dTexture(texture_size, texture_size,
                                   self.texture_component_type, self.texture_format)
            self.texture.setRamImageAs(self.texture_array, "L")
        elif self.ndims == 3:
            self.texture_format = Texture.F_rgb8
            self.texture.setup2dTexture(texture_size, texture_size,
                                   self.texture_component_type, self.texture_format)
            self.texture.setRamImageAs(self.texture_array, "RGB")
        else:
            raise ValueError("Texture needs to be 2d or 3d")

        self.textureStage = TextureStage("Stimulus")

        #Create scenegraph
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        self.card = self.aspect2d.attachNewNode(cm.generate())
        self.card.setTexture(self.textureStage, self.texture)  #ts, tx

        #Set the scale on the card (note this is different from scaling the texture)
        self.card.setScale(np.sqrt(2))

        if self.scale != 0:
            #Add task to taskmgr to translate texture
            self.taskMgr.add(self.scaleTextureTask, "scaleTextureTask")

    #Move the texture
    def scaleTextureTask(self, task):
        if task.time > 1:
            new_scale = task.time*(self.scale)
            self.card.setTexScale(self.textureStage, new_scale, new_scale) #u_scale, v
            #Set conditional so when it reaches 0 or some max it resets to 1

        return Task.cont
    
    




#%%
if __name__ == '__main__':
    import textures
    print("\nNote for more complete set of examples to get started, see stimulus_examples.py\n")
    sin_red_tex = textures.SinRgbTex(texture_size = 512,
                                     spatial_frequency = 20,
                                     rgb = (255, 0, 0))
    sin_red_stim = ShowTexMoving(sin_red_tex,
                                 angle = 25, 
                                 velocity = -0.05,
                                 profile_on = False)
    sin_red_stim.run()