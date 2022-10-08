"""Tests on the **pygada_runtime.node** module."""
from __future__ import annotations
import pytest
from pygada_runtime import node
from pygada_runtime.node import NodeLoader
from test.conftest import (
    BAR_GADA_YML,
    FOO_GADA_YML,
    clean_test,
    FOO_DIR,
    BAR_DIR,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Iterable, Union
    from pygada_runtime.module import ModuleLike
    from pygada_runtime.node import Node


def _assert_nodes(
    nodes: Iterable[Union[Node, NodeLoader]],
    expected: list[str],
    unexpected: list[str],
) -> None:
    nodes = [_.name for _ in nodes]
    # Those are in PYTHONPATH and should be returned
    for _ in expected:
        assert _ in nodes
    # Those are subpackages and should not be returned
    for _ in unexpected:
        assert _ not in nodes


@pytest.mark.node
@pytest.mark.parametrize(
    "fun,mod,expected,unexpected",
    [
        (node.iter_nodes, None, ["foo"], ["bar"]),
        (node.walk_nodes, None, ["foo", "bar"], []),
        (node.iter_nodes, "test", ["foo"], ["bar"]),
        (node.walk_nodes, "test", ["foo", "bar"], []),
        (node.iter_nodes, "test.foo", ["bar"], []),
        (node.walk_nodes, "test.foo", ["bar"], []),
    ],
)
@clean_test
def test_iter_nodes(
    fun: Any, mod: ModuleLike, expected: list[str], unexpected: list[str]
) -> None:
    """Test both **iter_nodes** and **walk_nodes**."""
    _assert_nodes(fun(mod), expected, unexpected)


@pytest.mark.node
@pytest.mark.parametrize(
    "mod,expected,unexpected",
    [
        ("test.foo", ["foo"], ["bar"]),
        ("test.foo.bar", ["bar"], []),
    ],
)
@clean_test
def test_from_module(
    mod: ModuleLike, expected: list[str], unexpected: list[str]
) -> None:
    """Test **from_module** returns the correct nodes."""
    _assert_nodes(node.from_module(mod), expected, unexpected)


@pytest.mark.node
@pytest.mark.parametrize(
    "mod,name,package,file",
    [
        ("test.foo", "foo", FOO_DIR, FOO_GADA_YML),
        ("test.foo.bar", "bar", BAR_DIR, BAR_GADA_YML),
    ],
)
@clean_test
def test_nodeloader(mod: str, name: str, package: str, file: str) -> None:
    """Test **NodeLoader** correctly loads nodes."""

    def _assert(n: Any) -> None:
        assert n.module == mod
        assert n.name == name
        assert n.__package__ == package
        assert n.__file__ == file
        assert n.__path__ == f"{mod}.{name}"

    n = NodeLoader(mod, name)
    # First check NodeLoader class
    _assert(n)
    # Then check Node class
    _assert(n.load())
