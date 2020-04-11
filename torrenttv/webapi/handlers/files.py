from aiohttp import web


async def index(req):
    session = req.app["data"].session
    info_hash = req.match_info.get("info_hash")
    files = _all(session, info_hash)
    return web.json_response({"list": files})


async def show(req):
    session = req.app["data"].session
    info_hash = req.match_info.get("info_hash")
    file_idx = int(req.match_info.get("file_idx"))
    _file = _find(session, info_hash, file_idx)
    return web.json_response(_file)


async def update(req):
    session = req.app["data"].session
    info_hash = req.match_info.get("info_hash")
    file_idx = int(req.match_info.get("file_idx"))
    kwargs = await req.json()
    _file = await _update(session, info_hash, file_idx, **kwargs)
    return web.json_response(_file)


def _all(session, info_hash, **kwargs):
    torrent = session.get_torrent(info_hash)
    if not torrent:
        raise web.HTTPNotFound()
    files = torrent.files
    return [_to_dict(_file) for _file in files]


def _find(session, info_hash, file_idx, **kwargs):
    torrent = session.get_torrent(info_hash)
    if not torrent:
        raise web.HTTPNotFound()
    _file = torrent.files[file_idx]
    return _to_dict(_file)


async def _update(session, info_hash, file_idx, **kwargs):
    torrent = session.get_torrent(info_hash)
    if not torrent:
        raise web.HTTPNotFound()
    _file = torrent.files[file_idx]
    if "priority" in kwargs:
        priority = int(kwargs["priority"])
        _file.set_priority(priority)
    return _to_dict(_file)


def _to_dict(_file, _filter=None):
    d = {
        "name": _file.name,
        "size": _file.size,
        "path": _file.path,
        "mimeType": _file.mime_type,
        "priority": _file.priority,
    }
    if _filter is not None:
        d = {key: value for key, value in d.items() if key in _filter}
    return d
