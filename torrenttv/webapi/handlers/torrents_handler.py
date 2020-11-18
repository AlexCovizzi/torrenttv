import tempfile
import base64
from aiohttp import web
from torrenttv.bittorrent import Session, Torrent, AddTorrentError, DeleteFailedError


class TorrentsHandler:

    def __init__(self, session: Session):
        self._session = session

    async def index(self, _request: web.Request) -> web.Response:
        torrents = self._session.get_torrents()
        json = {"list": [self._convert_to_json(torrent) for torrent in torrents]}
        return web.json_response(json)

    async def show(self, request: web.Request) -> web.Response:
        info_hash = request.match_info.get("info_hash")
        torrent = self._find_torrent_or_404(info_hash)
        json = self._convert_to_json(torrent)
        return web.json_response(json)

    async def update(self, request: web.Request) -> web.Response:
        info_hash = request.match_info.get("info_hash")
        body = await request.json()
        torrent = self._find_torrent_or_404(info_hash)
        if "downloadRateLimit" in body:
            download_rate_limit = int(body["downloadRateLimit"])
            torrent.set_download_rate_limit(download_rate_limit)
        if "uploadRateLimit" in body:
            upload_rate_limit = int(body["uploadRateLimit"])
            torrent.set_upload_rate_limit(upload_rate_limit)
        if "connectionsLimit" in body:
            connections_limit = int(body["connectionsLimit"])
            torrent.set_connections_limit(connections_limit)
        if "paused" in body:
            paused = bool(body["paused"])
            if paused and not torrent.paused:
                await torrent.pause()
            elif not paused and torrent.paused:
                await torrent.resume()
        json = self._convert_to_json(torrent)
        return web.json_response(json)

    async def create(self, request: web.Request) -> web.Response:
        body = await request.json()
        if "uri" not in body:
            raise web.HTTPBadRequest(reason="Uri was not provided")
        uri = body.pop("uri")
        # URI can start with file:, magnet:, data:
        if uri.startswith("file:"):
            # remove the scheme
            # NOTE: for now we assume that host is always omitted
            link = uri[5:]
            link = uri[3:] if link.startswith("///") else uri[1:]
        elif uri.startswith("data:"):
            # TODO: add support for search result json data
            # remove the scheme
            uri = uri[5:]
            _, data_encoded = uri.split(",", 1)
            # NOTE: for now we assume that data is always "octet-stream" encoded base64
            data = base64.urlsafe_b64decode(data_encoded)
            temp = tempfile.NamedTemporaryFile(mode="w+b", delete=False)
            temp.write(data)
            temp.flush()
            link = temp.name
        elif uri.startswith("magnet:"):
            link = uri
        else:
            raise web.HTTPBadRequest(reason="Uri is not supported")
        try:
            torrent = await self._session.add_torrent(link, **body)
        except RuntimeError as e:
            raise web.HTTPBadRequest(reason=str(e))
        except AddTorrentError as e:
            raise web.HTTPConflict(reason=str(e))
        json = self._convert_to_json(torrent)
        return web.json_response(json)

    async def destroy(self, request: web.Request) -> web.Response:
        info_hash = request.match_info.get("info_hash")
        body = await request.json()
        delete_files = body.get("deleteFiles", False)
        torrent = self._find_torrent_or_404(info_hash)
        try:
            await self._session.remove_torrent(torrent, delete_files=delete_files)
        except DeleteFailedError as e:
            raise web.HTTPInternalServerError(reason=str(e))
        return web.HTTPOk()

    def _find_torrent_or_404(self, info_hash) -> Torrent:
        torrent = self._session.get_torrent(info_hash)
        if not torrent:
            raise web.HTTPNotFound()
        return torrent

    def _convert_to_json(self, torrent: Torrent) -> dict:
        return {
            "name": torrent.name,
            "infoHash": torrent.info_hash,
            "path": torrent.path,
            "state": torrent.state,
            "numFiles": torrent.num_files,
            "numSeeds": torrent.num_seeds,
            "numPeers": torrent.num_peers,
            "numConnections": torrent.num_connections,
            "total": torrent.total,
            "totalDone": torrent.total_done,
            "totalWanted": torrent.total_wanted,
            "totalWantedDone": torrent.total_wanted_done,
            "progress": torrent.progress,
            "pieces": [1 if piece else 0 for piece in torrent.pieces],
            "downloadRate": torrent.download_rate,
            "uploadRate": torrent.upload_rate,
            "connectionsLimit": torrent.connections_limit,
            "downloadRateLimit": torrent.download_rate_limit,
            "uploadRateLimit": torrent.upload_rate_limit,
            "paused": torrent.paused
        }
