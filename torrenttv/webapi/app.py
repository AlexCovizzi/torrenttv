import os
import asyncio
from aiohttp import web
from torrenttv.bittorrent import Session
from torrenttv.torrentsearchengine import TorrentSearchEngine
from .routes import routes


class App:
    def __init__(self, loop=None, config_path=None):
        self._loop = loop or asyncio.get_event_loop()
        self._config_path = config_path or os.path.join(
            os.path.expanduser("~"), ".torrenttv"
        )
        self._resume_data_path = os.path.join(self._config_path, "resume_data")
        self._app = web.Application(loop=self._loop, middlewares=[])

        # create config directory, if it already exists do nothing
        try:
            os.mkdir(self._config_path)
        except FileExistsError:
            pass

        try:
            os.mkdir(self._resume_data_path)
        except FileExistsError:
            pass

        self._session = Session(loop=self._loop)
        self._torrent_search_engine = TorrentSearchEngine(loop=self._loop)

        provider_dir_path = "resources/providers/"
        for provider_file_name in os.listdir(provider_dir_path):
            provider_path = os.path.join(provider_dir_path, provider_file_name)
            self._torrent_search_engine.add_provider(provider_path)

        for resume_data_file_name in os.listdir(self._resume_data_path):
            if not resume_data_file_name.endswith("fastresume"):
                continue
            resume_data_file_path = os.path.join(
                self._resume_data_path, resume_data_file_name
            )
            self._loop.create_task(self._session.add_torrent(resume_data_file_path))

        self._app["data"] = AppData(self._session, self._torrent_search_engine)

        self._app.router.add_routes(routes)
        self._app.router.add_static("/", "./static/")

    @property
    def router(self):
        return self._app.router

    def run(self, **kwargs):
        try:
            self._loop.create_task(self._session.run())
            self._loop.run_until_complete(web._run_app(self._app, **kwargs))
        except (web.GracefulExit, KeyboardInterrupt):
            pass
        finally:
            # remove every fastresume file in the directory
            for resume_data_file_name in os.listdir(self._resume_data_path):
                if not resume_data_file_name.endswith("fastresume"):
                    continue
                try:
                    resume_data_file_path = os.path.join(
                        self._resume_data_path, resume_data_file_name
                    )
                    os.unlink(resume_data_file_path)
                except IOError as e:
                    print(e)
            # after the web server is stopped, shutdown the session
            self._loop.run_until_complete(
                self._session.shutdown(resume_data_path=self._resume_data_path)
            )

            web._cancel_all_tasks(self._loop)
            self._loop.shutdown_asyncgens()

            self._loop.close()


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
