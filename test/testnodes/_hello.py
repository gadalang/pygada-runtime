"""Version of hello node without using intercom.
"""
import sys
import asyncio
import pygada_runtime


def main(argv, *, stdout=None, **kwargs):
    """Entrypoint used with ``pymodule`` and ``python`` runner."""

    async def _hello(args, **_):
        print(f"hello {args.name} !", file=stdout if stdout is not None else sys.stdout)

    parser = pygada_runtime.get_parser("hello")
    parser.add_argument("name", type=str, help="your name")
    pygada_runtime.main(_hello, parser=parser, argv=argv)


if __name__ == "__main__":
    main(sys.argv)
