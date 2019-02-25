# -*- coding: utf-8 -*-
"""
pandastim/stimuli.py
Classes and functions used to create the visual stimuli (e.g., texture arrays).

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""

import numpy as np
from scipy import signal  #for grating (square wave)
import matplotlib.pyplot as plt

from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage
from panda3d.core import WindowProperties
from direct.showbase import ShowBaseGlobal  #global vars defined by p3d


"""
P3D CLASSES FOR SHOWING STIMULI
"""
class FullFieldStatic(ShowBase):
    """
    Presents given texture array at given angle
    """
    def __init__(self, texture_array, angle = 0, window_size = 512, texture_size = 512):
        super().__init__()

        self.texture_array = texture_array
        self.ndims = self.texture_array.ndim
        self.angle = angle
        
        #Set window title (need to update with each stim) and size
        self.windowProps = WindowProperties()
        self.windowProps.setSize(window_size, window_size)
        self.windowProps.setTitle("FullFieldStatic( )")
        ShowBaseGlobal.base.win.requestProperties(self.windowProps)  #base is a panda3d global
        
        #Create texture stage
        self.texture = Texture("static")
               
        #Select Texture Format (color or b/w etc)
        #https://www.panda3d.org/reference/python/classpanda3d_1_1core_1_1Texture.html#ab4e88c89b3b7ea1735996cc4def22d58
        if self.ndims == 2:
            self.data_format = Texture.F_luminance #grayscale
        elif self.ndims == 3:
            self.data_format = Texture.F_rgb8
        else:
            raise ValueError("Texture needs to be 2d or 3d")

        #Select Texture ComponentType (e.g., uint8 or whatever)
        #https://www.panda3d.org/reference/python/classpanda3d_1_1core_1_1Texture.html#a81f78fc173dedefe5a049c0aa3eed2c0
        self.data_type = Texture.T_unsigned_byte
        
        self.texture.setup2dTexture(texture_size, texture_size, 
                               self.data_type, self.data_format) 
        
        self.texture.setRamImage(self.texture_array)   
        self.textureStage = TextureStage("static")
                                                                    
        #Create scenegraph
        cm = CardMaker('card1')
        cm.setFrameFullscreenQuad()
        self.card1 = self.aspect2d.attachNewNode(cm.generate())  
        self.card1.setTexture(self.textureStage, self.texture)  #ts, tx
       
        #Transform the model(s)
        self.card1.setScale(np.sqrt(2))
        self.card1.setR(self.angle)
        

"""
TEXTURES
"""
"""SINUSOIDS:
    Note for a float, just use np.sin(freq*x) 
