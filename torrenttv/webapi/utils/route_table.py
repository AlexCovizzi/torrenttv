from aiohttp import web, hdrs


class RouteTableDef:

    """
    Route definition table
    Note: this is the same as aiohttp.web.RouteTableDef,
          but without decorators
    """
    def __init__(self):
        self._items = []

    def __repr__(self):
        return "<RouteTableDef count={}>".format(len(self._items))

    def __getitem__(self, index):
        return self._items[index]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __contains__(self, item):
        return item in self._items

    def route(self, method, path, handler, **kwargs):
        self._items.append(web.RouteDef(method, path, handler, kwargs))

    def head(self, path, handler, **kwargs):
        return self.route(web.METH_HEAD, path, handler, **kwargs)

    def get(self, path, handler, **kwargs):
        return self.route(hdrs.METH_GET, path, handler, **kwargs)

    def post(self, path, handler, **kwargs):
        return self.route(hdrs.METH_POST, path, handler, **kwargs)

    def put(self, path, handler, **kwargs):
        return self.route(hdrs.METH_PUT, path, handler, **kwargs)

    def patch(self, path, handler, **kwargs):
        return self.route(hdrs.METH_PATCH, path, handler, **kwargs)

    def delete(self, path, handler, **kwargs):
        return self.route(hdrs.METH_DELETE, path, handler, **kwargs)
