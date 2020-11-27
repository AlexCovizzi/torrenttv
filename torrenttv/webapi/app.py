import os
import sys
import asyncio
from aiohttp import web
from torrenttv.bittorrent import Session
from torrenttv.torrentsearchengine import TorrentSearchEngine
from torrenttv.mediaplayer import play
from .handlers import SearchHandler, SessionHandler, TorrentsHandler, FilesHandler, WatchHandler


class WebApplication:

    def __init__(self,
                 session: Session,
                 search_engine: TorrentSearchEngine,
                 loop=None,
                 config_path=None):
        self._loop = loop or asyncio.get_event_loop()
        self._config_path = config_path or os.path.join(
            os.path.expanduser("~"), ".torrenttv")
        self._resume_data_path = os.path.join(self._config_path, "resume_data")
        self._app = web.Application(loop=self._loop, middlewares=[])
        self._app_runner = web.AppRunner(self._app)

        # create config directory, if it already exists do nothing
        try:
            os.mkdir(self._config_path)
        except FileExistsError:
            pass

        try:
            os.mkdir(self._resume_data_path)
        except FileExistsError:
            pass

        self._session = session  # TODO: Remove once _play() is sorted out

        self._search_handler = SearchHandler(search_engine)
        self._session_handler = SessionHandler(session)
        self._torrents_handler = TorrentsHandler(session)
        self._files_handler = FilesHandler(session)
        self._watch_handler = WatchHandler(session)

        self._register_routes()

        provider_dir_path = self.resource_path("resources/providers/")
        for provider_file_name in os.listdir(provider_dir_path):
            provider_path = os.path.join(provider_dir_path, provider_file_name)
            search_engine.add_provider(provider_path)

        for resume_data_file_name in os.listdir(self._resume_data_path):
            if not resume_data_file_name.endswith("fastresume"):
                continue
            resume_data_file_path = os.path.join(self._resume_data_path,
                                                 resume_data_file_name)
            self._loop.create_task(session.add_torrent(resume_data_file_path))

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        base_path = getattr(sys, '_MEIPASS', "")
        if not base_path and relative_path == "web/":
            # TODO: improve this logic because at the moment it sucks
            relative_path = "build/web/"
        return os.path.join(base_path, relative_path)

    @property
    def router(self):
        return self._app.router

    async def run(self, **kwargs):
        host = kwargs.get("host", "localhost")
        port = kwargs.get("port", 8080)
        await self._app_runner.setup()
        site = web.TCPSite(self._app_runner, host, port)
        await site.start()

    async def graceful_shutdown(self):
        await self._app_runner.cleanup()

        # remove every fastresume file in the directory
        for resume_data_file_name in os.listdir(self._resume_data_path):
            if not resume_data_file_name.endswith("fastresume"):
                continue
            try:
                resume_data_file_path = os.path.join(self._resume_data_path,
                                                     resume_data_file_name)
                os.unlink(resume_data_file_path)
            except IOError as e:
                print(e)

        # after the web server is stopped, shutdown the session
        await self._session.shutdown(resume_data_path=self._resume_data_path)

    def _register_routes(self):
        self._app.add_routes([
            web.get("/", lambda _: web.HTTPFound("/index.html")),
            # search
            web.get("/api/v1/search", self._search_handler.search),
            web.get("/api/v1/details", self._search_handler.details),
            # session
            web.get("/api/v1/session", self._session_handler.show),
            web.post("/api/v1/session", self._session_handler.update),
            # torrents
            web.get("/api/v1/session/torrents", self._torrents_handler.index),
            web.get("/api/v1/session/torrents/{info_hash}",
                    self._torrents_handler.show),
            web.post("/api/v1/session/torrents", self._torrents_handler.create),
            web.patch("/api/v1/session/torrents/{info_hash}",
                      self._torrents_handler.update),
            web.delete("/api/v1/session/torrents/{info_hash}",
                       self._torrents_handler.destroy),
            # files
            web.get("/api/v1/session/torrents/{info_hash}/files",
                    self._files_handler.index),
            web.get("/api/v1/session/torrents/{info_hash}/files/{file_idx}",
                    self._files_handler.show),
            web.patch("/api/v1/session/torrents/{info_hash}/files/{file_idx}",
                      self._files_handler.update),
            # watch
            web.get("/watch", self._watch_handler.show),
            web.get("/watch/{info_hash}", self._watch_handler.show),
            web.get("/watch/{info_hash}/{file_name}", self._watch_handler.show),
            web.get("/play/{info_hash}/{file_name}", self._play),
            # static
            # always keep static route last
            web.static("/", self.resource_path("web/"))
        ])

    async def _play(self, request):
        info_hash = request.match_info.get("info_hash", "")
        # file_idx = int(req.match_info.get("file_idx")) or 0
        file_name = request.match_info.get("file_name") or ""
        torrent = self._session.get_torrent(info_hash)
        if torrent is None:
            raise web.HTTPNotFound()
        await play("http://localhost:8080/watch/{}/{}".format(info_hash, file_name))
        return web.HTTPOk()
