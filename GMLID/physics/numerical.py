from struct import pack
from random import random

from PIL import Image
import numpy as np
from arcade import get_window, ArcadeContext
import arcade.gl as gl

from GMLID.util import get_glsl, get_symmetric_geometry

from .system import System


class IRSDeflectionMap:
    """
    The IRSDeflectionMap (Inverse Ray Shooting Deflection Map) maps positions in
    the lens plane with their corresponding location in the source plane. This
    is used by the IRSHistogram to save on calculating the ray deflection.

    getting the deflection map texture using the `deflection_map` property won't
    automatically generate it. After updating the system or other attributes you
    must explicitly call `IRSDeflectionMap.generate()`.
    """

    def __init__(self, system: System, size: tuple[int, int], lazy: bool = False) -> None:
        self._system: System = system
        self._size: tuple[int, int] = size

        self._ctx: ArcadeContext

        self._lens_block: gl.Buffer
        self._lens_image: gl.Texture2D

        self._render_geometry: gl.Geometry
        self._render_program: gl.Program
        self._render_frame: gl.Framebuffer

        self._stale: bool = False
        self._initialised: bool = False
        if not lazy:
            self.initialise()

    def initialise(self, force: bool = False):
        if self._initialised and not force:
            return

        self._ctx = ctx = get_window().ctx

        # 2 32-bit ints + 4 32-bit floats per lens
        size = 8 + len(self._system.lenses) * 16
        self._lens_block = ctx.buffer(reserve=size)
        self._stale = True

        # Only two lens components are needed, and each component in 32-bit so this
        # saves 64-bits per pixel. Even if it does add complexity to reading the texture
        self._lens_image = ctx.texture(
            self._size,
            components=2,
            dtype="f4",
            wrap_x=gl.CLAMP_TO_EDGE,
            wrap_y=gl.CLAMP_TO_EDGE,
            filter=(gl.LINEAR, gl.LINEAR),
        )

        self._render_geometry = get_symmetric_geometry(ctx, 4.0, 4.0)
        self._render_program = ctx.load_program(
            vertex_shader=get_glsl("unprojected_uv_vs"),
            fragment_shader=get_glsl("lens_centered_IRS_fs"),
        )
        self._render_frame = ctx.framebuffer(color_attachments=[self._lens_image])

        self._initialised = True

    @property
    def deflection_map(self) -> gl.Texture2D:
        self.initialise()
        return self._lens_image

    def update_system(self, system: System):
        self.initialise()
        old = self._system
        self._system = system

        if len(old.lenses) != len(system.lenses):
            # 2 32-bit ints + 4 32-bit floats per lens
            size = 8 + len(system.lenses) * 16
            self._lens_block.orphan(size)

        self._stale = True

    def update(self, force: bool = False):
        self.initialise()
        if self._stale and not force:
            return

        count = len(self._system.lenses)
        self._lens_block.write(pack(f"2i {count * 4}f", count, 0, *self._system.pack_lenses()))
        self._stale = False

    def generate(self):
        self.initialise()
        self.update()

        self._ctx.disable(gl.BLEND)
        with self._render_frame.activate() as fbo:
            fbo.clear()
            self._lens_block.bind_to_storage_buffer()
            self._render_geometry.render(self._render_program)

    def read(self) -> np.ndarray:
        data = self._lens_image.read()
        w, h = self._size
        return np.frombuffer(data, dtype=np.float32, count=w * h * 2).reshape((w, h, 2))

    def capture(
        self, distance_range: float = 2.0, clipped: bool = True, blue_value: float = 127
    ) -> Image.Image:
        # maps -distance_range/2 - distance_range/2 to 0.0 - 1.0
        data = (self.read() / distance_range + 0.5) * 255
        if clipped:
            data = np.clip(data, 0.0, 255.0)
        pixels = np.zeros((self._size[0], self._size[1], 3), dtype=np.float32)
        pixels[::-1, ::, :2] = data  # set Red and Green values
        pixels[:, :, 2] = blue_value  # set Blue values
        img = Image.fromarray(pixels.astype(np.uint8), "RGB")
        return img


