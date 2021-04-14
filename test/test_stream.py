import io
import pytest
from pygada_runtime import (
    async_stream,
    feed,
    PipeStream,
    BytesIOStream,
    TextIOStream,
    StreamBase,
)
from pygada_runtime.test_utils import *


def test_wrap():
    """Test wrapping Python ``io`` classes with ``stream.StreamBase``."""
    # Valid types
    assert isinstance(async_stream(io.BytesIO()), BytesIOStream)
    assert isinstance(async_stream(io.TextIOBase()), TextIOStream)
    assert isinstance(async_stream(async_stream(io.TextIOBase())), StreamBase)

    # Invalid type
    with pytest.raises(Exception):
        wrap(1)


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_pipestream():
    """Test writing and reading to the same ``stream.PipeStream``."""
    with PipeStream() as pipe:
        # Write a first line
        pipe.write(b"hello\n")
        await pipe.drain()
        assert (await pipe.readline()) == b"hello\n"

        # Write a second line
        pipe.write(b"world\n")
        await pipe.drain()
        assert (await pipe.readline()) == b"world\n"

        # Write EOF
        pipe.write(b"!")
        pipe.eof()
        assert (await pipe.read()) == b"!"


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_feed():
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
                assert (await stdout.read()) == b"hello"


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_feed_bytes():
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
                assert (await stdout.read()) == b"hello"
