import asyncio
import requests


class RequestError(IOError):

    def __init__(self, message):
        super().__init__(str(message))


class RequestTimeoutError(RequestError, TimeoutError):

    def __init__(self, message):
        super().__init__(str(message))


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


def fetch(url, method="GET", loop=None, executor=None, session=None, **kwargs):

    def _fetch(url, kwargs):
        try:
            if session:
                requests_res = session.request(method, url, **kwargs)
            else:
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
    return fut
