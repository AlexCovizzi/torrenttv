from typing import AsyncIterable
import asyncio
import async_timeout


def stream(iterable):
    if isinstance(iterable, AsyncIterable):
        return AsyncStream(iterable)
    raise TypeError()


class AsyncStream:

    def __init__(self, iterable):
        self._iterable = iterable

    def map(self, func):

        async def _map(iterable, func):
            async for item in iterable:
                yield func(item)

        return AsyncStream(_map(self._iterable, func))

    def for_each(self, func):

        async def _for_each(iterable, func):
            async for item in iterable:
                func(item)
                yield item

        return AsyncStream(_for_each(self._iterable, func))

    def timeout(self, timeout, raise_err=False):

        async def _timeout(iterable, timeout, raise_err):
            try:
                async with async_timeout.timeout(timeout):
                    async for item in iterable:
                        yield item
            except asyncio.TimeoutError as exc:
                if raise_err:
                    raise exc

        return AsyncStream(_timeout(self._iterable, timeout, raise_err))

    def capture(self, exc_type, func=None):

        async def _capture(iterable, exc_type, func):
            try:
                async for item in iterable:
                    yield item
            except Exception as exc:  # pylint: disable=broad-except
                if isinstance(exc, exc_type):
                    if callable(func):
                        func(exc)
                else:
                    raise exc

        return AsyncStream(_capture(self._iterable, exc_type, func))

    async def collect(self):
        lst = []
        async for item in self._iterable:
            lst.append(item)
        return lst

    def __aiter__(self):
        return self._iterable.__aiter__()
