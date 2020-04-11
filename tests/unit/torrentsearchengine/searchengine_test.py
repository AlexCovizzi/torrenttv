import pytest
import time
import asyncio
from torrenttv.torrentsearchengine import TorrentSearchEngine
from torrenttv.torrentsearchengine import TorrentProvider
from torrenttv.torrentsearchengine import TorrentSearchResult, TorrentSearchResultDetails


class TorrentProviderMock(TorrentProvider):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


def test_get_provider():
    search_engine = TorrentSearchEngine()
    search_engine.add_provider(TorrentProviderMock("test"))
    provider = search_engine.get_provider("test")
    assert provider.name == "test"


def test_get_providers_returns_None():
    search_engine = TorrentSearchEngine()
    provider = search_engine.get_provider("test")
    assert provider is None


def test_get_providers():
    search_engine = TorrentSearchEngine()
    search_engine.add_provider(TorrentProviderMock("test1"))
    search_engine.add_provider(TorrentProviderMock("test2"))
    search_engine.add_provider(TorrentProviderMock("test3"))
    providers = search_engine.get_providers()
    assert "test1" in [provider.name for provider in providers]
    assert "test2" in [provider.name for provider in providers]
    assert "test3" in [provider.name for provider in providers]


def test_get_providers_returns_empty_list():
    search_engine = TorrentSearchEngine()
    providers = search_engine.get_providers()
    assert len(providers) == 0


def test_remove_provider():
    search_engine = TorrentSearchEngine()
    search_engine.add_provider(TorrentProviderMock("test"))
    search_engine.remove_provider("test")
    providers = search_engine.get_providers()
    assert len(providers) == 0


@pytest.mark.asyncio
async def test_search_returns_results(event_loop):
    async def search_mock(self, *args, **kwargs):
        for result in [TorrentSearchResult(provider="test", name="name")] * 4:
            yield result

    search_engine = TorrentSearchEngine(loop=event_loop)
    provider_mock = TorrentProviderMock("test")
    provider_mock.search = search_mock
    search_engine.add_provider(provider_mock)
    results = await search_engine.search("query")
    assert len(results) == 4


@pytest.mark.asyncio
async def test_search_returns_results_yielded_before_timeout(event_loop):
    async def search_mock(self, *args, **kwargs):
        yield TorrentSearchResult(provider="test", name="res1")
        await asyncio.sleep(0.2, loop=event_loop)
        yield TorrentSearchResult(provider="test", name="res2")

    search_engine = TorrentSearchEngine(loop=event_loop)
    provider_mock = TorrentProviderMock("test")
    provider_mock.search = search_mock
    search_engine.add_provider(provider_mock)
    results = await search_engine.search("query", timeout=0.1)

    assert len(results) == 1
    assert results[0].name == "res1"


@pytest.mark.asyncio
async def test_search_returns_nothing(event_loop):
    search_engine = TorrentSearchEngine(loop=event_loop)
    provider_mock = TorrentProviderMock("test")
    search_engine.add_provider(provider_mock)
    results = await search_engine.search("")

    assert len(results) == 0
