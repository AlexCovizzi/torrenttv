import pytest
import time
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


def test_search_returns_results():
    search_engine = TorrentSearchEngine()
    provider_mock = TorrentProviderMock("test")
    provider_mock.search = (
        lambda self, *args, **kwargs: [SearchResult(provider="test", name="name")] * 4
    )
    search_engine.add_provider(provider_mock)
    results = search_engine.search("query")
    assert len(results) == 4


def test_search_returns_results_yielded_before_timeout():
    def search_mock(self, *args, **kwargs):
        time.sleep(1)
        yield SearchResult(provider="test", name="res1")
        time.sleep(1)
        yield SearchResult(provider="test", name="res2")

    search_engine = TorrentSearchEngine()
    provider_mock = TorrentProviderMock("test")
    provider_mock.search = search_mock
    search_engine.add_provider(provider_mock)
    results = search_engine.search("query", timeout=1)

    assert len(results) == 1
    assert results[0].name == "res1"


def test_search_returns_nothing():
    search_engine = TorrentSearchEngine()
    provider_mock = TorrentProviderMock("test")
    search_engine.add_provider(provider_mock)
    results = search_engine.search("")

    assert len(results) == 0
