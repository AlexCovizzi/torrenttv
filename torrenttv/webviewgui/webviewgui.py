import webview


class WebviewGui:

    def __init__(self, title: str, url: str, width: int = 800, height: int = 600):
        self._window = webview.create_window(title, url=url, width=width, height=height)

    def start(self):
        webview.start()

    def destroy(self):
        self._window.destroy()

    def is_closed(self):
        return self._window.closed.is_set()

    def is_closing(self):
        return self._window.closing.is_set()

    def wait_closed(self):
        return self._window.closed.wait()
