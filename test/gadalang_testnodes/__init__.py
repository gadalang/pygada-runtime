"""Collection of nodes used in unittests.

PYTHONPATH will be automatically set so Python can find this package.
"""
import sys
import asyncio
import pygada_runtime
from pygada_runtime.stream import *
import binaryiotools


def get_parser():
    parser = pygada_runtime.get_parser("sum")
    parser.add_argument("values", type=int, nargs="*", help="values to sum")

    return parser


def _sum(args):
    from functools import reduce

    if args.chain_input:
        # Chain input => receive arguments from stdin
        data = asyncio.get_event_loop().run_until_complete(read_packet(sys.stdin))
        buffer = binaryiotools.IO(data)
        values = [buffer.i32 for _ in range(buffer.i32)]
    else:
        # Take arguments from CLI
        values = args.values

    # Raise if there is only one int
    if len(values) < 2:
        raise Exception("expected at least two int")

    result = reduce(lambda x, y: x + y, [int(_) for _ in values])

    if args.chain_output:
        # Chain output => send result to stdout
        buffer = binaryiotools.IO()
        buffer.i32 = result
        asyncio.get_event_loop().run_until_complete(write_packet(sys.stdout, buffer.data))
    else:
        # Print result to stdout
        print(result)


def sum(argv):
    """Entrypoint used with **pymodule** runner."""
    pygada_runtime.main(_sum, get_parser(), argv)


def main(argv):
    """Entrypoint used with **python** runner."""
    sum(argv=argv)


if __name__ == "__main__":
    main(sys.argv)
