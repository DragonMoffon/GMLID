"""
The lens system that causes the light to bend.

By convention the lens masses are stored such that the mass sum is equal to 1.
Additionally in the use cases GMLID was built for, most of the mass is found in the
primary star so the mass is approximately one, and so is the einstein radius.
"""

from typing import Generator, Iterable, NamedTuple, Self
from math import tan

from GMLID.util import calculate_einstein_angle, pc_to_au


class Lens(NamedTuple):
    m: float  # In Solar Masses (M*)
    x: float  # In Astronomical Units (Au)
    y: float  # In Astronomical Units (Au)


class System(NamedTuple):
    # Input Values
    lens_distance: float  # In parsecs (pc)
    source_distance: float  # In parsces (pc)
    lenses: tuple[Lens, ...]

    # Mass
    mass: float  # In solar masses (M*)
    com_x: float  # In Astronomical units (Au)
    com_y: float  # In Astronomical units (Au)

    # Radii
    einstein_angle: float  # In radians (rad)
    lens_radius: float  # In Astronomical units (Au)
    source_radius: float  # In Astronomical units (Au)

    @classmethod
    def create(
        cls,
        lens_distance: float,
        source_distance: float,
        lenses: Iterable[Lens],
        use_max_mass: bool = True,
    ) -> Self:
        """
        Create a lens system, and precalculate values required in calculations.
        """
        if source_distance <= lens_distance:
            raise ValueError(
                "The distance to the source must be strictly greater than the distance to the lens"
            )
        lenses = tuple(lenses)
        if len(lenses) == 0:
            return cls(lens_distance, source_distance, (), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        # Collect the total mass and center of mass
        mass = com_x = com_y = 0.0
        for lens in lenses:
            mass += lens.m
            com_x += lens.x * lens.m
            com_y += lens.y * lens.m
        if mass <= 0.0:
            raise ValueError(
                f"total system mass ({mass}) is invalid. Ensure all lenses have mass, and none are negative."
            )

        com_x /= mass
        com_y /= mass

        # * The Einstein mass can either be the systems total mass or the max mass
        # * generally the max mass is ~100% of the system in which case the difference is negligible
        einstein_mass = max(lens.m for lens in lenses) if use_max_mass else mass

        # * Calculation of the Einstein angle is differed to GMLID.util as it optimises
        # * for floating point imprecision.
        einstein_angle = calculate_einstein_angle(einstein_mass, lens_distance, source_distance)
        lens_radius = pc_to_au * (lens_distance * tan(einstein_angle))
        source_radius = pc_to_au * (source_distance * tan(einstein_angle))

        return cls(
            lens_distance,
            source_distance,
            lenses,
            mass,
            com_x,
            com_y,
            einstein_angle,
            lens_radius,
            source_radius,
        )

    def pack_lenses(self, use_com: bool = True) -> Generator[float, None, None]:
        # ! This assume the first lens is the largest.
        # It does not actually impact the maths as this is just a translation,
        # but it may look wrong if it isn't true. Especially as the system's
        # Einstein Radius is based on the greatest mass.
        c_x = self.com_x if use_com else self.lenses[0].x
        c_y = self.com_y if use_com else self.lenses[0].y

        Dl = self.lens_distance
        Ds = self.source_distance

        Ae = self.einstein_angle

        Rl = self.lens_radius

        for lens in self.lenses:
            yield lens.m
            # * The einstein radius is squared on the CPU as it saves of cycles on the
            # * GPU. This also uses the small angle approximation.
            yield (calculate_einstein_angle(lens.m, Dl, Ds) / Ae) ** 2.0
            yield (lens.x - c_x) / Rl
            yield (lens.y - c_y) / Rl
