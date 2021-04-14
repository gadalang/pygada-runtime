"""Version of hello node using intercom.
"""
import sys
import asyncio
import pygada_runtime


def main(argv, *, stdout=None, **kwargs):
    """Entrypoint used with ``pymodule`` and ``python`` runner."""

    async def _hello(args, intercom, **_):
        data = await pygada_runtime.read_json(intercom.reader)

        pygada_runtime.write_json(intercom.writer, {"hello": data["name"]})
        await intercom.writer.drain()

    parser = pygada_runtime.get_parser("hello", use_intercom=True)
    pygada_runtime.main(_hello, parser=parser, argv=argv)


if __name__ == "__main__":
    main(sys.argv)
