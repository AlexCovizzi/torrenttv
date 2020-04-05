from aiohttp import web


async def search(req):
    search_engine = req.app["data"].torrent_search_engine
    url_query = req.url.query
    query = url_query.get("query", "")
    limit = int(url_query.get("limit")) if "limit" in url_query else None
    timeout = int(url_query.get("timeout")) if "timeout" in url_query else 5
    results = await _search(search_engine, query, limit=limit, timeout=timeout)
    return web.json_response({"list": results})


async def details(req):
    search_engine = req.app["data"].torrent_search_engine
    url_query = req.url.query
    data = {k: v for k, v in url_query.items() if k in ["provider", "info_url"]}
    timeout = int(url_query.get("timeout")) if "timeout" in url_query else 5
    result = await _details(search_engine, data, timeout=timeout)
    return web.json_response(result)


async def _search(search_engine, query, limit=None, timeout=None):
    results = await search_engine.search(query, limit=limit, timeout=timeout)
    return [_to_dict(result) for result in results]


async def _details(search_engine, data, timeout=None):
    result = await search_engine.details(data, timeout=timeout)
    return _to_dict(result)


def _to_dict(result):
    # converts keys from snake_case to camelCase
    def _to_camel_case(s):
        chunks = s.split("_")
        return chunks[0] + "".join(x.title() for x in chunks[1:])

    return {_to_camel_case(k): v for k, v in result.to_dict().items()}
