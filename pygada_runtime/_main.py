__all__ = ["get_parser", "main"]
import sys
import asyncio
import argparse
from typing import Optional, List
from ._intercom import open_intercom


def get_parser(
    prog: Optional[str] = None, *, use_intercom: Optional[bool] = None
) -> argparse.ArgumentParser:
    """Get a default configured ``argparse.ArgumentParser`` for parsing
    command line arguments passed to your gada node:

    .. code-block:: python

        >>> import pygada_runtime
        >>>
        >>> parser = pygada_runtime.get_parser("mynode", use_intercom=True)
        >>> parser.print_help()
        usage: mynode [-h] [--intercom-port INTERCOM_PORT]
        <BLANKLINE>
        optional arguments:
          -h, --help            show this help message and exit
          --intercom-port INTERCOM_PORT
                                port for node intercom
        >>>

    :param use_intercom: use intercom communication
    """
    parser = argparse.ArgumentParser(prog)
    if use_intercom:
        parser.add_argument("--intercom-port", type=int, help="port for node intercom")
    return parser


def main(
    run,
    *,
    parser: Optional[argparse.ArgumentParser] = None,
    argv: Optional[List] = None,
    use_intercom: Optional[bool] = None
):
    r"""Call this function from the main entrypoint of your component:

    .. code-block:: python

        >>> import pygada_runtime
        >>>
        >>> async def foo(args, **_):
        ...     print(args.values)
        >>>
        >>> parser = pygada_runtime.get_parser("foo", use_intercom=True)
        >>> parser.add_argument("values", type=str, nargs="*", help="some values")
        _StoreAction(option_strings=[], dest='values', nargs='*', const=None, default=None, type=<class 'str'>, choices=None, help='some values', metavar=None)
        >>> parser.print_help()
        usage: foo [-h] [--intercom-port INTERCOM_PORT] [values ...]
        <BLANKLINE>
        positional arguments:
          values                some values
        <BLANKLINE>
        optional arguments:
          -h, --help            show this help message and exit
          --intercom-port INTERCOM_PORT
                                port for node intercom
        >>> pygada_runtime.main(foo, parser=parser, argv=['foo', 'a', 'b'])
        ['a', 'b']
        >>>

    :param run: function to run
    :param parser: custom argument parser
    :param argv: command line arguments
    :param use_intercom: use intercom communication
    """
    parser = parser if parser is not None else get_parser(use_intercom=use_intercom)
    argv = argv if argv is not None else sys.argv

    args = parser.parse_args(argv[1:])

    async def worker():
        # Start intercom
        intercom = None
        if hasattr(args, "intercom_port") and args.intercom_port is not None:
            intercom = await open_intercom(args.intercom_port)

        try:
            await run(args, intercom=intercom)
        finally:
            # Close intercom
            if intercom is not None:
                intercom.close()
                await intercom.wait_closed()

    asyncio.run(worker())
