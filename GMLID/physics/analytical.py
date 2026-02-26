"""
The Amplification of a lens system in analytical for one and two lens systems.
Generically the amplification is equal to `1/|Det(J)|`. That is the amplification
is inversely proportional to the determinant of the jacobian of the lens mapping.
"""

import numpy as np

from .system import System


def get_amplification_at_position(system: System, location: tuple[float, float]) -> float:
    """
    Get the analytical amplification at a location for a one or two lens system.

    Args:
        system: The lens system which holds the data used to calculate the amplification
        location: The sampled location in Angular Einstein Radii
    """
    count = len(system.lenses)
    if count == 1:
        return one_lens_amplificiation(system, location)
    elif count == 2:
        return two_lens_amplification(system, location)
    raise ValueError(
        f"No analytical solution for a {count} lens system. Use GMLID.physics.numerical instead"
    )


def one_lens_amplificiation(system: System, location: tuple[float, float]) -> float:
    if len(system.lenses) != 1:
        raise ValueError("This amplification solution only works for one lens")

    # Given there is only one lens, we can assume it will be centered at (0, 0)
    separation = (location[0] ** 2.0 + location[1] ** 2.0) ** 0.5

    if separation == 0.0:
        # python does not handle division by zero
        return float("inf")

    # The impact parameter (mu)
    # classically the deflection is divided by the Einstein angle,
    # however the location angle is already scaled by the Einstein angle so it can
    # be skipped.
    mu = separation - system.einstein_angle**2 / separation

    return (mu**2 + 2) / (mu * (mu**2 + 4) ** 0.5)


def two_lens_amplification(system: System, location: tuple[float, float]) -> float:
    if len(system.lenses) != 2:
        raise ValueError("This amplification solution only works for two lenses")

    return 0.0


def get_critical_curves(system: System, count: int) -> tuple[tuple[float, float], ...]:
    """
    get count samples of the analytical critical curves for a one or two lens system.
    """
    count = len(system.lenses)
    if count == 1:
        return one_lens_critical_curves(system, count)
    elif count == 2:
        return two_lens_critical_curves(system, count)
    raise ValueError(
        f"No analytical solution for a {count} lens system. Use GMLID.physics.numerical instead"
    )


def one_lens_critical_curves(system: System, count: int) -> tuple[tuple[float, float], ...]:
    angles = np.linspace(0.0, 2.0 * np.pi, count, endpoint=False)
    radius = system.einstein_angle

    return tuple((radius * np.cos(angle), radius * np.sin(angle)) for angle in angles)


def two_lens_critical_curves(system: System, count: int) -> tuple[tuple[float, float], ...]:
    if len(system.lenses) != 1:
        raise ValueError("This amplification solution only works for one lens")

    return ()


def apply_lens_equation(system: System, locations: tuple[float, float]) -> tuple[float, float]:
    if len(system.lenses) != 2:
        raise ValueError("This amplification solution only works for two lenses")

    return ()
