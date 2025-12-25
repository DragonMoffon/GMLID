"""
The LensSystem object holds all of the info for a lensing event.
This is on the microscale with distances in parsecs and masses in suns.

Each Lens stores itself relative to the center of the solar system it comes from.
The LensSystem then transforms it to be in Einstein radii before packing them into
a buffer to send to the GPU. 

By relying on the small angle approximation and Einstein radius it is possible
to simplify the equation for the deflection to be Er^2 / sep. where Er is the 
Einstein radius for the specific lens, and sep is the angluar seperation between
the lens and the ray.
"""
from typing import Sequence, Generator
from math import tan
from struct import pack
from dataclasses import dataclass

from arcade import get_window, ArcadeContext
import arcade.gl as gl

from .util import get_glsl, get_symmetric_byte_data, calculate_einstein_angle, pc_to_au

@dataclass
class Lens:
    x: float # Position in AU, relative to Primary Body
    y: float # Position in AU, relative to Primary Body
    m: float # Mass in Solar Masses

    @property
    def position(self) -> tuple[float, float]:
        return (self.x, self.y)

    @position.setter
    def position(self, value: tuple[float, float]):
        self.x, self.y = value

class LensSystem:
    
    def __init__(self, lens_distance: float, source_distance: float):
        self._lenses: list[Lens] = []
        self._lens_mass: float = 0.0 # In Solar Masses
        self._lens_com: tuple[float, float] = (0.0, 0.0) # In AU

        self._einstein_angle: float = 0.0 # In radians
        self._lens_radius: float = 0.0 # In AU
        self._source_radius: float = 0.0 # In AU

        self._lens_distance: float = lens_distance # In parsecs
        self._source_distance: float = source_distance # In parsecs

        self.recalculate_com()
        self.recalculate_einstein_radius()

    @property
    def lenses(self) -> list[Lens]:
        return self._lenses

    def add_lens(self, lens: Lens) -> None:
        self._lenses.append(lens)
        self.recalculate_com()
        self.recalculate_einstein_radius()

    def extend_lenses(self, lenses: Sequence[Lens]) -> None:
        self._lenses.extend(lenses)
        self.recalculate_com()
        self.recalculate_einstein_radius()

    def remove_lens(self, lens: Lens) -> None:
        self._lenses.remove(lens)
        self.recalculate_com()
        self.recalculate_einstein_radius()

    @property
    def lens_mass(self) -> float:
        return self._lens_mass

    @property
    def lens_com(self) -> tuple[float, float]:
        return self._lens_com

    @property
    def lens_distance(self) -> float:
        return self._lens_distance

    @lens_distance.setter
    def lens_distance(self, distance: float) -> None:
        if distance == self._lens_distance:
            return
        self._lens_distance = distance
        self.recalculate_einstein_radius()

    @property
    def source_distance(self) -> float:
        return self._source_distance

    @source_distance.setter
    def source_distance(self, distance: float) -> None:
        if distance == self._source_distance:
            return
        self._source_distance = distance
        self.recalculate_einstein_radius()

    @property
    def plane_seperation(self) -> float:
        return self._source_distance - self._lens_distance

    @property
    def einstein_angle(self) -> float:
        return self._einstein_angle

    @property
    def lens_radius(self) -> float:
        return self._lens_radius

    @property
    def source_radius(self) -> float:
        return self._source_radius

    def recalculate_com(self):
        x_sum = 0.0
        y_sum = 0.0
        mass_sum = 0.0
        for lens in self.lenses:
            x_sum += lens.m * lens.x
            y_sum += lens.m * lens.y
            mass_sum += lens.m
        if mass_sum == 0.0:
            self._lens_mass = 0.0
            self._lens_com = (0.0, 0.0)
            return
        self._lens_mass = mass_sum
        self._lens_com = x_sum / mass_sum, y_sum / mass_sum

    def recalculate_einstein_radius(self):
        self._einstein_angle = calculate_einstein_angle(self._lens_mass, self._lens_distance, self._source_distance) 
        self._lens_radius = pc_to_au * (self._lens_distance * tan(self._einstein_angle))
        self._source_radius = pc_to_au * (self._source_distance * tan(self._einstein_angle))
        print(self.lens_radius, self._source_radius)

    def pack_lenses(self) -> Generator[float, None, None]:
        cx, cy = self.lens_com
        e = self._einstein_angle
        # Uses small angle approximation to avoid arctan with very large values
        for lens in self._lenses:
            yield lens.m
            yield (calculate_einstein_angle(lens.m, self._lens_distance, self.source_distance)/e)**2
            yield (lens.x - cx) / self.lens_radius
            yield (lens.y - cy) / self.lens_radius

class LensImage:

    def __init__(self, system: LensSystem, size: tuple[int, int], lazy: bool = True):
        self._system: LensSystem = system
        self._size: tuple[int, int] = size

        self._ctx: ArcadeContext

        self._lens_block: gl.Buffer
        self._lens_image: gl.Texture2D

        self._render_geometry: gl.Geometry
        self._render_program: gl.Program
        self._render_frame: gl.Framebuffer

        self._stale: bool = True
        self._initialised: bool = False
        if not lazy:
            self.initialise()
    
    def initialise(self):
        if self._initialised:
            return
        
        self._ctx = ctx = get_window().ctx
        
        size = 8 + len(self._system.lenses) * 16 # 2 32-bit ints + 4 32-bit floats per lens
        self._lens_block = ctx.buffer(reserve=size)
        # Only two components are needed, and since we are doing 32 bit floats this halves the size of the image from 128 bits to 64 bits per pixel
        self._lens_image = ctx.texture(self._size, components=2, dtype="f4", wrap_x=gl.CLAMP_TO_EDGE, wrap_y=gl.CLAMP_TO_EDGE, filter=(gl.LINEAR, gl.LINEAR))

        self._render_geometry = ctx.geometry([gl.BufferDescription(ctx.buffer(data=get_symmetric_byte_data(4.0, 4.0)), "4f", ["in_coordinate"])], mode=gl.TRIANGLE_STRIP)
        self._render_program = ctx.load_program(
            vertex_shader=get_glsl("unprojected_uv_vs"),
            fragment_shader=get_glsl("lens_centered_IRS_fs")
        )
        self._render_frame = ctx.framebuffer(color_attachments=[self._lens_image])

        self._initialised = True

    def update(self):
        if not self._stale:
            return
        
        count = len(self._system.lenses)
        if self._lens_block.size != (8 + count * 16):
            self._lens_block.orphan(8 + count * 16)
        self._lens_block.write(pack(f"2i {len(self._system.lenses)*4}f", count, 0, *self._system.pack_lenses()))

        with self._render_frame.activate() as fbo:
            fbo.clear()
            self._lens_block.bind_to_storage_buffer()
            self._render_geometry.render(self._render_program)

        self._stale = False

    def use(self, idx: int = 0):
        self.initialise()
        self.update()
        self._lens_image.use(idx)
