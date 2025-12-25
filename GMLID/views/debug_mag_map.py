from array import array

from arcade import View
from arcade.clock import GLOBAL_CLOCK
import arcade.gl as gl

from GMLID.system import Lens, LensSystem, LensImage
from GMLID.magnification import MagnificationMap
from GMLID.util import get_uv_byte_data, get_glsl

class DebugMagMapView(View):

    def __init__(self):
        View.__init__(self)

        self.system = LensSystem(4000, 8000)
        self.system.extend_lenses((
            Lens(0.0, 0.0, 1.0), # Sun
            Lens(0.4, 0.0, 1.66e-7), # Mercury
            Lens(0.7, 0.0, 2.45e-6), # Venus
            Lens(1.0, 0.0, 3.01e-6), # Earth,
            Lens(1.5, 0.0, 3.23e-7), # Mars
            Lens(5.2, 0.0, 9.55e-4), # Jupiter
            Lens(9.6, 0.0, 2.86e-4), # Saturn
            Lens(19.2, 0.0, 4.37e-5), # Uranus
            Lens(30.0, 0.0, 5.15e-5), # Neptune 
        ))
        print(tuple(self.system.pack_lenses()), self.system.einstein_angle)
        self.system_image = LensImage(self.system, (4000, 4000), lazy=False)


        self.mag = MagnificationMap(self.system_image, lazy=False)

        self.system_image.update()
        self.mag.generate_semi_map()
        self.mag.generate_map()

        ctx = self.window.ctx

        self._image_geometry = ctx.geometry(
            [gl.BufferDescription(ctx.buffer(data=get_uv_byte_data()), "4f", ["in_coordinate"])],
            mode=gl.TRIANGLE_STRIP
        ) 
        self._image_program = ctx.load_program(
            vertex_shader=get_glsl("unprojected_uv_vs"),
            fragment_shader=get_glsl("texture_uv_fs")
        )

    def on_draw(self):
        self.clear()
        
        # self._mag._lens_compute["px_off"] = (int(GLOBAL_CLOCK.ticks % 1024), int((GLOBAL_CLOCK.ticks//1024)%1024))
        self.mag.generate_semi_map()
        self.mag.generate_map()
        self._image_geometry.render(self._image_program)

        print(array("l", self.mag._magnication_map.read()))
