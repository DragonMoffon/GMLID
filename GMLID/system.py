from dataclasses import dataclass

@dataclass
class Lens:
    x: float
    y: float
    m: float

    @property
    def position(self) -> tuple[float, float]:
        return (self.x, self.y)

    @position.setter
    def position(self, value: tuple[float, float]):
        self.x, self.y = value

    def pack(self, com_x: float = 0.0, com_y: float = 0.0):
        return self.m, 0.0, self.x - com_x, self.y - com_y

class LensSystem:
    
    def __init__(self):
        self.lenses: list[Lens] = []
        self.lens_mass: float = 0.0
        self.lens_com: tuple[float, float] = (0.0, 0.0)

