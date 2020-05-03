import asyncio
from torrenttv.utils import compat_utils, http_utils
from .start import start_app


class MediaPlayer:

    def __init__(self, cmd=None, loop=None):
        self._cmd = cmd
        self._loop = loop or asyncio.get_event_loop()

    async def start(self, path, **kwargs):
        if self._cmd is None:
            cmd = self._find_best_player(path)
        else:
            cmd = self._cmd
        fullcmd = self._format(cmd, path)
        await start_app(fullcmd, loop=self._loop, **kwargs)

    def _find_best_player(self, path):
        try:
            return compat_utils.cmd.get_default(path)
        except FileNotFoundError:
            """
            from win32com.client import Dispatch

            mp = Dispatch("WMPlayer.OCX")
            mp.openPlayer(url)
            """
            return "C:\\Program Files\\Windows Media Player\\wmplayer.exe"

    def _format(self, cmd, path):
        if "{path}" not in cmd:
            cmd = cmd + " \"{path}\""
        path = http_utils.Uri(path)
        return cmd.format(path=path)
