from aiohttp import web
from torrenttv.torrentsearchengine import TorrentSearchEngine
from .search_params import SearchParams
from .details_params import DetailsParams


class SearchController:

    def __init__(self, search_engine: TorrentSearchEngine):
        self._search_engine = search_engine

    async def search(self, request: web.Request):
        params = SearchParams.from_request(request)
        results = await self._search_engine.search(
            params.query, limit=params.limit, timeout=params.timeout)
        return web.json_response({"list": results})

    async def details(self, request: web.Request):
        params = DetailsParams.from_request(request)
        result = await self._search_engine.info(
            {
                "provider": params.provider,
                "infourl": params.infourl
            },
            timeout=params.timeout)
        return web.json_response(result)
