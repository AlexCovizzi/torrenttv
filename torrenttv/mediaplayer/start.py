import asyncio
import pywinauto
from torrenttv.utils import async_utils


def start_app(cmd, loop=None, executor=None, **kwargs):
    """
    Start an application and leave control
    """
    loop = loop or asyncio.get_event_loop()
    fut = async_utils.futurize(
        pywinauto_start, args=(cmd,), kwargs=kwargs, loop=loop, executor=executor)
    return fut


def pywinauto_start(cmd, focus_window=True, **kwargs):
    app = pywinauto.application.Application()
    app.start(cmd, **kwargs)
    if focus_window:
        app.window().set_focus()
