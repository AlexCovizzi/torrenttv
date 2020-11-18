import asyncio
from aiohttp import web
from torrenttv.bittorrent import Session


class WatchHandler:

    def __init__(self, session: Session):
        self._session = session

    async def show(self, request: web.Request) -> web.Response:
        info_hash = request.match_info.get("info_hash", None)
        # file_idx = int(req.match_info.get("file_idx")) or 0
        file_name = request.match_info.get("file_name") or ""
        # if an infohash is provided return the matching torrent
        # otherwise return the first torrent in the session
        if info_hash:
            torrent = self._session.get_torrent(info_hash)
            if not torrent:
                raise web.HTTPNotFound()
        else:
            torrents = self._session.get_torrents()
            if len(torrents) == 0:
                raise web.HTTPNotFound()
            torrent = torrents[0]
        torrent_file = torrent.get_file_by_name(file_name, fuzzy_search=True)

        if request.http_range.start is None:
            response = web.Response()
            response.content_type = torrent_file.mime_type
            response.headers.add("Accept-Ranges", "bytes")
            response.headers.add("Content-Length", str(torrent_file.size))
            response.headers.add("Cache-Control", "no-cache")
            return response

        first_byte = request.http_range.start or 0
        last_byte = (
            request.http_range.stop if request.http_range.stop is not None and
            request.http_range.stop < torrent_file.size else torrent_file.size - 1)
        response = web.StreamResponse(status=206)
        response.content_length = last_byte - first_byte + 1
        response.content_type = torrent_file.mime_type
        response.headers.add("Accept-Ranges", "bytes")
        response.headers.add(
            "Content-Range",
            "bytes %s-%s/%s" % (first_byte, last_byte, torrent_file.size))
        response.headers.add("Cache-Control", "no-cache")

        await response.prepare(request)

        try:
            async for chunk in torrent_file.stream(
                    offset=first_byte, chunk_size=16 * 1024):
                await asyncio.shield(response.write(chunk))
        except BaseException as e:
            print("asyncio socket.send() raised exception: %s" % e)
        finally:
            await response.write_eof()

        return response
