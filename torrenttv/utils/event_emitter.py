from typing import Callable
from collections import OrderedDict


class EventEmitter:

    def __init__(self):
        self.__listeners = dict()

    def on(self, event: str, func: Callable):
        self.__add_listener(event, func)

    def once(self, event: str, func: Callable):
        self.__add_listener(event, func, ttl=1)

    def off(self, event: str, func: Callable):
        self.__remove_listener(event, func)

    def emit(self, event: str, *args):
        self.__emit_event(event, *args)

    def listeners(self, event: str):
        return list(self.__event_listeners(event))

    def __add_listener(self, event, func, ttl=-1):
        if event not in self.__listeners:
            self.__listeners[event] = HashList()

        listener = Listener(
            func, ttl=ttl, cb=lambda: self.__remove_listener(event, func))
        self.__listeners[event].append(listener)

    def __remove_listener(self, event, func):
        if event in self.__listeners:
            self.__listeners[event].remove(func)

    def __event_listeners(self, event):
        return self.__listeners.get(event, [])

    def __emit_event(self, event, *args):
        if event in self.__listeners:
            for listener in list(self.__listeners[event]):
                listener(*args)


class Listener:

    def __init__(self, func, ttl=-1, cb=None):
        self._ttl = ttl
        self._func = func
        self._cb = cb
        self._exc = None

    @property
    def func(self):
        return self._func

    @property
    def ttl(self):
        return self._ttl

    @property
    def exc(self):
        return self._exc

    def __call__(self, *args):
        try:
            self.func(*args)
        except Exception as e:  # pylint: disable=broad-except
            self._exc = e

        if self._ttl > 0:
            self._ttl -= 1
            if self._ttl == 0:
                self._cb()

    def __hash__(self):
        return hash(self._func)


class HashList:

    def __init__(self):
        self._dict = OrderedDict()

    def append(self, item):
        self._dict[hash(item)] = item

    def remove(self, item):
        return self._dict.pop(hash(item), None)

    def __iter__(self):
        return self._dict.values().__iter__()
