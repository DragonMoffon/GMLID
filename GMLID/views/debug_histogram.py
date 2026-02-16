from PIL import Image

from arcade import View, draw_text
import arcade.gl as gl
import numpy as np

from GMLID.system import Lens, LensSystem, LensImage
from GMLID.util import get_uv_byte_data, get_glsl


def lens_spread(w, h):
    for x in range(int(0.0 * w), int(1.0 * w)):
        for y in range(int(0.0 * h), int(1.0 * h)):
            yield x / w
            yield y / w


class DebugHistogramView(View):
    def __init__(self):
        View.__init__(self)

        x = np.linspace(0.0, 1.0, 1000, dtype=np.float32)
        xy, yx = np.meshgrid(x, x)
        j = np.asarray((xy, yx)).transpose((1, 2, 0))

        ctx = self.window.ctx
        self._image_geometry = ctx.geometry(
            [gl.BufferDescription(ctx.buffer(data=get_uv_byte_data()), "4f", ["in_coordinate"])],
            mode=gl.TRIANGLE_STRIP,
        )
        self._image_program = ctx.load_program(
            vertex_shader=get_glsl("unprojected_uv_vs"),
            fragment_shader=get_glsl("IRS_histogram_texture_fs"),
        )

        self.histogram = ctx.texture((2048, 2048), components=1, dtype="f4")
        self.histogram_target = ctx.framebuffer(color_attachments=[self.histogram])

        self.histogram_geometry = ctx.geometry(
            [gl.BufferDescription(ctx.buffer(data=j.tobytes()), "2f", ["origin"])], mode=gl.POINTS
        )
        self.histogram_program = ctx.load_program(
            vertex_shader=get_glsl("IRS_histogram_vs"), fragment_shader=get_glsl("IRS_histogram_fs")
        )

        self.system = LensSystem(4000, 8000)
        self.system.extend_lenses(
            (
                Lens(0.0, 0.0, 1.0),  # Sun
                # Lens(5.2, 0.0, 0.1),  # Test Mass
                # Lens(0.4, 0.0, 1.66e-7),  # Mercury
                # Lens(0.7, 0.0, 2.45e-6),  # Venus
                # Lens(1.0, 0.0, 3.01e-6),  # Earth,
                # Lens(1.5, 0.0, 3.23e-7),  # Mars
                Lens(5.2, 0.0, 9.55e-4),  # Jupiter
                # Lens(9.6, 0.0, 2.86e-4),  # Saturn
                # Lens(19.2, 0.0, 4.37e-5),  # Uranus
                # Lens(30.0, 0.0, 5.15e-5),  # Neptune
            )
        )
        print(tuple(self.system.pack_lenses()), self.system.einstein_angle)
        self.system_image = LensImage(self.system, (10000, 10000), False)
        self.ray_count = 1.0

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        data = np.frombuffer(self.histogram.read(), np.float32).reshape((2048, 2048))
        m = np.max(data)
        data = ((data / m) * 255).astype(np.uint8)
        im = Image.fromarray(data, mode="L")
        im.save("test.png")

    def on_mouse_drag(
        self, x: int, y: int, dx: int, dy: int, _buttons: int, _modifiers: int
    ) -> bool | None:
        return
        nx = (x * (4.0 / self.width) - 2.0) * self.system.lens_radius
        ny = (y * (4.0 / self.height) - 2.0) * self.system.lens_radius
        dist = float("inf")
        target = None
        for lens in self.system.lenses:
            sep = (lens.x - nx) ** 2 + (lens.y - ny) ** 2
            if sep < dist:
                dist = sep
                target = lens
        if target is None:
            return
        target.position = (nx, ny)
        self.system.recalculate_com()
        self.system.recalculate_einstein_radius()
        self.system_image._stale = True

    def on_draw(self):
        print(1.0 / self.window.delta_time)
        ctx = self.window.ctx
        with self.histogram_target.activate() as fbo:
            # fbo.clear()
            ctx.blend_func = gl.BLEND_ADDITIVE
            ctx.enable(gl.BLEND)
            ctx.point_size = 1
            self.system_image.use()
            self.histogram_program["seed"] = self.window.time
            self.histogram_geometry.render(self.histogram_program)
            # print(np.frombuffer(self.histogram.read(), np.float32))

        # self.clear()
        ctx.disable(gl.BLEND)
        self.histogram.use()
        self.system_image.use(1)
        self.ray_count += 1
        self._image_program["ray_count"] = self.ray_count
        self._image_geometry.render(self._image_program)

        draw_text(f"{self.system.lens_radius}", self.center_x, 200)
