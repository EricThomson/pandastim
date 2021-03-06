"""
pandastim/stimuli.py
Classes to present visual stimuli in pandastim (subclasses of ShowBase, which 
implements the main event loop in panda3d).

Part of pandastim package: https://github.com/EricThomson/pandastim
"""
import sys
import numpy as np
from datetime import datetime
import logging

from direct.showbase.ShowBase import ShowBase
from direct.showbase import ShowBaseGlobal  #global vars defined by p3d
from panda3d.core import Texture, CardMaker, TextureStage, KeyboardButton
from panda3d.core import WindowProperties, ColorBlendAttrib, TransformState, ClockObject
from panda3d.core import AntialiasAttrib
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText   #for binocular stim
from panda3d.core import PStatClient

import utils

# Set up a logger
log_level = logging.INFO
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) #because annoying reasons
if not logger.hasHandlers():
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setLevel(log_level)
    logger.addHandler(log_handler)


class TexMoving(ShowBase):
    """
    Shows single texture drifting across the window at specified velocity and angle.
    
    Usage:
        tex = SinGreyTex()
        stim_show = ShowTexMoving(tex, angle = 30, velocity = 0.1, fps = 40, profile_on = True)
        stim_show.run()
        
    Note(s):
        Positive angles are clockwise, negative ccw.
        Velocity is normalized to window size, so 1.0 is the entire window width (i.e., super-fast).
    """
    def __init__(self, tex, angle = 0, velocity = 0.1, fps = 30,
                 window_name = "ShowTexMoving", window_size = None, profile_on = False):
        super().__init__()
        self.tex = tex
        if window_size is None:
            self.window_size = self.tex.texture_size
        else:
            self.window_size = window_size
        self.angle = angle
        self.velocity = velocity
        self.texture_stage = TextureStage("texture_stage") 
        self.window_name = window_name
        
        # Set frame rate (fps)
        ShowBaseGlobal.globalClock.setMode(ClockObject.MLimited)
        ShowBaseGlobal.globalClock.setFrameRate(fps) 
        
        #Set up profiling if desired
        if profile_on:
            PStatClient.connect() # this will only work if pstats is running: see readme
            ShowBaseGlobal.base.setFrameRateMeter(True)  #Show frame rate
            self.center_indicator = None
            
        #Window properties set up 
        self.window_properties = WindowProperties()
        self.window_properties.setSize(self.window_size, self.window_size)
        self.window_properties.setTitle(window_name)
        ShowBaseGlobal.base.win.requestProperties(self.window_properties)
        
        #Create scenegraph, attach stimulus to card.
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        self.card = self.aspect2d.attachNewNode(cm.generate())
        # Scale is so it can handle arbitrary rotations and shifts in binocular case
        self.card.setScale(np.sqrt(8))
        self.card.setColor((1, 1, 1, 1)) # makes it bright when bright (default combination with card is add)
        self.card.setTexture(self.texture_stage, self.tex.texture)
        self.card.setTexRotate(self.texture_stage, self.angle)
        
        if self.velocity != 0:
            #Add task to taskmgr to translate texture
            self.taskMgr.add(self.moveTextureTask, "moveTextureTask")
        
    #Task for moving the texture
    def moveTextureTask(self, task):
        new_position = -task.time*self.velocity
        self.card.setTexPos(self.texture_stage, new_position, 0, 0) #u, v, w
        return Task.cont
    
                
class TexFixed(TexMoving):
    """
    Presents single texture without any motion. Useful for debugging: no need to set fps high.
    
    Usage:
        tex = SinGreyTex()
        stim_show = ShowTexStatic(tex, fps = 10, profile_on = True)
        stim_show.run()
    """
    def __init__(self, tex, angle = 0,  fps = 30, window_size = None, 
                 window_name = "ShowTexStatic", profile_on = False):     
        super().__init__(tex, angle = angle, velocity = 0, 
                         fps = fps, window_size = window_size, 
                         profile_on = profile_on, window_name = window_name)
        self.window_properties.setTitle(self.window_name)
        ShowBaseGlobal.base.win.requestProperties(self.window_properties)



