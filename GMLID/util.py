from struct import pack
from importlib.resources import path
from pathlib import Path

import GMLID.glsl as glsl_module

def get_glsl(name: str) -> Path:
    with path(glsl_module, f"{name}.glsl") as pth:
        return pth

def get_symmetric_byte_data(width: float, height: float):
    return pack(
        '16f',
        -1.0, -1.0, -width/2, -height/2,
        -1.0, 1.0, -width/2, height/2,
        1.0, -1.0, width/2, -height/2,
        1.0, 1.0, width/2, height/2,
    )

def get_uv_byte_data():
    return pack(
        '16f',
        -1.0, -1.0, 0.0, 0.0,
        -1.0, 1.0, 0.0, 1.0,
        1.0, -1.0, 1.0, 0.0,
        1.0, 1.0, 1.0, 1.0
    )

LIGHT_SPEED_m = 299_792_458
LIGHT_SPEED_km = 299_792.458
LIGHT_SPEED_au = 0.0020039888041
LIGHT_SPEED_pc = 9.71561e-9

pc_to_au = 206264.80624538
au_to_pc = 1.0 / pc_to_au
au_to_m = 1.496e+11
m_to_au = 1 / au_to_m
pc_to_m = 3.08567758128e16

GRAVITATIONAL_CONSTANT = 6.6743e-11
SOLAR_MASS = 1.988475e30
# EINSTEIN_FACTOR = (4 * GRAVITATIONAL_CONSTANT / LIGHT_SPEED_m**2) * (SOLAR_MASS / pc_to_m) # collect constant terms of einstein radius equation
# EINSTEIN_FACTOR = 5906.69361643 # Precalculated to try avoid precision issues as much as possible (in Solar Masses / m)
EINSTEIN_FACTOR = 1.9142290343 * 10**(-13) # Precalculated to try avoid precision issues as much as possible. (in Solar Masses / pc)

def calculate_einstein_angle(mass: float, lens: float, source: float) -> float:
    if lens <= 0 or source <= lens:
        raise ValueError("lens or source plane distance is invalid and the einstein angle cannot be calculted")
    return (EINSTEIN_FACTOR * mass * (source - lens) / (source * lens))**0.5



