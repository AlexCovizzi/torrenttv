import asyncio
from aiohttp import web
from torrenttv.bittorrent import Session
from torrenttv.torrentsearchengine import TorrentSearchEngine
from .routes import routes


class App:
    def __init__(self, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._app = web.Application(loop=self._loop, middlewares=[])

        self._session = Session(loop=self._loop)
        self._torrent_search_engine = TorrentSearchEngine(loop=self._loop)

        self._torrent_search_engine.add_provider("provider.json")

        self._app["data"] = AppData(self._session, self._torrent_search_engine)

        self._app.router.add_routes(routes)
        self._app.router.add_static("/", "./static/")

    @property
    def router(self):
        return self._app.router

    def run(self, **kwargs):
        self._loop.create_task(self._session.run())
        web.run_app(self._app, **kwargs)


class AppData:

    def __init__(self, session, torrent_search_engine):
        self._session = session
        self._torrent_search_engine = torrent_search_engine

    @property
    def session(self):
        return self._session

    @property
    def torrent_search_engine(self):
        return self._torrent_search_engine
