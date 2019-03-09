# -*- coding: utf-8 -*-
"""
pandastim/textures.py
Functions used to create textures used for display by classes in stimulus_classes.py.

Part of pandastim package: https://github.com/EricThomson/pandastim 
"""

import numpy as np
from scipy import signal  #for grating (square wave)
import matplotlib.pyplot as plt


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


def sin_texture(texture_size = 512, spatial_frequency = 10):
    """
    Create sinusoidal numpy array that is wrap-periodic (the last
    element is cut off when it wraps around to the beginning it
    is smooth)
    """
    x = np.linspace(0, 2*np.pi, texture_size+1)
    y = np.linspace(0, 2*np.pi, texture_size+1)
    X, Y = np.meshgrid(x[:texture_size],y[:texture_size])
    return sin_byte(X, freq = spatial_frequency)


def sin_texture_2byte(texture_size = 512, spatial_frequency = 10):
    """
    Create sinusoidal 2 byte numpy array that is wrap-periodic (the last
    element is cut off when it wraps around to the beginning it
    is smooth)
    """
    x = np.linspace(0, 2*np.pi, texture_size+1)
    y = np.linspace(0, 2*np.pi, texture_size+1)
    X, Y = np.meshgrid(x[:texture_size],y[:texture_size])
    return sin_2byte(X, freq = spatial_frequency)
    
def sin_texture_rgb(texture_size = 512, spatial_frequency = 10, rgb = (255, 255, 255)):
    """ sinusoid that goes from 0 0 0 to the given rgb value. For fish often want red."""
    if not (all([x >= 0 for x in rgb]) and all([x <= 255 for x in rgb])):
        raise ValueError("rgb values must lie in [0,255]")
    x = np.linspace(0, 2*np.pi, texture_size+1)
    y = np.linspace(0, 2*np.pi, texture_size+1)
    X, Y = np.meshgrid(x[:texture_size],y[:texture_size])
    R = np.uint8((rgb[0]/255)*sin_byte(X, freq = spatial_frequency))
    G = np.uint8((rgb[1]/255)*sin_byte(X, freq = spatial_frequency))
    B = np.uint8((rgb[2]/255)*sin_byte(X, freq = spatial_frequency))
    rgb_sin = np.zeros((texture_size, texture_size, 3), dtype = np.uint8)
    rgb_sin[...,0] = R
    rgb_sin[...,1] = G
    rgb_sin[...,2] = B
    return rgb_sin

""" 
GRATINGS 
"""
def grating_byte(X, freq = 1):
    grating_float = signal.square(X*freq)
    grating_transformed = (grating_float+1)*127.5; #from 0-255
    return np.uint8(grating_transformed)


def grating_texture(texture_size = 512, spatial_frequency = 10):
    x = np.linspace(0, 2*np.pi, texture_size+1)
    y = np.linspace(0, 2*np.pi, texture_size+1)
    X, Y = np.meshgrid(x[:texture_size],y[:texture_size])
    return grating_byte(X, freq = spatial_frequency)

    
""" 
CIRCLE 
"""
def circle_texture(texture_size = 512, circle_center = (0,0), circle_radius = 100, 
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
    

""" 
PURE COLOR 
"""
def rgb_texture(texture_size = 512, rgb = (0, 0, 0)):
    """ Create an rgb array. Note you could make a card just by setting its 
    bgcolor, but this can be useful for combining multiple hues in different regions,
    while bgcolor is always a single color"""
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


#%%  for main, plot a bunch of instances/slices
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
    sin_tex_byte = sin_texture()
    plt.figure(3)
    plt.imshow(sin_tex_byte, cmap = 'gray')
    plt.title('sin_texture()')
    
    #grating_texture_byte
    grating_tex_byte = grating_texture()
    plt.figure(4)
    plt.imshow(grating_tex_byte, cmap = 'gray')
    plt.title('grating_texture()')

    #Circle byte
    circle_tex_byte = circle_texture()
    plt.figure(5)
    plt.imshow(circle_tex_byte, cmap = 'gray')
    plt.title('circle_texture()')
    
    #rgb_texture_byte
    purple_texture = rgb_texture(rgb = (125, 0 , 125))
    plt.figure(6)
    plt.imshow(purple_texture)
    plt.title('rgb_texture()')
    
    #sine rgb
    red_sin = sin_texture_rgb(texture_size = 512, spatial_frequency = 10, rgb = (255, 0, 0))
    plt.figure(7)
    plt.imshow(red_sin)
    plt.title('sin_texture_rgb()')
    plt.show()

