import json
from torrenttv.utils import http_utils
from .provider import TorrentSearchProvider
from .config import TorrentSearchProviderConfig


class TorrentSearchProviderLoader:

    def __init__(self):
        pass

    def load(self, src) -> TorrentSearchProvider:
        if isinstance(src, dict):
            return self._load_from_dict(src)
        elif isinstance(src, str):
            if src.startswith('http'):
                return self._load_from_url(src)
            else:
                return self._load_from_file(src)
        raise ValueError("Invalid torrent provider source: " + str(src))

    def _load_from_file(self, path: str) -> TorrentSearchProvider:
        try:
            with open(path, 'r', encoding='utf-8') as _file:
                data = json.load(_file)
        except json.JSONDecodeError as e:
            # raise exceptions.ValidationError(e) from e
            raise e

        return self._load_from_dict(data)

    def _load_from_url(self, url, **kwargs) -> TorrentSearchProvider:
        res = http_utils.fetch(url, **kwargs)
        try:
            data = json.loads(res.text)
        except json.JSONDecodeError as e:
            # raise exceptions.ValidationError(e) from e
            raise e

        return self._load_from_dict(data)

    def _load_from_dict(self, data: dict) -> TorrentSearchProvider:
        config = TorrentSearchProviderConfig(**data)
        provider = TorrentSearchProvider(config)
        return provider
