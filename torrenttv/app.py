import os
import sys
import asyncio
import threading
import multiprocessing
from .bittorrent import Session
from .torrentsearchengine import TorrentSearchEngine
from .webapi import WebApplication
from .webviewgui import WebviewGui
from .icon import Icon

_gui_process = None


def run_app(**kwargs):
    global _gui_process  # pylint: disable=global-statement

    def on_open():
        global _gui_process  # pylint: disable=global-statement
        if not _gui_process.is_alive():
            _gui_process = multiprocessing.Process(target=_run_gui, kwargs=kwargs)
            _gui_process.start()

    def on_exit():
        icon.stop()

    title = kwargs.get("title", "TorrentTV")

    try:
        backend_loop = asyncio.new_event_loop()
        backend_queue = asyncio.Queue(loop=backend_loop)
        backend_thread = threading.Thread(
            target=_run_backend, args=(backend_loop, backend_queue), kwargs=kwargs)

        _gui_process = multiprocessing.Process(target=_run_gui, kwargs=kwargs)

        icon = Icon(
            title,
            os.path.join(getattr(sys, '_MEIPASS', ""), "resources/images/icon.png"))
        icon.add_menu_item("Open", on_open)
        icon.add_menu_item("Exit", on_exit)

        backend_thread.start()
        _gui_process.start()
        icon.run()
    finally:
        _gui_process.terminate()
        backend_loop.call_soon_threadsafe(backend_queue.put_nowait, "graceful_shutdown")
        backend_thread.join()
        backend_loop.shutdown_asyncgens()
        backend_loop.close()


def _run_gui(**kwargs):
    title = kwargs.get("title", "TorrentTV")
    host = kwargs.get("host", "localhost")
    port = kwargs.get("port", 8080)

    WebviewGui(title, "http://{}:{}".format(host, port)).open()


def _run_backend(loop: asyncio.AbstractEventLoop, queue: asyncio.Queue, **kwargs):

    async def run_backend_async():
        await session.run()
        await web_app.run(**kwargs)

        is_running = True

        while is_running:
            event = await queue.get()

            if event == "graceful_shutdown":
                await web_app.graceful_shutdown()
                is_running = False

    # set event loop in the thread
    asyncio.set_event_loop(loop)

    session = Session()
    search_engine = TorrentSearchEngine()
    web_app = WebApplication(session, search_engine)

    loop.run_until_complete(run_backend_async())
