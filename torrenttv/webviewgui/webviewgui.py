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
        webview.start(func=self._on_start)

    def close(self):
        try:
            self._window.destroy()
        except KeyError:
            # window is already closed
            pass

    def _on_start(self):
        self._window.loaded.wait()
        self._window.hide()
        self._window.show()
