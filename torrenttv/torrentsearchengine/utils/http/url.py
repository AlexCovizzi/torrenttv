import re
import urllib


class Url:

    def __init__(self, scheme: str, netloc: str,
                 path: str, qs: str, anchor: str):
        self._scheme = scheme
        self._netloc = netloc
        self._path = path
        self._qs = qs
        self._anchor = anchor

        self._str = urllib.parse.urlunsplit((self.scheme, self.netloc,
                                             self.path, self.qs, self.anchor))

    @property
    def scheme(self):
        return self._scheme

    @property
    def netloc(self):
        return self._netloc

    @property
    def path(self):
        return self._path

    @property
    def qs(self):
        return self._qs

    @property
    def anchor(self):
        return self._anchor

    def to_string(self):
        return self._str

    def to_dict(self):
        return {
            "scheme": self.scheme,
            "netloc": self.netloc,
            "path": self.path,
            "qs": self.qs,
            "anchor": self.anchor
        }

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.__class__.__name__ + str(self.to_dict())

    @staticmethod
    def parse(*chunks, scheme: str = "http"):
        if len(chunks) == 0:
            return ""
        has_trailing_slash = True if chunks[-1].endswith('/') else False
        url = '/'.join([chunk.strip('/') for chunk in chunks])
        url = url + ('/' if has_trailing_slash else '')

        has_scheme = re.match('(?:http:|https:)?//', url)
        if not has_scheme:
            url = scheme + '://' + url
        scheme, netloc, path, qs, anchor = urllib.parse.urlsplit(url)
        path = urllib.parse.quote(path, '/%')
        qs = urllib.parse.quote_plus(qs, ':&=')

        return Url(scheme, netloc, path, qs, anchor)
