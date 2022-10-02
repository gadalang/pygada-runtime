"""Tests on the **gada.parser** module."""
import pytest
from pygada_runtime import typing, parser


@pytest.mark.parser
@pytest.mark.parametrize(
    "input,type",
    [
        ("int", typing.IntType()),
        ("float", typing.FloatType()),
        (
            "(int, int, [[int | float]])",
            typing.TupleType(
                [
                    typing.IntType(),
                    typing.IntType(),
                    typing.ListType(
                        typing.ListType(
                            typing.UnionType(
                                [typing.IntType(), typing.FloatType()]
                            )
                        )
                    ),
                ]
            ),
        ),
    ],
)
def test_parse_int(input: str, type: typing.Type) -> None:
    """Test **parser.type** output."""
    assert parser.type(input) == type
