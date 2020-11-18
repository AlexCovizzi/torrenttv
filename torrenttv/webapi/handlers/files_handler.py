from aiohttp import web
from torrenttv.bittorrent import Session, Torrent, File


class FilesHandler:

    def __init__(self, session: Session):
        self._session = session

    async def index(self, request: web.Request) -> web.Response:
        info_hash = request.match_info.get("info_hash")
        torrent = self._find_torrent_or_404(info_hash)
        json = {
            "list": [
                self._convert_to_json(torrent_file) for torrent_file in torrent.files
            ]
        }
        return web.json_response(json)

    async def show(self, request: web.Request) -> web.Response:
        info_hash = request.match_info.get("info_hash")
        file_idx = int(request.match_info.get("file_idx"))
        torrent_file = self._find_torrent_file_or_404(info_hash, file_idx)
        json = self._convert_to_json(torrent_file)
        return web.json_response(json)

    async def update(self, request: web.Request) -> web.Response:
        info_hash = request.match_info.get("info_hash")
        file_idx = int(request.match_info.get("file_idx"))
        kwargs = await request.json()
        torrent_file = self._find_torrent_file_or_404(info_hash, file_idx)
        if "priority" in kwargs:
            priority = int(kwargs["priority"])
            torrent_file.set_priority(priority)
        json = self._convert_to_json(torrent_file)
        return web.json_response(json)

    def _find_torrent_file_or_404(self, info_hash, file_idx) -> File:
        torrent = self._find_torrent_or_404(info_hash)
        if len(torrent.files) >= file_idx:
            raise web.HTTPNotFound()
        return torrent.files[file_idx]

    def _find_torrent_or_404(self, info_hash) -> Torrent:
        torrent = self._session.get_torrent(info_hash)
        if not torrent:
            raise web.HTTPNotFound()
        return torrent

    def _convert_to_json(self, torrent_file: File) -> dict:
        return {
            "name": torrent_file.name,
            "size": torrent_file.size,
            "path": torrent_file.path,
            "mimeType": torrent_file.mime_type,
            "priority": torrent_file.priority,
        }
