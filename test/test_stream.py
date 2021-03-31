__all__ = ["StreamTestCase"]
import io
import unittest
from pygada_runtime import (
    async_stream,
    feed,
    PipeStream,
    BytesIOStream,
    TextIOStream,
    StreamBase,
)
from pygada_runtime.test_utils import *


class StreamTestCase(unittest.TestCase):
    def test_wrap(self):
        """Test wrapping Python ``io`` classes with ``stream.StreamBase``."""
        # Valid types
        self.assertIsInstance(
            async_stream(io.BytesIO()), BytesIOStream, "wrong wrapping"
        )
        self.assertIsInstance(
            async_stream(io.TextIOBase()), TextIOStream, "wrong wrapping"
        )
        self.assertIsInstance(
            async_stream(async_stream(io.TextIOBase())), StreamBase, "wrong wrapping"
        )

        # Invalid type
        with self.assertRaises(Exception):
            wrap(1)

    @async_test
    async def test_pipestream(self):
        """Test writing and reading to the same ``stream.PipeStream``."""
        with PipeStream() as pipe:
            # Write a first line
            pipe.write(b"hello\n")
            await pipe.drain()
            self.assertEqual(await pipe.readline(), b"hello\n")

            # Write a second line
            pipe.write(b"world\n")
            await pipe.drain()
            self.assertEqual(await pipe.readline(), b"world\n")

            # Write EOF
            pipe.write(b"!")
            pipe.eof()
            self.assertEqual(await pipe.read(), b"!")

    @async_test
    async def test_feed(self):
        """Test feeding an input stream to an output stream."""
        # Create stdin and stdout streams
        with PipeStream() as stdout:
            with PipeStream() as stdin:
                # Async feed stdin to stdout
                async with SafeTask(feed(stdin, stdout)):
                    # Write to stdin and mark EOF
                    stdin.write(b"hello")
                    stdin.eof()

                    # Read from stdout until EOF
                    self.assertEqual(await stdout.read(), b"hello")

    @async_test
    async def test_feed_bytes(self):
        """Test feeding an input stream to an output stream."""
        # Create stdin and stdout streams
        with PipeStream() as stdout:
            with PipeStream() as stdin:
                # Async feed stdin to stdout
                async with SafeTask(feed(stdin, stdout)):
                    # Write to stdin and mark EOF
                    stdin.write(b"hello")
                    stdin.eof()

                    # Read from stdout until EOF
                    self.assertEqual(await stdout.read(), b"hello")


if __name__ == "__main__":
    unittest.main()
