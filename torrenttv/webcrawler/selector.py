from typing import Optional
from re import match
from functools import lru_cache
import soupsieve


class Selector:

    def __init__(self, pattern: str, attr: Optional[str], regx: Optional[str],
                 fmt: Optional[str], cvt: Optional[str], defval: Optional[str]):
        self.pattern = pattern
        self.attr = attr
        self.regx = regx
        self.fmt = fmt
        self.cvt = cvt
        self.defval = defval

    def is_null(self):
        return self.pattern == ""

    def has_attr(self) -> bool:
        return self.attr is not None

    def has_regx(self) -> bool:
        return self.regx is not None

    def has_fmt(self) -> bool:
        return self.fmt is not None

    def has_cvt(self) -> bool:
        return self.cvt is not None

    def has_defval(self) -> bool:
        return self.defval is not None

    def to_string(self) -> str:
        s = self.pattern
        if self.has_attr():
            s += "@" + self.attr
        if self.has_regx():
            s += "|regx:" + self.regx
        if self.has_fmt():
            s += "|fmt:" + self.fmt
        if self.has_cvt():
            s += "|cvt:" + self.cvt
        if self.has_defval():
            s += "|defval:" + self.defval
        return s

    def to_dict(self) -> dict:
        return {
            "pattern": self.pattern,
            "attr": self.attr,
            "regx": self.regx,
            "fmt": self.fmt,
            "cvt": self.cvt,
            "defval": self.defval
        }

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.__class__.__name__ + str(self.to_dict())

    def __bool__(self):
        return not self.is_null()

    @staticmethod
    def null() -> "Selector":
        return Selector("", None, None, None, None, None)

    @staticmethod
    @lru_cache()
    def compile(selector: str) -> "Selector":
        parts = [""]
        in_brackets = 0
        last_char = None
        for char in selector:
            if char == '|' and last_char != '\\' and in_brackets == 0:
                parts.append('')
                continue
            if char == '(' and last_char != '\\':
                in_brackets += 1
            elif char == ')' and last_char != '\\':
                in_brackets -= 1
            last_char = char
            parts[-1] += char

        parts = [part.strip() for part in parts]

        attr_selector = parts[0] if len(parts) > 0 else ""

        attr_selector_parts = attr_selector.split('@')
        attr_selector_parts = [part.strip() for part in attr_selector_parts]

        pattern = attr_selector_parts[0] if len(attr_selector_parts) > 0 else ""
        attr = attr_selector_parts[1] if len(attr_selector_parts) > 1 else None

        regx = None
        fmt = None
        cvt = None
        defval = None
        for part in parts[1:]:
            if part.startswith('regx:'):
                matched = match(r"regx:\s*(.*)\s*", part)
                if matched:
                    regx = matched.group(1).strip()
            elif part.startswith('fmt:'):
                matched = match(r"fmt:\s*(.*)\s*", part)
                if matched:
                    fmt = matched.group(1).strip()
            elif part.startswith('cvt:'):
                matched = match(r"cvt:\s*(\w+)\s*", part)
                if matched:
                    cvt = matched.group(1).strip()
            elif part.startswith('defval:'):
                matched = match(r"defval:(.*)\s*", part)
                if matched:
                    defval = matched.group(1).strip()

        if pattern:
            try:
                soupsieve.compile(pattern)
            except soupsieve.SelectorSyntaxError as e:
                raise ValueError("Syntax error: {}".format(e)) from e

        return Selector(pattern, attr, regx, fmt, cvt, defval)
