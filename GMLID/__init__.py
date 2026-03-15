from GMLID.logging import setup_logging, get_logger
from GMLID.setup import setup_GMLID

import GMLID.physics as physics
from GMLID.physics.system import System, Lens
from GMLID.physics.analytical import (
    get_amplification_at_position,
    get_critical_curves,
    apply_lens_equation,
)
from GMLID.physics.numerical import IRSDeflectionMap, IRSHistogram

__all__ = (
    "setup_logging",
    "get_logger",
    "setup_GMLID",
    "physics",
    "System",
    "Lens",
    "get_amplification_at_position",
    "get_critical_curves",
    "apply_lens_equation",
    "IRSDeflectionMap",
    "IRSHistogram",
)
