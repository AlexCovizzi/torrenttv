from typing import Dict
import jsonschema
from torrenttv.torrentsearchengine.provider.html.scraper import Selector
from .validator import validator


class Config:

    def __init__(self, **kwargs):
        self._name = kwargs.get('name')
        self._fullname = kwargs.get('fullname', self.name)
        self._url = kwargs.get('url')

        self._headers = kwargs.get('headers')
        self._whitespace = kwargs.get('whitespace')
        self._search = kwargs.get('search')
        # convert to dictionary
        self._search = self._search if isinstance(self._search, dict) \
            else {"all": self._search}

        list_section = kwargs.get('list', {})
        list_item_section = list_section.get('item', {})
        item_section = kwargs.get('item', {})

        # parse selectors
        self._next_page_selector = Selector.parse(
            list_section.get('next', ""))
        self._list_selector = Selector.parse(
            list_section.get('items', ""))
        self._list_item_selectors = {key: Selector.parse(sel)
                                     for key, sel in list_item_section.items()}
        self._item_selectors = {key: Selector.parse(sel)
                                for key, sel in item_section.items()}

    @property
    def name(self) -> str:
        return self._name

    @property
    def fullname(self) -> str:
        return self._fullname

    @property
    def url(self) -> str:
        return self._url

    @property
    def search(self) -> Dict[str, str]:
        return self._search

    @property
    def whitespace(self) -> str:
        return self._whitespace

    @property
    def headers(self) -> Dict[str, str]:
        return self._headers

    @property
    def list_selector(self) -> Selector:
        return self._list_selector

    @property
    def list_item_selectors(self) -> Dict[str, Selector]:
        return self._list_item_selectors

    @property
    def item_selectors(self) -> Dict[str, Selector]:
        return self._item_selectors

    @property
    def next_page_selector(self) -> Selector:
        return self._next_page_selector

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "fullname": self.fullname,
            "url": self.url,
            "search": self.search,
            "whitespace": self.whitespace,
            "headers": self.headers,
            "list_selector": self.list_selector,
            "list_item_selectors": self.list_item_selectors,
            "item_selectors": self.item_selectors,
            "next_page_selector": self.next_page_selector
        }

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__class__.__name__ + str(self.to_dict())

    @staticmethod
    def from_dict(data: dict):
        try:
            validator.validate(data)
        except jsonschema.ValidationError as e:
            # raise exceptions.ValidationError(e) from e
            raise e
        return Config(**data)
