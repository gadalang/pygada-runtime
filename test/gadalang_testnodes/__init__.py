"""Collection of nodes used in unittests.

PYTHONPATH will be automatically set so Python can find this package.
"""
import sys
import pygada_runtime


def hello(argv, *, stdout=None, **kwargs):
    """Entrypoint used with **pymodule** runner."""
    def run(args):
        print(f"hello {args.name} !", file=stdout if stdout is not None else sys.stdout)

    parser = pygada_runtime.get_parser("hello")
    parser.add_argument("name", type=str, help="your name")
    pygada_runtime.main(run, parser, argv)


def main(argv):
    """Entrypoint used with **python** runner."""
    hello(argv=argv)


if __name__ == "__main__":
    main(sys.argv)