class InputControlParams(ShowBase):
    """
    Input signal sends in x, y, theta values for binocular stimuli to control
    those parameters of the stim in real time. Need to expand to single texture.

    Usage:
        InputControlParams(texture_object,
                        stim_angles = (0, 0),
                        strip_angle = 0,
                        position = (0,0),
                        velocities = (0,0),
                        strip_width = 2,
                        window_size = 512,
                        window_name = 'FunStim',
                        profile_on  = False)

    Note(s):
        - angles are relative to strip angle
        - position is x,y in card-based coordinates (from [-1 1]), so (.5, .5) will be in middle of top right quadrant
        - Velocity is in same direction as angle, and units of window size (so 1 is super-fast)
        - strip_width is just the width of the strip down the middle. Can be 0.
    """
    def __init__(self, tex, stim_angles = (0, 0), initial_angle = 0, initial_position = (0,0),
                 velocities = (0,0), strip_width = 4, fps = 30, window_size = None,
                 window_name = 'position control', profile_on = False, save_path = None):
        super().__init__()
        self.render.setAntialias(AntialiasAttrib.MMultisample)
        self.aspect2d.prepareScene(ShowBaseGlobal.base.win.getGsg())  # pre-loads world
        self.tex = tex
        if window_size == None:
            self.window_size = tex.texture_size
        else:
            self.window_size = window_size
        self.mask_position_card = initial_position
        self.strip_width = strip_width
        self.scale = np.sqrt(8)  #so it can handle arbitrary rotations and shifts
        self.strip_angle = initial_angle #this will change fairly frequently
        self.stim_angles = stim_angles
        self.left_texture_angle = self.stim_angles[0] + self.strip_angle  #make this a property
        self.right_texture_angle = self.stim_angles[1] + self.strip_angle
        self.left_velocity = velocities[0]
        self.right_velocity = velocities[1]
        self.fps = fps
        self.window_name = window_name
        self.profile_on = profile_on
        print(save_path)
        self.save_path = save_path
        if self.save_path:
            initial_params = {'angles': stim_angles, 'initial_angle': self.strip_angle, 
                              'velocities': velocities, 'strip_width': self.strip_width,
                              'initial_position': initial_position}
            print(tex, initial_params)
            self.filestream = utils.save_initialize(self.save_path, [tex], [initial_params])
            print(self.filestream)
        else:
            self.filestream = None 
        
        #Set window title and size
        self.window_properties = WindowProperties()
        self.window_properties.setSize(self.window_size, self.window_size)
        self.window_properties.setTitle(self.window_name)
        ShowBaseGlobal.base.win.requestProperties(self.window_properties)  #base is a panda3d global

        # Set frame rate
        ShowBaseGlobal.globalClock.setMode(ClockObject.MLimited)
        ShowBaseGlobal.globalClock.setFrameRate(self.fps)  #can lock this at whatever
        
        #CREATE MASK ARRAYS
        self.left_mask_array = 255*np.ones((self.tex.texture_size, self.tex.texture_size), dtype=np.uint8)
        self.left_mask_array[:, self.tex.texture_size//2 - self.strip_width//2 :] = 0
        self.right_mask_array = 255*np.ones((self.tex.texture_size, self.tex.texture_size), dtype=np.uint8)
        self.right_mask_array[:, : self.tex.texture_size//2 + self.strip_width//2] = 0

        #TEXTURE STAGES FOR LEFT CARD
        self.left_texture_stage = TextureStage('left_texture_stage')
        #Mask
        self.left_mask = Texture("left_mask_texture")
        self.left_mask.setup2dTexture(self.tex.texture_size, self.tex.texture_size,
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
        self.right_mask.setup2dTexture(self.tex.texture_size, self.tex.texture_size,
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
        #self.setBackgroundColor((0,0,0,1))
        self.left_card = self.aspect2d.attachNewNode(cm.generate())
        self.right_card = self.aspect2d.attachNewNode(cm.generate())
        self.left_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
        self.right_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))

        #ADD TEXTURE STAGES TO CARDS
        self.left_card.setTexture(self.left_texture_stage, self.tex.texture)
        self.left_card.setTexture(self.left_mask_stage, self.left_mask)
        self.right_card.setTexture(self.right_texture_stage, self.tex.texture)
        self.right_card.setTexture(self.right_mask_stage, self.right_mask)
        self.setBackgroundColor((0,0,0,1))  # without this the cards will appear washed out
        #self.left_card.setAntialias(AntialiasAttrib.MMultisample)
        #self.right_card.setAntialias(AntialiasAttrib.MMultisample)
        #TRANSFORMS
        # Masks
        self.mask_transform = self.trs_transform()
        self.left_card.setTexTransform(self.left_mask_stage, self.mask_transform)
        self.right_card.setTexTransform(self.right_mask_stage, self.mask_transform)
        
        # Textures
        # Left
        self.left_card.setTexScale(self.left_texture_stage, 1/self.scale)
        self.left_card.setTexRotate(self.left_texture_stage, self.left_texture_angle)
        # Right 
        self.right_card.setTexScale(self.right_texture_stage, 1/self.scale)
        self.right_card.setTexRotate(self.right_texture_stage, self.right_texture_angle)
        
        #Set task manager(s) for textures
        if self.left_velocity != 0 and self.right_velocity != 0:
            self.taskMgr.add(self.textures_update, "move_both")
        elif self.left_velocity != 0 and self.right_velocity == 0:
            self.taskMgr.add(self.left_texture_update, "move_left")
        elif self.left_velocity == 0 and self.right_velocity != 0:
            self.taskMgr.add(self.right_texture_update, "move_right")

        # Event handler to process the messages
        self.accept("stim", self.process_stim, [])

        #Set up profiling if desired
        if profile_on:
            PStatClient.connect() # this will only work if pstats is running
            ShowBaseGlobal.base.setFrameRateMeter(True)  #Show frame rate


    @property
    def mask_position_uv(self):
        return (utils.card2uv(self.mask_position_card[0]),
                                 utils.card2uv(self.mask_position_card[1]))
        
    def process_stim(self, x, y, theta):
        """
        Event handler method for processing message about current x,y, theta
        """
        # If new values are same as previous, return to caller. Otherwise, reset
        if (self.strip_angle, self.mask_position_card) == (theta, (x, y)):
            return
        else:
            self.strip_angle = theta
            self.right_texture_angle = self.stim_angles[1] + self.strip_angle
            self.left_texture_angle = self.stim_angles[0] + self.strip_angle
            #print(self.strip_angle, self.left_texture_angle, self.right_texture_angle)  
            self.mask_position_card = (x, y)
            self.mask_transform = self.trs_transform()
            self.left_card.setTexTransform(self.left_mask_stage, self.mask_transform)
            self.right_card.setTexTransform(self.right_mask_stage, self.mask_transform)
            self.left_card.setTexRotate(self.left_texture_stage, self.left_texture_angle)
            self.right_card.setTexRotate(self.right_texture_stage, self.right_texture_angle)
            
        if self.filestream:
            self.filestream.write(f"{str(datetime.now())}\t{x}\t{y}\t{theta}\n")
            self.filestream.flush()
            return
        
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
        #print(self.strip_angle)
        pos = 0.5 + self.mask_position_uv[0], 0.5 + self.mask_position_uv[1]
        center_shift = TransformState.make_pos2d((-pos[0], -pos[1]))
        scale = TransformState.make_scale2d(1/self.scale)
        rotate = TransformState.make_rotate2d(self.strip_angle)
        translate = TransformState.make_pos2d((0.5, 0.5))
        return translate.compose(rotate.compose(scale.compose(center_shift)))
 
    
class BinocularMoving(ShowBase):
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
                        window_name = 'FunStim',
                        profile_on  = False)

    Note(s):
        - angles are (left_texture_angle, right_texture_angle): >0 is cw, <0 ccw
        - Make texture_size a power of 2: this makes the GPU happier.
        - position is x,y in card-based coordinates (from [-1 1]), so (.5, .5) will be in middle of top right quadrant
        - Velocity is in card-based units, so 1.0 is the entire window width (i.e., super-fast).
        - strip_width is just the width of the strip down the middle. It can be 0. Even is better.
        - The texture array can be 2d (gray) or NxNx3 (rgb) with unit8 or uint16 elements.
    """
    def __init__(self, tex, stim_angles = (0, 0), strip_angle = 0, position = (0,0),
                 velocities = (0,0), strip_width = 4, fps = 30, window_size = None,
                 window_name = 'BinocularDrift', profile_on = False):
        super().__init__()
        self.tex = tex
        if window_size == None:
            self.window_size = tex.texture_size
        else:
            self.window_size = window_size
        self.mask_position_card = position
        self.mask_position_uv = (utils.card2uv(self.mask_position_card[0]),
                                 utils.card2uv(self.mask_position_card[1]))
        self.scale = np.sqrt(8)  #so it can handle arbitrary rotations and shifts
        self.left_texture_angle = stim_angles[0]
        self.right_texture_angle = stim_angles[1]
        self.left_velocity = velocities[0]
        self.right_velocity = velocities[1]
        self.strip_angle = strip_angle #this will change fairly frequently
        self.fps = fps
        self.window_name = window_name
        self.profile_on = profile_on

        #Set window title and size
        self.window_properties = WindowProperties()
        self.window_properties.setSize(self.window_size, self.window_size)
        self.window_properties.setTitle(self.window_name)
        ShowBaseGlobal.base.win.requestProperties(self.window_properties)  #base is a panda3d global

        #CREATE MASK ARRAYS
        self.left_mask_array = 255*np.ones((self.tex.texture_size, self.tex.texture_size), dtype=np.uint8)
        self.left_mask_array[:, self.tex.texture_size//2 - strip_width//2 :] = 0
        self.right_mask_array = 255*np.ones((self.tex.texture_size, self.tex.texture_size), dtype=np.uint8)
        self.right_mask_array[:, : self.tex.texture_size//2 + strip_width//2] = 0

        #TEXTURE STAGES FOR LEFT CARD
        self.left_texture_stage = TextureStage('left_texture_stage')
        #Mask
        self.left_mask = Texture("left_mask_texture")
        self.left_mask.setup2dTexture(self.tex.texture_size, self.tex.texture_size,
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
        self.right_mask.setup2dTexture(self.tex.texture_size, self.tex.texture_size,
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
        #self.setBackgroundColor((0,0,0,1))
        self.left_card = self.aspect2d.attachNewNode(cm.generate())
        self.right_card = self.aspect2d.attachNewNode(cm.generate())
        self.left_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
        self.right_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))

        #ADD TEXTURE STAGES TO CARDS
        self.left_card.setTexture(self.left_texture_stage, self.tex.texture)
        self.left_card.setTexture(self.left_mask_stage, self.left_mask)
        self.right_card.setTexture(self.right_texture_stage, self.tex.texture)
        self.right_card.setTexture(self.right_mask_stage, self.right_mask)
        self.setBackgroundColor((0,0,0,1))  # without this the cards will appear washed out

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
            self.taskMgr.add(self.textures_update, "move_both")
        elif self.left_velocity != 0 and self.right_velocity == 0:
            self.taskMgr.add(self.left_texture_update, "move_left")
        elif self.left_velocity == 0 and self.right_velocity != 0:
            self.taskMgr.add(self.right_texture_update, "move_right")

        # Set frame rate
        ShowBaseGlobal.globalClock.setMode(ClockObject.MLimited)
        ShowBaseGlobal.globalClock.setFrameRate(self.fps)  #can lock this at whatever
        
        #Set up profiling if desired
        if profile_on:
            PStatClient.connect() # this will only work if pstats is running
            ShowBaseGlobal.base.setFrameRateMeter(True)  #Show frame rate
            # Following will show a small x at the center
            self.title = OnscreenText("x",
                                      style = 1,
                                      fg = (1,1,1,1),
                                      bg = (0,0,0,.8),
                                      pos = self.mask_position_card,
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

    
        
        
class BinocularFixed(BinocularMoving):
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


class KeyboardToggleTex(ShowBase):
    """
    toggles between two textures based on keyboard inputs (0 and 1). Not set up
    for binocular stim. Similar call to InputControlStim
    """
    def __init__(self, tex_classes, stim_params, window_size = 512, 
                 profile_on = False, fps = 30, save_path = None):
        super().__init__()

        self.tex_classes = tex_classes
        self.current_tex_num = 0
        self.stim_params = stim_params
        self.window_size = window_size
        self.stimulus_initialized = False  #to handle case from -1 (uninitalize) to 0 (first stim)
        self.fps = fps
        self.save_path = save_path
        if self.save_path:
            self.filestream = utils.save_initialize(save_path, tex_classes, stim_params)
        else:
            self.filestream = None
        
        #Window properties
        self.windowProps = WindowProperties()
        self.windowProps.setSize(self.window_size, self.window_size)
        self.set_title("Initializing")

        #Create scenegraph
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        self.card = self.aspect2d.attachNewNode(cm.generate())
        self.card.setScale(np.sqrt(8))
        self.texture_stage = TextureStage("texture_stage") 
        
        # Set frame rate
        ShowBaseGlobal.globalClock.setMode(ClockObject.MLimited)
        ShowBaseGlobal.globalClock.setFrameRate(self.fps)  #can lock this at whatever
        
        if profile_on:
            PStatClient.connect()
            ShowBaseGlobal.base.setFrameRateMeter(True) 
            
        #Set initial texture
        self.set_stimulus(str(self.current_tex_num))
        
        # Set up event handlers and tasks
        self.accept('0', self.set_stimulus, ['0']) #event handler
        self.accept('1', self.set_stimulus, ['1'])
        self.taskMgr.add(self.move_texture_task, "move_texture") #task

    @property
    def current_stim_params(self):
        """ 
        returns parameters of current stimulus
        """
        return self.stim_params[self.current_tex_num]
    
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
            self.card.detachNode()  


        if data == '0':
            self.current_tex_num = 0
        elif data == '1':
            self.current_tex_num = 1

        if self.filestream:
            current_datetime = str(datetime.now())
            self.filestream.write(f"{current_datetime}\t{data}\n")
            self.filestream.flush()
        logger.info(self.current_tex_num, self.current_stim_params)
        self.tex = self.tex_classes[self.current_tex_num]

        self.card.setColor((1, 1, 1, 1))
        self.card.setTexture(self.texture_stage, self.tex.texture)
        self.card.setTexRotate(self.texture_stage, self.current_stim_params['angle'])
        other_stim = 1 if self.current_tex_num == 0 else 0
        self.set_title(f"Press {other_stim} to switch")

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

    
class InputControlStim(ShowBase):
    """
    Generic input-controll stimulus class: takes in list of texture classes, and stimulus parameters.
    Stimulus shown, in real-time, depends on events produced by utils.Monitor() class.
    
    Inputs:
        Positional
            tex_classes: m-element list of texture classes
            stim_params: m-element list of dictionaries: each contains parameters (e.g., velocity)
        
        Keyword 
            initial_tex_ind (0): index for first stim to show
            window_size (512): size of the panda3d window (pixels)
            window_name ('InputControlStim'): title of window in gui
            profile_on (False): will show actual fps, profiler, and little x at center if True
            fps (30): controls frame rate of display
            save_path (None): if set to a file path, will save data about stimuli, and time they are delivered
    """
    def __init__(self, tex_classes, stim_params, initial_tex_ind = 0, window_size = 512, 
                 window_name = "InputControlStim", profile_on = False, fps = 30, save_path = None):
        super().__init__()

        self.current_tex_num = initial_tex_ind
        self.previous_tex_num = None
        self.tex_classes = tex_classes
        self.stim_params = stim_params
        self.window_size = window_size
        self.stimulus_initialized = False  # for setting up first stim (don't clear cards they don't exist)
        self.fps = fps
        self.profile_on = profile_on
        self.save_path = save_path
        if self.save_path:
            self.filestream = utils.save_initialize(save_path, tex_classes, stim_params)
        else:
            self.filestream = None 
        self.scale = np.sqrt(8)  #so it can handle arbitrary rotations and shifts
        self.window_name = window_name
        
        #Window properties
        self.window_props = WindowProperties()
        self.window_props.setSize(self.window_size, self.window_size)
        self.set_title(self.window_name)

        # Set frame rate
        ShowBaseGlobal.globalClock.setMode(ClockObject.MLimited)
        ShowBaseGlobal.globalClock.setFrameRate(self.fps)  
        
        #Set up profiling if desired
        if self.profile_on:
            PStatClient.connect() # this will only work if pstats is running
            ShowBaseGlobal.base.setFrameRateMeter(True)  #Show frame rate
                       
        #Set initial texture(s)
        self.set_stimulus(str(self.current_tex_num))
        
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
            try:
                self.left_card.setTexPos(self.left_texture_stage, left_tex_position, 0, 0)
                self.right_card.setTexPos(self.right_texture_stage, right_tex_position, 0, 0)
            except Exception as e:
                logger.error(e)
        elif self.current_stim_params['stim_type'] == 's':
            if self.current_stim_params['velocity'] == 0:
                pass
            else:
                new_position = -task.time*self.current_stim_params['velocity']
                # Sometimes setting position fails when the texture stage isn't fully set
                try:
                    self.card.setTexPos(self.texture_stage, new_position, 0, 0) #u, v, w
                except Exception as e:
                    logger.error(e)
        return task.cont
    
    @property
    def texture_size(self):
        return self.tex_classes[self.current_tex_num].texture_size

    @property
    def current_stim_params(self):
        """ 
        Parameters of current texture (e.g., velocity, stim_type) 
        """
        return self.stim_params[self.current_tex_num]
    
    def create_cards(self):
        """ 
        Create cards: these are panda3d objects that are required for displaying textures.
        You can't just have a disembodied texture. In pandastim (at least for now) we are
        only showing 2d projections of textures, so we use cards.       
        """
        cardmaker = CardMaker("stimcard")
        cardmaker.setFrameFullscreenQuad()
        #Binocular cards
        if self.current_stim_params['stim_type'] == 'b':
            self.setBackgroundColor((0,0,0,1))  # without this the cards will appear washed out
            self.left_card = self.aspect2d.attachNewNode(cardmaker.generate())
            self.left_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add)) # otherwise only right card shows
    
            self.right_card = self.aspect2d.attachNewNode(cardmaker.generate())
            self.right_card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.M_add))
            if self.profile_on:
                self.center_indicator = OnscreenText("x",
                                                     style = 1,
                                                     fg = (1,1,1,1),
                                                     bg = (0,0,0,.8),
                                                     pos = self.current_stim_params['position'],
                                                     scale = 0.05)
        # Tex card
        elif self.current_stim_params['stim_type'] == 's':
            self.card = self.aspect2d.attachNewNode(cardmaker.generate())
            self.card.setColor((1, 1, 1, 1)) #?
            self.card.setScale(self.scale)
        return
        
    def create_texture_stages(self):
        """
        Create the texture stages: these are basically textures that you can apply
        to cards (sometimes mulitple textures at the same time -- is useful with
        masks).
        
        For more on texture stages:
        https://docs.panda3d.org/1.10/python/programming/texturing/multitexture-introduction
        """
        #Binocular cards
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
        # Tex card
        elif self.current_stim_params['stim_type'] == 's':
            self.texture_stage = TextureStage("texture_stage") 
        return
    
    def set_stimulus(self, data):
        """ 
        Uses events from zmq to set the stimulus value. 
        """
        logger.debug("\tset_stimulus(%s)", data)
        if not self.stimulus_initialized:
            # If this is first stim, then toggle initialization to on, and
            # do not clear previous texture (there is no previous texture).
            self.stimulus_initialized = True
            self.data_previous = data
        elif data == self.data_previous:
            return
        else:
            self.data_previous = data
            self.clear_cards() #clear the textures before adding new ones

        # This assumes data streaming is string numbers 0, 1, etc.
        self.current_tex_num = int(data)
            
        # Set new texture stages/cards etc
        self.tex = self.tex_classes[self.current_tex_num]
        
        logger.debug("\t%d: %s", self.current_tex_num, self.tex)
        self.create_texture_stages()
        self.create_cards()
        self.set_texture_stages()
        self.set_transforms()
        #Save stim to file (put this last as you want to set transforms quickly)
        if self.filestream:
            self.filestream.write(f"{str(datetime.now())}\t{data}\n")
            self.filestream.flush()
        return
    
    def clear_cards(self):
        """ 
        Clear cards when new stimulus: stim-class sensitive
        """
        if self.current_stim_params['stim_type'] == 'b':
            self.left_card.detachNode()
            self.right_card.detachNode()
            if self.profile_on:
                self.center_indicator.detachNode()
        elif self.current_stim_params['stim_type'] == 's':
            self.card.detachNode()
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

            #Right texture
            self.right_card.setTexScale(self.right_texture_stage, 1/self.scale)
            self.right_card.setTexRotate(self.right_texture_stage, self.current_stim_params['angles'][1])
            
        if self.current_stim_params['stim_type'] == 's':
            self.card.setTexRotate(self.texture_stage, self.current_stim_params['angle'])
        return
          
    def set_texture_stages(self):
        """ 
        Add texture stages to cards
        """
        if self.current_stim_params['stim_type'] == 'b':
            self.mask_position_uv = (utils.card2uv(self.current_stim_params['position'][0]),
                                     utils.card2uv(self.current_stim_params['position'][1]))
            
            #CREATE MASK ARRAYS
            self.left_mask_array = 255*np.ones((self.texture_size, 
                                                self.texture_size), dtype=np.uint8)
            self.left_mask_array[:, self.texture_size//2 - self.current_stim_params['strip_width']//2 :] = 0
            self.right_mask_array = 255*np.ones((self.texture_size, 
                                                  self.texture_size), dtype=np.uint8)
            self.right_mask_array[:, : self.texture_size//2 + self.current_stim_params['strip_width']//2] = 0
    
            #ADD TEXTURE STAGES TO CARDS
            self.left_mask.setRamImage(self.left_mask_array)
            self.left_card.setTexture(self.left_texture_stage, self.tex.texture)
            self.left_card.setTexture(self.left_mask_stage, self.left_mask)
            #Multiply the texture stages together
            self.left_mask_stage.setCombineRgb(TextureStage.CMModulate,
                                               TextureStage.CSTexture,
                                               TextureStage.COSrcColor,
                                               TextureStage.CSPrevious,
                                               TextureStage.COSrcColor)
            self.right_mask.setRamImage(self.right_mask_array)
            self.right_card.setTexture(self.right_texture_stage, self.tex.texture)
            self.right_card.setTexture(self.right_mask_stage, self.right_mask)
            #Multiply the texture stages together
            self.right_mask_stage.setCombineRgb(TextureStage.CMModulate,
                                                TextureStage.CSTexture,
                                                TextureStage.COSrcColor,
                                                TextureStage.CSPrevious,
                                                TextureStage.COSrcColor)
            
        elif self.current_stim_params['stim_type'] == 's':
            self.card.setTexture(self.texture_stage, self.tex.texture)
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
   
    def set_title(self, title):
        self.window_props.setTitle(title)
        ShowBaseGlobal.base.win.requestProperties(self.window_props)  #base is a panda3d global
    

#%%  below stuff has NOT been refactors and probably will not work
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
    sin_red_tex = textures.SinRgbTex(texture_size = 512,
                                     spatial_frequency = 20,
                                     rgb = (255, 0, 0))
    sin_red_stim = TexMoving(sin_red_tex,
                             angle = 25, 
                             velocity = -0.05,
                             window_name = 'red sin test stim',
                             profile_on = False)
    sin_red_stim.run()