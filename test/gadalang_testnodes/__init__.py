"""Collection of nodes used in unittests.

PYTHONPATH will be automatically set so Python can find this package.
"""
import sys


def sum(argv):
    """Entrypoint used with **pymodule** runner."""
    from functools import reduce

    if len(argv) < 2:
        raise Exception("expected a list of int")

    print(reduce(lambda x, y: x + y, [int(_) for _ in argv[1:]]))


def main(argv):
    """Entrypoint used with **python** runner."""
    sum(argv=argv)


if __name__ == "__main__":
    main(sys.argv)