"""

def sin_byte(X, freq = 1):
    """
    Converts sine to unsigned 8 bit representation (T_unsigned_Byte). 
    Good for memory intensive situations.
    """
    sin_float = np.sin(freq*X)
    sin_transformed = (sin_float + 1)*127.5; #from 0-255
    return np.uint8(sin_transformed)


def sin_2byte(X, freq = 1):
    """
    Converts sine to unsigned 16 bit representation (T_unsigned_short). 
    Good when you want to avoid a float, but 8 bits isn't enough.
    """
    sin_float = np.sin(freq*X)
    sin_transformed = (sin_float + 1)*32767.5; #from 0-65535
    return np.uint16(sin_transformed)


def sin_texture_byte(texture_size = 512, spatial_frequency = 10):
    """
    Create sinusoidal numpy array that is wrap-periodic (the last
    element is cut off when it wraps around to the beginning it
    is smooth)
    """
    x = np.linspace(0, 2*np.pi, texture_size+1)
    y = np.linspace(0, 2*np.pi, texture_size+1)
    X, Y = np.meshgrid(x[:texture_size],y[:texture_size])
    return sin_byte(X, freq = spatial_frequency)
    

""" GRATINGS """
def grating_byte(X, freq = 1):
    grating_float = signal.square(X*freq)
    grating_transformed = (grating_float+1)*127.5; #from 0-255
    return np.uint8(grating_transformed)

def grating_texture_byte(texture_size = 512, spatial_frequency = 10):
    x = np.linspace(0, 2*np.pi, texture_size+1)
    y = np.linspace(0, 2*np.pi, texture_size+1)
    X, Y = np.meshgrid(x[:texture_size],y[:texture_size])
    return grating_byte(X, freq = spatial_frequency)

    
""" CIRCLE """
def circle_texture_byte(texture_size = 512, circle_center = (0,0), circle_radius = 100, 
                        bg_intensity = 0, face_intensity = 255):
    """ Create an array with a circle with radius circle_radius, centered at circle_center
    with face color face_intensity on background bg_intensity"""
    if face_intensity > 255 or bg_intensity < 0:
        raise ValueError('Circle intensity must be between 0 and 255')
    x = np.linspace(-texture_size/2, texture_size/2, texture_size)
    y = np.linspace(-texture_size/2, texture_size/2, texture_size)
    X, Y = np.meshgrid(x, y)
    circle_texture = bg_intensity*np.ones((texture_size, texture_size), dtype = np.uint8)
    circle_mask = (X - circle_center[0])**2 + (Y - circle_center[1])**2 <= circle_radius**2
    circle_texture[circle_mask] = face_intensity
    return circle_texture
    
""" PURE COLOR """
def rgb_texture_byte(texture_size = 512, rgb = (0, 0, 0)):
    """ Create an rgb array. Note you could make a card just by setting its 
    bgcolor, but this can be useful for combining multiple hues in different regions,
    while bgcolor is always a single color."""
    if not (all([x >= 0 for x in rgb]) and all([x <= 255 for x in rgb])):
        raise ValueError("rgb values must lie in [0,255]")

    x = np.linspace(-texture_size/2, texture_size/2, texture_size)
    y = np.linspace(-texture_size/2, texture_size/2, texture_size)
    X, Y = np.meshgrid(x, y)
    rgb_texture = np.zeros((texture_size, texture_size, 3), dtype = np.uint8)
    rgb_texture[..., 0] = rgb[0]
    rgb_texture[..., 1] = rgb[1]
    rgb_texture[..., 2] = rgb[2]
    return rgb_texture


#%% 
if __name__ == "__main__":
    num_vals = 256
    spatial_freq = 15
    
    #sin_byte
    x1 = np.linspace(0, 2*np.pi, num_vals+1)
    y1 = sin_byte(x1, freq = spatial_freq)
    plt.figure(1)
    plt.plot(x1,y1)
    plt.scatter(x1,y1)
    plt.title('sin_byte()')

    #sin_2byte
    x2 = np.linspace(0, 2*np.pi, num_vals+1)
    y2 = sin_2byte(x2, freq = spatial_freq)
    plt.figure(2)
    plt.plot(x2,y2)
    plt.scatter(x2,y2)
    plt.title('sin_2byte()')

    #quick tests for minimal conditional for periodicity (note this is necessary, not close to suff)
    assert(y1[0] == y1[-1])
    assert(y2[0] == y2[-1])
    
    #sin_texture_byte
    sin_tex_byte = sin_texture_byte()
    plt.figure(3)
    plt.imshow(sin_tex_byte, cmap = 'gray')
    plt.title('sin_tex_byte()')
    
    #grating_texture_byte
    grating_tex_byte = grating_texture_byte()
    plt.figure(4)
    plt.imshow(grating_tex_byte, cmap = 'gray')
    plt.title('grating_tex_byte()')

    #Circle byte
    circle_tex_byte = circle_texture_byte()
    plt.figure(5)
    plt.imshow(circle_tex_byte, cmap = 'gray')
    plt.title('circle_tex_byte()')
    
    #rgb_texture_byte
    purple_texture = rgb_texture_byte(rgb = (125, 0 , 125))
    plt.figure(6)
    plt.imshow(purple_texture)
    plt.title('rgb_texture_byte()')
    plt.show()

    #Full field static
    #Test with grating
    stim_params = {'spatial_freq': 15, 'angle': -45}
    texture_size = 512
    window_size = 512
    tex_array = grating_texture_byte(texture_size, stim_params['spatial_freq'])
    pandastim_static = FullFieldStatic(tex_array, angle = stim_params["angle"], 
                                        window_size = window_size, texture_size = texture_size)
    pandastim_static.run()