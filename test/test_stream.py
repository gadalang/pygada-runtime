__all__ = ["StreamTestCase"]
import os
import sys
import io
import asyncio
import unittest
from pygada_runtime.stream import *
import aiopipe


class SafeTask():
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


class StreamTestCase(unittest.TestCase):
    def test_wrap(self):
        # Valid types
        self.assertIsInstance(wrap(io.BytesIO()), BytesIOStream, "wrong wrapping")
        self.assertIsInstance(wrap(io.TextIOBase()), TextIOStream, "wrong wrapping")
        self.assertIsInstance(wrap(wrap(io.TextIOBase())), StreamBase, "wrong wrapping")

        # Invalid type
        with self.assertRaises(Exception):
            wrap(1)

    def test_feed(self):
        async def work():
            # Create stdin and stdout streams
            with PipeStream() as stdout:
                with PipeStream() as stdin:
                    # Write a single line to stdin
                    stdin.write(b"hello\n")
                    await stdin.drain()

                    # Feed stdin to stdout
                    async with SafeTask(feed(stdin, stdout)):
                        # Read a single line from stdout
                        self.assertEqual(await stdout.readline(), b"hello\n", "invalid value")

                        # Write a second line to stdin
                        stdin.write(b"world\n")
                        await stdin.drain()

                        # Read a single line from stdout
                        self.assertEqual(await stdout.readline(), b"world\n", "invalid value")


        asyncio.get_event_loop().run_until_complete(work())

    def test_feed_eof(self):
        async def work():
            # Create stdin and stdout streams
            with PipeStream() as stdout:
                with PipeStream() as stdin:
                    # Write a single line to stdin
                    stdin.write(b"hello")
                    await stdin.drain()

                    # Mark EOF so stdin.read() doesn't block
                    stdin.eof()

                    # Feed stdin to stdout
                    await feed(stdin, stdout)

                    # Mark EOF so stdout.read() doesn't block
                    stdout.eof()

                    # Read a single line from stdout
                    self.assertEqual(await stdout.read(), b"hello", "invalid value")


        asyncio.get_event_loop().run_until_complete(work())


if __name__ == "__main__":
    unittest.main()
