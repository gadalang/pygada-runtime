__all__ = ["SafeTask", "timeout", "async_test"]
import asyncio


class SafeTask:
    def __init__(self, coro):
        self._coro = coro
        self._task = None

    async def __aenter__(self):
        self._task = asyncio.get_event_loop().create_task(self._coro)
        return self._task

    async def __aexit__(self, *args, **kwargs):
        try:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        except:
            pass


def timeout(fun):
    @timeout
    async def wrapper(*args, **kwargs):
        await asyncio.wait_for(fun(*args, **kwargs), timeout=1)

    return wrapper


def async_test(fun):
    def wrapper(*args, **kwargs):
        asyncio.get_event_loop().run_until_complete(fun(*args, **kwargs))

    return wrapper
