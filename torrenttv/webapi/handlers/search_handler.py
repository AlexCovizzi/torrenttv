import urllib
from aiohttp import web
from torrenttv.torrentsearchengine import TorrentSearchEngine


class SearchHandler:

    DEFAULT_LIMIT = 20
    DEFAULT_TIMEOUT = 5

    def __init__(self, search_engine: TorrentSearchEngine):
        self._search_engine = search_engine

    async def search(self, request: web.Request) -> web.Response:
        url_query = request.url.query
        query = url_query.get("query", "")
        limit = int(url_query.get("limit", SearchHandler.DEFAULT_LIMIT))
        timeout = int(url_query.get("timeout", SearchHandler.DEFAULT_TIMEOUT))
        results = await self._search_engine.search(query, limit=limit, timeout=timeout)
        return web.json_response({"list": results})

    async def details(self, request: web.Request) -> web.Response:
        url_query = request.url.query
        provider = url_query.get("provider")
        infourl = urllib.parse.unquote(url_query.get("infourl"))
        timeout = int(url_query.get("timeout", SearchHandler.DEFAULT_TIMEOUT))
        search_data = {"provider": provider, "infourl": infourl}
        result = await self._search_engine.details(search_data, timeout=timeout)
        return web.json_response(result)
