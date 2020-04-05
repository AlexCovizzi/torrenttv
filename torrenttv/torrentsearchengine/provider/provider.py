from .type import ProviderType


class TorrentProvider:
    @property
    def name(self) -> str:
        raise NotImplementedError()

    @property
    def fullname(self) -> str:
        raise NotImplementedError()

    @property
    def ptype(self) -> ProviderType:
        raise NotImplementedError()

    async def search(self, query: str, **kwargs):
        raise NotImplementedError()

    async def details(self, item, **kwargs):
        raise NotImplementedError()
