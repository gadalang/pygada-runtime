"""Cache for runtime data."""
from __future__ import annotations

__all__ = [
    "clear",
    "load_module",
    "get_module_path",
    "load_module_config",
    "dump_module_config",
    "get_cached_node",
    "set_cached_node",
]
from typing import TYPE_CHECKING
from types import ModuleType
import importlib
from pathlib import Path
import yaml

if TYPE_CHECKING:
    from typing import Union, Any


_GADA_YML_FILENAME = "gada.yml"
_LOAD_MODULE_CACHE: dict = {}
_MODULE_PATH_CACHE: dict = {}
_MODULE_CONFIG_CACHE: dict = {}
_MODULE_NODE_CACHE: dict = {}


def clear() -> None:
    """Clear the cache."""
    global _LOAD_MODULE_CACHE, _MODULE_PATH_CACHE
    global _MODULE_CONFIG_CACHE, _MODULE_NODE_CACHE
    _LOAD_MODULE_CACHE = {}
    _MODULE_PATH_CACHE = {}
    _MODULE_CONFIG_CACHE = {}
    _MODULE_NODE_CACHE = {}


def load_module(module: Union[ModuleType, str, list[str]], /) -> ModuleType:
    """Load a module by path and cache the result.

    This will raise **ModuleNotFoundError** if the module is not installed.

    :param module: name or path to module
    :return: loaded module
    """
    if isinstance(module, ModuleType):
        return module

    if isinstance(module, list):
        module = ".".join(module)

    mod = _LOAD_MODULE_CACHE.get(module, None)
    if mod is None:
        mod = importlib.import_module(module)
        _LOAD_MODULE_CACHE[module] = mod

    return mod


def get_module_path(module: Union[ModuleType, str, list[str]], /) -> Path:
    """Locate a module installed in **PYTHONPATH**.

    This will raise **ModuleNotFoundError** if the module is not installed.

    :param module: name or path to module
    :return: a tuple (module, absolute path)
    """
    mod = load_module(module)

    path = _MODULE_PATH_CACHE.get(mod, None)
    if path is None:
        path = Path(mod.__file__).parent.absolute()
        _MODULE_PATH_CACHE[mod] = path

    return path


def load_module_config(module: Union[ModuleType, str, list[str]]) -> dict:
    r"""Load ``gada.yml`` from a module installed in **PYTHONPATH**.

    This will raise **ModuleNotFoundError** if the module is not installed.

    :param module: name or path to module
    :return: configuration
    """
    mod = load_module(module)

    conf = _MODULE_CONFIG_CACHE.get(mod, None)
    if conf is None:
        path = get_module_path(mod)
        try:
            with open(path / _GADA_YML_FILENAME, "r") as f:
                conf = yaml.safe_load(f.read())
        except FileNotFoundError:
            conf = {}

        _MODULE_CONFIG_CACHE[mod] = conf

    return conf


def dump_module_config(
    module: Union[ModuleType, str, list[str]], /, config: dict
) -> None:
    r"""Dump ``gada.yml`` to a module installed in **PYTHONPATH**.

    This will raise **ModuleNotFoundError** if the module is not installed.

    :param module: module or path
    :param config: configuration to dump
    """
    mod = load_module(module)
    path = get_module_path(mod)

    _MODULE_CONFIG_CACHE[mod] = None
    with open(path / _GADA_YML_FILENAME, "w+") as f:
        f.write(yaml.safe_dump(config))


def get_cached_node(module: ModuleType, name: str, /) -> Any:
    """Get a cached node."""
    cache = _MODULE_NODE_CACHE.get(module, None)
    if not cache:
        return None

    return cache.get(name, None)


def set_cached_node(module: ModuleType, name: str, node: Any, /) -> None:
    """Cache a node."""
    _MODULE_NODE_CACHE.setdefault(module, {})[name] = node
