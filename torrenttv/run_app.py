import asyncio
from torrenttv.bittorrent import Session
from torrenttv.torrentsearchengine import TorrentSearchEngine
from torrenttv.webapi import WebApplication


def run_app(queue: asyncio.Queue, loop: asyncio.AbstractEventLoop = None):
    loop = loop or asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    session = Session()
    search_engine = TorrentSearchEngine()
    app = WebApplication(session, search_engine)

    loop.run_until_complete(_run_app(app, session, search_engine, queue))

    loop.shutdown_asyncgens()
    loop.close()


async def _run_app(app: WebApplication, session: Session,
                   _search_engine: TorrentSearchEngine, queue: asyncio.Queue):
    await session.run()
    await app.run()
    while True:
        event = await queue.get()
        if event == "graceful_exit":
            await app.graceful_shutdown()
            break
