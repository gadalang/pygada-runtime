"""Provide functions for async IO.
"""
__all__ = [
    "StreamBase",
    "IOBaseStream",
    "BytesIOStream",
    "TextIOStream",
    "wrap",
    "feed",
    "PipeStream",
    "PacketStream",
    "write_packet",
    "read_packet"
]
import io
import os
import asyncio
import functools
import struct
from abc import ABC, abstractmethod


class StreamBase(ABC):
    """Base to wrap ``IOBase`` subclasses throught a common interface."""

    @abstractmethod
    async def read(self, size: int = -1) -> bytes:
        raise NotImplementedError()

    async def readexactly(self, size: int = -1) -> bytes:
        data = await self.read(size)
        if len(data) != size:
            raise Exception(f"{len(data)} != {size}")
        return data

    @abstractmethod
    def write(self, data):
        raise NotImplementedError()

    @abstractmethod
    async def drain(self):
        raise NotImplementedError()

    @abstractmethod
    def eof(self):
        raise NotImplementedError()

    @abstractmethod
    def close(self):
        """
        Ask to close the connection.

        """
        raise NotImplementedError()

    @abstractmethod
    async def wait_closed(self):
        """
        Return when the connection is fully closed.

        """
        raise NotImplementedError()


class IOBaseStream(StreamBase):
    def __init__(self, inner: io.IOBase):
        """Wrap a ``IOBase`` throught common ``StreamBase`` interface.

        :param inner: IOBase to wrap
        """
        self._inner = inner

    async def readline(self) -> str:
        return await self._inner.readline()

    async def read(self, size: int = -1) -> str:
        raise NotImplementedError()

    def write(self, data):
        raise NotImplementedError()

    async def drain(self):
        raise NotImplementedError()

    def eof(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    async def wait_closed(self):
        raise NotImplementedError()


class TextIOStream(IOBaseStream):
    def __init__(self, inner: io.TextIOBase):
        """Wrap a ``TextIOBase`` throught common ``StreamBase`` interface.

        :param inner: TextIOBase to wrap
        """
        IOBaseStream.__init__(self, inner)

    async def read(self, size: int = -1) -> bytes:
        return (await asyncio.get_event_loop().run_in_executor(
            None, functools.partial(self._inner.read, size)
        )).encode()

    def write(self, data):
        self._inner.write(data.decode(errors="ignore"))

    async def drain(self):
        pass

    def eof(self):
        pass

    def close(self):
        pass

    async def wait_closed(self):
        pass


class BytesIOStream(IOBaseStream):
    def __init__(self, inner: io.BytesIO):
        """Wrap a ``BytesIO`` throught common ``StreamBase`` interface.

        :param inner: BytesIO to wrap
        """
        IOBaseStream.__init__(self, inner)

    async def read(self, size: int = -1) -> bytes:
        return await asyncio.get_event_loop().run_in_executor(
            None, functools.partial(self._inner.read, size)
        )

    def write(self, data):
        self._inner.write(data)

    async def drain(self):
        pass

    def eof(self):
        pass

    def close(self):
        pass

    async def wait_closed(self):
        pass


def wrap(inner) -> StreamBase:
    """Wrap a Python stream throught the common ``StreamBase`` interface.

    :param inner: Python stream
    :return: StreamBase instance
    """
    if isinstance(inner, StreamBase):
        return inner
    if isinstance(inner, io.BytesIO):
        return BytesIOStream(inner)
    if isinstance(inner, io.TextIOBase):
        return TextIOStream(inner)
    if isinstance(inner, asyncio.StreamReader):
        return inner

    raise Exception(
        f"expected an instance of io.BytesIO, io.TextIOBase, asyncio.StreamReader or StreamBase, got {inner.__class__.__name__}"
    )


async def feed(stdin: StreamBase, stdout: StreamBase):
    """Feed content of stdin to stdout until EOF.

    :param stdin: input stream
    :param stdout: output stream
    """
    stdin = wrap(stdin)
    stdout = wrap(stdout)

    while True:
        line = await stdin.readline()
        if not line:
            stdout.eof()
            return

        stdout.write(line)
        await stdout.drain()


class PipeStream(StreamBase):
    def __init__(self):
        """Stream allowing both read and write operations.

        This is a wrapper for ``os.pipe()`` and make read operations
        asynchronous.
        """
        self._r = None
        self._w = None

    def __enter__(self):
        self._r, self._w = os.pipe()
        self._r, self._w = os.fdopen(self._r, "rb"), os.fdopen(self._w, "wb")
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    @property
    def reader(self):
        return self._r

    @property
    def writer(self):
        return self._w

    async def read(self, size: int = -1) -> bytes:
        """Read size bytes from the reader end or until EOF.

        :param size: number of bytes to read
        :return: read bytes
        """
        # Avoid blocking the main thread
        return await asyncio.get_event_loop().run_in_executor(
            None, functools.partial(self._r.read, size)
        )

    async def readline(self) -> bytes:
        """Read data until newline character from the reader end.

        :return: read bytes
        """
        # Avoid blocking the main thread
        return await asyncio.get_event_loop().run_in_executor(None, self._r.readline)

    def write(self, data):
        """Write data in the writer end.

        :param data: bytes to write
        """
        self._w.write(data)

    async def drain(self):
        """Drain data in the writer end."""
        await asyncio.get_event_loop().run_in_executor(None, self._w.flush)

    def close(self):
        """Close both ends."""
        self._close_reader()
        self._close_writer()

    def eof(self):
        """Close the writer end to mark EOF."""
        self._close_writer()

    def _close_reader(self):
        """Close the reader end."""
        if not self._r:
            return

        try:
            os.close(self._r)
        except:
            pass
        self._r = None

    def _close_writer(self):
        """Close the writer end."""
        if not self._w:
            return

        try:
            os.close(self._w)
        except:
            pass
        self._w = None

    async def wait_closed(self):
        """Wait for both ends to be closed."""
        pass


class PacketStream():
    def __init__(self, inner: StreamBase):
        self._inner = wrap(inner)

    async def read(self, size: int = -1) -> bytes:
        data = await self._inner.readexactly(4)
        size = struct.unpack("<I", data)[0]
        return await self._inner.readexactly(size)

    def write(self, data):
        self._inner.write(struct.pack("<I", len(data)))
        self._inner.write(data)

    async def drain(self):
        await self._inner.drain()

    def close(self):
        self._inner.close()

    async def wait_closed(self):
        await self._inner.wait_closed()


async def write_packet(stdout: StreamBase, data: bytes):
    """Write a packet to output stream.
    """
    writer = PacketStream(stdout)
    writer.write(data)
    await writer.drain()


async def read_packet(stdin) -> bytes:
    """Read a packet from input stream.
    """
    reader = PacketStream(stdin)
    return await reader.read()
