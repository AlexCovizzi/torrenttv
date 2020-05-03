import sys
import os

__all__ = ["is_win32", "is_linux", "is_macos", "is_nt", "is_posix"]


def is_win32():
    return sys.platform == "win32"


def is_linux():
    return sys.platform == "linux"


def is_macos():
    return sys.platform == "darwin"


def is_nt():
    return os.name == "nt"


def is_posix():
    return os.name == "posix"
