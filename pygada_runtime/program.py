"""Interface for creating and running Gada programs."""
from __future__ import annotations

__all__ = ["Program"]
import yaml
from dataclasses import dataclass
from typing import TYPE_CHECKING
from pathlib import Path
from pygada_runtime.node import Param, NodeCall


if TYPE_CHECKING:
    from typing import Optional, Any, Union


@dataclass
class Program(object):
    """In-memory representation of a Gada program.

    :param steps: list of nodes
    :param name: program name
    :param inputs: program inputs
    :param outputs: unique id of a node from the program
    """

    name: str
    file: str
    steps: list[NodeCall]
    inputs: list[Param]
    outputs: str

    def __init__(
        self,
        steps: list[NodeCall],
        *,
        name: Optional[str] = None,
        file: Optional[str] = None,
        inputs: Optional[list[Param]] = None,
        outputs: Optional[str] = None,
    ) -> None:
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "file", file)
        object.__setattr__(
            self, "steps", list(steps) if steps is not None else []
        )
        object.__setattr__(
            self, "inputs", list(inputs) if inputs is not None else []
        )
        object.__setattr__(self, "outputs", outputs)

    @staticmethod
    def from_dict(o: dict, /) -> Program:
        r"""Create a new program from a JSON dict.

        .. code-block:: python

            >>> from pygada_runtime.program import Program
            >>>
            >>> Program.from_dict({
            ...   "name": "min",
            ...   "inputs": [
            ...     {"name": "a", "type": "int"},
            ...     {"name": "b", "type": "int"}
            ...   ],
            ...   "steps": [
            ...     {"name": "min", "inputs": {"a": "{{ a }}", "b": "{{ b }}"}}
            ...   ]
            ... })
            ...
            Program(name='min', ...)
            >>>

        :param o: JSON dict
        :return: new program
        """
        return Program(
            name=o.get("name", None),
            file=o.get("file", None),
            steps=[NodeCall.from_dict(_) for _ in o.get("steps", [])],
            inputs=[Param.from_dict(_) for _ in o.get("inputs", [])],
        )

    def to_dict(self) -> dict:
        """Convert this object to dict.

        :return: dict
        """
        return {
            "name": self.name,
            "file": self.file,
            "steps": [_.to_dict() for _ in self.steps],
            "inputs": [_.to_dict() for _ in self.inputs],
            "outputs": self.outputs,
        }

    @staticmethod
    def load(file: Union[str, Any], /) -> Program:
        r"""Load a program from file.

        :param file: filename or filelike object
        :return: loaded program
        """
        path: Optional[Path] = None

        if isinstance(file, str):
            path = Path(file)
            with open(file, "r") as f:
                content = f.read()
        elif hasattr(file, "read"):
            content = file.read()
        else:
            raise Exception("argument must be a str or filelike object")

        conf = yaml.safe_load(content)
        conf["file"] = path
        return Program.from_dict(conf)
