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
    data = {k: v for k, v in url_query.items() if k in ["provider", "infourl"]}
    timeout = int(url_query.get("timeout")) if "timeout" in url_query else 5
    result = await _details(search_engine, data, timeout=timeout)
    return web.json_response(result)


async def _search(search_engine, query, limit=None, timeout=None):
    results = await search_engine.search(query, limit=limit, timeout=timeout)
    return results


async def _details(search_engine, data, timeout=None):
    result = await search_engine.info(data, timeout=timeout)
    return result
