from aiohttp import web
from .utils import RouteTableDef
from torrenttv.mediaplayer import play
from .handlers import (
    watch_show,
    session_show,
    session_update,
    torrents_index,
    torrents_show,
    torrents_create,
    torrents_update,
    torrents_destroy,
    torrent_files_index,
    torrent_files_show,
    torrent_files_update,
    search,
    details,
)


async def play_(req):
    session = req.app["data"].session
    info_hash = req.match_info.get("info_hash", "")
    # file_idx = int(req.match_info.get("file_idx")) or 0
    file_name = req.match_info.get("file_name") or ""
    torrent = session.get_torrent(info_hash)
    if torrent is None:
        raise web.HTTPNotFound()
    await play("http://localhost:8080/watch/{}/{}".format(info_hash, file_name))
    return web.HTTPOk()


async def home(req):
    raise web.HTTPFound("/index.html")


routes = RouteTableDef()

routes.get("/", home)

routes.get("/play/{info_hash}/{file_name}", play_)

routes.get("/watch", watch_show)
routes.get("/watch/{info_hash}", watch_show)
routes.get("/watch/{info_hash}/{file_name}", watch_show)

routes.get("/api/v1/session", session_show)
routes.post("/api/v1/session", session_update)

routes.get("/api/v1/session/torrents", torrents_index)
routes.get("/api/v1/session/torrents/{info_hash}", torrents_show)
routes.post("/api/v1/session/torrents", torrents_create)
routes.patch("/api/v1/session/torrents/{info_hash}", torrents_update)
routes.delete("/api/v1/session/torrents/{info_hash}", torrents_destroy)

routes.get("/api/v1/session/torrents/{info_hash}/files", torrent_files_index)
routes.get("/api/v1/session/torrents/{info_hash}/files/{file_idx}", torrent_files_show)
routes.post("/api/v1/session/torrents/{info_hash}/files/{file_idx}",
            torrent_files_update)

# NOTE: the search api needs revising
routes.get("/api/v1/search", search)
routes.get("/api/v1/details", details)
"""
routes.get("/api/v1/search/providers", search_providers_index)
routes.get("/api/v1/search/providers/{name}", search_providers_show)
routes.post("/api/v1/search/providers", search_providers_create)
routes.delete("/api/v1/search/providers/{name}", search_providers_destroy)
"""
