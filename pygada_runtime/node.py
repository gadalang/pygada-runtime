"""Package containing everything for manipulating nodes."""
from __future__ import annotations

__all__ = [
    "Param",
    "Node",
    "NodeCall",
    "NodeLoader",
    "iter_nodes",
    "walk_nodes",
]
from dataclasses import dataclass, field
from types import ModuleType
from typing import TYPE_CHECKING, Iterable
from pathlib import Path
import yaml
from pygada_runtime import typing, parser, module

if TYPE_CHECKING:
    from typing import Optional, Any, Callable, IO, Union
    from pkgutil import ModuleInfo
    from pygada_runtime.module import ModuleLike


@dataclass
class Param(object):
    """Represent an input or output of a node.

    :param name: name of parameter
    :param type: it's type
    :param help: description of the parameter
    """

    name: str
    value: Any
    type: typing.Type
    help: str

    def __init__(
        self,
        name: str,
        *,
        value: Optional[Any] = None,
        type: Optional[typing.Type] = None,
        help: Optional[str] = None,
    ) -> None:
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "type", type if type is not None else typing.AnyType())
        object.__setattr__(self, "help", help)

    @staticmethod
    def from_dict(o: dict, /) -> Param:
        r"""Create a new **Param** from a JSON dict.

        .. code-block:: python

            >>> from pygada_runtime.node import Param
            >>>
            >>> Param.from_dict({"name": "a", "type": "int"})
            Param(name='a', ...)
            >>>

        :param o: JSON dict
        :return: loaded **Param**
        """
        type = o.get("type", None)
        if type:
            type = parser.type(type)

        return Param(
            name=o.get("name", None),
            value=o.get("value", None),
            type=type,
            help=o.get("help", None),
        )

    def to_dict(self) -> dict:
        """Convert this object to dict.

        :return: dict
        """
        return {
            "name": self.name,
            "value": self.value,
            "type": str(self.type),
            "help": self.help,
        }


@dataclass(frozen=True)
class Node(object):
    """Represent a node definition.

    :param name: name of the node
    :param module: parent module
    :param file: absolute path to the source code
    :param lineno: line number in the source code
    :param runner: name of runner
    :param is_pure: if the node is pure
    :param inputs: inputs of the node
    :param outputs: outputs of the node
    :param extra: extra parameters
    """

    name: str
    module: ModuleType
    file: Path
    lineno: int
    runner: str
    is_pure: bool
    inputs: list[Param]
    outputs: list[Param]
    extras: dict

    def __init__(
        self,
        name: str,
        *,
        module: Optional[ModuleType] = None,
        file: Optional[Path] = None,
        lineno: Optional[int] = None,
        runner: Optional[str] = None,
        is_pure: Optional[bool] = None,
        inputs: Optional[list[Param]] = None,
        outputs: Optional[list[Param]] = None,
        extras: Optional[dict] = None,
    ) -> None:
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "module", module)
        object.__setattr__(self, "file", file)
        object.__setattr__(self, "lineno", lineno if lineno is not None else 0)
        object.__setattr__(self, "runner", runner)
        object.__setattr__(self, "is_pure", is_pure)
        object.__setattr__(self, "inputs", inputs if inputs is not None else [])
        object.__setattr__(self, "outputs", outputs if outputs is not None else [])
        object.__setattr__(self, "extras", extras if extras is not None else {})

    @staticmethod
    def from_dict(o: dict, /, *, module: Optional[ModuleType] = None) -> Node:
        r"""Create a new **Node** from a JSON dict.

        .. code-block:: python

            >>> from pygada_runtime.node import Node
            >>>
            >>> Node.from_dict({
            ...   "name": "min",
            ...   "inputs": [
            ...     {"name": "a", "type": "int"},
            ...     {"name": "b", "type": "int"}
            ...   ],
            ...   "outputs": [
            ...     {"name": "out", "type": "int"}
            ...   ]
            ... })
            ...
            Node(name='min', ...)
            >>>

        :param o: JSON dict
        :param module: parent module
        :return: loaded **Node**
        """
        return Node(
            name=o.get("name", None),
            module=module,
            file=o.get("file", None),
            lineno=o.get("lineno", None),
            runner=o.get("runner", None),
            is_pure=o.get("pure", False),
            inputs=[Param.from_dict(_) for _ in o.get("inputs", [])],
            outputs=[Param.from_dict(_) for _ in o.get("outputs", [])],
            extras=o,
        )

    def to_dict(self) -> dict:
        """Convert this object to dict.

        :return: dict
        """
        return {
            "name": self.name,
            "module": self.module,
            "file": self.file,
            "lineno": self.lineno,
            "runner": self.runner,
            "pure": self.is_pure,
            "inputs": [_.to_dict() for _ in self.inputs],
            "outputs": [_.to_dict() for _ in self.outputs],
        }


