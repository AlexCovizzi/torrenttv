import os
from .system import is_nt

if is_nt():
    import winreg

__all__ = ["join", "get_ext", "get_home", "get_download"]


def join(*args):
    return os.path.join(*args)


def get_ext(path):
    _, ext = os.path.splitext(path)
    return ext.lower()


def get_home():
    return os.path.expanduser("~")


def get_download():
    if is_nt():
        sub_key = (
            "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders")
        downloads_guid = "{374DE290-123F-4565-9164-39C4925E467B}"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return join(get_home(), "Downloads")
