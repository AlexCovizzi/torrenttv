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


class NullTorrentProvider:

    @property
    def name(self) -> str:
        return "null"

    @property
    def fullname(self) -> str:
        return "null"

    @property
    def ptype(self) -> ProviderType:
        return ProviderType.NULL

    async def search(self, *_args, **_kwargs):
        return []

    async def details(self, item, **_kwargs):
        return item
