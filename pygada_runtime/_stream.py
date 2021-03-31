""":mod:`pygada_runtime` provides common async IO functionalities that might
be useful for any gada nodes written in Python.
"""
__all__ = [
    "StreamBase",
    "BytesIOStream",
    "TextIOStream",
    "async_stream",
    "feed",
    "PipeStream",
    "write_packet",
    "read_packet",
    "write_json",
    "read_json",
]
import io
import os
import asyncio
import functools
import struct
import json
from abc import ABC, abstractmethod


class StreamBase(ABC):
    r"""Base to wrap ``io.IOBase`` subclasses throught a common async interface.

    The builtin Python module ``io`` provides multiple classes derived from ``IOBase``,
    such as ``BytesIO``, ``TextIOBase`` or ``StringIO``, that work in a synchronous way:

    .. code-block:: python

        >>> import sys
        >>>
        >>> def main():
        ...     print(type(sys.stdin))
        ...
        ...     # Will block until reading a newline from stdin
        ...     print(sys.stdin.readline())
        >>>
        >>> # main()
        <class '_io.TextIOWrapper'>
        ..\n
        >>>

    The goal of ``StreamBase`` is to wrap those classes so it becomes possible to
    read input asynchronously:

    .. code-block:: python

        >>> import sys
        >>> import asyncio
        >>> import pygada_runtime
        >>>
        >>> async def main():
        ...     stream = pygada_runtime.TextIOStream(sys.stdin)
        ...
        ...     # readline is now an async task
        ...     print(await stream.readline())
        >>>
        >>> # asyncio.run(main())
        ..\n
        >>>

    For convenience, the :func:`async_stream` method is provided to wrap an
    instance of ``io.IOBase`` to ``StreamBase``:

    .. code-block:: python

        >>> import sys
        >>> import asyncio
        >>> import pygada_runtime
        >>>
        >>> async def main():
        ...     stream = pygada_runtime.async_stream(sys.stdin)
        ...
        ...     # readline is now an async task
        ...     print(await stream.readline())
        >>>
        >>> # asyncio.run(main())
        ..\n
        >>>

    """

    @abstractmethod
    async def read(self, size: int = -1) -> bytes:
        """Read ``size`` bytes or until EOF.

        :param size: number of bytes to read
        :return: byte array
        """
        raise NotImplementedError()

    async def readexactly(self, size: int = -1) -> bytes:
        """Read exactly ``size`` bytes.

        :param size: number of bytes to read
        :return: byte array
        """
        return await self.read(size)

    @abstractmethod
    async def readline(self) -> bytes:
        """Read all bytes until newline character.

        :return: byte array
        """
        raise NotImplementedError()

    @abstractmethod
    def write(self, data: bytes):
        """Write a raw byte array.

        :param data: byte array
        """
        raise NotImplementedError()

    @abstractmethod
    async def drain(self):
        """Drain written data."""
        raise NotImplementedError()

    @abstractmethod
    def eof(self):
        """Close and mark EOF."""
        raise NotImplementedError()

    @abstractmethod
    def close(self):
        """Close inner transport layer."""
        raise NotImplementedError()

    @abstractmethod
    async def wait_closed(self):
        """Wait for the transport layer to be closed."""
        raise NotImplementedError()


class TextIOStream(StreamBase):
    r"""Async wrapper for ``io.TextIOBase``:

    .. code-block:: python

        >>> import io
        >>> import asyncio
        >>> import pygada_runtime
        >>>
        >>> async def main():
        ...     stream = pygada_runtime.TextIOStream(io.StringIO("hello"))
        ...     print(await stream.read())
        >>>
        >>> asyncio.run(main())
        b'hello'
        >>>

    """

    def __init__(self, inner: io.TextIOBase):
        self._inner = inner

    async def read(self, size: int = -1) -> bytes:
        return (
            await asyncio.get_event_loop().run_in_executor(
                None, functools.partial(self._inner.read, size)
            )
        ).encode()

    async def readline(self) -> bytes:
        return (
            await asyncio.get_event_loop().run_in_executor(None, self._inner.readline)
        ).encode()

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


