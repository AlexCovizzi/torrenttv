import asyncio


def futurize(func, args=None, kwargs=None, loop=None, executor=None):
    loop = loop or asyncio.get_event_loop()
    args = args or ()
    kwargs = kwargs or {}
    awaitable = loop.run_in_executor(executor, func, *args, **kwargs)
    return asyncio.ensure_future(awaitable)


def futurize_callback(callback, loop=None):
    loop = loop or asyncio.get_event_loop()

    def func_wrapper(*args, **kwargs):

        def set_result(fut, result):
            if not fut.done():
                fut.set_result(result)

        result = callback(*args, **kwargs)
        loop.call_soon_threadsafe(set_result, fut, result)

    fut = loop.create_future()

    return fut, func_wrapper
