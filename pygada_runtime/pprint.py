"""Functions for pretty formatting nodes and programs."""
from __future__ import annotations

__all__ = ["help"]
import argparse
from typing import TYPE_CHECKING
from pygada_runtime import node
from pygada_runtime.node import Node

if TYPE_CHECKING:
    from typing import Any, Optional, Union
    from pygada_runtime.node import Param, Node
    from pygada_runtime.program import Program


def _format_params(o: list[Param]) -> str:
    return "- {}".format(
        "\n- ".join(
            [
                "{}: {}{}".format(
                    _.name, _.type, f"\t{_.help}" if _.help else ""
                )
                for _ in o
            ]
        )
    )


def _node_help(o: Node, /) -> str:
    return """{}

Inputs:
{}

Outputs:
{}
""".format(
        o.name,
        _format_params(o.inputs) if o.inputs else "- This node has no inputs",
        _format_params(o.outputs)
        if o.outputs
        else "- This node has no outputs",
    )


def _program_help(o: Program, /) -> str:
    parser = argparse.ArgumentParser(o.name)
    for _ in o.inputs:
        parser.add_argument(f"--{_.name}", help=_.help)

    return parser.format_help()


def help(o: Union[Program, Node], /, *, stream: Optional[Any] = None) -> None:
    """Print informations about a program or node.

    :param o: program or node
    :param stream: stream to write output to
    """
    if isinstance(o, Node):
        output = _node_help(o)
    else:
        output = _program_help(o)

    if stream is not None:
        stream.write(output)
    else:
        print(output)
