from .result import TorrentSearchResult


class TorrentSearchResultDetails(TorrentSearchResult):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._time = self._data.pop("time", "")
        self._files = self._data.pop("files", [])
        self._infohash = self._data.pop("infohash", "")
        self._description = self._data.pop("description", "")
        self._uploader = self._data.pop("uploader", "")
        self._uploader_url = self._data.pop("uploader_url", "")
        self._trackers = self._data.pop("trackers", [])

    @property
    def time(self) -> str:
        return self._time

    @property
    def files(self) -> list:
        return self._files

    @property
    def infohash(self) -> str:
        return self._infohash

    @property
    def description(self) -> str:
        return self._description

    @property
    def uploader(self) -> str:
        return self._uploader

    @property
    def uploader_url(self) -> str:
        return self._uploader_url

    @property
    def trackers(self) -> list:
        return self._trackers

    def to_dict(self):
        data = super().to_dict()
        return {
            **data,
            "time": self.time,
            "files": self.files,
            "infohash": self.infohash,
            "description": self.infohash,
            "uploader": self.uploader,
            "uploader_url": self.uploader_url,
            "trackers": self.trackers,
        }

    @staticmethod
    def extend(torrent: TorrentSearchResult, **kwargs) -> "TorrentSearchResultDetails":
        kwargs = {**torrent.to_dict(), **kwargs}
        return TorrentSearchResultDetails(**kwargs)
