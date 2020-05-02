# pylint: disable=too-many-instance-attributes
class TorrentSearchProviderConfig:

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.fullname = kwargs.get('fullname', self.name)
        self.baseurl = kwargs.get('baseurl')

        self.headers = kwargs.get('headers')
        self.whitespace = kwargs.get('whitespace')
        self.search = kwargs.get('search')

        self.list_selector = kwargs.get("list", "")
        self.nexturl_selector = kwargs.get("nexturl", "")
        self.item_selectors = kwargs.get("item", {})
        self.info_selectors = kwargs.get("info", {})

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "fullname": self.fullname,
            "baseurl": self.baseurl,
            "search": self.search,
            "whitespace": self.whitespace,
            "headers": self.headers,
            "list_selector": self.list_selector,
            "nexturl_selector": self.nexturl_selector,
            "item_selectors": self.item_selectors,
            "info_selectors": self.item_selectors
        }

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__class__.__name__ + str(self.to_dict())
