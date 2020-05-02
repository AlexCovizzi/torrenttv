from typing import Dict
from torrenttv.typing import Primitive
from torrenttv.utils import Uri
from torrenttv.webcrawler import WebCrawler
from .utils import format_search_path


class TorrentSearchProvider:

    def __init__(self, config, crawler=None):
        self._config = config
        self._crawler = crawler or WebCrawler()

    @property
    def name(self):
        return self._config.name

    @property
    def fullname(self):
        return self._config.fullname

    @property
    def baseurl(self):
        return self._config.baseurl

    async def search(self, query: str):
        path = format_search_path(
            self._config.search, query, whitespace_char=self._config.whitespace)

        while path:
            url = Uri(self._config.baseurl, path, scheme="https")
            document = await self._crawler.fetch(url, headers=self._config.headers)
            element_list = document.select(self._config.list_selector)
            for element in element_list:
                item = {"provider": self.name}
                for key, selector in self._config.item_selectors.items():
                    item[key] = element.extract_one(selector)
                yield item
            path = document.extract_one(self._config.nexturl_selector)

    async def info(self, item: Dict[str, Primitive], timeout=None):
        info = {}
        path = item.get("infourl")
        if not path:
            # no info is returned
            return info
        url = Uri(path, scheme="https")
        document = await self._crawler.fetch(
            url, headers=self._config.headers, timeout=timeout)
        for key, selector in self._config.info_selectors.items():
            info[key] = document.extract_one(selector)
        return info

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "fullname": self.fullname,
            "baseurl": self.baseurl,
            "config": self._config.to_dict()
        }

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__class__.__name__ + str(self.to_dict())
