import shlex
from .path import get_ext
from .system import is_nt

if is_nt():
    import winreg

__all__ = ["get_default"]


def get_default(file_path):
    file_ext = get_ext(file_path)
    if is_nt():
        class_root = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, file_ext)
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,
                            r'{}\shell\open\command'.format(class_root)) as key:
            command = winreg.QueryValueEx(key, '')[0]
            return shlex.split(command)[0]
    else:
        raise NotImplementedError()
