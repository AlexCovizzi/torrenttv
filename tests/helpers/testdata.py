from typing import IO, Any
import os
import sys
import json


class TestData:

    def __init__(self, path):
        self._path = path
        self._abs_path = os.path.join(os.path.dirname(__file__), "..", "data", path)
        self._rel_path = os.path.relpath(
            self._abs_path, os.path.dirname(sys.modules['__main__'].__file__))

    @property
    def abs_path(self):
        return self._abs_path

    @property
    def rel_path(self):
        return self._rel_path

    @property
    def path(self):
        return self._path

    def open(self, mode="r") -> IO[Any]:
        return open(self._abs_path, mode=mode)

    def read_json(self) -> dict:
        text = self.read_text()
        return json.loads(text)

    def read_text(self) -> str:
        with self.open(mode="r") as f:
            return f.read()

    def read_bytes(self) -> bytes:
        with self.open(mode="rb") as f:
            return f.read()
