__all__ = [
    "get_parser",
    "main"
]
import sys
import argparse
from typing import Optional


def get_parser(prog: Optional[str] = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog)
    parser.add_argument(
        "--chain-input", action="store_true", help="read input from stdin"
    )
    parser.add_argument(
        "--chain-output", action="store_true", help="write output to stdout"
    )
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
