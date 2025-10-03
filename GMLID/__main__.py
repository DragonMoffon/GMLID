import arcade

from GMLID.inverse_ray import InverseRayImageView

GRAV_CONST = 6.6743e-11
SPEED_OF_LIGHT = 299_792_458.0


class AppState:
    lens_distance: float  # Distance observer -> lens
    source_distance: float  # Distance lens -> source
    total_distance: float = property(
        (lambda self: self.lens_distance + self.total_distance)
    )


state = AppState()


class MagMapView(arcade.View):
    def __init__(self):
        super().__init__()

    def on_draw(self):
        self.clear()


class Window(arcade.Window):
    def __init__(self):
        super().__init__(
            720, 720, "Gravitational Micro-Lensing Magnification Interactive Demo"
        )

        self.ivri_view = InverseRayImageView()
        self.mm_view = MagMapView()
        self.show_view(self.ivri_view)

    def on_key_press(self, symbol, modifiers):
        if not modifiers & arcade.key.MOD_CTRL:
            return

        match symbol:
            case arcade.key.KEY_1:
                self.show_view(self.ivri_view)
                return True
            case arcade.key.KEY_2:
                self.show_view(self.mm_view)
                return True


def main():
    window = Window()
    window.run()


if __name__ == "__main__":
    main()
