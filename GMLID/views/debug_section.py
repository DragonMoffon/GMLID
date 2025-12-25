from random import randint
from typing import Any

from arcade import View, SectionManager, Section, draw_rect_filled, Rect, LBWH
from arcade.clock import GLOBAL_CLOCK
from arcade.easing import ease_in_out
from arcade.math import lerp

GRID_SIZE = 400
TRANSITION_DURATION = 0.3

class FrameManager:

    def __init__(self, view: View) -> None:
        self.view: View = view
        self.sm: SectionManager = SectionManager(view)
        self.sm.add_section(DebugFrame(0, 0, GRID_SIZE, GRID_SIZE, name="initial"))
        self.grid: dict[tuple[int, int], int] = {}
        self.prev_state: tuple[Rect] = ()
        self.next_state: tuple[Rect] = ()
        self.prev_size: tuple[int, int] | None = None
        self.next_size: tuple[int, int] | None = None
        self.to_remove: tuple[Section, ...] = ()
        self.change_time: float = -float('inf')
        self.animating: bool = False

    def update(self):
        if not self.animating:
            return
        
        if self.change_time + TRANSITION_DURATION <= GLOBAL_CLOCK.time:
            for section, end in zip(self.sm.sections, self.next_state):
                section.rect = end
            if self.next_size is not None:
                self.view.window.set_size(*self.next_size)


            for section in self.to_remove:
                self.sm.remove_section(section)
            self.to_remove = ()
            self.animating = False
            return
        
        frac = GLOBAL_CLOCK.time - self.change_time / TRANSITION_DURATION
        ease = ease_in_out(frac)

        if self.prev_size is not None:
            w = lerp(self.prev_size[0], self.next_size[1], ease)
            h = lerp(self.prev_size[1], self.next_size[1], ease)
            self.view.window.set_size(w, h)

        for section, start, end in zip(self.sm.sections, self.prev_state, self.next_state):
            section._left = lerp(start.left, end.left, ease)
            section._bottom = lerp(start.bottom, end.bottom, ease)
            section._width = lerp(start.width, end.width, ease)
            section._right = section._left + section._width
            section._height = lerp(start.height, end.height, ease)
            section._top = section._bottom + section._height

            section._ec_left = 0 if section.modal else section._left
            section._ec_right = self.view.window.width if section.modal else section._right
            section._ec_bottom = 0 if section.modal else section._bottom
            section._ec_top = self.view.window.height if section.modal else section._top

    def add_section[T: Section](self, typ: type[T], name: str | None = None, **kwds: Any) -> T:
        print("t")
        if self.animating:
            # finish animating
            pass

        idx = len(self.sm.sections)
        if name is None:
            name = str(idx)
        # Todo: actual layouting
        section = typ(0, 0, 1, GRID_SIZE, name=name, **kwds)
        self.sm.add_section(section)
        
        self.animating = True
        self.change_time = GLOBAL_CLOCK.time 

        self.prev_state = tuple(s.rect for s in self.sm.sections) 
        self.next_state = (*(s.rect.align_left(s.left + GRID_SIZE) for s in self.sm.sections[:-1]), LBWH(0, 0, GRID_SIZE, GRID_SIZE))

        self.prev_size = self.view.window.size
        self.next_size = self.view.window.width + GRID_SIZE, self.view.window.height 

class DebugFrame(Section):

    def __init__(self, left: int | float, bottom: int | float, width: int | float, height: int | float, *, name: str | None = None):
        super().__init__(left, bottom, width, height, name=name, prevent_dispatch={False})
        self.color = (randint(0, 255), randint(0, 255), randint(0, 255), 255)

    def on_draw(self):
        draw_rect_filled(LBWH(self.left+5, self.bottom+5, self.width-10, self.height-10), self.color)

class DebugSectionView(View):

    def __init__(self) -> None:
        super().__init__()
        self.window.set_size(GRID_SIZE, GRID_SIZE)
        self.frames = FrameManager(self)

    def on_show_view(self) -> None:
        self.window.set_size(400, 400)
        self.frames.sm.enable()

    def on_hide_view(self) -> None:
        self.frames.sm.disable()
    
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> bool | None:
        self.frames.add_section(DebugFrame)

    def on_update(self, delta_time: float) -> bool | None:
        self.frames.update()