class IRSHistogram:
    """
    The IRSHistogram (Inverse Ray Shooting Histogram) produces caustic maps
    for the given LensSystem. This is an iterative process where a relatively
    small (~1 million) number of rays are shot towards the source plane. For each
    location (in eistein angles) the number of rays that land is stored. when
    the texture is then copied to the CPU from the GPU the pixels are transformed
    to be as a fraction of the maximum number of rays.

    To generate the image a number of iterations can be specified, or to do the
    iteration over time a single iteration can be requested.

    When properties of the LensSystem change the histogram has to be flushed.
    This is an expensive operation so avoid doing it more than necessary.

    # TODO: add on-fly calculation mode
    There are two methods for calculating where in the source plane the image lands.
    Firstly a "deflection map" can be generated which computes the deflection at set
    angles. This is then interpolated for interim positions. The second is to compute
    the deflection for each ray directly. This is more costly, but more accurate.
    """

    def __init__(
        self,
        system: System,
        count: int,
        output_size: tuple[int, int],
        lens_size: tuple[int, int] | None = None,
        lazy: bool = False,
    ) -> None:
        self._system: System = system
        self._output_size: tuple[int, int] = output_size
        self._lens_size: tuple[int, int] = lens_size if lens_size is not None else output_size
        self._ray_count: int = count

        self._ctx: ArcadeContext

        # TODO: add on-fly calculation mode
        self._deflection_map: IRSDeflectionMap
        self._histogram: gl.Texture2D

        self._ray_geometry: gl.Geometry
        self._ray_program: gl.Program
        self._ray_frame: gl.Framebuffer

        self._initialised: bool = False
        self._stale: bool = False
        if not lazy:
            self.initialise()

    def initialise(self, force: bool = True):
        if self._initialised and not force:
            return

        self._ctx = ctx = get_window().ctx

        self._deflection_map = IRSDeflectionMap(self._system, self._lens_size)
        self._deflection_map.generate()
        self._histogram = ctx.texture(self._output_size, components=1, dtype="f4")

        # Evenly space x rays between 0.0 and 1.0 (inclusive)/
        # On th GPU these are used to find the deflection and final location
        # in the output histogram.
        x = np.linspace(0.0, 1.0, self._ray_count)
        xy, yx = np.meshgrid(x, x)
        rays = np.asarray((xy, yx)).transpose((1, 2, 0))  # create 2d array of x,y positions
        self._ray_geometry = ctx.geometry(
            [gl.BufferDescription(ctx.buffer(data=rays.tobytes()), "2f", ["origin"])],
            mode=gl.POINTS,
        )

        self._ray_program = ctx.load_program(
            vertex_shader=get_glsl("IRS_histogram_vs"), fragment_shader=get_glsl("IRS_histogram_fs")
        )
        self._ray_frame = ctx.framebuffer(color_attachments=(self._histogram))

    @property
    def histogram(self):
        return self._histogram

    def update_system(self, system: System):
        self.initialise()
        self._system = system
        self._deflection_map.update_system(system)
        self._deflection_map.generate()

        self._ray_frame.clear()

    def step(self):
        self._ctx.blend_func = gl.BLEND_ADDITIVE
        self._ctx.enable(gl.BLEND)
        self._ctx.point_size = 3

        with self._ray_frame.activate():
            self._deflection_map.deflection_map.use()
            self._ray_program["seed"] = random()
            self._ray_geometry.render(self._ray_program)

        self._ctx.disable(gl.BLEND)

    def generate(self, iterations: int = 1000, flush: bool = False):
        self.initialise()
        if flush:
            self._ray_frame.clear()

        self._ctx.blend_func = gl.BLEND_ADDITIVE
        self._ctx.enable(gl.BLEND)
        self._ctx.point_size = 1

        with self._ray_frame.activate():
            self._deflection_map.deflection_map.use()
            for _ in range(iterations):
                self._ray_program["seed"] = random()
                self._ray_geometry.render(self._ray_program)
                self._ctx.finish()  # TODO: test if this is necessary

        self._ctx.disable(gl.BLEND)

    def flush(self):
        self._ray_frame.clear()

    def read(self) -> np.ndarray:
        data = self._histogram.read()
        w, h = self._output_size
        array = np.frombuffer(data, dtype=np.float32, count=w * h).reshape((w, h))
        cap = np.max(array)
        return array / cap

    def capture(self) -> Image.Image:
        return Image.fromarray((self.read() * 255.0).astype(np.uint8), "L").convert("RGB")
