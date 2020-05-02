import logging
import asyncio
from torrenttv.utils import stream, flatten
from .loader import TorrentSearchProviderLoader

logger = logging.getLogger(__name__)


class TorrentSearchEngine:

    def __init__(self, loop=None, loader=None):
        self._loop = loop or asyncio.get_event_loop()
        self._loader = loader or TorrentSearchProviderLoader()
        self._providers = {}

    async def search(self, query, limit=None, timeout=None):
        providers = self.get_providers()
        results = await asyncio.gather(
            *[
                stream(provider.search(query)).timeout(timeout).collect()
                for provider in providers
            ],
            loop=self._loop)
        results = flatten(results)
        # results = sorted(results, key=lambda item: item.get("seeds", 0), reverse=True)
        results = results[:limit]
        return results

    async def info(self, item, timeout=None):
        provider_name = item.get("provider")
        if not self.has_provider(provider_name):
            return {}
        provider = self.find_provider(provider_name)
        info = await provider.info(item, timeout=timeout)
        return info

    def add_provider(self, src):
        provider = self._loader.load(src)
        self._providers[provider.name] = provider
        return provider

    def get_providers(self):
        return list(self._providers.values())

    def find_provider(self, name):
        return self._providers.get(name, None)

    def has_provider(self, name):
        return name in self._providers

    def remove_provider(self, name):
        return self._providers.pop(name, None)
