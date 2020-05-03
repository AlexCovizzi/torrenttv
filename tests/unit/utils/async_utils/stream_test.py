import asyncio
from unittest.mock import Mock, call
import pytest
from torrenttv.utils.async_utils.stream import AsyncStream


async def generator(items, sleep=0, loop=None):
    for item in items:
        yield item
        await asyncio.sleep(sleep, loop=loop)


async def assert_stream_equals_exactly(iterable, expected_items):
    actual_items = []
    async for item in iterable:
        actual_items.append(item)
    assert expected_items == actual_items


@pytest.mark.asyncio
async def test_collect(event_loop):
    stream = AsyncStream(generator([1, 2, 3], loop=event_loop))
    items = await stream.collect()
    assert items == [1, 2, 3]


@pytest.mark.asyncio
async def test_map(event_loop):
    stream = AsyncStream(generator([1, 2, 3], loop=event_loop))
    stream = stream.map(lambda i: i * 2)

    await assert_stream_equals_exactly(stream, [2, 4, 6])


@pytest.mark.asyncio
async def test_for_each(event_loop):
    func = Mock()

    stream = AsyncStream(generator([1, 2, 3], loop=event_loop))
    stream = stream.for_each(func)

    await assert_stream_equals_exactly(stream, [1, 2, 3])
    func.assert_has_calls([call(1), call(2), call(3)])


@pytest.mark.asyncio
async def test_timeout(event_loop):
    stream = AsyncStream(generator([1, 2, 3], sleep=0.1, loop=event_loop))
    stream = stream.timeout(0.15)

    await assert_stream_equals_exactly(stream, [1, 2])


@pytest.mark.asyncio
async def test_timeout_raise_err(event_loop):
    stream = AsyncStream(generator([1, 2, 3], sleep=0.1, loop=event_loop))
    stream = stream.timeout(0.15, raise_err=True)

    with pytest.raises(asyncio.TimeoutError):
        await assert_stream_equals_exactly(stream, [1, 2])


@pytest.mark.asyncio
async def test_capture(event_loop):

    async def generator_with_exception(exc):
        yield 1
        raise exc

    func = Mock()
    exc = Exception("exception")

    stream = AsyncStream(generator_with_exception(exc))
    stream = stream.capture(Exception, func)

    await assert_stream_equals_exactly(stream, [1])
    func.assert_called_once_with(exc)
