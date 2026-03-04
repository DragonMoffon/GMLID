from struct import pack
from importlib.resources import path
from pathlib import Path

from arcade import ArcadeContext
import arcade.gl as gl

import GMLID.glsl as glsl_module


def get_glsl(name: str) -> Path:
    with path(glsl_module, f"{name}.glsl") as pth:
        return pth


def get_symmetric_byte_data(width: float, height: float):
    return pack(
        "16f",
        -1.0,
        -1.0,
        -width / 2,
        -height / 2,
        -1.0,
        1.0,
        -width / 2,
        height / 2,
        1.0,
        -1.0,
        width / 2,
        -height / 2,
        1.0,
        1.0,
        width / 2,
        height / 2,
    )


def get_symmetric_geometry(ctx: ArcadeContext, width: float, height: float):
    return ctx.geometry(
        [
            gl.BufferDescription(
                ctx.buffer(data=get_symmetric_byte_data(width, height)), "4f", ["in_coordinate"]
            )
        ],
        mode=gl.TRIANGLE_STRIP,
    )


def get_uv_byte_data():
    return pack(
        "16f", -1.0, -1.0, 0.0, 0.0, -1.0, 1.0, 0.0, 1.0, 1.0, -1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0
    )


def get_fullscreen_geometry(ctx: ArcadeContext):
    return ctx.geometry(
        [gl.BufferDescription(ctx.buffer(data=get_uv_byte_data()), "4f", ["in_coordinate"])],
        mode=gl.TRIANGLE_STRIP,
    )
