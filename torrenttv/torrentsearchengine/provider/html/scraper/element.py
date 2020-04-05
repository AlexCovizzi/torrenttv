from typing import Union, Optional
from bs4 import BeautifulSoup, Tag
from .exceptions import ParseError
from .selector import Selector, NullSelector
from .attribute import Attribute, NullAttribute


class Element:

    def __init__(self, tag: Optional[Tag] = None):
        self.tag = tag

    def select_elements(self, selector: Union[Selector, str], limit: int = 0):
        if not self.tag or not selector:
            return []

        if isinstance(selector, str):
            selector = Selector.parse(selector)

        try:
            tags = self.tag.select(selector.pattern, limit=limit)
        except ValueError:
            tags = []

        elements = [Element(tag) for tag in tags]

        return elements

    def select_one_element(self, selector: Union[Selector, str]):
        if not self.tag or not selector \
           or isinstance(selector, NullSelector):
            return NullElement()

        if isinstance(selector, str):
            selector = Selector.parse(selector)

        try:
            tag = self.tag.select_one(selector.pattern)
        except (ValueError, SyntaxError):
            tag = None

        element = Element(tag) if tag else NullElement()

        return element

    def select(self, selector: Union[Selector, str], limit: int = 0):
        elements = self.select_elements(selector, limit=limit)

        for i in range(len(elements)):
            elements[i] = elements[i].attr(selector.attr)
            if selector.has_re():
                elements[i] = elements[i].re(selector.re, selector.fmt)

        return elements

    def select_one(self, selector: Union[Selector, str]):
        element = self.select_one_element(selector)

        element = element.attr(selector.attr)
        if selector.has_re():
            element = element.re(selector.re, selector.fmt)
        else:
            element = element.to_string()

        return element

    def attr(self, attr: str = 'text') -> Attribute:
        attr = attr.lower()

        if not self.tag:
            return NullAttribute()

        if attr == 'text' or attr == '':
            return Attribute(self.tag.text)

        return Attribute(self.tag.get(attr, ''))

    def to_dict(self) -> dict:
        return {'tag': self.tag}

    def to_string(self) -> dict:
        return str(self.tag)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.__class__.__name__ + str(self.to_dict())

    @staticmethod
    def parse(html: str) -> "Element":
        try:
            tag = BeautifulSoup(html, 'html.parser')
            return Element(tag)
        except ValueError as e:
            raise ParseError(e) from e


class NullElement(Element):

    def __init__(self):
        super(NullElement, self).__init__(None)
