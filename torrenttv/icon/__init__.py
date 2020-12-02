import time
import threading
from PIL import Image

# Workaround to make pywebview work when packaging the app
import ctypes  #pylint: disable=wrong-import-order

GetModuleHandleW_argtypes = ctypes.windll.kernel32.GetModuleHandleW.argtypes
GetModuleHandleW_restype = ctypes.windll.kernel32.GetModuleHandleW.restype

import pystray  #pylint: disable=wrong-import-position

pystray._util.win32.GetModuleHandle.argtypes = GetModuleHandleW_argtypes  #pylint: disable=protected-access
pystray._util.win32.GetModuleHandle.restype = GetModuleHandleW_restype  #pylint: disable=protected-access

pystray._util.win32.GetModuleHandle = ctypes.WinDLL('kernel32').GetModuleHandleW  #pylint: disable=protected-access
pystray._util.win32.GetModuleHandle.argtypes = (ctypes.wintypes.LPCWSTR,)  #pylint: disable=protected-access
pystray._util.win32.GetModuleHandle.restype = ctypes.wintypes.HMODULE  #pylint: disable=protected-access
pystray._util.win32.GetModuleHandle.errcheck = pystray._util.win32._err  #pylint: disable=protected-access
# End of workaround


class Icon:

    def __init__(self, title: str, image: str):
        self._icon = None
        self._title = title
        self._image = self._load_image(image)
        self._menu = []

    def add_menu_item(self, text: str, action, default=False):
        self._menu.append(
            pystray.MenuItem(text, lambda _icon, _item: action(), default=default))

    def run(self, on_start=None):
        self._icon = pystray.Icon(self._title, menu=pystray.Menu(*self._menu))
        self._icon.icon = self._image
        # handle on_start here because apparently in pystray it does not work
        threading.Thread(target=self._on_start, args=(on_start,)).start()
        self._icon.run()

    def stop(self):
        self._icon.stop()

    def show_notification(self, text, title=None, duration=None):
        if not self._icon.HAS_NOTIFICATION:
            print("Notifications are not supported")
            return
        self._icon.notify(text, title=title)
        if duration is not None:
            time.sleep(duration)
            self._icon.remove_notification()

    def _on_start(self, on_start=None):
        if on_start:
            while not self._icon._running:
                time.sleep(0.1)
            on_start()

    def _load_image(self, path: str):
        image = Image.open(path)
        image.thumbnail((128, 128))
        return image