class BytesIOStream(StreamBase):
    r"""Async wrapper for ``io.BytesIO``:

    .. code-block:: python

        >>> import io
        >>> import asyncio
        >>> import pygada_runtime
        >>>
        >>> async def main():
        ...     stream = pygada_runtime.BytesIOStream(io.BytesIO(b'hello'))
        ...     print(await stream.read())
        >>>
        >>> asyncio.run(main())
        b'hello'
        >>>

    """

    def __init__(self, inner: io.BytesIO):
        self._inner = inner

    async def read(self, size: int = -1) -> bytes:
        return await asyncio.get_event_loop().run_in_executor(
            None, functools.partial(self._inner.read, size)
        )

    async def readline(self) -> bytes:
        return await asyncio.get_event_loop().run_in_executor(
            None, self._inner.readline
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


def async_stream(inner) -> StreamBase:
    """Wrap an instance of ``io.IOBase`` throught the common :class:`StreamBase` interface:

    .. code-block:: python

        >>> import io
        >>> import pygada_runtime
        >>>
        >>> type(pygada_runtime.async_stream(io.BytesIO()))
        <class 'pygada_runtime._stream.BytesIOStream'>
        >>> type(pygada_runtime.async_stream(io.StringIO()))
        <class 'pygada_runtime._stream.TextIOStream'>
        >>>

    :param inner: ``io.IOBase`` instance
    :return: wrapped instance
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
    """Feed content of stdin to stdout until EOF:

    .. code-block:: python

        >>> import io
        >>> import asyncio
        >>> import pygada_runtime
        >>>
        >>> async def main():
        ...     stdin = io.BytesIO(b'hello')
        ...     stdout = io.BytesIO()
        ...
        ...     # Feed data from stdin to stdout
        ...     await pygada_runtime.feed(stdin, stdout)
        ...
        ...     # We need to reset current position in stdout
        ...     stdout.seek(0)
        ...
        ...     # Read all data from stdout
        ...     print(stdout.read())
        >>>
        >>> asyncio.run(main())
        b'hello'
        >>>

    :param stdin: input stream
    :param stdout: output stream
    """
    stdin = async_stream(stdin)
    stdout = async_stream(stdout)

    while True:
        line = await stdin.readline()
        if not line:
            stdout.eof()
            return

        stdout.write(line)
        await stdout.drain()


class PipeStream(StreamBase):
    """Pipe allowing both read and write operations on the same stream.

    This is a wrapper for ``os.pipe()`` that makes read operations asynchronous.

    Use ``PipeStream`` as a context so it will be automatically closed afterward:

    .. code-block:: python

        >>> import sys
        >>> import asyncio
        >>> import pygada_runtime
        >>>
        >>> async def main():
        ...     # Pipe will be closed when exiting the context
        ...     with pygada_runtime.PipeStream() as stream:
        ...         # Write some data to writer end
        ...         stream.write(b'hello world')
        ...         # Close the writer end and mark EOF
        ...         stream.eof()
        ...
        ...         # Read data from reader end until EOF
        ...         print(await stream.read())
        >>>
        >>> asyncio.run(main())
        b'hello world'
        >>>

    Or use ``PipeStream`` without a context, but be sure to close it properly afterward:

    .. code-block:: python

        >>> import sys
        >>> import asyncio
        >>> import pygada_runtime
        >>>
        >>> async def main():
        ...     stream = pygada_runtime.PipeStream()
        ...
        ...     # Write some data to writer end
        ...     stream.write(b'hello world')
        ...     # Close the writer end and mark EOF
        ...     stream.eof()
        ...
        ...     # Read data from reader end until EOF
        ...     print(await stream.read())
        ...
        ...     stream.close()
        ...     await stream.wait_closed()
        >>>
        >>> asyncio.run(main())
        b'hello world'
        >>>

    By default, the pipe is opened in binary mode. But you change this behavior by doing:

    .. code-block:: python

        >>> import sys
        >>> import asyncio
        >>> import pygada_runtime
        >>>
        >>> async def main():
        ...     # Open the pipe in text mode
        ...     with pygada_runtime.PipeStream(rmode='r', wmode='w') as stream:
        ...         # Can write text
        ...         stream.write('hello world')
        ...         # Close the writer end and mark EOF
        ...         stream.eof()
        ...
        ...         # Can read text
        ...         print(await stream.read())
        >>>
        >>> asyncio.run(main())
        hello world
        >>>

    """

    def __init__(self, *, rmode:str=None, wmode:str=None, **kwargs):
        """Stream allowing both read and write operations.

        This is a wrapper for ``os.pipe()`` and make read operations
        asynchronous.

        :param rmode: reading mode
        :param wmode: writing mode
        :param kwargs: additional arguments for ``fdopen``
        """
        rmode = rmode if rmode is not None else "rb"
        wmode = wmode if wmode is not None else "wb"

        self._r, self._w = os.pipe()
        self._r, self._w = os.fdopen(self._r, rmode, **kwargs), os.fdopen(self._w, wmode, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    @property
    def reader(self):
        return self._r

    @property
    def writer(self):
        return self._w

    async def read(self, size: int = -1):
        r"""Read ``size`` bytes from the reader end or until EOF:

        .. code-block:: python

            >>> import sys
            >>> import asyncio
            >>> import pygada_runtime
            >>>
            >>> async def main():
            ...     with pygada_runtime.PipeStream() as stream:
            ...         stream.write(b'hello')
            ...         stream.write(b'world')
            ...         # Mark EOF and close the writer end
            ...         stream.eof()
            ...
            ...         # Read the 5 first bytes
            ...         print(await stream.read(size=5))
            ...         # Read until EOF
            ...         print(await stream.read())
            >>>
            >>> asyncio.run(main())
            b'hello'
            b'world'
            >>>

        :return: bytes including the newline character
        """
        # Avoid blocking the main thread
        return await asyncio.get_event_loop().run_in_executor(
            None, functools.partial(self._r.read, size)
        )

    async def readline(self):
        r"""Read bytes from the reader end until newline character:

        .. code-block:: python

            >>> import sys
            >>> import asyncio
            >>> import pygada_runtime
            >>>
            >>> async def main():
            ...     with pygada_runtime.PipeStream() as stream:
            ...         stream.write(b'hello\n')
            ...         stream.write(b'world\n')
            ...         # Mark EOF and close the writer end
            ...         stream.eof()
            ...
            ...         print(await stream.readline())
            ...         print(await stream.readline())
            >>>
            >>> asyncio.run(main())
            b'hello\n'
            b'world\n'
            >>>

        :return: bytes including the newline character
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
            ...         stream.write(b'world')
            ...         # Mark EOF and close the writer end
            ...         stream.eof()
            ...
            ...         print(await stream.read())
            >>>
            >>> asyncio.run(main())
            b'helloworld'
            >>>

        :param data: data to write
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
        r"""Close both ends.

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
    stdout = async_stream(stdout)
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
    stdin = async_stream(stdin)
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
