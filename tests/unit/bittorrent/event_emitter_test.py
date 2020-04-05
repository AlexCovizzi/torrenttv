import pytest
import asyncio
from torrenttv.bittorrent.event_emitter import EventEmitter


class FuncMock:

    def __init__(self, func=None):
        self.func = func
        self.called = 0
        self._calls = []

    def __call__(self, *args, **kwargs):
        ret = None
        if self.func is not None:
            ret = self.func(*args, **kwargs)
        self.called += 1
        self._calls.append({'args': args, 'kwargs': kwargs})
        return ret

    def has_been_called(self, times=None):
        if times is None:
            assert self.called > 0
        else:
            assert self.called == times

    def has_been_called_with_args(self, call_idx, *args, **kwargs):
        assert self._calls[call_idx]['args'] == args and \
            self._calls[call_idx]['kwargs'] == kwargs


def test_on():
    func1 = FuncMock()
    func2 = FuncMock()
    emitter = EventEmitter()
    emitter.on('event', func1)
    emitter.on('event', func2)
    listeners = emitter.listeners('event')
    assert len(listeners) == 2
    assert listeners[0].func == func1
    assert listeners[1].func == func2


def test_emit():
    func = FuncMock()
    emitter = EventEmitter()
    emitter.on('event', func)
    emitter.emit('event', "arg1", 2)

    func.has_been_called(times=1)
    func.has_been_called_with_args(0, "arg1", 2)


def test_off():
    func1 = FuncMock()
    func2 = FuncMock()
    func3 = FuncMock()
    emitter = EventEmitter()
    emitter.on('event', func1)
    emitter.on('event', func2)
    emitter.off('event', func1)
    emitter.off('event', func2)
    emitter.off('event', func3)  # not a listener
    listeners = emitter.listeners('event')

    assert len(listeners) == 0


def test_once():
    func = FuncMock()
    emitter = EventEmitter()
    emitter.once('event', func)
    emitter.emit('event', "arg1", 2)

    func.has_been_called(times=1)
    func.has_been_called_with_args(0, "arg1", 2)
    assert len(emitter.listeners('event')) == 0


def test_emit_does_not_block_on_listener_exception():
    def func1_impl():
        raise Exception()

    func1 = FuncMock(func=lambda _: func1_impl())
    func2 = FuncMock()

    emitter = EventEmitter()
    emitter.on('event', func1)
    emitter.on('event', func2)

    emitter.emit('event', "arg")

    func2.has_been_called(times=1)


@pytest.mark.asyncio
async def test_async_event(event_loop):
    emitter = EventEmitter()
    event_loop.call_later(0.1, emitter.emit, "event", "arg", 2)
    ret = await emitter.event('event', loop=event_loop)

    assert ret == ("arg", 2)
    assert len(emitter.listeners('event')) == 0


@pytest.mark.asyncio
async def test_async_event_cancelled(event_loop):
    emitter = EventEmitter()

    fut = asyncio.ensure_future(emitter.event('event', loop=event_loop),
                                loop=event_loop)

    event_loop.call_later(0.1, fut.cancel)

    with pytest.raises(asyncio.CancelledError):
        await fut

    assert len(emitter.listeners('event')) == 0
