""":mod:`pygada_runtime` provides a way for gada nodes to communicate
with each other via an TCP client/server interface.
"""
__all__ = ["IntercomServer", "IntercomClient", "open_intercom", "start_intercom"]
import asyncio
from typing import Optional, List


class IntercomServer:
    """Don't initialize it directly, use ``start_intercom`` instead."""

    def __init__(self):
        self._server = None
        self._reader = None
        self._writer = None
        self._on_connected = asyncio.Event()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._server.__aexit__(self, *args, **kwargs)

    def _set_server(self, server: asyncio.AbstractServer):
        self._server = server

    async def _handle_client(self, reader, writer):
        self._reader = reader
        self._writer = writer
        self._on_connected.set()

    @property
    def reader(self) -> asyncio.StreamReader:
        """Get reader stream.

        :return: reader stream
        """
        return self._reader

    @property
    def writer(self) -> asyncio.StreamWriter:
        """Get writer stream.

        :return: writer stream
        """
        return self._writer

    @property
    def port(self) -> int:
        """Get opened port.

        :return: port
        """
        return self._server.sockets[0].getsockname()[1]

    async def wait_connected(self):
        """Wait for client to be connected."""
        await self._on_connected.wait()

    def close(self):
        """Close server."""
        self._server.close()

    async def wait_closed(self):
        """Wait for server to be closed."""
        await self._server.wait_closed()


class IntercomClient:
    """Don't initialize it directly, use ``open_intercom`` instead."""

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self._reader = reader
        self._writer = writer

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        self.close()
        await self.wait_closed()

    @property
    def reader(self) -> asyncio.StreamReader:
        """Get reader stream.

        :return: reader stream
        """
        return self._reader

    @property
    def writer(self) -> asyncio.StreamWriter:
        """Get writer stream.

        :return: writer stream
        """
        return self._writer

    def close(self):
        """Close client."""
        self._writer.close()

    async def wait_closed(self):
        """Wait for client to be closed."""
        await self._writer.wait_closed()


async def open_intercom(port: int) -> IntercomClient:
    """Open an intercom connection:

    .. code-block:: python

        >>> import asyncio
        >>> import pygada_runtime
        >>>
        >>> async def main():
        ...     server = await pygada_runtime.start_intercom()
        ...     async with server:
        ...         # Connect to server
        ...         client = await pygada_runtime.open_intercom(server.port)
        ...
        ...         # Do something
        ...
        ...         # Close
        ...         client.close()
        ...         await client.wait_closed()
        >>>
        >>> asyncio.run(main())
        >>>

    Usable as a context:

    .. code-block:: python

        >>> import asyncio
        >>> import pygada_runtime
        >>>
        >>> async def main():
        ...     server = await pygada_runtime.start_intercom()
        ...     async with server:
        ...         client = await pygada_runtime.open_intercom(server.port)
        ...         async with client:
        ...             # Do something
        ...             pass
        >>>
        >>> asyncio.run(main())
        >>>

    :return: intercom client
    """
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    return IntercomClient(reader, writer)


async def start_intercom() -> IntercomServer:
    """Start an intercom server:

    .. code-block:: python

        >>> import asyncio
        >>> import pygada_runtime
        >>> from pygada_runtime import test_utils
        >>>
        >>> async def connect(port):
        ...     await asyncio.sleep(1)
        ...     reader, writer = await asyncio.open_connection("127.0.0.1", port)
        ...     await reader.read()
        >>>
        >>> async def main():
        ...     intercom = await pygada_runtime.start_intercom()
        ...
        ...     # Run async client
        ...     async with test_utils.SafeTask(connect(intercom.port)):
        ...         # Wait for client connection
        ...         await intercom.wait_connected()
        ...
        ...     intercom.close()
        ...     await intercom.wait_closed()
        >>>
        >>> asyncio.run(main())
        >>>

    Usable as a context:

    .. code-block:: python

        >>> import asyncio
        >>> import pygada_runtime
        >>> from pygada_runtime import test_utils
        >>>
        >>> async def connect(port):
        ...     await asyncio.sleep(1)
        ...     reader, writer = await asyncio.open_connection("127.0.0.1", port)
        ...     await reader.read()
        >>>
        >>> async def main():
        ...     intercom = await pygada_runtime.start_intercom()
        ...     async with intercom:
        ...         # Run async client
        ...         async with test_utils.SafeTask(connect(intercom.port)):
        ...             # Wait for client connection
        ...             await intercom.wait_connected()
        >>>
        >>> asyncio.run(main())
        >>>

    :return: intercom server
    """
    intercom = IntercomServer()
    intercom._set_server(
        await asyncio.start_server(intercom._handle_client, host="0.0.0.0", limit=1)
    )
    return intercom
