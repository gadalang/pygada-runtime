"""Package containing everything for manipulating nodes."""
from __future__ import annotations

__all__ = [
    "Param",
    "Node",
    "NodeCall",
    "NodeLoader",
    "iter_modules",
    "walk_modules",
    "iter_nodes",
    "walk_nodes",
]
import os
from dataclasses import dataclass, field
from types import ModuleType
from typing import TYPE_CHECKING, Iterable
from pathlib import Path
import pkgutil
import yaml
from pygada_runtime import typing, parser

if TYPE_CHECKING:
    from typing import Optional, Any, Callable
    from pkgutil import ModuleInfo


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
        object.__setattr__(
            self, "type", type if type is not None else typing.AnyType()
        )
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
        object.__setattr__(
            self, "outputs", outputs if outputs is not None else []
        )
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
            inputs=[
                Param(name=k, value=v) for k, v in o.get("inputs", {}).items()
            ],
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

    def __init__(
        self, module_info: ModuleInfo, name: str, *, config: dict
    ) -> None:
        object.__setattr__(self, "module_info", module_info)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "_config", config)

    def load(self) -> Node:
        """Load the node."""
        return Node.from_dict(self._config)


def _module_path(mod: ModuleInfo) -> str:
    """Return the path to a module.

    :param mod: module infos
    """
    mod_path = mod.module_finder.path  # type: ignore
    return os.path.join(mod_path, mod.name.split(".")[-1])


def _module_gada_yml(mod: ModuleInfo) -> str:
    """Return the path the **gada.yml** file in a module.

    :param mod: module infos
    """
    return os.path.join(_module_path(mod), "gada.yml")


def _iter_modules(
    fun: Callable[[Optional[Iterable[str]]], Iterable[ModuleInfo]],
    path: Optional[Iterable[str]] = None,
) -> Iterable[ModuleInfo]:
    """Yield modules containing a **gada.yml** file.

    :param path: either None or a list of paths
    """
    for mod in fun(path):
        if os.path.exists(_module_gada_yml(mod)):
            yield mod


def _iter_nodes(
    fun: Callable[[Optional[Iterable[str]]], Iterable[ModuleInfo]],
    path: Optional[Iterable[str]] = None,
) -> Iterable[NodeLoader]:
    """Yield nodes from installed modules.

    :param path: either None or a list of paths
    """
    for mod in fun(path):
        with open(_module_gada_yml(mod), "r", encoding="utf8") as f:
            content = yaml.safe_load(f)

        if content is not None:
            for _ in content.get("nodes", []):
                yield NodeLoader(mod, _["name"], config=_)


def iter_modules(path: Optional[Iterable[str]] = None) -> Iterable[ModuleInfo]:
    """Yield top-level modules containing a **gada.yml** file.

    This function only returns top-level modules installed in
    the **PYTHONPATH**. See :func:`walk_modules` for a fully
    recursive version.

    :param path: either None or a list of paths
    """
    return _iter_modules(pkgutil.iter_modules, path)


def walk_modules(path: Optional[Iterable[str]] = None) -> Iterable[ModuleInfo]:
    """Yield all modules containing a **gada.yml** file recursively.

    This function recursively analyze the modules installed in
    the **PYTHONPATH** to return not only the top-level modules,
    but also the submodules containing a **gada.yml** file. See
    :func:`iter_modules` for a non recursive version.

    :param path: either None or a list of paths
    """
    return _iter_modules(pkgutil.walk_packages, path)


def iter_nodes(path: Optional[Iterable[str]] = None) -> Iterable[NodeLoader]:
    """Yield top-level nodes installed in the **PYTHONPATH**.

    This function only returns nodes from top-level modules installed
    in the **PYTHONPATH**. See :func:`walk_nodes` for a fully
    recursive version.

    :param path: either None or a list of paths
    """
    return _iter_nodes(iter_modules, path)


def walk_nodes(path: Optional[Iterable[str]] = None) -> Iterable[NodeLoader]:
    """Yield all nodes installed in the **PYTHONPATH** recursively.

    This function not only returns nodes from top-level modules installed
    in the **PYTHONPATH**, but also from submodules. See :func:`iter_nodes`
    for a non recursive version.

    :param path: either None or a list of paths
    """
    return _iter_nodes(walk_modules, path)
