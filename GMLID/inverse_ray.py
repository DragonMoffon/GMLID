from struct import pack

from arcade import View
import arcade.gl as gl

from GMLID.loading import get_glsl

def get_geometry_byte_data(width: float, height: float):
    return pack(
        '12f',
        -1.0,
        -1.0,
        -width/2,
        -height/2,
        -1.0,
        3.0,
        -width/2,
        1.5*height,
        3.0,
        -1.0,
        1.5*width,
        -height/2
    )

class LensMass:
    
    def __init__(self, x: float, y: float, m: float):
        self.x = x
        self.y = y
        self.m = m 

    @property
    def position(self) -> tuple[float, float]:
        return (self.x, self.y)

    @position.setter
    def position(self, pos: tuple[float, float]):
        self.x, self.y = pos

    @property
    def packed(self) -> tuple[float, float, float, float]:
        return self.m, 0.0, self.x, self.y

class InverseRayImageView(View):
    def __init__(self):
        super().__init__()

        self.lenses: list[LensMass] = [LensMass(0.0, 0.0, 1.0), LensMass(50.0, 50.0, 2.0)]
        self.lenses_stale: bool = False

        self._program: gl.Program
        self._geometry: gl.Geometry
        self._lens_buffer: gl.Buffer
        self._source_image: gl.Texture2D

        self._initialised: bool = False

    def init_deffered(self):
        if self._initialised:
            return
        ctx = self.window.ctx

        self._program = ctx.load_program(
            vertex_shader=get_glsl("unprojected_uv_vs"),
            fragment_shader=get_glsl("lens_fs"),
        )
        self._program['plane'] = 10000.0, 10000.0, 20000.0, 0.0

        self._geometry = ctx.geometry(
            [
                gl.BufferDescription(
                    ctx.buffer(
                        data=get_geometry_byte_data(2000.0, 2000.0)
                    ),
                    "4f",
                    ["in_coordinate"],
                )
            ],
            mode=ctx.TRIANGLES,
        )

        self._lens_buffer = ctx.buffer(reserve=8+16*len(self.lenses))
        self.update_lens_buffer()

        self._source_image = ctx.load_texture(
            "GMLID/MonoCircleSource.png",
            wrap_x=gl.CLAMP_TO_EDGE,
            wrap_y=gl.CLAMP_TO_EDGE,
        )
        self._initialised = True

    def update_lens_buffer(self):
        byte_data = pack(f'2i{4*len(self.lenses)}f', len(self.lenses), 0, *sum((lens.packed for lens in self.lenses), start=()))
        self._lens_buffer.write(byte_data)
        self.lenses_stale = False

    def on_mouse_motion(self, x, y, dx, dy):
        xp = (x / self.width - 0.5) * 2000.0
        yp = (y / self.height - 0.5) * 2000.0
        self.lenses[0].position = xp, yp
        self.lenses_stale = True

    def on_draw(self):
        if not self._initialised:
            self.init_deffered()
        if self.lenses_stale:
            self.update_lens_buffer()
        self.clear()
        self._source_image.use()
        self._lens_buffer.bind_to_storage_buffer()
        self._geometry.render(self._program)


