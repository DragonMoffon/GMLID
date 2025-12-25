from arcade import View
import arcade.gl as gl

from GMLID.system import Lens, LensSystem, LensImage
from GMLID.util import get_uv_byte_data, get_glsl

class DebugLensImageView(View):

    def __init__(self):
        View.__init__(self)
        
        ctx = self.window.ctx
        self._image_geometry = ctx.geometry(
            [gl.BufferDescription(ctx.buffer(data=get_uv_byte_data()), "4f", ["in_coordinate"])],
            mode=gl.TRIANGLE_STRIP
        ) 
        self._image_program = ctx.load_program(
            vertex_shader=get_glsl("unprojected_uv_vs"),
            fragment_shader=get_glsl("IRS_image_fs")
        )

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
        self.system_image = LensImage(self.system, (4000, 4000), False)

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        sx = (x / self.width - 0.5) * 4.0
        sy = (y / self.height - 0.5) * 4.0
        self._image_program["source"] = sx, sy, 10.0/1000.0, 0.0

    def on_draw(self):
        self.clear()
        self.system_image.use()
        self._image_geometry.render(self._image_program)

