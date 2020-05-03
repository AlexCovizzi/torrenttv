import asyncio
from aiohttp import web


async def show(req):
    session = req.app["data"].session
    info_hash = req.match_info.get("info_hash", None)
    # file_idx = int(req.match_info.get("file_idx")) or 0
    file_name = req.match_info.get("file_name") or ""
    # if an infohash is provided return the matching torrent
    # otherwise return the first torrent in the session
    if info_hash:
        torrent = session.get_torrent(info_hash)
        if torrent is None:
            raise web.HTTPNotFound()
    else:
        torrents = session.get_torrents()
        if len(torrents) == 0:
            raise web.HTTPNotFound()
        else:
            torrent = torrents[0]
    f = torrent.get_file_by_name(file_name, fuzzy_search=True)

    if req.http_range.start is None:
        response = web.Response()
        response.content_type = f.mime_type
        response.headers.add("Accept-Ranges", "bytes")
        response.headers.add("Content-Length", str(f.size))
        response.headers.add("Cache-Control", "no-cache")
        return response

    first_byte = req.http_range.start or 0
    last_byte = (
        req.http_range.stop if req.http_range.stop is not None and
        req.http_range.stop < f.size else f.size - 1)
    response = web.StreamResponse(status=206)
    response.content_length = last_byte - first_byte + 1
    response.content_type = f.mime_type
    response.headers.add("Accept-Ranges", "bytes")
    response.headers.add("Content-Range",
                         "bytes %s-%s/%s" % (first_byte, last_byte, f.size))
    response.headers.add("Cache-Control", "no-cache")

    await response.prepare(req)

    try:
        async for chunk in f.stream(offset=first_byte, chunk_size=16 * 1024):
            await asyncio.shield(response.write(chunk))
    except BaseException as e:
        print("asyncio socket.send() raised exception: %s" % e)
        pass
    finally:
        await response.write_eof()

    return response
