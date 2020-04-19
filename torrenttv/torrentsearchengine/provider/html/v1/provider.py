import re
import logging
from torrenttv.utils import Uri, fetch
from torrenttv.torrentsearchengine.result import (
    TorrentSearchResult,
    TorrentSearchResultDetails,
)
from torrenttv.torrentsearchengine.provider.provider import (
    ProviderType,
    TorrentProvider,
)
from torrenttv.torrentsearchengine.provider.exceptions import (
    NotSupportedError,
    FormatError,
)
from torrenttv.torrentsearchengine.provider.html.scraper import Element
from .config import Config


logger = logging.getLogger(__name__)


class TorrentProviderHtmlV1(TorrentProvider):
    def __init__(self, config: Config):
        self._config = config

    @property
    def name(self):
        return self._config.name

    @property
    def fullname(self):
        return self._config.fullname

    @property
    def ptype(self):
        return ProviderType.HTML_V1

    async def search(self, query: str, category=None):
        path = self._format_search_path(query, category)

        while path:
            url = Uri(self._config.url, path, scheme="https")

            res = await fetch(url, headers=self._config.headers)

            doc = Element.parse(res.text)

            items = doc.select_elements(self._config.list_selector)
            for item in items:
                search_result_data = self._get_torrent_data(item)
                try:
                    torrent = TorrentSearchResult(**search_result_data)
                    yield torrent
                except ValueError:
                    # the torrent is missing some important properties
                    # in this case we dont return the torrent
                    pass

            if self._config.next_page_selector.pattern:
                path = doc.select_one(self._config.next_page_selector)
            else:
                path = ""

    async def details(self, item, timeout=None):
        """
        Fetch torrent details data (e.g link, description, files, ecc)
        from the Torrent's info_url.

        Parameters:
            torrent: Torrent - The torrent that we want the details of.
            timeout: int - Timeout in seconds.

        Returns:
            dict - Torrent details.

        Raises:
            ParseError - Something went wrong parsing the page received.
            RequestError - Something went wrong requesting the search page.
            Timeout - The search lasted longer than timeout.
        """

        data = item.to_dict() if isinstance(item, TorrentSearchResult) else item
        # retrieve the info page url
        path = data["info_url"]

        if not path:
            # basically we return the same data of the torrent
            return TorrentSearchResultDetails(**data)

        url = Uri(path, scheme="https")

        res = await fetch(url, headers=self._config.headers, timeout=timeout)

        doc = Element.parse(res.text)

        details_data = self._get_torrent_details_data(doc)

        return TorrentSearchResultDetails(**data, **details_data)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "fullname": self.fullname,
            "ptype": self.ptype,
            "config": self._config.to_dict(),
        }

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__class__.__name__ + str(self.to_dict())

    @staticmethod
    def from_dict(data: dict) -> "TorrentProviderHtmlV1":
        config = Config.from_dict(data)
        return TorrentProviderHtmlV1(config)

    def _format_search_path(self, query, category):
        query = query.lower().strip()
        # replace whitespace with whitespace character
        if self._config.whitespace:
            query = re.sub(r"\s+", self._config.whitespace, query)

        if category is None:
            category = "all"
        if category not in self._config.search:
            message = "category '{}' is not supported.".format(category)
            raise NotSupportedError(message)
        else:
            try:
                path = self._config.search.get(category)
                path = path.format(query=query)
            except KeyError as e:
                message = "Can't format {} (query='{}', category='{}')".format(
                    path, query, category
                )
                raise FormatError(message) from e
        return path

    def _get_torrent_data(self, element):
        props = {"provider": self.name}
        for key, selector in self._config.list_item_selectors.items():
            prop = element.select_one(selector)
            props[key] = prop

        # make the url full (with the host)
        url_str = props.get("info_url", "")
        if url_str and not url_str.startswith("http"):
            url = Uri(self._config.url, url_str)
            props["info_url"] = str(url)

        return props

    def _get_torrent_details_data(self, element):
        props = {}
        # retrieve the info page selectors
        for key, selector in self._config.item_selectors.items():
            # for some properties we need to select all elements that match
            if key == "files" or key == "trackers":
                prop = element.select(selector)
            else:
                prop = element.select_one(selector)
            props[key] = prop

        # make the uploader url full (add the host)
        url_str = props.get("uploader_url", None)
        if url_str and not url_str.startswith("http"):
            url = Uri(self._config.url, url_str)
            props["uploader_url"] = str(url)

        return props
