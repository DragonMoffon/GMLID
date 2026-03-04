"""
The physics sub-module contains all of the actual maths and physics used by GMLID.

The objects and methods in the module generate the Lens Events, Histograms, etc.
"""

from .util import (
    LIGHT_SPEED_m,
    LIGHT_SPEED_km,
    LIGHT_SPEED_au,
    LIGHT_SPEED_pc,
    pc_to_au,
    au_to_pc,
    au_to_m,
    m_to_au,
    pc_to_m,
    GRAVITATIONAL_CONSTANT,
    SOLAR_MASS,
    EINSTEIN_FACTOR,
    calculate_einstein_angle,
)
from .system import Lens, System
from .analytical import (
    get_amplification_at_position,
    one_lens_amplificiation,
    two_lens_amplification,
    get_critical_curves,
    one_lens_critical_curves,
    two_lens_critical_curves,
    apply_lens_equation,
)
from .numerical import IRSDeflectionMap, IRSHistogram, IRSCriticalMap

__all__ = (
    "LIGHT_SPEED_m",
    "LIGHT_SPEED_km",
    "LIGHT_SPEED_au",
    "LIGHT_SPEED_pc",
    "pc_to_au",
    "au_to_pc",
    "au_to_m",
    "m_to_au",
    "pc_to_m",
    "GRAVITATIONAL_CONSTANT",
    "SOLAR_MASS",
    "EINSTEIN_FACTOR",
    "calculate_einstein_angle",
    "Lens",
    "System",
    "get_amplification_at_position",
    "one_lens_amplificiation",
    "two_lens_amplification",
    "get_critical_curves",
    "one_lens_critical_curves",
    "two_lens_critical_curves",
    "apply_lens_equation",
    "IRSDeflectionMap",
    "IRSHistogram",
    "IRSCriticalMap",
)
