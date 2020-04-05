from re import match
import soupsieve


class Selector:

    def __init__(self, pattern: str = '', attr: str = None, re: str = None,
                 fmt: str = None):
        self.pattern = pattern
        self.attr = attr
        self.re = re
        self.fmt = fmt

    def has_attr(self) -> bool:
        return self.attr is not None

    def has_re(self) -> bool:
        return self.re is not None

    def has_fmt(self) -> bool:
        return self.fmt is not None

    def to_string(self) -> str:
        return "{}@{}|re:{}|fmt:{}".format(self.pattern, self.attr,
                                           self.re, self.fmt)

    def to_dict(self) -> dict:
        return {"pattern": self.pattern, "attr": self.attr, "re": self.re,
                "fmt": self.fmt}

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.__class__.__name__ + str(self.to_dict())

    @staticmethod
    def parse(selector: str) -> "Selector":
        """
        <selector pattern>@<attribute> | re: <matcher> | fmt: <formatter>
        """
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

        # parts = selector.split('|')
        parts = [part.strip() for part in parts]

        attr_selector = parts[0] if len(parts) > 0 else ''

        attr_selector_parts = attr_selector.split('@')
        attr_selector_parts = [part.strip() for part in attr_selector_parts]

        patt = attr_selector_parts[0] if len(attr_selector_parts) > 0 else ''
        attr = attr_selector_parts[1] if len(attr_selector_parts) > 1 else None

        regex = None
        fmt = None
        for part in parts[1:]:
            if part.startswith('re:'):
                m = match(r"re:\s*(.*)\s*", part)
                if m:
                    regex = m.group(1).strip()
            elif part.startswith('fmt:'):
                m = match(r"fmt:\s*(.*)\s*", part)
                if m:
                    fmt = m.group(1).strip()

        if patt:
            soupsieve.compile(patt)

        return Selector(patt, attr, regex, fmt)


class NullSelector(Selector):

    def __init__(self):
        super(NullSelector, self).__init__()
