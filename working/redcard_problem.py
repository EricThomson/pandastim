import numpy as np 
import matplotlib.pyplot as plt
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage

def rgb_texture_byte(texture_size = 512, rgb = (0, 0, 0)):
    """ Return Could just set card's bg color but this has other uses."""
    if not (all([x >= 0 for x in rgb]) and all([x <= 255 for x in rgb])):
        raise ValueError("rgb values must lie in [0,255]")
    rgb_texture = np.zeros((texture_size, texture_size, 3), dtype = np.uint8)
    rgb_texture[..., 0] = rgb[0]
    rgb_texture[..., 1] = rgb[1]
    rgb_texture[..., 2] = rgb[2]
    return rgb_texture

class FullFieldStatic(ShowBase):
    def __init__(self, texture_array, window_size = 512, texture_size = 512):
        super().__init__()
        self.texture_array = texture_array
        self.texture = Texture("static")       
        self.texture.setup2dTexture(texture_size, texture_size, 
                              Texture.T_unsigned_byte, Texture.F_rgb8) 
        self.texture.setRamImageAs(self.texture_array, "RGB")   #so it isn't bgr bc fuck that
        self.textureStage = TextureStage("static")
        cm = CardMaker('card1')
        cm.setFrameFullscreenQuad()
        self.card1 = self.aspect2d.attachNewNode(cm.generate())  
        self.card1.setTexture(self.textureStage, self.texture) 
        
if __name__ == '__main__':
    rgb = (255, 0, 0)
    texture_size = 512
    window_size = 512
    red_texture = rgb_texture_byte(texture_size, rgb)
    plt.imshow(red_texture)
    plt.title('Matplotlib red texture')
    plt.show()
    red_static = FullFieldStatic(red_texture, window_size = window_size, texture_size = texture_size)
    red_static.run()
