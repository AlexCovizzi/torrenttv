import webview


class WebviewGui:

    def __init__(self, title: str, url: str, width: int = 800, height: int = 600):
        self._title = title
        self._url = url
        self._width = width
        self._height = height
        self._window = webview.create_window(
            self._title, url=self._url, width=self._width, height=self._height)

    def open(self):
        if len(webview.windows) == 0:
            self._window = webview.create_window(
                self._title, url=self._url, width=self._width, height=self._height)
        webview.start()

    def close(self):
        if not self.is_closed():
            if self.is_closing():
                self.wait_closed()
            else:
                self._window.destroy()
                self.wait_closed()

    def is_closed(self):
        return self._window.closed.is_set()

    def is_closing(self):
        return self._window.closing.is_set()

    def wait_closed(self):
        return self._window.closed.wait()
