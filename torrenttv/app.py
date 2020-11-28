import asyncio
import threading
from .bittorrent import Session
from .torrentsearchengine import TorrentSearchEngine
from .webapi import WebApplication
from .webviewgui import WebviewGui


def run_app(**kwargs):
    name = kwargs.get("name", "TorrentTV")
    host = kwargs.get("host", "localhost")
    port = kwargs.get("port", 8080)
    try:
        backend_loop = asyncio.new_event_loop()
        backend_queue = asyncio.Queue(loop=backend_loop)
        backend_thread = threading.Thread(
            target=_run_backend, args=(backend_loop, backend_queue), kwargs=kwargs)
        gui = WebviewGui(name, "http://{}:{}".format(host, port))

        backend_thread.start()
        gui.start()
    finally:
        if not gui.is_closing() or not gui.is_closed():
            gui.destroy()
        backend_loop.call_soon_threadsafe(backend_queue.put_nowait, "graceful_shutdown")
        gui.wait_closed()
        backend_thread.join()
        backend_loop.shutdown_asyncgens()
        backend_loop.close()


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
