"""Package containing the builtin Gada types."""
from __future__ import annotations

__all__ = [
    "Type",
    "AnyType",
    "BoolType",
    "IntType",
    "FloatType",
    "StringType",
    "ListType",
    "VariableType",
    "TupleType",
    "UnionType",
    "isinstance",
    "typeof",
]
import builtins
from dataclasses import dataclass
from typing import Any, Optional, Union, Iterator
from abc import ABC, abstractmethod


_isinstance = builtins.isinstance


class Type(ABC):
    """Base for Gada types."""

    @abstractmethod
    def _match(self, o: Any, /) -> bool:
        raise NotImplementedError()


@dataclass
class AnyType(Type):
    r"""Represent any type.

    .. code-block:: python

        >>> t = AnyType()
        >>> repr(t)
        'AnyType()'
        >>> str(t)
        'any'
        >>>

    """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return "any"

    def _match(self, o: Any, /) -> bool:
        return True


@dataclass
class BoolType(Type):
    r"""Wrap the Python **bool** type.

    .. code-block:: python

        >>> t = BoolType()
        >>> repr(t)
        'BoolType()'
        >>> str(t)
        'bool'
        >>>

    """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return "bool"

    def _match(self, o: Any, /) -> bool:
        return _isinstance(o, bool)


@dataclass
class IntType(Type):
    r"""Wrap the Python **int** type.

    .. code-block:: python

        >>> t = IntType()
        >>> repr(t)
        'IntType()'
        >>> str(t)
        'int'
        >>>

    """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return "int"

    def _match(self, o: Any, /) -> bool:
        return _isinstance(o, int)


@dataclass
class FloatType(Type):
    r"""Wrap the Python **float** type.

    .. code-block:: python

        >>> t = FloatType()
        >>> repr(t)
        'FloatType()'
        >>> str(t)
        'float'
        >>>

    """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return "float"

    def _match(self, o: Any, /) -> bool:
        return _isinstance(o, float)


@dataclass
class StringType(Type):
    r"""Wrap the Python **str** type.

    .. code-block:: python

        >>> t = StringType()
        >>> repr(t)
        'StringType()'
        >>> str(t)
        'str'
        >>>

    """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return "str"

    def _match(self, o: Any, /) -> bool:
        return _isinstance(o, str)


@dataclass
class ListType(Type):
    r"""Wrap the Python **list** type.

    .. code-block:: python

        >>> t = ListType(IntType())
        >>> repr(t)
        'ListType(IntType())'
        >>> str(t)
        '[int]'
        >>>

    :param item_type: type of list items
    """

    __slot__ = "_item_type"

    def __init__(self, item_type: Optional[Type], /) -> None:
        self._item_type = item_type

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self._item_type)})"

    def __str__(self) -> str:
        return f"[{self._item_type}]"

    def _match(self, o: Any, /) -> bool:
        if not _isinstance(o, list):
            return False

        if not self._item_type or not o:
            return True

        return self._item_type._match(o[0])


@dataclass
class VariableType(Type):
    r"""Represent one or multiple values of the same type.

    .. code-block:: python

        >>> t = VariableType(IntType())
        >>> repr(t)
        'VariableType(IntType())'
        >>> str(t)
        '*int'
        >>>

    :param item_type: type of items
    """

    __slot__ = "_item_type"

    def __init__(self, item_type: Type, /) -> None:
        self._item_type = item_type

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self._item_type)})"

    def __str__(self) -> str:
        return f"*{self._item_type}"

    def _match(self, o: Any, /) -> bool:
        if _isinstance(o, list):
            return self._item_type._match(o[0]) if o else True

        return self._item_type._match(o[0])


@dataclass
class TupleType(Type):
    r"""Wrap the Python **tuple** type.

    .. code-block:: python

        >>> t = TupleType([IntType(), StringType()])
        >>> repr(t)
        'TupleType([IntType(), StringType()])'
        >>> str(t)
        '(int, str)'
        >>>

    :param items_types: types of tuple items
    """

    __slot__ = "_items_types"

    def __init__(
        self, items_types: Union[list[Type], Iterator[Type]], /
    ) -> None:
        self._items_types = list(items_types) if items_types is not None else []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self._items_types)})"

    def __str__(self) -> str:
        return f"({', '.join(map(str, self._items_types))})"

    def _match(self, o: Any, /) -> bool:
        if not _isinstance(o, tuple):
            return False

        if len(self._items_types) != len(o):
            return False

        return all((t._match(v) for t, v in zip(self._items_types, o)))


@dataclass
class UnionType(Type):
    r"""Represent an union of multiple types.

    .. code-block:: python

        >>> t = UnionType([IntType(), StringType()])
        >>> repr(t)
        'UnionType([IntType(), StringType()])'
        >>> str(t)
        'int | str'
        >>>

    :param items_types: possible types
    """

    __slot__ = "_items_types"

    def __init__(self, items_types: list[Type], /) -> None:
        self._items_types = list(items_types) if items_types is not None else []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self._items_types)})"

    def __str__(self) -> str:
        return " | ".join(map(str, self._items_types))

    def _match(self, o: Any, /) -> bool:
        if not _isinstance(o, tuple):
            return False

        if len(self._items_types) != len(o):
            return False

        return all((t._match(v) for t, v in zip(self._items_types, o)))


def isinstance(value: Any, type: Type, /) -> bool:
    r"""Check if a Python object is an instance of a Gada type.

    .. code-block:: python

        >>> from pygada_runtime import typing
        >>>
        >>> typing.isinstance(1, IntType())
        True
        >>> typing.isinstance("hello", IntType())
        False
        >>>

    :param value: Python object
    :param type: type to check
    :return: if **value** is an instance of **type**
    """
    return type._match(value)


def typeof(value: Any, /) -> Type:
    r"""Get the Gada type of a Python object.

    .. code-block:: python

        >>> from pygada_runtime import typing
        >>>
        >>> typing.typeof(True)
        BoolType()
        >>> typing.typeof(1)
        IntType()
        >>> typing.typeof("hello")
        StringType()
        >>> typing.typeof([[1]])
        ListType(ListType(IntType()))
        >>> typing.typeof((1, "hello"))
        TupleType([IntType(), StringType()])
        >>>

    :param value: Python object
    :return: type of **value**
    """
    if _isinstance(value, bool):
        return BoolType()
    if _isinstance(value, int):
        return IntType()
    if _isinstance(value, float):
        return FloatType()
    if _isinstance(value, str):
        return StringType()
    if _isinstance(value, list):
        return ListType(typeof(value[0]) if value else None)
    if _isinstance(value, tuple):
        return TupleType(map(typeof, value))

    raise Exception(f"unsupported type {type(value)}")
