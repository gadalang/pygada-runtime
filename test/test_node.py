"""Tests on the **gada.parser** module."""
from __future__ import annotations
import pytest
from pygada_runtime import node
from pathlib import Path
from typing import Any, Union
from types import ModuleType
from pkgutil import ModuleInfo
from test import foo
from test.foo import bar


TEST_DIR = str(Path(__file__).parent.absolute())
FOO_DIR = str(Path(TEST_DIR) / "foo")
FOO_GADA_YML = str(Path(FOO_DIR) / "gada.yml")
BAR_DIR = str(Path(FOO_DIR) / "bar")
BAR_GADA_YML = str(Path(BAR_DIR) / "gada.yml")


@pytest.mark.node
@pytest.mark.parametrize(
    "mod,expected",
    [
        ("foo", "foo"),
        ("test.foo", "test.foo"),
        (foo, "test.foo"),
        ("foo.bar", "foo.bar"),
        ("test.foo.bar", "test.foo.bar"),
        (bar, "test.foo.bar"),
    ],
)
def test_module_name(mod: Union[ModuleInfo, ModuleType], expected: str) -> None:
    """Test **module_name** returns the correct name."""
    assert node.module_name(mod) == expected


@pytest.mark.node
@pytest.mark.parametrize(
    "mod,expected",
    [
        ("foo", FOO_DIR),
        ("test.foo", FOO_DIR),
        (foo, FOO_DIR),
        ("foo.bar", BAR_DIR),
        ("test.foo.bar", BAR_DIR),
        (bar, BAR_DIR),
    ],
)
def test_module_path(mod: Union[ModuleInfo, ModuleType], expected: str) -> None:
    """Test **module_path** returns the correct absolute path."""
    assert node.module_path(mod) == expected


@pytest.mark.node
@pytest.mark.parametrize(
    "mod,expected",
    [
        ("foo", FOO_GADA_YML),
        ("test.foo", FOO_GADA_YML),
        (foo, FOO_GADA_YML),
        ("foo.bar", BAR_GADA_YML),
        ("test.foo.bar", BAR_GADA_YML),
        (bar, BAR_GADA_YML),
    ],
)
def test_module_gada_yml(
    mod: Union[ModuleInfo, ModuleType], expected: str
) -> None:
    """Test **module_gada_yml** returns the correct absolute path."""
    assert node.module_gada_yml(mod) == expected


@pytest.mark.node
@pytest.mark.parametrize(
    "fun,path,expected,unexpected",
    [
        (node.iter_modules, None, [FOO_DIR], [BAR_DIR]),
        (node.walk_modules, None, [FOO_DIR, BAR_DIR], []),
        (node.iter_modules, ["test"], [FOO_DIR], [BAR_DIR]),
        (node.walk_modules, ["test"], [FOO_DIR, BAR_DIR], []),
        (node.iter_modules, ["test/foo"], [BAR_DIR], []),
        (node.walk_modules, ["test/foo"], [BAR_DIR], []),
        (node.iter_modules, ["invalidpath"], [], []),
        (node.walk_modules, ["invalidpath"], [], []),
    ],
)
def test_iter_modules(
    fun: Any, path: str, expected: list[str], unexpected: list[str]
) -> None:
    """Test both **iter_modules** and **walk_modules**."""
    modules = list(map(node.module_path, fun(path)))
    # Those are in PYTHONPATH and should be returned
    for _ in expected:
        assert _ in modules
    # Those are subpackages and should not be returned
    for _ in unexpected:
        assert _ not in modules


@pytest.mark.node
@pytest.mark.parametrize(
    "fun,path,expected,unexpected",
    [
        (node.iter_nodes, None, ["foo"], ["bar"]),
        (node.walk_nodes, None, ["foo", "bar"], []),
        (node.iter_nodes, ["test"], ["foo"], ["bar"]),
        (node.walk_nodes, ["test"], ["foo", "bar"], []),
        (node.iter_nodes, ["test/foo"], ["bar"], []),
        (node.walk_nodes, ["test/foo"], ["bar"], []),
        (node.iter_nodes, ["invalidpath"], [], []),
        (node.walk_nodes, ["invalidpath"], [], []),
    ],
)
def test_iter_nodes(
    fun: Any, path: str, expected: list[str], unexpected: list[str]
) -> None:
    """Test both **iter_nodes** and **walk_nodes**."""
    nodes = [_.name for _ in fun(path)]
    # Those are in PYTHONPATH and should be returned
    for _ in expected:
        assert _ in nodes
    # Those are subpackages and should not be returned
    for _ in unexpected:
        assert _ not in nodes
