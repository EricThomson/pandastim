# -*- coding: utf-8 -*-
"""
stimuli.py: module in pandastim package
Code related to producing stimuli
https://github.com/EricThomson/pandastim

Includes classes and functions for generating textures (e.g., sines and gratings),
and other resources directly related to generating stimuli.


Component types:
https://www.panda3d.org/reference/python/classpanda3d_1_1core_1_1Texture.html#a81f78fc173dedefe5a049c0aa3eed2c0
    T_unsigned_byte 	(1byte = 8 bits: 0 to 255)
    T_unsigned_short (2 bytes (16 bits): 0 to 65535, but this is platform dependent)
    T_float 	 (floats: not sure if single (32 bit) or double (64 bit))
    T_unsigned_int_24_8 	 (packed: one 24 bit for depth, one 8 bit for stencil)
    T_int 	(signed int)
    T_byte 	(signed byte: from -128 to 127)
    T_short 	(signed short: 2 bytes from -32768 to 32767)
    T_half_float (2 bytes: may sometimes be good if you are inside the 0-1 range)
    T_unsigned_int (4 bytes (32 bits): from 0 to ~4 billion)
"""

import numpy as np
from scipy import signal  #for grating (square wave)
import matplotlib.pyplot as plt


"""
SINUSOID: note if you want a flat-out sine float, just use np.sin(freq*x) 
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
    

    
