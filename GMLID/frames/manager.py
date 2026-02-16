from arcade import Rect, LBWH, Camera2D


class Frame:
    def __init__(self, area: Rect | None = None, aspect: float | None = None):
        self._area: Rect = area or LBWH(0, 0, 1, 1)
        self._scissor_area: Rect | None = None

        self._camera: Camera2D = Camera2D(viewport=self._area)

        self.active: bool = True
        self.visible: bool = True

        self._aspect = aspect

    @property
    def area(self) -> Rect:
        return self._area

    @area.setter
    def area(self, area: Rect):
        if self._area == area:
            return

        self._area = area
        self._camera.update_values(area, aspect=self._aspect)

    @property
    def aspect(self) -> float | None:
        return self._aspect

    @aspect.setter
    def aspect(self, aspect: float | None):
        if self._aspect == aspect:
            return

        self._aspect = aspect
        self._camera.update_values(self._area, aspect=aspect)

    def ready(self):
        return self._camera.activate()

    def on_update(self, delta_time: float): ...
    def on_fixed_update(self, delta_time: float): ...
    def on_draw(self): ...


type Slot = tuple[int, int]


class FrameGrid:
    def __init__(self):
        self._grid: dict[Slot, Frame | None] = {}
        self._width: int = 0
        self._height: int = 0

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def __getitem__(self, slot: Slot) -> Frame | None:
        return self._grid.get(slot, None)

    def __setitem__(self, slot: Slot, frame: Frame | None):
        if self._width <= slot[0]:
            self.grow_axis(slot[0] + 1)
        elif slot[0] < 0:
            self.grow_axis(self._width - slot[0], 0)

        if self._height <= slot[1]:
            self.grow_axis(slot[1] + 1, rows=True)
        elif slot[1] < 0:
            self.grow_axis(self._height - slot[1], 0, rows=True)

        self._grid[slot] = frame

    def is_slot_free(self, slot: Slot) -> bool:
        return self[slot] is None

    # -- Grid Size Methods --

    def grow_axis(self, new_size: int, from_slot: int | None = None, rows: bool = False):
        along = self._height if rows else self._width
        across = self._width if rows else self._height

        if new_size <= along:
            raise ValueError(
                "grow axis cannot decrease the size of an axis, use shrink_axis instead"
            )

        for a in range(along, new_size):
            for b in range(across):
                self._grid[(b, a) if rows else (a, b)] = None

        if from_slot is None:
            if rows:
                self._height = new_size
            else:
                self._width = new_size
            return

        shift = new_size - along
        for a in range(along - 1, from_slot - 1, -1):
            for b in range(across):
                slot = (b, a) if rows else (a, b)
                slot_shifted = (b, a + shift) if rows else (a + shift, b)
                self._grid[slot_shifted], self._grid[slot] = self._grid[slot], None

        if rows:
            self._height = new_size
        else:
            self._width = new_size

    def shrink_axis(self, new_size: int, from_slot: int | None = None, rows: bool = False):
        along = self._height if rows else self._width
        across = self._width if rows else self._height

        if along <= new_size:
            raise ValueError(
                "shrink axis cannot increase the size of an axis, use grow_axis instead"
            )

        if from_slot is not None:
            shift = along - new_size
            for a in range(from_slot, from_slot + shift):
                for b in range(across):
                    a_s = a + shift
                    self._grid[(b, a) if rows else (a, b)] = self[(b, a_s) if rows else (a_s, b)]

        for a in range(new_size, along):
            for b in range(across):
                self._grid.pop((b, a) if rows else (a, b))

        if rows:
            self._height = new_size
        else:
            self._width = new_size


class FrameManager:
    def __init__(self, area: Rect) -> None:
        self._area: Rect = area
        self._frames: list[Frame] = []
        self._grid: FrameGrid = FrameGrid()

    @property
    def area(self) -> Rect:
        return self._area

    @area.setter
    def area(self, area: Rect):
        if self._area == area:
            return
        self._area = area
        self.layout_frames()

    def layout_frames(self):
        if not self._grid.width or not self._grid.height:
            return

        sub_width = self._area.width / self._grid.width
        sub_height = self._area.height / self._grid.height
        for col in range(self._grid.width):
            for row in range(self._grid.height):
                frame = self._grid[col, row]
                if frame is None:
                    continue
                l = col * sub_width
                b = self.area.height - (row + 1) * sub_height
                frame.area = LBWH(l, b, l + sub_width, b + sub_height)

    def on_update(self, delta_time):
        for frame in self._frames:
            if not frame.active:
                continue
            frame.on_update(delta_time)

    def on_fixed_update(self, delta_time):
        for frame in self._frames:
            if not frame.active:
                continue
            frame.on_fixed_update(delta_time)

    def on_draw(self):
        for frame in self._frames:
            if not frame.visible:
                continue
            with frame.ready():
                frame.on_draw()
