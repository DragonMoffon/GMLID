from typing import Any

from GMLID.lib.data_subject import DataSubject
from GMLID.lib.schema import DataSchema, create_schema, load_schema, dump_schema

from .system import Lens

WINDOW_TITLE = ""

class GMLIDContext(DataSubject):
    schema: DataSchema = {
        "window": { # The actual window config
            "width": ("window_width", 720),
            "height": ("window_height", 405),
            "fullscreen": ("window_fullscreen", False),
        },
        "system": { # The lenses active for GMLID
            "distance": ("lens_distance", 4000),
        },
        "source": { # Info about the source star
            "distance": ("source_distance", 8000),
        },
        "histogram": { # Control variables for the histogram
        },
        "event": { # Control variables for the lens event system
        }
    }

    def __init__(self, values: dict[str, Any] | None = None) -> None:
        DataSchema.__init__(self, values, print)

        # Window Config
        self.window_width: int
        self.window_height: int
        self.window_fullscreen: bool

        # Lens System Config
        self.lens_distance: float
        self.source_distance: float
        self.lenses: tuple[Lens, ...]

        # Histogram Config

        # Lens Event Config
