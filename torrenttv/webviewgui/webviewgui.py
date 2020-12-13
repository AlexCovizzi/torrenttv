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
        webview.start()

    def close(self):
        try:
            self._window.destroy()
        except KeyError:
            # window is already closed
            pass
