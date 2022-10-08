"""Package containing everything for manipulating nodes."""
from __future__ import annotations

__all__ = [
    "Param",
    "Node",
    "NodeCall",
    "NodeLoader",
    "load",
    "from_module",
    "iter_nodes",
    "walk_nodes",
]
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable
from pathlib import Path
import yaml
from pygada_runtime import typing, parser, module, _cache

if TYPE_CHECKING:
    from typing import Optional, Any, Callable, IO, Union
    from pkgutil import ModuleInfo
    from pygada_runtime.module import ModuleLike

    NodeLike = Union["Node", "NodeLoader", str]


class NodeNotFoundException(Exception):
    pass


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


def _fill_metadata(node: Any, mod: Optional[ModuleLike], name: str) -> None:
    object.__setattr__(
        node,
        "__package__",
        module.module_path(mod) if mod is not None else None,
    )
    object.__setattr__(
        node,
        "__file__",
        module.gada_yml_path(mod) if mod is not None else None,
    )
    object.__setattr__(
        node,
        "__path__",
        "{}{}".format(f"{mod}." if mod is not None else "", name),
    )


@dataclass
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
    module: str
    file: Path
    lineno: int
    runner: str
    is_pure: bool
    inputs: list[Param]
    outputs: list[Param]
    extras: dict
    """Absolute path to Python package containing the node."""
    __package__: str = field(repr=False)
    """Absolute path to file containing the node."""
    __file__: str = field(repr=False)
    """Fully qualified path to the node **module.name**."""
    __path__: str = field(repr=False)

    def __init__(
        self,
        name: str,
        *,
        module: Optional[str] = None,
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
        _fill_metadata(self, module, name)

    @staticmethod
    def from_dict(o: dict, /, *, module: Optional[str] = None) -> Node:
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

    module: Optional[str]
    name: str
    """Absolute path to Python package containing the node."""
    __package__: str = field(repr=False)
    """Absolute path to file containing the node."""
    __file__: str = field(repr=False)
    """Fully qualified path to the node **module.name**."""
    __path__: str = field(repr=False)
    """Loaded node if :func:`load` has already been called."""
    _node: Optional[Node] = field(repr=False)

    def __init__(
        self, mod: Optional[str], name: str, node: Optional[Node] = None
    ) -> None:
        object.__setattr__(self, "module", mod)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "_node", node)
        _fill_metadata(self, mod, name)

    def load(self) -> Node:
        """Load the node."""
        if self._node is None:
            self._node = load(self.__path__)

        return self._node


def load(path: str, /) -> Node:
    """Load a node by its path.

    :param path: node path
    """
    parts = path.rsplit(".", maxsplit=1)
    mod = parts[0] if len(parts) == 2 else "gada"
    name = parts[-1]

    def _loader() -> Node:
        for _ in module.load_gada_yml(mod).get("nodes", []):
            if _.get("name", None) == name:
                return Node.from_dict(_, module=mod)

        raise NodeNotFoundException()

    return _cache.get_cached_node(mod, name, _loader)


def _from_file(
    fp: Union[IO, str, dict], /, *, module: Optional[str]
) -> Iterable[NodeLoader]:
    """Yield nodes from a YAML file or string.

    :param fp: a file-like object or dict
    :param module: module path
    """
    if isinstance(fp, str):
        with open(fp, "r", encoding="utf8") as f:
            fp = f.read()

    if not isinstance(fp, dict):
        fp = yaml.safe_load(fp)

    for _ in fp.get("nodes", []):  # type: ignore
        yield NodeLoader(module, _["name"], _)


def from_module(mod: ModuleLike, /) -> Iterable[NodeLoader]:
    """Yield top-level nodes of a module.

    Imagine you have the following package:

    .. code-block::

        sample/
        ├─ __init__.py
        ├─ gada.yml
        ├─ foo/
        │  ├─ __init__.py
        │  ├─ gada.yml
        │  ├─ bar/
        │  │  ├─ __init__.py
        │  │  ├─ gada.yml
        ├─ baz/
        │  ├─ __init__.py
        │  ├─ gada.yml

    This is what you would get in the different scenarios:

    - `from_module("sample")`: nodes from `sample` module.
    - `from_module("sample.foo")`: nodes from `foo` module.
    - `from_module("sample.foo.bar")`: nodes from `bar` module.
    - `from_module("sample.baz")`: nodes from `baz` module.

    :param mod: a module-like object
    """
    return _from_file(module.gada_yml_path(mod), module=module.module_name(mod))


def _iter_nodes(
    fun: Callable[[Optional[ModuleLike]], Iterable[ModuleInfo]],
    mod: Optional[ModuleLike] = None,
) -> Iterable[NodeLoader]:
    """Yield nodes from installed modules.

    :param path: either None or a list of paths
    """
    for item in fun(mod):
        with open(module.gada_yml_path(item), "r", encoding="utf8") as f:
            content = yaml.safe_load(f)

        if content is not None:
            for _ in content.get("nodes", []):
                yield NodeLoader(item.name, _["name"], _)


def iter_nodes(mod: Optional[ModuleLike] = None) -> Iterable[NodeLoader]:
    """Yield nodes from top-level modules of a parent module or **PYTHONPATH**.

    This function only returns nodes from top-level modules. See
    :func:`walk_nodes` for a fully recursive version.

    Imagine you have the following package:

    .. code-block::

        sample/
        ├─ __init__.py
        ├─ gada.yml
        ├─ foo/
        │  ├─ __init__.py
        │  ├─ gada.yml
        │  ├─ bar/
        │  │  ├─ __init__.py
        │  │  ├─ gada.yml
        ├─ baz/
        │  ├─ __init__.py
        │  ├─ gada.yml

    This is what you would get in the different scenarios:

    - `iter_nodes()`: nodes from `sample` module.
    - `iter_nodes("sample")`: nodes from `foo` and `baz` modules.
    - `iter_nodes("sample.foo")`: nodes from `bar` module.
    - `iter_nodes("sample.foo.bar")`: an empty list.
    - `iter_nodes("sample.baz")`: an empty list.

    :param mod: a module-like object
    """
    return _iter_nodes(module.iter_modules, mod)


def walk_nodes(mod: Optional[ModuleLike] = None) -> Iterable[NodeLoader]:
    """Yield nodes from all submodules of a parent module or **PYTHONPATH**.

    This function not only returns nodes from top-level modules, but also
    from submodules. See :func:`iter_nodes` for a non recursive version.

    Imagine you have the following package:

    .. code-block::

        sample/
        ├─ __init__.py
        ├─ gada.yml
        ├─ foo/
        │  ├─ __init__.py
        │  ├─ gada.yml
        │  ├─ bar/
        │  │  ├─ __init__.py
        │  │  ├─ gada.yml
        ├─ baz/
        │  ├─ __init__.py
        │  ├─ gada.yml

    This is what you would get in the different scenarios:

    - `walk_nodes()`: nodes from `sample`, `foo`, `bar` and `baz` modules.
    - `walk_nodes("sample")`: nodes from `foo`, `bar` and `baz` modules.
    - `walk_nodes("sample.foo")`: nodes from `bar` module.
    - `walk_nodes("sample.foo.bar")`: an empty list.
    - `walk_nodes("sample.baz")`: an empty list.

    :param mod: a module-like object
    """
    return _iter_nodes(module.walk_modules, mod)
