from typing import Union
import json
from torrenttv.utils import Uri, fetch
from .type import ProviderType
from .provider import TorrentProvider
from .html import TorrentProviderHtmlV1


class TorrentProviderLoader:

    def __init__(self):
        pass

    def load(self, src: Union[dict, str, Uri]) -> TorrentProvider:
        if isinstance(src, dict):
            provider = self.load_from_dict(src)
        elif isinstance(src, Uri):
            provider = self.load_from_url(src)
        elif isinstance(src, str):
            if src.startswith('http'):
                provider = self.load_from_url(src)
            else:
                provider = self.load_from_file(src)
        else:
            raise ValueError()
        return provider

    def load_from_file(self, path: str) -> TorrentProvider:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            # raise exceptions.ValidationError(e) from e
            raise e

        return self.load_from_dict(data)

    def load_from_url(self, url: Union[str, Uri],
                      **kwargs) -> TorrentProvider:
        res = fetch(url, **kwargs)
        try:
            data = json.loads(res.text)
        except json.JSONDecodeError as e:
            # raise exceptions.ValidationError(e) from e
            raise e

        return self.load_from_dict(data)

    def load_from_dict(self, data: dict) -> TorrentProvider:
        ptype_str = data.get('type', "")
        ptype = ProviderType.from_str(ptype_str)
        if ptype == ProviderType.HTML_V1:
            return TorrentProviderHtmlV1.from_dict(data)
        raise NotImplementedError()
