"""Package for creating and running Gada nodes in Python."""
__all__ = ["AbstractRunContext", "run", "__version__", "version_info"]
from . import __version__ as version_info
from .__version__ import __version__
import os
import subprocess
from tempfile import NamedTemporaryFile
import json
from abc import ABC, abstractmethod
from typing import Optional, Union
from pygada_runtime.node import Node
from pygada_runtime.program import Program


ProgramLike = Union[Program, Node, str, dict]


class AbstractRunContext(ABC):
    """Context returned by the **run** method."""

    @abstractmethod
    def __enter__(self) -> subprocess.Popen:
        raise NotImplementedError()

    @abstractmethod
    def __exit__(self, *args: list, **kwargs: dict) -> None:
        raise NotImplementedError()


class _RunContext(AbstractRunContext):
    """Context for running a Gada program in a subprocess.

    :param prog: a program-like object
    :param gada_bin: custom path to **gada** binary
    """

    def __init__(
        self, prog: ProgramLike, *, gada_bin: Optional[str] = None
    ) -> None:
        self._prog = prog
        self._gada_bin = gada_bin if gada_bin else "gada"

    def __enter__(self) -> subprocess.Popen:
        # Convert program to string
        prog = self._prog
        if isinstance(prog, Program):
            prog = prog.to_dict()
        elif isinstance(prog, Node):
            prog = prog.to_dict()

        # Write to a temporary file
        self._tmp = NamedTemporaryFile("w+", delete=False, encoding="utf8")
        if isinstance(prog, dict):
            json.dump(prog, self._tmp)
        else:
            self._tmp.write(prog)
        self._tmp.flush()
        self._tmp.close()

        self._process = subprocess.Popen(
            [self._gada_bin, self._tmp.name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        return self._process

    def __exit__(self, *args: list, **kwargs: dict) -> None:
        try:
            self._process.wait()
        finally:
            os.unlink(self._tmp.name)


def run(
    prog: ProgramLike, *, gada_bin: Optional[str] = None
) -> AbstractRunContext:
    """Open a new subprocess for running a Gada program.

    The program is converted to its textual representation and
    saved to a temporary file in order to be run by gada.

    .. code-block:: python

        from pygada_runtime import program

        with program.Process(prog) as process:
            process.wait()

    :param prog: a program-like object
    :param gada_bin: custom path to **gada** binary
    """
    return _RunContext(prog, gada_bin=gada_bin)
