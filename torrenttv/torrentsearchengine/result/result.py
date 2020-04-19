
class TorrentSearchResult:

    def __init__(self, **kwargs):
        """
        Parameters:
            provider: str - The nae of the provider.
            name: str - The name of this torrent.
            url: str - The info page path of this torrent.
            size: str - The size of this torrent.
            seeds: int - The number of seeders.
            leeches: int - The number of leeches.
        """
        self._data = kwargs

        self._provider = self._data.pop('provider')
        self._name = self._data.pop('name', "")
        self._info_url = self._data.pop('info_url', "")
        self._size = self._data.pop('size', "")
        self._seeds = self._data.pop('seeds', -1)
        self._leeches = self._data.pop('leeches', -1)
        self._link = self._data.pop('link', "")

        # convert seeds and leeches to int
        try:
            self._seeds = int(self._seeds)
        except Exception:
            self._seeds = -1
        try:
            self._leeches = int(self._leeches)
        except Exception:
            self._leeches = -1

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def name(self) -> str:
        return self._name

    @property
    def info_url(self) -> str:
        return self._info_url

    @property
    def size(self) -> str:
        return self._size

    @property
    def seeds(self) -> int:
        return self._seeds

    @property
    def leeches(self) -> int:
        return self._leeches

    @property
    def link(self) -> str:
        return self._link

    def get(self, key: str, default):
        if key == 'provider':
            return self.provider
        elif key == 'name':
            return self.name
        elif key == 'info_url':
            return self.info_url
        elif key == 'size':
            return self.size
        elif key == 'seeds':
            return self.seeds
        elif key == 'leeches':
            return self.leeches
        else:
            return self._data.get(key, default)

    def to_dict(self) -> dict:
        return {
            'provider': self.provider,
            'name': self.name,
            'info_url': self.info_url,
            'size': self.size,
            'seeds': self.seeds,
            'leeches': self.leeches,
            'link': self.link,
            **self._data
        }

    def to_string(self) -> str:
        return self.name

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.__class__.__name__ + str(self.to_dict())
