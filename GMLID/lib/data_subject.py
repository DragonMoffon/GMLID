"""
A DataSubject relies on the observer pattern to make it easy to
respond to changes to a database. In this case the Database is 
just a python object with attributes set by `setattr`.

When a system wants to know when an attribute changes is subscribes as 
a listener to the subject. This is a weakreference so subscribing
does not preserve the listener.

use `with data_subject.silenced():` to prevent the dispatch of notifications to
listeners. This is will likely cause undefined behaviour.

! Warning: Because this relies on __setattr__ it cannot be used with __slots__
"""

from __future__ import annotations
from contextlib import contextmanager
from collections.abc import Callable, Sequence
from weakref import WeakMethod
from typing import Any


__all__ = (
    "DataSubject",
)

type LogFunc = Callable[[str], Any]
type RefreshFunc = Callable[[], Any] # No args, any return value (generally None)
type WeakRefreshFunc = WeakMethod[RefreshFunc]

class DataSubject:

    def __init__(self, values: dict[str, Any] | None = None, log_function: LogFunc = print) -> None:
        self._refresh_functions: dict[WeakRefreshFunc, set[str] | None] = {}
        self._log_function: Callable[[str], Any] = log_function
        self._silent: bool = False

        if values:
            self.update_values(**values)

    def __setattr__(self, name: str, value: Any) -> None:
        object.__setattr__(self, name, value)
        if (name and name[0] == "_") or self._silent:
            return

        for func, mask in self._refresh_functions.items():
            if mask is None or name in mask:
                self._call_listener(func, name)

    def update_values(self, **kwds: Any) -> None:
        for name, value in kwds.items():
            object.__setattr__(self, name, value)
        
        if self._silent:
            return
        
        updated = set(kwds)
        for func, mask in self._refresh_functions.items():
            if mask is None or updated.intersection(mask):
                self._call_listener(func, updated)
                
    def _call_listener(self, func: WeakRefreshFunc, updated: str | set[str]):
        listener = func()
        if listener is None:
            return
        try:
            listener()
        except Exception as exception:
                raise RuntimeError(f"The Listener function: {listener.__name__} raised an exception while observing {updated}") from exception

    def register_refresh_func(self, f: RefreshFunc, mask: Sequence[str] | None = None) -> None:
        m = None if mask is None else set(mask)
        w = WeakMethod(f, self._clear_function)
        self._refresh_functions[w] = m

    def _clear_function(self, w: WeakRefreshFunc) -> None:
        self._refresh_functions.pop(w)
        self._log_function(f'refresh function {w} automatically deregistered')

    def deregister_refresh_func(self, f: RefreshFunc) -> None:
        w = WeakMethod(f)
        if w not in self._refresh_functions:
            return
        self._refresh_functions.pop(w)

    @contextmanager
    def silenced(self):
        was_silent = self._silent
        try:
            self._silent = True
            yield
        finally:
            self._silent = was_silent
