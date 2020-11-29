import time
from PIL import Image
import pystray


class Icon:

    def __init__(self, title: str, image: str):
        self._icon = None
        self._title = title
        self._image = self._load_image(image)
        self._menu = []

    def add_menu_item(self, text: str, action):
        self._menu.append(pystray.MenuItem(text, lambda _icon, _item: action()))

    def run(self, on_start=None):
        self._icon = pystray.Icon(self._title, menu=pystray.Menu(*self._menu))
        self._icon.icon = self._image
        self._icon.run(setup=on_start)

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

    def _load_image(self, path: str):
        image = Image.open(path)
        image.thumbnail((128, 128))
        return image
