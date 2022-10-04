"""Tests on the **gada.parser** module."""
from __future__ import annotations
import pytest
from pygada_runtime import node
from pathlib import Path
from typing import Any


TEST_DIR = str(Path(__file__).parent.absolute())
FOO_DIR = str(Path(TEST_DIR) / "foo")
BAR_DIR = str(Path(FOO_DIR) / "bar")


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
    modules = list(map(node._module_path, fun(path)))
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
    nodes = list(map(lambda _: _.name, fun(path)))
    # Those are in PYTHONPATH and should be returned
    for _ in expected:
        assert _ in nodes
    # Those are subpackages and should not be returned
    for _ in unexpected:
        assert _ not in nodes
