import urllib


class Uri(str):
    def __new__(
        cls,
        *chunks,
        scheme=None,
        netloc=None,
        path=None,
        qs=None,
        anchor=None,
        urlsafe=False
    ):
        """
        Uri
        """
        scheme, netloc, path, qs, anchor = Uri.parse(
            *chunks,
            scheme=scheme,
            netloc=netloc,
            path=path,
            qs=qs,
            anchor=anchor,
            urlsafe=False
        )
        txt = urllib.parse.urlunsplit((scheme, netloc, path, qs, anchor))
        return super().__new__(cls, txt)

    def __init__(
        self,
        *chunks,
        scheme=None,
        netloc=None,
        path=None,
        qs=None,
        anchor=None,
        urlsafe=False
    ):
        scheme, netloc, path, qs, anchor = Uri.parse(
            *chunks,
            scheme=scheme,
            netloc=netloc,
            path=path,
            qs=qs,
            anchor=anchor,
            urlsafe=False
        )
        self._scheme = scheme
        self._netloc = netloc
        self._path = path
        self._qs = qs
        self._anchor = anchor

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

    def to_dict(self):
        return {
            "scheme": self.scheme,
            "netloc": self.netloc,
            "path": self.path,
            "qs": self.qs,
            "anchor": self.anchor,
        }

    @staticmethod
    def parse(
        *chunks,
        scheme=None,
        netloc=None,
        path=None,
        qs=None,
        anchor=None,
        urlsafe=False
    ):
        # join all chunks
        if len(chunks) == 0:
            uri = ""
        else:
            has_trailing_slash = True if chunks[-1].endswith("/") else False
            uri = "/".join([chunk.strip("/") for chunk in chunks])
            uri = uri + ("/" if has_trailing_slash else "")
        (
            orig_scheme,
            orig_netloc,
            orig_path,
            orig_qs,
            orig_anchor,
        ) = urllib.parse.urlsplit(uri)
        scheme = orig_scheme or scheme or ""
        netloc = orig_netloc or netloc or ""
        path = orig_path or path or ""
        path = path if not path.startswith("/") else path[1:]
        qs = orig_qs or qs or ""
        anchor = orig_anchor or anchor or ""
        if urlsafe or scheme.startswith("http"):
            path = urllib.parse.quote(path, "/%")
            qs = urllib.parse.quote_plus(qs, ":&=")

        return scheme, netloc, path, qs, anchor
