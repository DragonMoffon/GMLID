from arcade import Window as ArcadeWindow

from ctypes import pointer, c_long
from pyglet import gl as pygl


class Window(ArcadeWindow):
    def __init__(self):
        ArcadeWindow.__init__(self, 1024, 1024, "Gravitational Micro-Lensing Interactive Demo")

        local_size = (c_long(), c_long(), c_long())
        pygl.glGetIntegeri_v(pygl.GL_MAX_COMPUTE_WORK_GROUP_SIZE, 0, pointer(local_size[0]))
        pygl.glGetIntegeri_v(pygl.GL_MAX_COMPUTE_WORK_GROUP_SIZE, 1, pointer(local_size[1]))
        pygl.glGetIntegeri_v(pygl.GL_MAX_COMPUTE_WORK_GROUP_SIZE, 2, pointer(local_size[2]))
        local_max = c_long()
        pygl.glGetIntegerv(pygl.GL_MAX_COMPUTE_WORK_GROUP_INVOCATIONS, pointer(local_max))

        local_count = (c_long(), c_long(), c_long())
        pygl.glGetIntegeri_v(pygl.GL_MAX_COMPUTE_WORK_GROUP_COUNT, 0, pointer(local_count[0]))
        pygl.glGetIntegeri_v(pygl.GL_MAX_COMPUTE_WORK_GROUP_COUNT, 1, pointer(local_count[1]))
        pygl.glGetIntegeri_v(pygl.GL_MAX_COMPUTE_WORK_GROUP_COUNT, 2, pointer(local_count[2]))

        texture_size = c_long()
        pygl.glGetIntegerv(pygl.GL_MAX_TEXTURE_SIZE, pointer(texture_size))

        texture_depth = c_long()
        pygl.glGetIntegerv(pygl.GL_MAX_ARRAY_TEXTURE_LAYERS, pointer(texture_depth))

        print(
            f"compute local maximum: {local_max}\n"
            f"compute local shape: {local_size}\n"
            f"compute local count: {local_count}\n"
            f"texture size: {texture_size}, depth: {texture_depth}"
        )
