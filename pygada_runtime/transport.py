__all__ = ["AbstractTransport", "StdinTransport"]
from abc import ABC, abstractmethod


class AbstractTransport(ABC):
    """
    Base to wrap a transport layer as a byte stream.

    """

    @abstractmethod
    async def readexactly(self, size):
        raise NotImplementedError()

    @abstractmethod
    async def write(self, data):
        raise NotImplementedError()

    @abstractmethod
    async def drain(self):
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


class StdinTransport(AbstractTransport):
    def __init__(self, stdin, stdout):
        self._stdin = stdin
        self._stdout = stdout

    async def readexactly(self, size):
        return self._stdin.buffer.read(size)

    async def write(self, data):
        self._stdout.buffer.write(data)

    async def drain(self):
        pass

    def close(self):
        pass

    async def wait_closed(self):
        pass
