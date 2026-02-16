from typing import Any

from GMLID.lib.data_subject import DataSubject
from GMLID.lib.schema import DataSchema, create_schema, load_schema, dump_schema

from .system import Lens

WINDOW_TITLE = ""


class GMLIDContext(DataSubject):
    schema: DataSchema = {
        "window": {  # The actual window config
            "width": ("window_width", 720),
            "height": ("window_height", 405),
            "fullscreen": ("window_fullscreen", False),
        },
        "system": {  # The lenses active for GMLID
            "lens_distance": ("lens_distance", 4000),
            "source_distance": ("source_dstance", 8000),
            "image_size": ("lens_image_size", (4000, 4000)),
        },
        "histogram": {  # Control variables for the histogram
            "ray_count": ("histogram_ray_count", 10000),
            "image_size": ("histogram_image_size", (2048, 2048)),
        },
        "event": {  # Control variables for the lens event system
        },
    }

    def __init__(self, values: dict[str, Any] | None = None) -> None:
        DataSubject.__init__(self, values, print)

        # Window Config
        self.window_width: int
        self.window_height: int
        self.window_fullscreen: bool

        # Lens System Config
        self.lens_distance: float
        self.source_distance: float
        self.lens_image_size: tuple[int, int]
        self.lenses: tuple[Lens, ...]

        # Histogram Config
        self.histogram_ray_count: int
        self.histogram_image_size: tuple[int, int]

        # Lens Event Config

    def pre_process(self):
        pass

    def post_process(self):
        pass
