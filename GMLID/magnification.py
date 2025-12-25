"""
To compute the magnification map requires two steps.

First over 1024 work groups sized 1024x1024x64 capture every pixel of every lens event.
each worker only computes a 4x4 area of pixels with 64 workers per source position that covers
32x32 area of lens texture. Then 32x32 worker groups are dispatched so the whole lens image gets sampled.

In the second step the sub images are unified into one image. This required 8x8x1024 samples by each worker
which might be too many.
"""

from arcade import get_window, ArcadeContext
import arcade.gl as gl

from .util import get_glsl
from .system import LensImage

class MagnificationMap:

    def __init__(self, lens: LensImage, lazy: bool = True):
        self.ctx: ArcadeContext
        
        self._lens: LensImage = lens

        self._lens_compute: gl.ComputeShader
        self._lens_collect: gl.ComputeShader
        self._lens_output_array: gl.TextureArray

        self._magnification_map: gl.Texture2D
        
        self._initialised: bool = False
        if not lazy:
            self.initialise()

    def initialise(self):
        if self._initialised:
            return
        
        self._lens.initialise()

        self.ctx = ctx = get_window().ctx

        self._lens_compute = ctx.load_compute_shader(get_glsl("mag_map_calculation_cs"))
        self._lens_collect = ctx.load_compute_shader(get_glsl("mag_map_collection_cs"))

        self._lens_output_array = ctx.texture_array((1, 1, 1024), components=1, dtype="i4")
        self._magnication_map = ctx.texture((1, 1), components=1, dtype="i4")

        self._initialised = True

    def generate_semi_map(self):
        self._lens.use(0)
        self._lens_output_array.use(1)
        self._lens_compute.run(1, 1, 1024)

    def generate_map(self):
        self._magnication_map.use(0)
        self._lens_output_array.use(1)
        self._lens_collect.run(1, 1)



