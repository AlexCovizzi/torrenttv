import asyncio
from concurrent.futures import ThreadPoolExecutor
import requests
from torrenttv.utils import fetch
from .element import Element


class WebCrawler:

    def __init__(self, loop=None, executor=None, session=None):
        self._loop = loop or asyncio.get_event_loop()
        self._executor = executor or ThreadPoolExecutor()
        self._session = session or requests.Session()

    async def get(self, url: str, **kwargs) -> Element:
        return self.fetch(url, method="GET", **kwargs)

    async def post(self, url: str, **kwargs) -> Element:
        return self.fetch(url, method="POST", **kwargs)

    async def fetch(self, url: str, method="GET", **kwargs) -> Element:
        res = await fetch(
            url,
            method=method,
            loop=self._loop,
            executor=self._executor,
            session=self._session,
            **kwargs)
        html = res.text
        document = Element.parse(html)
        return document
