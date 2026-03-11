from pathlib import Path

from GMLID.logging import get_logger
from GMLID.physics.numerical import IRSHistogram

logger = get_logger("export")
try:
    from astropy.io import fits

    _USE_FITS = True
except ImportError:
    logger.warning("Failed to import astropy.io.fits falling back on json format")
    fits = None
    _USE_FITS = False


def convert_to_fits():
    if _USE_FITS is False:
        logger.exception("Cannot convert the json to fits as astropy failed to import")
        return None


def _dump_histogram_fits(path: Path, histogram: IRSHistogram):
    pass


def _dump_histogram_json(path: Path, histogram: IRSHistogram):
    pass


def dump_histogram(path: Path, histogram: IRSHistogram):
    if _USE_FITS:
        return _dump_histogram_fits(path, histogram)
    return _dump_histogram_json(path, histogram)


def _load_histogram_fits(path: Path) -> IRSHistogram: ...


def _load_histogram_json(path: Path) -> IRSHistogram: ...


def load_histogram(path: Path) -> IRSHistogram:
    if _USE_FITS:
        return _load_histogram_fits(path)
    return _load_histogram_json(path)
