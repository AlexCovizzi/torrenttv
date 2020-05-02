from unittest.mock import Mock, call
from torrenttv.utils.event_emitter import EventEmitter


def test_on():
    func = Mock()
    emitter = EventEmitter()

    emitter.on("event", func)

    emitter.emit("event", 1)
    emitter.emit("event", 2)

    func.assert_has_calls([call(1), call(2)])


def test_once():
    func = Mock()
    emitter = EventEmitter()

    emitter.once("event", func)

    emitter.emit("event", 1)
    emitter.emit("event", 2)

    func.assert_called_once_with(1)


def test_emit():
    func = Mock()
    emitter = EventEmitter()
    emitter.on('event', func)

    emitter.emit('event', "arg1", 2)

    func.assert_called_once_with("arg1", 2)


def test_off():
    func1, func2 = Mock(), Mock()

    emitter = EventEmitter()
    emitter.on('event', func1)
    emitter.on('event', func2)

    emitter.off('event', func1)

    emitter.emit("event", "arg")

    func1.assert_not_called()
    func2.assert_called_once_with("arg")


def test_exception():

    def raise_exception():
        raise Exception()

    func1 = Mock(side_effect=raise_exception)
    func2 = Mock()

    emitter = EventEmitter()
    emitter.on("event", func1)
    emitter.on("event", func2)

    emitter.emit("event", "arg")

    func2.assert_called_once_with("arg")
