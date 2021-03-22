import sys
import asyncio
import json
import shlex
from typing import Optional
import argparse
from .transport import StdinTransport, StdoutTransport, PipeTransport
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
        self._transport = PacketTransport(size_codec=BinarySizeCodec, inner=PipeTransport(stdin, stdout))

    def read_json(self):
        try:
            return json.loads(asyncio.get_event_loop().run_until_complete(self._transport.read()).decode())
        except Exception as e:
            print(e)
            return None

    def write_json(self, data, indent=None):
        try:
            asyncio.get_event_loop().run_until_complete(self._transport.write(json.dumps(data, indent=indent).encode()))
            asyncio.get_event_loop().run_until_complete(self._transport.drain())
        except Exception as e:
            print(e)

    def read_bytes(self):
        try:
            return asyncio.get_event_loop().run_until_complete(self._transport.read())
        except Exception as e:
            print(e)
            return None

    def write_bytes(self, data):
        try:
            return asyncio.get_event_loop().run_until_complete(self._transport.write(data))
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
        

def call(argv, *, stdin = None, stdout = None, stderr = None):
    """Run a node with gada.

    :param argv: additional CLI arguments
    :param stdin: input stream (default sys.stdin)
    :param stdout: output stream (default sys.stdout)
    :param stderr: error stream (default sys.stderr)
    """
    argv = argv if argv is not None else []
    stdin = stdin if stdin is not None else sys.stdin
    stdout = stdout if stdout is not None else StdoutTransport(sys.stdout)
    stderr = stderr if stderr is not None else StdoutTransport(sys.stderr)

    async def stream(stdin, stdout):
        """Pipe content of stdin to stdout until EOF.

        :param stdin: input stream
        :param stdout: output stream
        """
        try:
            while True:
                line = await stdin.readline()
                if not line:
                    return

                stdout.write(line)
                await stdout.drain()
        except Exception as e:
            pass

    async def run_subprocess():
        """Run a subprocess."""
        proc = await asyncio.create_subprocess_shell(
            f"gada {' '.join(argv)}",
            stdin=stdin,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        await asyncio.wait(
            [
                asyncio.create_task(stream(proc.stdout, stdout)),
                asyncio.create_task(stream(proc.stderr, stderr)),
                asyncio.create_task(proc.wait()),
            ],
            return_when=asyncio.ALL_COMPLETED,
        )

    asyncio.get_event_loop().run_until_complete(run_subprocess())
