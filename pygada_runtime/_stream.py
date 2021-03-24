""":mod:`pygada_runtime` provides common async IO functionalities that might
be useful for any gada nodes written in Python.
"""
__all__ = [
    "StreamBase",
    "IOBaseStream",
    "BytesIOStream",
    "TextIOStream",
    "wrap",
    "feed",
    "PipeStream",
    "write_packet",
    "read_packet",
    "write_json",
    "read_json"
]
import io
import os
import asyncio
import functools
import struct
import json
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
        r"""Write data to the writer end:

        .. code-block:: python

            >>> import sys
            >>> import asyncio
            >>> import pygada_runtime
            >>>
            >>> async def main():
            ...     with pygada_runtime.PipeStream() as stream:
            ...         stream.write(b'hello')
            ...         await stream.drain()
            ...
            ...         print(await stream.read(size=5))
            >>>
            >>> asyncio.run(main())
            b'hello'
            >>>

        .. note:: Make sure to call this method to flush written data to avoid any
            deadlock when attempting to read from the same pipe

        """
        self._w.write(data)

    async def drain(self):
        r"""Drain data from the writer end:

        .. code-block:: python

            >>> import sys
            >>> import asyncio
            >>> import pygada_runtime
            >>>
            >>> async def main():
            ...     with pygada_runtime.PipeStream() as stream:
            ...         stream.write(b'hello')
            ...         # Drain written data
            ...         await stream.drain()
            ...
            ...         # It is now safe to read data
            ...         print(await stream.read(size=5))
            >>>
            >>> asyncio.run(main())
            b'hello'
            >>>

        .. note:: Make sure to call this method to flush written data to avoid any
            deadlock when attempting to read from the same pipe

        """
        await asyncio.get_event_loop().run_in_executor(None, self._w.flush)

    def close(self):
        """Close both ends."""
        self._close_reader()
        self._close_writer()

    def eof(self):
        r"""Close the writer end to mark EOF:

        .. code-block:: python

            >>> import sys
            >>> import asyncio
            >>> import pygada_runtime
            >>>
            >>> async def main():
            ...     with pygada_runtime.PipeStream() as stream:
            ...         stream.write(b'hello')
            ...         # Mark EOF and close the writer end
            ...         stream.eof()
            ...
            ...         # It if now safe to read until EOF
            ...         print(await stream.read())
            >>>
            >>> asyncio.run(main())
            b'hello'
            >>>

        .. note:: Make sure to call this method to flush written data to avoid any
            deadlock when attempting to read from the same pipe

        """
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
        r"""Wait for the pipe to be closed:

        .. code-block:: python

            >>> import sys
            >>> import asyncio
            >>> import pygada_runtime
            >>>
            >>> async def main():
            ...     stream = pygada_runtime.PipeStream()
            ...     # Do something
            ...
            ...     stream.close()
            ...     await stream.wait_closed()
            >>>
            >>> asyncio.run(main())
            >>>

        """
        pass


def write_packet(stdout: StreamBase, data: bytes) -> None:
    r"""Write a packet to output stream.

    A packet is a single byte array prefixed by the number of bytes:

    .. code-block:: python

        >>> import sys
        >>> import asyncio
        >>> import pygada_runtime
        >>>
        >>> async def main():
        ...     with pygada_runtime.PipeStream() as stream:
        ...         pygada_runtime.write_packet(stream, b'hello')
        ...         pygada_runtime.write_packet(stream, b'world')
        ...         stream.eof()
        ...         
        ...         print(await stream.read())
        >>>
        b'\x05\x00\x00\x00hello\x05\x00\x00\x00world'
        >>>

    .. note:: Packet size is encoded in little-endian

    :param stdout: output stream
    :param data: byte array
    """
    stdout = wrap(stdout)
    stdout.write(struct.pack("<I", len(data)))
    stdout.write(data)


async def read_packet(stdin: StreamBase) -> bytes:
    r"""Read a packet from input stream.

    A packet is a single byte array prefixed by the number of bytes:

    .. code-block:: python

        >>> import sys
        >>> import asyncio
        >>> import pygada_runtime
        >>>
        >>> async def main():
        ...     with pygada_runtime.PipeStream() as stream:
        ...         stream.write(b'\x05\x00\x00\x00hello\x05\x00\x00\x00world')
        ...         await stream.drain()
        ...
        ...         print(await pygada_runtime.read_packet(stream))
        ...         print(await pygada_runtime.read_packet(stream))
        >>>
        >>> asyncio.run(main())
        b'hello'
        b'world'
        >>>

    .. note:: Packet size must be encoded in little-endian

    :param stdin: input stream
    :return: byte array
    """
    stdin = wrap(stdin)
    data = await stdin.readexactly(4)
    size = struct.unpack("<I", data)[0]
    return await stdin.readexactly(size)


def write_json(stdout: StreamBase, data: dict, *args, **kwargs) -> None:
    r"""Write a JSON object to output stream:

    .. code-block:: python

        >>> import sys
        >>> import asyncio
        >>> import pygada_runtime
        >>>
        >>> async def main():
        ...     with pygada_runtime.PipeStream() as stream:
        ...         pygada_runtime.write_json(stream, {"msg": "hello 田中"})
        ...         stream.eof()
        ...         
        ...         print(await stream.read())
        >>>
        >>> asyncio.run(main())
        b'\x1d\x00\x00\x00{"msg": "hello \\u7530\\u4e2d"}'
        >>>

    .. note:: The JSON object is encoded as UTF-8

    :param stdout: output stream
    :param data: JSON object
    :param args: additional positional arguments for ``json.dumps``
    :param kwargs: additional keyword arguments for ``json.dumps``
    """
    write_packet(stdout, json.dumps(data, *args, **kwargs).encode())


async def read_json(stdin: StreamBase, *args, **kwargs) -> dict:
    r"""Read a JSON object from input stream:

    .. code-block:: python

        >>> import sys
        >>> import asyncio
        >>> import pygada_runtime
        >>>
        >>> async def main():
        ...     with pygada_runtime.PipeStream() as stream:
        ...         stream.write(b'\x1d\x00\x00\x00{"msg": "hello \\u7530\\u4e2d"}')
        ...         await stream.drain()
        ...         
        ...         print(await pygada_runtime.read_json(stream))
        >>>
        >>> asyncio.run(main())
        {'msg': 'hello 田中'}
        >>>

    .. note:: The JSON object is decoded as UTF-8

    :param stdin: input stream
    :param args: additional positional arguments for ``json.loads``
    :param kwargs: additional keyword arguments for ``json.loads``
    :return: JSON object
    """
    return json.loads((await read_packet(stdin)).decode(), *args, **kwargs)
