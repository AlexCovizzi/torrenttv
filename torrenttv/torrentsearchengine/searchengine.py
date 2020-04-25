import logging
import asyncio
from torrenttv.utils import stream
from .provider import TorrentProviderLoader, TorrentProvider

logger = logging.getLogger(__name__)


class TorrentSearchEngine:

    def __init__(self, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._provider_loader = TorrentProviderLoader()
        self._providers = {}

    async def search(
        self, query: str, limit: int = 0, providers=None, timeout: int = None
    ):
        """
        Search torrents.

        Parameters:
            query: str - The query to perform.
            limit: int - The number of results to return.
            providers: List[Union[str, TorrentProvider]] - Providers to use.
            timeout: int - The max number of seconds to wait.

        Returns:
            List[Torrent] - The torrents found.
                            Returns an empty list if the query is empty
                            or if no provider is used.
        """

        # an empty query simply returns no torrent (for now?)
        if not query:
            return []

        if providers is None:
            providers = self.get_providers()
        else:
            # get as TorrentProvider
            providers = [
                self._ensure_torrent_provider(provider) for provider in providers
            ]
            providers = [provider for provider in providers if provider is not None]

        n_providers = len(providers)
        if n_providers == 0:
            return []

        results = await asyncio.gather(
            *[
                stream(provider.search(query)).timeout(timeout).collect()
                for provider in providers
            ],
            loop=self._loop
        )

        results = [item for items in results for item in items]

        results = self._sort_by_seeds(results)

        if limit:
            results = results[:limit]

        return results

    async def details(self, item, timeout=None):
        provider_name = item.get("provider")
        provider = self.get_provider(provider_name)
        if not provider:
            return None
        details = await provider.details(item, timeout=timeout)
        return details

    def add_provider(self, provider):
        """
        Add a provider from dict/file/url.

        Raises:
            ValueError - There is an error in a property.
            ValidationError - The resource is incorrect.
            RequestError - The resource could not be retrieve from url.
            IOError - The file could not be read.
        """

        if isinstance(provider, TorrentProvider):
            provider_instance = provider
        else:
            provider_instance = self._provider_loader.load(provider)

        self._providers[provider_instance.name] = provider_instance

        return provider_instance

    def get_providers(self):
        return list(self._providers.values())

    def get_provider(self, name: str):
        return self._providers.get(name, None)

    def remove_provider(self, name: str):
        return self._providers.pop(name, None)

    def _sort_by_seeds(self, items):
        return sorted(items, key=lambda item: item.seeds, reverse=True)

    def _ensure_torrent_provider(self, provider):
        if isinstance(provider, TorrentProvider):
            return provider
        else:
            return self.get_provider(provider)
