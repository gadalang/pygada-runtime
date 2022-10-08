"""Tests on the **pygada_runtime.program** module."""
from __future__ import annotations
import pytest
from pygada_runtime import node, program


@pytest.mark.program
def test_from_node() -> None:
    """Test creating a program from node."""
    p = program.from_node(node.load("foo.foo"))
