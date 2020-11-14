from aiohttp import web


class SearchParams:

    DEFAULT_LIMIT = 20
    DEFAULT_TIMEOUT = 5

    def __init__(self, query: str, limit: int, timeout: int):
        self._query = query
        self._limit = limit
        self._timeout = timeout

    @property
    def query(self):
        return self._query

    @property
    def limit(self):
        return self._limit

    @property
    def timeout(self):
        return self._timeout

    @staticmethod
    def from_request(request: web.Request):
        url_query = request.url.query
        query = url_query.get("query", "")
        limit = int(url_query.get("limit", SearchParams.DEFAULT_LIMIT))
        timeout = int(url_query.get("timeout", SearchParams.DEFAULT_TIMEOUT))
        return SearchParams(query, limit, timeout)
