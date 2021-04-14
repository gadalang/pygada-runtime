import io
import pytest
from pygada_runtime import start_intercom, open_intercom, write_json, read_json
from pygada_runtime.test_utils import *


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test():
    """Test communication with intercom module."""
    server = await start_intercom()
    async with server:
        client = await open_intercom(server.port)
        async with client:
            await server.wait_connected()

            write_json(client.writer, {"a": 1})

            assert (await read_json(server.reader)) == {"a": 1}

            write_json(server.writer, {"b": 2})

            assert (await read_json(client.reader)) == {"b": 2}
