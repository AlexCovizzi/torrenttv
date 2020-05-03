import asyncio
import configparser
from torrenttv.utils import async_utils

__all__ = ["Configuration"]


class Configuration:

    def __init__(self, filename, loop=None, driver=None):
        self._filename = filename
        self._loop = loop or asyncio.get_event_loop()
        self._driver = driver or configparser.ConfigParser()

    def get(self, prop, default=None):
        return self._driver.get(prop, default=default)

    def update(self, **kwargs):
        self._driver.update(**kwargs)

    def read(self):
        fut = async_utils.futurize(
            self._driver.read, args=(self._filename,), loop=self._loop)
        return fut

    def write(self):
        fut = async_utils.futurize(
            self._driver.write, args=(self._filename,), loop=self._loop)
        return fut

    def __getitem__(self, prop):
        return self.get(prop)

    def __setitem__(self, prop, value):
        self.update(**{prop: value})
