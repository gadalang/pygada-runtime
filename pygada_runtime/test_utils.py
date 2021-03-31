# -*- coding: utf-8 -*-
"""Some utility tools used in tests.
"""
from __future__ import annotations

__all__ = ["SafeTask", "timeout", "async_test", "run"]
import asyncio
from typing import Optional
import pygada_runtime


class SafeTask:
    """Safely run a task:

    .. code-block:: python

        >>> import asyncio
        >>> from pygada_runtime import test_utils
        >>>
        >>> async def worker():
        ...     pass
        >>>
        >>> async def main():
        ...     # Will start and stop "worker" within a context
        ...     async with test_utils.SafeTask(worker()):
        ...         pass
        >>>
        >>> asyncio.run(main())
        >>>

    :param coro: task to run
    """
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
    """Run a function with timeout:

    .. code-block:: python

        >>> import asyncio
        >>> from pygada_runtime import test_utils
        >>>
        >>> @test_utils.timeout
        ... async def main():
        ...     pass
        >>>
        >>> asyncio.run(main())
        >>>

    :return: decorated function result
    """
    async def wrapper(*args, **kwargs):
        return await asyncio.wait_for(fun(*args, **kwargs), timeout=1)

    return wrapper


def async_test(fun):
    """Run an async function:

    .. code-block:: python

        >>> from pygada_runtime import test_utils
        >>>
        >>> @test_utils.async_test
        ... async def main():
        ...     pass
        >>>
        >>> main()
        >>>

    :return: decorated function result
    """
    def wrapper(*args, **kwargs):
        return asyncio.run(fun(*args, **kwargs))

    return wrapper


async def run(node: str, argv: Optional[list[str]] = None) -> tuple[str, str]:
    """Run a gada node and return a tuple ``(stdout, stderr)``:

    .. code-block:: python

        >>> import asyncio
        >>> import pygada_runtime
        >>>
        >>> async def main():
        ...     stdout, stderr = await pygada_runtime.test_utils.run('testnodes.hello', ['john'])
        ...     print(stdout.strip())
        >>>
        >>> asyncio.run(main())
        hello john !
        >>>

    :param node: node to run
    :param argv: CLI arguments
    :return: ``(stdout, stderr)`` tuple
    """
    # Create readable stdout and stderr streams
    with pygada_runtime.PipeStream(rmode="r", wmode="wb") as stdout:
        with pygada_runtime.PipeStream(rmode="r", wmode="wb") as stderr:
            # Run gada node
            proc = await pygada_runtime.run(
                node,
                argv,
                stdout=stdout,
                stderr=stderr,
            )

            # Wait for completion
            await proc.wait()

            stdout.eof()
            stderr.eof()

            return await stdout.read(), await stderr.read()
