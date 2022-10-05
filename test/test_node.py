"""Tests on the **pygada_runtime.node** module."""
from __future__ import annotations
import pytest
from pygada_runtime import node
from typing import Any
from test.conftest import *


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
