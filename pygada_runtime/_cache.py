"""Cache for runtime data."""
from __future__ import annotations

__all__ = [
    "clear",
    "get_cached_node",
    "set_cached_node",
]
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Optional
    from pygada_runtime.node import Node


_MODULE_NODE_CACHE: dict = {}


def clear() -> None:
    """Clear the cache."""
    global _MODULE_NODE_CACHE
    _MODULE_NODE_CACHE = {}


def get_cached_node(
    module: Optional[str], name: str, /, get_value: Callable[[], "Node"]
) -> "Node":
    """Get a cached node."""
    module = module if module is not None else ""
    node = _MODULE_NODE_CACHE.get(module, {}).get(name, None)
    return node if node else set_cached_node(get_value())


def set_cached_node(node: "Node", /) -> "Node":
    """Cache a node."""
    _MODULE_NODE_CACHE.setdefault(node.module, {})[node.name] = node
    return node
