__all__ = [
    "PacketTransport",
    "SizeCodec",
    "B64SizeCodec",
    "BinarySizeCodec",
    "NetStringSizeCodec",
]
import base64
import struct
from abc import ABC, abstractmethod
from typing import Any, Optional

_UTF8 = "utf-8"


class SizeCodec(ABC):
    @staticmethod
    @abstractmethod
    async def read(transport):
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    async def write(transport, size):
        raise NotImplementedError()


class BinarySizeCodec(SizeCodec):
    """Binary size codec
    Write/Read size as 4 bytes.
    """

    @staticmethod
    async def read(transport):
        data = await transport.readexactly(4)
        return struct.unpack("<I", data)[0]

    @staticmethod
    async def write(transport, size):
        await transport.write(struct.pack("<I", size))


class B64SizeCodec(SizeCodec):
    """Base64 size codec
    Write/Read size as a base64 encoded string.
    """

    def __init__(self, size_length, *, byteorder=None):
        self._size_length = size_length
        self._byteorder = byteorder or "big"

    async def read(self, transport):
        data = await transport.readexactly(self._size_length)
        return int.from_bytes(base64.b64decode(data), byteorder=self._byteorder)

    async def write(self, transport, size):
        data = size.to_bytes((size.bit_length() + 7) // 8, byteorder=self._byteorder)
        await transport.write(base64.b64encode(data).ljust(self._size_length, b"="))


class NetStringSizeCodec(SizeCodec):
    """NetString size codec
    Write/Read size as string.
    """

    @staticmethod
    async def read(transport):
        data = await transport.readexactly(4)
        size = struct.unpack("<I", data)[0]
        return int((await transport.readexactly(size)).decode(_UTF8))

    @staticmethod
    async def write(transport, size):
        data = str(size).encode(_UTF8)
        await transport.write(struct.pack("<I", len(data)))
        await transport.write(data)


class PacketTransport:
    """
    Transport layer that prefix sent bytes by the length.

    It provide a read function that read exactly the number
    of required bytes.

    If `inner` is provided, this class act as a decorator for it.
    If `inner_type` is provided, it is used to create the `inner`
    instance.

    """

    def __init__(
        self,
        *args: Any,
        size_codec: SizeCodec,
        inner = None,
        inner_type = None,
        **kwargs
    ) -> None:
        self._inner = inner or inner_type(*args, **kwargs)
        self._size_codec = size_codec

    async def read(self):
        size = await self._size_codec.read(self._inner)
        return await self._inner.readexactly(size)

    async def write(self, data):
        await self._size_codec.write(self._inner, len(data))
        await self._inner.write(data)
        await self._inner.drain()

    async def readexactly(self, size):
        return await self._inner.readexactly(size)

    async def drain(self):
        await self._inner.drain()

    def close(self):
        self._inner.close()

    async def wait_closed(self):
        await self._inner.wait_closed()
