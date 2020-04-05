from aiohttp import web


async def show(req):
    session = req.app["data"].session
    json = _show(session)
    return web.json_response(json)


async def update(req):
    session = req.app["data"].session
    kwargs = await req.json()
    json = await _update(session, **kwargs)
    return web.json_response(json)


def _show(session):
    return _to_dict(session)


async def _update(session, **kwargs):
    if "downloadRateLimit" in kwargs:
        download_rate_limit = int(kwargs["downloadRateLimit"])
        session.set_download_rate_limit(download_rate_limit)
    if "uploadRateLimit" in kwargs:
        upload_rate_limit = int(kwargs["uploadRateLimit"])
        session.set_upload_rate_limit(upload_rate_limit)
    if "connectionsLimit" in kwargs:
        connections_limit = int(kwargs["connectionsLimit"])
        session.set_connections_limit(connections_limit)
    if "paused" in kwargs:
        paused = bool(kwargs["paused"])
        if paused and not session.paused:
            await session.pause()
        elif not paused and session.paused:
            await session.resume()
        else:
            raise web.HTTPConflict()
    return _to_dict(session)


def _to_dict(session, _filter=None):
    d = {
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
    if _filter is not None:
        d = {key: value for key, value in d.items() if key in _filter}
    return d
