__all__ = ["IntercomTestCase"]
import io
import unittest
from pygada_runtime import start_intercom, open_intercom, write_json, read_json
from pygada_runtime.test_utils import *


class IntercomTestCase(unittest.TestCase):
    @async_test
    async def test(self):
        """Test communication with intercom module."""
        server = await start_intercom()
        async with server:
            client = await open_intercom(server.port)
            async with client:
                await server.wait_connected()

                write_json(client.writer, {"a": 1})

                self.assertEqual(await read_json(server.reader), {"a": 1})

                write_json(server.writer, {"b": 2})

                self.assertEqual(await read_json(client.reader), {"b": 2})


if __name__ == "__main__":
    unittest.main()
