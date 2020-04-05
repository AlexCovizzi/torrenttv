from typing import Callable
from collections import OrderedDict
import asyncio


class EventEmitter:

    def __init__(self):
        self.__listeners = {}

    def event(self, event: str, loop=None):
        loop = loop or asyncio.get_event_loop()

        def func_wrapper(*args):
            if len(args) == 0:
                args = None
            elif len(args) == 1:
                args = args[0]

            def set_result(fut, args):
                if not fut.done():
                    fut.set_result(args)

            loop.call_soon(set_result, fut, args)

        fut = loop.create_future()

        # remove the listener once the future is done
        fut.add_done_callback(lambda _: self.off(event, func_wrapper))

        self.once(event, func_wrapper)

        return fut

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

        listener = Listener(func, ttl=ttl,
                            cb=lambda: self.__remove_listener(event, func))
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

    def __init__(self, func: Callable, ttl: int = -1, cb=None):
        self._ttl = ttl
        self._func = func
        self._cb = cb
        self._ex = None

    @property
    def func(self):
        return self._func

    @property
    def ttl(self):
        return self._ttl

    @property
    def ex(self):
        return self._ex

    def __call__(self, *args):
        try:
            self.func(*args)
        except Exception as e:
            self._ex = e

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
