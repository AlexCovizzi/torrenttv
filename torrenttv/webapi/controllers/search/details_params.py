from aiohttp import web


class DetailsParams:

    DEFAULT_TIMEOUT = 5

    def __init__(self, provider: str, infourl: str, timeout: int):
        self._provider = provider
        self._infourl = infourl
        self._timeout = timeout

    @property
    def provider(self):
        return self._provider

    @property
    def infourl(self):
        return self._infourl

    @property
    def timeout(self):
        return self._timeout

    @staticmethod
    def from_request(request: web.Request):
        url_query = request.url.query
        provider = url_query.get("provider")
        infourl = url_query.get("infourl")
        timeout = int(url_query.get("timeout", DetailsParams.DEFAULT_TIMEOUT))
        return DetailsParams(provider, infourl, timeout)
