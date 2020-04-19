import tempfile
import base64
from aiohttp import web
from torrenttv.bittorrent import AddTorrentError, DeleteFailedError


async def index(req):
    session = req.app["data"].session
    torrents = _all(session)
    return web.json_response({"list": torrents})


async def create(req):
    session = req.app["data"].session
    kwargs = await req.json()
    uri = kwargs.pop("uri", "")
    torrent = await _create(session, uri, **kwargs)
    return web.json_response(torrent)


async def show(req):
    session = req.app["data"].session
    info_hash = req.match_info.get("info_hash")
    torrent = _find(session, info_hash)
    return web.json_response(torrent)


async def update(req):
    session = req.app["data"].session
    info_hash = req.match_info.get("info_hash")
    kwargs = await req.json()
    torrent = await _update(session, info_hash, **kwargs)
    return web.json_response(torrent)


async def destroy(req):
    session = req.app["data"].session
    info_hash = req.match_info.get("info_hash")
    kwargs = await req.json()
    await _destroy(session, info_hash, **kwargs)
    return web.json_response({})


def _all(session, **kwargs):
    torrents = session.get_torrents()
    return [_to_dict(torrent) for torrent in torrents]


def _find(session, info_hash, **kwargs):
    torrent = session.get_torrent(info_hash)
    if not torrent:
        raise web.HTTPNotFound()
    return _to_dict(torrent)


async def _create(session, uri, **kwargs):
    # URI can start with file:, magnet:, data:,
    if uri.startswith("file:"):
        # remove the scheme
        # NOTE: for now we assume that host is always omitted
        link = uri[5:]
        if link.startswith("///"):
            link = uri[3:]
        else:
            link = uri[1:]
    elif uri.startswith("magnet:"):
        link = uri
    elif uri.startswith("data:"):
        # TODO: add support for search result json data
        # remove the scheme
        uri = uri[5:]
        data_type_and_base64, data_encoded = uri.split(",", 1)
        # NOTE: for now we assume that data is always "octet-stream" encoded base64
        data = base64.urlsafe_b64decode(data_encoded)
        temp = tempfile.NamedTemporaryFile(mode="w+b", delete=False)
        temp.write(data)
        temp.flush()
        link = temp.name
    else:
        raise web.HTTPBadRequest()
    try:
        torrent = await session.add_torrent(link, **kwargs)
    except RuntimeError as e:
        raise web.HTTPBadRequest(reason=str(e))
    except AddTorrentError as e:
        raise web.HTTPConflict(reason=str(e))
    return _to_dict(torrent)


async def _destroy(session, info_hash, **kwargs):
    delete_files = kwargs.get("deleteFiles", False)
    torrent = session.get_torrent(info_hash)
    if not torrent:
        raise web.HTTPNotFound()
    try:
        await session.remove_torrent(torrent, delete_files=delete_files)
    except DeleteFailedError:
        raise web.HTTPInternalServerError()


async def _update(session, info_hash, **kwargs):
    torrent = session.get_torrent(info_hash)
    if not torrent:
        raise web.HTTPNotFound()
    if "downloadRateLimit" in kwargs:
        download_rate_limit = int(kwargs["downloadRateLimit"])
        torrent.set_download_rate_limit(download_rate_limit)
    if "uploadRateLimit" in kwargs:
        upload_rate_limit = int(kwargs["uploadRateLimit"])
        torrent.set_upload_rate_limit(upload_rate_limit)
    if "connectionsLimit" in kwargs:
        connections_limit = int(kwargs["connectionsLimit"])
        torrent.set_connections_limit(connections_limit)
    if "paused" in kwargs:
        paused = bool(kwargs["paused"])
        if paused and not torrent.paused:
            await torrent.pause()
        elif not paused and torrent.paused:
            await torrent.resume()
        else:
            raise Exception()
    return _to_dict(torrent)


def _to_dict(torrent, _filter=None):
    d = {
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
    if _filter is not None:
        d = {key: value for key, value in d.items() if key in _filter}
    return d
