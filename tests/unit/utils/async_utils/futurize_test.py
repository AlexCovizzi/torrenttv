import time
import threading
from unittest.mock import Mock
import pytest
from torrenttv.utils.async_utils.futurize import futurize_callback


def run_in_thread(func, delay=0):
    time.sleep(delay)
    threading.Thread(target=func).start()


@pytest.mark.asyncio
async def test_callback_called(event_loop):
    func = Mock()

    fut, func_wrap = futurize_callback(func, loop=event_loop)

    run_in_thread(lambda: func_wrap(1, "arg"), delay=0.1)

    await fut

    func.assert_called_once_with(1, "arg")


@pytest.mark.asyncio
async def test_future_result(event_loop):
    func = Mock(return_value="result")

    fut, func_wrap = futurize_callback(func, loop=event_loop)

    run_in_thread(func_wrap, delay=0.1)

    result = await fut

    assert result == "result"
