from enum import Enum
from GMLID.application import Window

class LaunchOptions(Enum):
    debug_lens_image = 0
    debug_histogram = 1
    IRS = 2
    debug_mag_map = 3
    debug_section = 4

def launch(view: LaunchOptions):
    match view:
        case LaunchOptions.debug_lens_image:
            from GMLID.views.debug_lens_image import DebugLensImageView as shown_view
        case LaunchOptions.debug_histogram:
            from GMLID.views.debug_histogram import DebugHistogramView as shown_view
        case LaunchOptions.IRS:
            from GMLID.views.inverse_ray import InverseRayImageView as shown_view
        case LaunchOptions.debug_mag_map:
            from GMLID.views.debug_mag_map import DebugMagMapView as shown_view
        case LaunchOptions.debug_section:
            from GMLID.views.debug_section import DebugSectionView as shown_view
        case _:
            raise ValueError(f"no known view: {view}")
    
    win = Window()
    win.run(shown_view())
 
