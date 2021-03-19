import asyncio
import json
from typing import Optional
import argparse
from .transport import StdinTransport
from .packet import PacketTransport, BinarySizeCodec


class Transport():
    def __init__(self, reader, writer):
        self._reader = reader
        self._writer = writer

    def close(self):
        self._writer.close()

    async def wait_closed(self):
        await self._writer.wait_closed()


class Interface():
    def __init__(in_port: int, out_port: int) -> None:
        self._in_port = in_port
        self._out_port = out_port
        self._in: Transport = None
        self._out: Transport = None

    async def __aenter__(self):
        # Input stream
        reader, writer = await asyncio.open_connection('127.0.0.1', in_port)
        self._in = Transport(reader, writer)

        # Output stream
        reader, writer = await asyncio.open_connection('127.0.0.1', out_port)
        self._out = Transport(reader, writer)

    async def __aexit__(self, *args, **kwargs):
        # Close input and output stream
        self._in.close()
        self._out.close()
        await self._in.wait_closed()
        await self._out.wait_closed()


class BinaryStream():
    def __init__(self, stdin, stdout):
        self._transport = PacketTransport(size_codec=BinarySizeCodec, inner=StdinTransport(stdin, stdout))

    def read_json(self):
        try:
            return json.loads(asyncio.get_event_loop().run_until_complete(self._transport.read()).decode())
        except Exception as e:
            print(e)
            return None

    def write_json(self, data, indent=None):
        try:
            return asyncio.get_event_loop().run_until_complete(self._transport.write(json.dumps(data, indent=indent).encode()))
        except Exception as e:
            print(e)


def get_parser(prog: Optional[str] = None) -> argparse.ArgumentParser:
    import argparse

    parser = argparse.ArgumentParser(prog)
    parser.add_argument("--chain-input", action="store_true", help="read input from stdin")
    parser.add_argument("--chain-output", action="store_true", help="write output to stdout")
    return parser


def main(run, parser: argparse.ArgumentParser, argv=None):
    """Call this function from the main entrypoint of your component.

    :param parser: argument parser
    :param argv: command line arguments for standalone version
    :param run_component: called when run from another component
    :param run_standalone: called when run standalone
    """
    import sys

    argv = argv if argv is not None else sys.argv

    args = parser.parse_args(argv[1:])
    run(args)
        
