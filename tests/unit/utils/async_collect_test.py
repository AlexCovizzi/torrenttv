import pytest
import asyncio
from torrenttv.utils import async_collect


async def generator(items, sleep=0, loop=None):
    for item in items:
        yield item
        await asyncio.sleep(sleep, loop=loop)


@pytest.mark.asyncio
async def test_async_collect(event_loop):
    items = await async_collect(generator([1, 2, 3], loop=event_loop))
    assert items == [1, 2, 3]


@pytest.mark.asyncio
async def test_async_collect_timeout(event_loop):
    fut = async_collect(
        generator([1, 2, 3], sleep=0.1, loop=event_loop), timeout=0.15, loop=event_loop
    )

    items = await fut

    assert items == [1, 2]
