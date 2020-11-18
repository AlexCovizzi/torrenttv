from aiohttp import web
from torrenttv.bittorrent import Session


class SessionHandler:

    def __init__(self, session: Session):
        self._session = session

    async def show(self, _request: web.Request) -> web.Response:
        json = self._convert_to_json(self._session)
        return web.json_response(json)

    async def update(self, request: web.Request) -> web.Response:
        kwargs = await request.json()
        if "downloadRateLimit" in kwargs:
            download_rate_limit = int(kwargs["downloadRateLimit"])
            self._session.set_download_rate_limit(download_rate_limit)
        if "uploadRateLimit" in kwargs:
            upload_rate_limit = int(kwargs["uploadRateLimit"])
            self._session.set_upload_rate_limit(upload_rate_limit)
        if "connectionsLimit" in kwargs:
            connections_limit = int(kwargs["connectionsLimit"])
            self._session.set_connections_limit(connections_limit)
        if "paused" in kwargs:
            paused = bool(kwargs["paused"])
            if paused and not self._session.paused:
                await self._session.pause()
            elif not paused and self._session.paused:
                await self._session.resume()
        json = self._convert_to_json(self._session)
        return web.json_response(json)

    def _convert_to_json(self, session) -> dict:
        return {
            "numSeeds": session.num_seeds,
            "numPeers": session.num_peers,
            "numConnections": session.num_connections,
            "downloadRate": session.download_rate,
            "uploadRate": session.upload_rate,
            "connectionsLimit": session.connections_limit,
            "downloadRateLimit": session.download_rate_limit,
            "uploadRateLimit": session.upload_rate_limit,
            "paused": session.paused
        }
