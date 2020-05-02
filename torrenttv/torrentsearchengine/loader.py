from typing import Union
import json
from torrenttv.utils import Uri, fetch
from .provider import TorrentSearchProvider
from .config import TorrentSearchProviderConfig


class TorrentSearchProviderLoader:

    def __init__(self):
        pass

    def load(self, src: str) -> TorrentSearchProvider:
        if src.startswith('http'):
            provider = self._load_from_url(src)
        else:
            provider = self._load_from_file(src)
        return provider

    def _load_from_file(self, path: str) -> TorrentSearchProvider:
        try:
            with open(path, 'r', encoding='utf-8') as _file:
                data = json.load(_file)
        except json.JSONDecodeError as e:
            # raise exceptions.ValidationError(e) from e
            raise e

        return self._load_from_dict(data)

    def _load_from_url(self, url: Union[str, Uri], **kwargs) -> TorrentSearchProvider:
        res = fetch(url, **kwargs)
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
