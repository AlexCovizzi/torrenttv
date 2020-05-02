import asyncio
import configparser
from concurrent.futures import ThreadPoolExecutor

__all__ = ["Configuration"]


class Configuration:

    def __init__(self, filename, loop=None, executor=None, driver=None):
        self._filename = filename
        self._loop = loop or asyncio.get_event_loop()
        self._executor = executor or ThreadPoolExecutor(max_workers=1)
        self._driver = driver or configparser.ConfigParser()

    def get(self, prop, default=None):
        return self._driver.get(prop, default=default)

    def update(self, **kwargs):
        self._driver.update(**kwargs)

    async def read(self):
        await self._loop.run_in_executor(self._executor, self._driver.read,
                                         self._filename)

    async def write(self):
        await self._loop.run_in_executor(self._executor, self._driver.write,
                                         self._filename)

    def __getitem__(self, prop):
        return self.get(prop)

    def __setitem__(self, prop, value):
        self.update(**{prop: value})
