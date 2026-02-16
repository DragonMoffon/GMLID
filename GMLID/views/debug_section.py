from random import randint
from arcade import View, Rect, LBWH, Camera2D, draw_rect_filled


class Frame:
    def __init__(self, area: Rect = LBWH(0.0, 0.0, 1.0, 1.0), as_scissor: bool = False):
        self._area: Rect = area
        self._as_scissor: bool = as_scissor
        self._camera: Camera2D = Camera2D(
            viewport=None if as_scissor else area, scissor=area if as_scissor else None
        )

        self.debug_color = (randint(0, 255), randint(0, 255), randint(0, 255), 255)

    @property
    def area(self) -> Rect:
        return self._area

    @area.setter
    def area(self, area: Rect):
        self._area = area
        self._camera.update_values(
            area, viewport=not self._as_scissor, projection=not self._as_scissor
        )

    def on_draw(self):
        draw_rect_filled(self.area, self.debug_color)


FRAME_PADDING = 5


class FrameManager:
    def __init__(self, area: Rect) -> None:
        self._area: Rect = area
        self._frames: list[Frame] = []

        # grid properties
        self._width: int = 0
        self._height: int = 0
        self._grid: dict[tuple[int, int], Frame | None] = {}

        # animation properties
        pass

    def is_slot_free(self, slot: tuple[int, int]) -> bool:
        return self._grid.get(slot, None) is None

    def get_free_slot(self, reversed: bool = False):
        rows = range(self._height - 1, -1, -1) if reversed else range(self._height)
        for row in rows:
            slot = self.get_free_column(row, reversed)
            if slot is not None:
                return slot
        return None

    def get_free_column(self, row: int, reversed: bool = False) -> tuple[int, int] | None:
        if row < 0:
            row = self._height - row

        if not 0 <= row < self._height:
            return None  # out of bounds

        cols = range(self._width - 1, -1, -1) if reversed else range(self._width)
        for col in cols:
            if self._grid[(col, row)] is None:
                return col, row
        return None

    def get_free_row(self, col: int, reversed: bool = False) -> tuple[int, int] | None:
        if col < 0:
            col = self._width - col

        if not 0 <= col < self._width:
            return None  # out of bounds

        rows = range(self._height - 1, -1, -1) if reversed else range(self._height)
        for row in rows:
            if self._grid[(col, row)] is None:
                return col, row
        return None

    def grow_columns(self, new_width: int, from_slot: int | None = None):
        if new_width <= self._width:
            raise ValueError("grow_columns cannot shrink the number of columns")
        for col in range(self._width, new_width):
            for row in range(self._height):
                self._grid[(col, row)] = None

        if from_slot is None:
            self._width = new_width
            return

        shift = new_width - self._width
        for col in range(self._width - 1, from_slot - 1, -1):
            for row in range(self._height):
                self._grid[(col + shift, row)], self._grid[(col, row)] = (
                    self._grid[(col, row)],
                    None,
                )

        self._width = new_width

    def grow_rows(self, new_height: int, from_slot: int | None = None):
        if new_height <= self._height:
            raise ValueError("grow_rows cannot shrink the number of rows")

        for row in range(self._height, new_height):
            for col in range(self._width):
                self._grid[(col, row)] = None

        if from_slot is None:
            self._height = new_height
            return

        shift = new_height - self._height
        for row in range(self._height - 1, from_slot - 1, -1):
            for col in range(self._width):
                self._grid[(col, row + shift)], self._grid[(col, row)] = (
                    self._grid[(col, row)],
                    None,
                )
        self._height = new_height

    def create_frame[T: Frame](self, typ: type[T], slot: tuple[int, int] | None = None) -> T:
        if self._grid.get(slot, None) is not None:
            raise KeyError(f"slot: {slot} already has a frame, use replace_frame instead")

        if slot is None:
            slot = self.get_free_slot()
        if slot is None:
            slot = (self._width, 0)

        if self._width <= slot[0]:
            self.grow_columns(slot[0] + 1)
        elif slot[0] < 0:
            self.grow_columns(self._width - slot[0], 0)
            slot = 0, slot[1]

        if self._height <= slot[1]:
            self.grow_rows(slot[1] + 1)
        elif slot[1] < 0:
            self.grow_rows(self._height - slot[1], 0)
            slot = slot[0], 0
        self._grid[slot] = frame = typ()
        self._frames.append(frame)

        return frame

    def layout_frames(self):
        if self._width == 0 or self._height == 0:
            return
        sub_width = self._area.width / self._width
        sub_height = self._area.height / self._height

        for col in range(self._width):
            for row in range(self._height):
                frame = self._grid[(col, row)]
                if frame is None:
                    continue
                frame.area = LBWH(
                    sub_width * col + FRAME_PADDING,
                    self._height - sub_height * row - FRAME_PADDING,
                    sub_width - 2 * FRAME_PADDING,
                    sub_height - 2 * FRAME_PADDING,
                )

    def on_draw(self):
        for frame in self._frames:
            frame.on_draw()


class DebugSectionView(View):
    def __init__(self):
        View.__init__(self)

        self.frames = FrameManager(self.window.rect)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> bool | None:
        slot = self.frames.get_free_slot()
        if slot is None and self.frames._width > self.frames._height:
            slot = (self.frames._width, self.frames._height)  # (0, self.frames._height)
        self.frames.create_frame(Frame, slot)

    def on_draw(self):
        self.clear()
        self.frames.on_draw()
