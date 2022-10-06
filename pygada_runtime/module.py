"""Package containing everything for accessing Python modules.

Gada takes advantage of how Python packages are installed in
the **PYTHONPATH** for dynamically discovering and loading
installed nodes.

So it heavily relies on **pkgutil** and **importlib** for
accessing and getting informations on installed packages.
"""
from __future__ import annotations

__all__ = [
    "module_name",
    "module_path",
    "gada_yml_path",
    "load_gada_yml",
    "iter_modules",
    "walk_modules",
]
import os
from types import ModuleType
from typing import TYPE_CHECKING, Iterable
import pkgutil
import importlib
import yaml

if TYPE_CHECKING:
    from typing import Optional, Callable, Union
    from pkgutil import ModuleInfo

    ModuleLike = Union[ModuleInfo, ModuleType, str]


def module_name(mod: ModuleLike, /) -> str:
    """Get the name of a module.

    :param mod: a module-like object
    """
    if isinstance(mod, str):
        mod = importlib.import_module(mod)

    if isinstance(mod, ModuleType):
        return mod.__package__  # type: ignore

    return mod.name


def module_path(mod: ModuleLike, /) -> str:
    """Get the absolute path to a module.

    :param mod: a module-like object
    """
    if isinstance(mod, str):
        mod = importlib.import_module(mod)

    if isinstance(mod, ModuleType):
        path = os.path.dirname(mod.__file__)
    else:
        mod_path = mod.module_finder.path  # type: ignore
        path = os.path.join(mod_path, mod.name.split(".")[-1])

    return os.path.abspath(path)


def gada_yml_path(mod: ModuleLike, /) -> str:
    """Get the absolute path to the **gada.yml** file of a module.

    :param mod: a module-like object
    """
    return os.path.join(module_path(mod), "gada.yml")


def load_gada_yml(mod: ModuleLike, /) -> dict:
    """Load the **gada.yml** file of a module.

    :param mod: a module-like object
    """
    with open(gada_yml_path(mod), "r", encoding="utf8") as f:
        return yaml.safe_load(f)


def _iter_modules(
    fun: Callable[[Optional[Iterable[str]], str], Iterable[ModuleInfo]],
    mod: Optional[ModuleLike] = None,
) -> Iterable[ModuleInfo]:
    """Yield modules containing a **gada.yml** file.

    :param mod: a module-like object
    """
    path = [module_path(mod)] if mod is not None else None
    prefix = f"{module_name(mod)}." if mod is not None else ""

    for item in fun(path, prefix):
        if os.path.exists(gada_yml_path(item)):
            yield item


def iter_modules(mod: Optional[ModuleLike] = None) -> Iterable[ModuleInfo]:
    """Yield top-level modules containing a **gada.yml** file.

    This function only returns top-level modules installed in
    the **PYTHONPATH**. See :func:`walk_modules` for a fully
    recursive version.

    :param mod: a module-like object
    """
    return _iter_modules(pkgutil.iter_modules, mod)


def walk_modules(mod: Optional[ModuleLike] = None) -> Iterable[ModuleInfo]:
    """Yield all modules containing a **gada.yml** file recursively.

    This function recursively analyze the modules installed in
    the **PYTHONPATH** to return not only the top-level modules,
    but also the submodules containing a **gada.yml** file. See
    :func:`iter_modules` for a non recursive version.

    :param mod: a module-like object
    """
    return _iter_modules(pkgutil.walk_packages, mod)
