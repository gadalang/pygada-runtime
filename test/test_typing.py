"""Tests on the **pygada_runtime.typing** module."""
import pytest
from typing import Any
from pygada_runtime import typing


BOOL_VALUE = True
BOOL_TYPE = typing.BoolType()
INT_VALUE = 1
INT_TYPE = typing.IntType()
FLOAT_VALUE = 1.0
FLOAT_TYPE = typing.FloatType()
STRING_VALUE = "hello"
STRING_TYPE = typing.StringType()
LIST_INT_VALUE = [1]
LIST_INT_TYPE = typing.ListType(typing.IntType())
TUPLE_INT_STRING_VALUE = (1, "hello")
TUPLE_INT_STRING_TYPE = typing.TupleType(
    [typing.IntType(), typing.StringType()]
)


@pytest.mark.typing
@pytest.mark.parametrize(
    "value,type",
    [
        (BOOL_VALUE, BOOL_TYPE),
        (INT_VALUE, INT_TYPE),
        (FLOAT_VALUE, FLOAT_TYPE),
        (STRING_VALUE, STRING_TYPE),
        (LIST_INT_VALUE, LIST_INT_TYPE),
        (TUPLE_INT_STRING_VALUE, TUPLE_INT_STRING_TYPE),
    ],
)
def test_typeof_bool(value: Any, type: typing.Type) -> None:
    """Test that typeof(value) returns the correct type."""
    assert typing.typeof(value) == type


@pytest.mark.typing
@pytest.mark.parametrize(
    "value,type",
    [
        (BOOL_VALUE, BOOL_TYPE),
        (INT_VALUE, INT_TYPE),
        (FLOAT_VALUE, FLOAT_TYPE),
        (STRING_VALUE, STRING_TYPE),
        (LIST_INT_VALUE, LIST_INT_TYPE),
        (TUPLE_INT_STRING_VALUE, TUPLE_INT_STRING_TYPE),
    ],
)
def test_isinstance_bool(value: Any, type: typing.Type) -> None:
    """Test that isinstance(value, type) returns the correct result."""
    assert typing.isinstance(value, type)