@dataclass
class NodeCall(object):
    """Represent the call to a node in a program.

    :param name: name of the node
    :param id: unique id of the call
    :param file: absolute path to the source code
    :param lineno: line number in the source code
    :param inputs: inputs for the call
    """

    name: str
    id: str
    file: str
    lineno: int
    inputs: list[Param]

    def __init__(
        self,
        name: str,
        *,
        id: Optional[str] = None,
        file: Optional[Path] = None,
        lineno: Optional[int] = None,
        inputs: Optional[list[Param]] = None,
    ) -> None:
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "file", file)
        object.__setattr__(self, "lineno", lineno if lineno is not None else 0)
        object.__setattr__(self, "inputs", inputs if inputs is not None else [])

    @staticmethod
    def from_dict(o: dict, /) -> NodeCall:
        r"""Create a new **NodeCall** from a JSON dict.

        .. code-block:: python

            >>> from pygada_runtime.node import NodeCall
            >>>
            >>> NodeCall.from_dict({
            ...   "name": "min",
            ...   "inputs": {
            ...     "a": 1,
            ...     "b": 2
            ...   }
            ... })
            ...
            NodeCall(name='min', ...)
            >>>

        :param o: JSON dict
        :return: new **NodeCall**
        """
        return NodeCall(
            name=o.get("name", None),
            id=o.get("id", None),
            file=o.get("file", None),
            lineno=o.get("lineno", None),
            inputs=[Param(name=k, value=v) for k, v in o.get("inputs", {}).items()],
        )

    def to_dict(self) -> dict:
        """Convert this object to dict.

        :return: dict
        """
        return {
            "name": self.name,
            "id": self.id,
            "file": self.file,
            "lineno": self.lineno,
            "inputs": [_.to_dict() for _ in self.inputs],
        }


@dataclass
class NodeLoader(object):
    """Class for loading a node defined in a module."""

    module_info: ModuleInfo
    name: str
    _config: dict = field(repr=False)

    def __init__(self, module_info: ModuleInfo, name: str, *, config: dict) -> None:
        object.__setattr__(self, "module_info", module_info)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "_config", config)

    def load(self) -> Node:
        """Load the node."""
        return Node.from_dict(self._config)


def from_dict(o: dict, /, *, prefix: Optional[str]) -> Iterable[NodeLoader]:
    raise NotImplementedError()


def from_file(
    fp: Union[IO, str, dict], /, *, prefix: Optional[str]
) -> Iterable[NodeLoader]:
    """Yield top-level nodes from a YAML file or string.

    :param mod: a module-like object
    """
    if not isinstance(fp, dict):
        fp = yaml.safe_load(fp)

    return from_dict(fp, prefix=prefix)  # type: ignore


def from_module(mod: ModuleLike, /) -> Iterable[NodeLoader]:
    """Yield top-level nodes from a module.

    :param mod: a module-like object
    """
    if isinstance(mod, ModuleInfo):
        name = mod.name
    else:
        name = mod.__package__  # type: ignore

    return from_file(module.gada_yml_path(mod), prefix=name)


def _iter_nodes(
    fun: Callable[[Optional[Iterable[str]]], Iterable[ModuleInfo]],
    path: Optional[Iterable[str]] = None,
) -> Iterable[NodeLoader]:
    """Yield nodes from installed modules.

    :param path: either None or a list of paths
    """
    for mod in fun(path):
        with open(module.gada_yml_path(mod), "r", encoding="utf8") as f:
            content = yaml.safe_load(f)

        if content is not None:
            for _ in content.get("nodes", []):
                yield NodeLoader(mod, _["name"], config=_)


def iter_nodes(mod: Optional[ModuleLike] = None) -> Iterable[NodeLoader]:
    """Yield top-level nodes installed in the **PYTHONPATH**.

    This function only returns nodes from top-level modules installed
    in the **PYTHONPATH**. See :func:`walk_nodes` for a fully
    recursive version.

    :param mod: a module-like object
    """
    return _iter_nodes(
        module.iter_modules, [module.module_path(mod)] if mod is not None else None
    )


def walk_nodes(mod: Optional[ModuleLike] = None) -> Iterable[NodeLoader]:
    """Yield all nodes installed in the **PYTHONPATH** recursively.

    This function not only returns nodes from top-level modules installed
    in the **PYTHONPATH**, but also from submodules. See :func:`iter_nodes`
    for a non recursive version.

    :param mod: a module-like object
    """
    return _iter_nodes(
        module.walk_modules, [module.module_path(mod)] if mod is not None else None
    )
