import shlex
import winreg
import subprocess


def play(url, ext=None):
    ext = ext or str(url).split('.')[-1]
    try:
        cmd = get_default_windows_app(ext)
        subprocess.Popen([cmd, url])
    except FileNotFoundError:
        from win32com.client import Dispatch

        mp = Dispatch("WMPlayer.OCX")
        mp.openPlayer(url)


def get_default_windows_app(suffix):
    class_root = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, suffix)
    with winreg.OpenKey(
        winreg.HKEY_CLASSES_ROOT, r'{}\shell\open\command'.format(class_root)
    ) as key:
        command = winreg.QueryValueEx(key, '')[0]
        return shlex.split(command)[0]
