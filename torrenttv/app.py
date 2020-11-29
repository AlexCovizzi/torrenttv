import os
import sys
import asyncio
import threading
import multiprocessing
import webbrowser
from .bittorrent import Session
from .torrentsearchengine import TorrentSearchEngine
from .webapi import WebApplication
from .webviewgui import WebviewGui
from .icon import Icon


def run_app(**kwargs):
    title = kwargs.get("title", "TorrentTV")
    host = kwargs.get("host", "localhost")
    port = kwargs.get("port", 8080)

    try:
        backend_loop = asyncio.new_event_loop()
        backend_queue = asyncio.Queue(loop=backend_loop)
        backend_thread = threading.Thread(
            target=_run_backend, args=(backend_loop, backend_queue), kwargs=kwargs)

        gui_queue = multiprocessing.Queue()
        gui_process = multiprocessing.Process(target=_run_gui, args=(gui_queue,))

        icon = Icon(
            title,
            os.path.join(getattr(sys, '_MEIPASS', ""), "resources/images/icon.png"))
        icon.add_menu_item("Open", lambda: gui_queue.put("open"))
        icon.add_menu_item("Exit", icon.stop)

        backend_thread.start()
        gui_process.start()
        icon.run()
    finally:
        gui_queue.put("exit")
        backend_loop.call_soon_threadsafe(backend_queue.put_nowait, "graceful_shutdown")
        gui_process.join()
        backend_thread.join()
        backend_loop.shutdown_asyncgens()
        backend_loop.close()


def _run_gui(queue: multiprocessing.Queue):
    title = "TorrentTV"
    host = "localhost"
    port = 8080

    is_running = True

    gui = WebviewGui(title, "http://{}:{}".format(host, port))
    gui.open()

    while is_running:
        event = queue.get()

        if event == "open":
            gui.open()
        elif event == "exit":
            gui.close()
            is_running = False


def _run_backend(loop: asyncio.AbstractEventLoop, queue: asyncio.Queue, **kwargs):
    # set event loop in the thread
    asyncio.set_event_loop(loop)

    session = Session()
    search_engine = TorrentSearchEngine()
    web_app = WebApplication(session, search_engine)

    loop.run_until_complete(
        _run_backend_async(web_app, session, search_engine, queue, **kwargs))


async def _run_backend_async(web_app: WebApplication, session: Session,
                             _search_engine: TorrentSearchEngine, queue: asyncio.Queue,
                             **kwargs):
    await session.run()
    await web_app.run(**kwargs)

    is_running = True

    while is_running:
        event = await queue.get()

        if event == "graceful_shutdown":
            await web_app.graceful_shutdown()
            is_running = False
