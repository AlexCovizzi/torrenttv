import socket
import asyncio
import threading
import time
from json import dumps
from aiohttp import web


class Response(web.Response):

    def __init__(self, *, json=None, **kwargs):
        if json is not None:
            text = dumps(json)
            content_type = "application/json"
            kwargs.update(text=text, content_type=content_type)
        super().__init__(**kwargs)


class HandlerBuilder:

    def __init__(self):
        self.response = web.HTTPOk()
        self.delay = 0
        self.path = None
        self.method = None

    def with_response(self, response: web.Response):
        self.response = response
        return self

    def with_delay(self, delay: float):
        self.delay = delay
        return self

    def with_path(self, path: str):
        self.path = path
        return self

    def with_method(self, method: str):
        self.method = method
        return self


class TestHttpServer:

    def __init__(self, host=None, port=None):
        self._host = host or "localhost"
        self._port = port or self._find_free_port()
        self._ready = threading.Semaphore(0)
        self._enqueued = []
        self._thread = None
        self._loop = None
        self._app = None
        self._app_runner = None

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    def start(self):
        self._loop = asyncio.new_event_loop()
        self._app = web.Application(loop=self._loop)
        self._app.add_routes([web.route("*", "/{tail:.*}", self._handle)])
        self._app_runner = web.AppRunner(self._app)
        self._thread = threading.Thread(target=self._run_loop)
        self._thread.daemon = True
        self._thread.start()
        self._ready.acquire()

    def stop(self):
        self._loop.call_soon_threadsafe(self._app_runner.shutdown())
        self._loop.call_soon_threadsafe(self._app_runner.cleanup())
        self._loop.stop()
        self._thread.join()
        self._loop.close()

        self._thread = None
        self._loop = None
        self._app = None
        self._app_runner = None

    def enqueue(self, response: web.Response) -> HandlerBuilder:
        handler_builder = HandlerBuilder().with_response(response)
        self._enqueued.append(handler_builder)
        return handler_builder

    def reset(self):
        self._enqueued = []

    def _handle(self, request: web.Request) -> web.Response:

        def match_path(handler_, request_):
            return handler_.path is None or handler_.path == request_.path

        def match_method(handler_, request_):
            return handler_.method is None or handler_.method == "*" or \
                   str(handler_.method).lower() == str(request_.method).lower()

        matching_handlers = [
            (idx, handler)
            for idx, handler in enumerate(self._enqueued)
            if match_path(handler, request) and match_method(handler, request)
        ]
        if matching_handlers == []:
            raise AssertionError()
        idx, handler = matching_handlers[0]
        self._enqueued.pop(idx)
        if handler.delay is not None and handler.delay > 0:
            time.sleep(handler.delay)
        return handler.response

    def _run_loop(self):
        self._loop.run_until_complete(self._app_runner.setup())
        site = web.TCPSite(self._app_runner, host=self._host, port=self._port)
        self._loop.run_until_complete(site.start())
        self._ready.release()
        self._loop.run_forever()

    def _find_free_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        return port
