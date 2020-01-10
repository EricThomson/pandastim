import numpy as np
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture, CardMaker, TextureStage
from direct.task import Task
from panda3d.core import TransformState

def make_circle_tex(texture_size = 512, circle_center = (0, 0), circle_radius = 100):
    x = np.linspace(-texture_size/2, texture_size/2, texture_size)
    y = np.linspace(-texture_size/2, texture_size/2, texture_size)
    X, Y = np.meshgrid(x, y)
    circle_texture = np.zeros((texture_size, texture_size), dtype = np.uint8)
    circle_mask = (X - circle_center[0])**2 + (Y - circle_center[1])**2 <= circle_radius**2
    circle_texture[circle_mask] = 255
    return np.uint8(circle_texture)


class TexScaler(ShowBase):
    """
    Show a single full-field texture that scales up or down in time, starting after 1 second.
    """
    def __init__(self, texture_array, scale = 0.2, window_size = 512, texture_size = 512):
        super().__init__()
        self.scale = scale
        self.current_scale = 1
        self.texture_array = texture_array
        self.texture_dtype = type(self.texture_array.flat[0])
        self.ndims = self.texture_array.ndim
        self.center_shift = TransformState.make_pos2d((-0.5, -0.5))
        self.shift_back = TransformState.make_pos2d((0.5, 0.5))

        #Create texture stage
        self.texture = Texture("Stimulus")
        self.texture.setup2dTexture(texture_size, texture_size,
                               Texture.T_unsigned_byte, Texture.F_luminance)
        self.texture.setWrapU(Texture.WM_clamp)
        self.texture.setWrapV(Texture.WM_clamp)
        self.texture.setRamImageAs(self.texture_array, "L")
        self.textureStage = TextureStage("Stimulus")

        #Create scenegraph
        cm = CardMaker('card1')
        cm.setFrameFullscreenQuad()
        self.card1 = self.aspect2d.attachNewNode(cm.generate())
        self.card1.setTexture(self.textureStage, self.texture)  #ts, tx

        if self.scale != 0:
            self.taskMgr.add(self.scaleTextureTask, "scaleTextureTask")

    #Scale the texture
    def scaleTextureTask(self, task):
        if task.time > 1:
            self.current_scale *= 1/self.scale
            scale_transform = TransformState.make_scale2d(self.current_scale)
            full_transform = self.shift_back.compose(scale_transform.compose(self.center_shift))
            self.card1.setTexTransform(self.textureStage, full_transform)
        if self.current_scale <= 0.15:
            print("Done upscaling")
            self.current_scale = 1
        elif self.current_scale >= 15:
            print("Done downscaling")
            self.current_scale = 1

        return Task.cont

if __name__ == '__main__':
    circle_texture = make_circle_tex()
    #Try scale < 1: expect (single) circle to shrink
    circle_scaling = TexScaler(circle_texture, scale = 0.99)
    #Try scale > 1: expect circle to dilate
    #circle_scaling = TexScaler(circle_texture, scale = 1.02)
    circle_scaling.run()
