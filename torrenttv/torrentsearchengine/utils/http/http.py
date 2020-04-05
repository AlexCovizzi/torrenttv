import asyncio
import requests
from .exceptions import RequestError, RequestTimeoutError


class Response:
    def __init__(self, inner: requests.Response):
        self._inner = inner

    @property
    def text(self):
        return self._inner.text

    @property
    def encoding(self):
        return self._inner.encoding

    @encoding.setter
    def encoding(self, enc):
        self._inner.encoding = enc

    def raise_for_status(self):
        self._inner.raise_for_status()


async def fetch(url, method="GET", loop=None, executor=None, **kwargs):
    def _fetch(url, kwargs):
        try:
            requests_res = requests.request(method, url, **kwargs)
            # wrap the requests' response
            res = Response(requests_res)
            res.encoding = "utf-8"
            res.raise_for_status()
        except requests.exceptions.Timeout as e:
            raise RequestTimeoutError(e) from e
        except requests.exceptions.RequestException as e:
            raise RequestError(e) from e
        return res

    loop = loop or asyncio.get_event_loop()
    fut = loop.run_in_executor(executor, _fetch, str(url), kwargs)
    res = await fut
    return res
