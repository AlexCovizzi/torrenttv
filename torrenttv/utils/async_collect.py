import asyncio


async def async_collect(generator, loop=None, timeout=None):
    loop = loop or asyncio.get_event_loop()
    items = []

    async def _collect(generator, items):
        async for item in generator:
            items.append(item)

    if timeout and timeout > 0:
        try:
            await asyncio.wait_for(_collect(generator, items), timeout, loop=loop)
        except asyncio.TimeoutError:
            pass
        except BaseException as e:
            print("Error: {}".format(e))
    else:
        await _collect(generator, items)
    return items
