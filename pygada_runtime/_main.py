__all__ = ["get_parser", "main"]
import sys
import argparse
from typing import Optional, List


def get_parser(prog: Optional[str] = None) -> argparse.ArgumentParser:
    """Get a default configured ``argparse.ArgumentParser`` for parsing
    command line arguments passed to your gada node:

    .. code-block:: python

        >>> import pygada_runtime
        >>>
        >>> parser = pygada_runtime.get_parser("mynode")
        >>> parser.print_help()
        usage: mynode [-h] [--chain-input] [--chain-output]
        <BLANKLINE>
        optional arguments:
          -h, --help      show this help message and exit
          --chain-input   read input from stdin
          --chain-output  write output to stdout
        >>>

    """
    parser = argparse.ArgumentParser(prog)
    parser.add_argument(
        "--chain-input", action="store_true", help="read input from stdin"
    )
    parser.add_argument(
        "--chain-output", action="store_true", help="write output to stdout"
    )
    return parser


def main(
    run, parser: Optional[argparse.ArgumentParser] = None, argv: Optional[List] = None
):
    r"""Call this function from the main entrypoint of your component:

    .. code-block:: python

        >>> import pygada_runtime
        >>>
        >>> def foo(args):
        ...     print(args.values)
        >>>
        >>> parser = pygada_runtime.get_parser("foo")
        >>> parser.add_argument("values", type=str, nargs="*", help="some values")
        _StoreAction(option_strings=[], dest='values', nargs='*', const=None, default=None, type=<class 'str'>, choices=None, help='some values', metavar=None)
        >>> parser.print_help()
        usage: foo [-h] [--chain-input] [--chain-output] [values ...]
        <BLANKLINE>
        positional arguments:
          values          some values
        <BLANKLINE>
        optional arguments:
          -h, --help      show this help message and exit
          --chain-input   read input from stdin
          --chain-output  write output to stdout
        >>> pygada_runtime.main(foo, parser, ['foo', 'a', 'b'])
        ['a', 'b']
        >>>

    :param run: function to run
    :param parser: custom argument parser
    :param argv: command line arguments
    """
    parser = parser if parser is not None else get_parser()
    argv = argv if argv is not None else sys.argv

    args = parser.parse_args(argv[1:])
    run(args)
