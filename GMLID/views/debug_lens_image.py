from arcade import View
import arcade.gl as gl

import numpy as np
from PIL import Image

from GMLID.system import Lens, LensSystem, LensImage
from GMLID.util import get_uv_byte_data, get_glsl


class DebugLensImageView(View):
    def __init__(self):
        View.__init__(self)

        ctx = self.window.ctx
        self._image_geometry = ctx.geometry(
            [gl.BufferDescription(ctx.buffer(data=get_uv_byte_data()), "4f", ["in_coordinate"])],
            mode=gl.TRIANGLE_STRIP,
        )
        self._image_program = ctx.load_program(
            vertex_shader=get_glsl("unprojected_uv_vs"), fragment_shader=get_glsl("IRS_image_fs")
        )

        self.system = LensSystem(4000, 8000)
        self.system.extend_lenses(
            (
                Lens(0.0, 0.0, 1.0),  # Sun
                # Lens(5.2, 0.0, 1.0),  # Jupiter 9.55e-4 Solar Masses
            )
        )
        self.system_image = LensImage(self.system, (4000, 4000), False)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        data = np.frombuffer(
            self.system_image._lens_image.read(),
            dtype=np.float32,
            count=4000 * 4000 * 2,
        ).reshape((4000, 4000, 2))
        expanded = np.zeros((4000, 4000, 3), dtype=np.float32)
        expanded[::-1, :, :2] = np.clip(data * 0.5 + 0.5, 0.0, 1.0) * 255
        expanded[:, :, 2] = 255.0 / 2.0
        expanded = expanded.astype(np.uint8)
        img = Image.fromarray(expanded, "RGB")
        img.save("lens_image.png")

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        sx = (x / self.width - 0.5) * 4.0
        sy = (y / self.height - 0.5) * 4.0
        # self._image_program["source"] = sx, sy, 10.0 / 1000.0, 0.0

    def on_draw(self):
        self.clear()
        self.system_image.use()
        self._image_geometry.render(self._image_program)
