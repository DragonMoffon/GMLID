from math import tan
from dataclasses import dataclass

LIGHT_SPEED_m = 299_792_458
LIGHT_SPEED_km = 299_792.458
LIGHT_SPEED_au = 0.0020039888041
LIGHT_SPEED_pc = 9.71561e-9

au_to_pc = 206264.80624538
pc_to_au = 1.0 / au_to_pc
au_to_m = 1.496e+11
pc_to_m = 3.08567758128e16
m_to_au = 1 / au_to_m

GRAVITATIONAL_CONSTANT = 6.6743e-11
SOLAR_MASS = 1.988475e30
EINSTEIN_FACTOR = (4 * GRAVITATIONAL_CONSTANT / LIGHT_SPEED_m**2) * (SOLAR_MASS / pc_to_m) # collect constant terms of einstein radius equation

@dataclass
class Lens:
    x: float # Position in AU, relative to Primary Body
    y: float # Position in AU, relative to Primary Body
    m: float # Mass in Solar Masses

    @property
    def position(self) -> tuple[float, float]:
        return (self.x, self.y)

    @position.setter
    def position(self, value: tuple[float, float]):
        self.x, self.y = value

class LensSystem:
    
    def __init__(self):
        self.lenses: list[Lens] = []
        self.lens_mass: float = 0.0 # In Solar Masses
        self.lens_com: tuple[float, float] = (0.0, 0.0) # In AU

        self.einstein_radius: float = 0.0 # In radians
        self.lens_radius: float = 0.0 # In AU
        self.source_radius: float = 0.0 # In AU

        self.lens_distance: float = 0.0 # In parsecs
        self.source_distance: float = 0.0 # In parsecs

        self.source_position: tuple[float, float] = (0.0, 0.0) # In Einstein Radii

    @property
    def plane_seperation(self):
        return self.source_distance - self.lens_distance

    def add_lens(self, lens: Lens):
        self.lenses.append(lens)
        self.recalculate_com()
        self.recalculate_einstein_radius()

    def recalculate_com(self):
        x_sum = 0.0
        y_sum = 0.0
        mass_sum = 0.0
        for lens in self.lenses:
            x_sum += lens.m * lens.x
            y_sum += lens.m * lens.y
            mass_sum += lens.m
        self.lens_mass = mass_sum
        self.lens_com = x_sum / mass_sum, y_sum / mass_sum

    def recalculate_einstein_radius(self):
        if self.source_distance <= 0 or self.lens_distance <= 0:
            raise ValueError("Source or lens distance is invalid, and the einstein radius cannot be calculated")
        self.einstein_radius = (EINSTEIN_FACTOR * self.lens_mass * (self.source_distance - self.lens_distance) / (self.source_distance * self.lens_distance))**0.5
        self.lens_radius = pc_to_au * (self.lens_distance * tan(self.einstein_radius))
        self.source_radius = pc_to_au * (self.source_distance * tan(self.einstein_radius))

    def transform_lens():
        pass


