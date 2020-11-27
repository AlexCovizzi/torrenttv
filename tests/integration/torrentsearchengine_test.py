import pytest
from tests.helpers import TestHttpServer, Response, TestData
from torrenttv.torrentsearchengine import TorrentSearchEngine


@pytest.fixture
def provider_server():
    page_1 = TestData("torrentsearchengine/provider_1_search_1.html")
    page_2 = TestData("torrentsearchengine/provider_1_search_2.html")
    page_details = TestData("torrentsearchengine/provider_1_details.html")
    server = TestHttpServer(host="127.0.0.1")
    server.start()
    server.enqueue(Response(text=page_1.read_text(),
                            content_type="text/html")).with_method("GET").with_path(
                                "/search/big-buck-bunny-720p/1")
    server.enqueue(Response(text=page_2.read_text(),
                            content_type="text/html")).with_method("GET").with_path(
                                "/search/big-buck-bunny-720p/2")
    server.enqueue(
        Response(text=page_details.read_text(),
                 content_type="text/html")).with_method("GET").with_path("/torrent/4")
    yield server
    server.stop()


@pytest.mark.asyncio
async def test_search(event_loop, provider_server: TestHttpServer):
    query = "big buck bunny 720p"
    provider = TestData("torrentsearchengine/provider_1.json").read_json()
    provider["baseurl"] = "http://{}:{}".format(provider_server.host,
                                                provider_server.port)
    search_engine = TorrentSearchEngine(loop=event_loop)
    search_engine.add_provider(provider)

    results = await search_engine.search(query)

    assert len(results) == 4
    assert results[0]["name"] == "Big Buck Bunny 720p"
    assert results[1]["name"] == "Big Buck Bunny 720p - Extended Cut"
    assert results[2]["name"] == "Big Buck Bunny - Extended 1080p"
    assert results[3]["name"] == "Another Torrent"


@pytest.mark.asyncio
async def test_details(event_loop, provider_server: TestHttpServer):
    query = "big buck bunny 720p"
    provider = TestData("torrentsearchengine/provider_1.json").read_json()
    provider["baseurl"] = "http://{}:{}".format(provider_server.host,
                                                provider_server.port)
    search_engine = TorrentSearchEngine(loop=event_loop)
    search_engine.add_provider(provider)
    results = await search_engine.search(query)  # Big Buck Bunny - Extended Cut 720p

    details = await search_engine.details(results[1])

    assert details["link"] == "magnet:expected_magnet"
