
class inject:

    @staticmethod
    def app_data(key, _type=None):
        def wrap(fun):
            async def wrapped_fun(*args):
                request = args[0]
                data = request.app.get(key, None)
                if _type and not isinstance(data, _type):
                    raise TypeError()
                return await fun(*args, data)
            return wrapped_fun
        return wrap

    @staticmethod
    def path_param(key):
        def wrap(fun):
            async def wrapped_fun(*args):
                request = args[0]
                param = request.match_info.get(key, None)
                return await fun(*args, param)
            return wrapped_fun
        return wrap
