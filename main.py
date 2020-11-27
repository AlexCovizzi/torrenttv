import sys
import threading
import asyncio
from torrenttv.run_app import run_app
from torrenttv.webviewgui import WebviewGui


def main(*_):
    try:
        loop = asyncio.new_event_loop()
        app_queue = asyncio.Queue(loop=loop)
        app_thread = threading.Thread(target=run_app, args=(app_queue, loop))
        app_thread.start()
        gui = WebviewGui("TorrentTV", "http://localhost:8080")
        gui.start()
    finally:
        if not gui.is_closing() or not gui.is_closed():
            gui.destroy()
        app_queue.put_nowait("graceful_exit")
        gui.wait_closed()
        app_thread.join()


if __name__ == "__main__":
    main(sys.argv)
