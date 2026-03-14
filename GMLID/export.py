from pathlib import Path

from GMLID.logging import get_logger
from GMLID.physics.numerical import IRSHistogram
from GMLID.physics.system import Lens, System

logger = get_logger("export")
try:
    from astropy.io import fits

    _USE_FITS = True
except ImportError:
    logger.warning("Failed to import astropy.io.fits falling back on raw format")

    fits = None
    _USE_FITS = False
finally:
    import struct


def convert_to_fits(location: Path, name: str):
    if _USE_FITS is False:
        logger.exception("Cannot convert the raw to fits as astropy failed to import")
        return None


def _dump_histogram_fits(path: Path, histogram: IRSHistogram):
    pass


_HISTOGRAM_HEADERSIZE = struct.calcsize(">6q2d")
_LENS_SIZE = struct.calcsize(">3d")


def _dump_histogram_raw(path: Path, histogram: IRSHistogram):
    system = histogram._system
    count = len(system.lenses)

    header = b"type histogram"
    info = struct.pack(
        f">6q2d{3 * count}d",
        histogram._deflection_map._size[0],
        histogram._deflection_map._size[1],
        histogram.pixel_width,
        histogram.pixel_height,
        histogram._ray_count,
        count,
        system.lens_distance,
        system.source_distance,
        *(val for lens in system.lenses for val in lens),
    )
    data = histogram.histogram.read()

    with open(path, "wb") as fp:
        fp.write(header + info + data)


def dump_histogram(location: Path, name: str, histogram: IRSHistogram):
    if _USE_FITS:
        return _dump_histogram_fits(location / f"{name}.fits", histogram)
    return _dump_histogram_raw(location / f"{name}.histogram", histogram)


def _load_histogram_fits(path: Path) -> IRSHistogram | None: ...


def _load_histogram_raw(path: Path) -> IRSHistogram | None:
    with open(path, "rb") as fp:
        byte_data = fp.read()

    if byte_data[:14] != b"type histogram":
        logger.critical(f"{path} is not a valid histogram file")
        return None

    deflection_w, deflection_h, pixel_w, pixel_h, ray_count, count, Dl, Ds = struct.unpack(
        ">6q2d", byte_data[14 : 14 + _HISTOGRAM_HEADERSIZE]
    )
    lenses = struct.unpack(
        f">{3 * count}d",
        byte_data[14 + _HISTOGRAM_HEADERSIZE : 14 + _HISTOGRAM_HEADERSIZE + count * _LENS_SIZE],
    )
    data = byte_data[14 + _HISTOGRAM_HEADERSIZE + count * _LENS_SIZE :]

    system = System.create(
        Dl, Ds, (Lens(lenses[3 * i], lenses[3 * i + 1], lenses[3 * i + 2]) for i in range(count))
    )
    histogram = IRSHistogram(system, ray_count, (pixel_w, pixel_h), (deflection_w, deflection_h))
    histogram.histogram.write(data)
    return histogram


def load_histogram(location: Path, name: str) -> IRSHistogram | None:
    if _USE_FITS:
        return _load_histogram_fits(location / f"{name}.fits")
    return _load_histogram_raw(location / f"{name}.histogram")
