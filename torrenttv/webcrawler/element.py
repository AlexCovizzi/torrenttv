from typing import Optional, Iterable
from bs4 import BeautifulSoup, Tag
from torrenttv.typing import Primitive
from .selector import Selector
from .utils import format_


class Element:

    def __init__(self, tag: Optional[Tag] = None):
        self._tag = tag

    def is_null(self) -> bool:
        return self._tag is None

    def select(self, selector: str, limit: int = 0) -> Iterable["Element"]:
        selector = Selector.compile(selector)
        return self._select(selector, limit)

    def select_one(self, selector: str) -> "Element":
        selector = Selector.compile(selector)
        return self._select_one(selector)

    def extract(self, selector: str, limit: int = 0) -> Iterable[Primitive]:
        selector = Selector.compile(selector)
        return self._extract(selector, limit)

    def extract_one(self, selector: str) -> Primitive:
        selector = Selector.compile(selector)
        return self._extract_one(selector)

    def attr(self, selector: str) -> Primitive:
        selector = Selector.compile(selector)
        return self._attr(selector)

    def to_dict(self) -> dict:
        return {'tag': self._tag}

    def to_string(self) -> str:
        return str(self._tag)

    @staticmethod
    def parse(html: str) -> "Element":
        try:
            tag = BeautifulSoup(html, 'html.parser')
            return Element(tag)
        except ValueError as e:
            raise SyntaxError(e) from e

    @staticmethod
    def null() -> "Element":
        return Element(tag=None)

    def _select(self, selector: Selector, limit: int) -> Iterable["Element"]:
        if not self or not selector:
            return []
        limit = limit if limit > 0 else None
        pattern = selector.pattern
        try:
            tags = self._tag.select(pattern, limit=limit)
        except (ValueError, SyntaxError):
            # TODO: maybe raise error here
            tags = []

        elements = [Element(tag) for tag in tags]

        return elements

    def _select_one(self, selector: Selector) -> "Element":
        if not self or not selector:
            return Element.null()
        pattern = selector.pattern
        try:
            tag = self._tag.select_one(pattern)
            return Element(tag)
        except (ValueError, SyntaxError):
            # TODO: maybe raise error here
            return Element.null()

    def _extract(self, selector: Selector, limit: int = 0) -> Iterable[Primitive]:
        element_list = self._select(selector, limit=limit)
        # pylint: disable=protected-access
        values = [element._attr(selector) for element in element_list]
        return values

    def _extract_one(self, selector: Selector) -> Primitive:
        element = self._select_one(selector)
        # pylint: disable=protected-access
        value = element._attr(selector)
        return value

    def _attr(self, selector: Selector) -> Primitive:
        attr = (selector.attr or "text").lower()
        regx = selector.regx or r"(.*)"
        fmt = selector.fmt
        cvt = (selector.cvt or "str").lower()
        defval = selector.defval

        if not self._tag:
            value = defval
        elif attr == "text":
            value = self._tag.text
        else:
            value = self._tag.get(attr, default=defval)

        value = format_(value, regx, fmt, cvt, defval)
        return value

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.__class__.__name__ + str(self.to_dict())

    def __bool__(self):
        return not self.is_null()
