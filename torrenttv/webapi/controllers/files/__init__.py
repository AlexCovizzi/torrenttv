from aiohttp import web
from torrenttv.bittorrent import Session


class FilesController:

    def __init__(self, session: Session):
        self._session = session

    async def index(self, request: web.Request):
        info_hash = request.match_info.get("info_hash")
        files = _all(session, info_hash)
        return web.json_response({"list": files})


async def show(self, request: web.Request):
    info_hash = request.match_info.get("info_hash")
    file_idx = int(request.match_info.get("file_idx"))
    _file = _find(session, info_hash, file_idx)
    return web.json_response(_file)


async def update(self, request: web.Request):
    info_hash = request.match_info.get("info_hash")
    file_idx = int(request.match_info.get("file_idx"))
    kwargs = await request.json()
    _file = await _update(session, info_hash, file_idx, **kwargs)
    return web.json_response(_file)