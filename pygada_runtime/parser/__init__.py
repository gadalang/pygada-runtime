"""Package containing a parser for the special syntax used by Gada."""
from __future__ import annotations

__all__ = ["type"]
from antlr4 import *
from .dist.GadaLexer import GadaLexer
from .dist.GadaParser import GadaParser
from .dist.GadaVisitor import GadaVisitor
from pygada_runtime import typing


class Visitor(GadaVisitor):
    def visitChunk(self, ctx: GadaParser.ChunkContext):
        return self.visit(ctx.block())

    def visitBlock(self, ctx: GadaParser.BlockContext):
        return self.visit(ctx.typeUnion())

    def visitTypeUnion(self, ctx: GadaParser.TypeUnionContext):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.typeVariable(0))

        return typing.UnionType(map(self.visit, ctx.typeVariable()))

    def visitTypeList(self, ctx: GadaParser.TypeListContext):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.typeUnion(0))

        return map(self.visit, ctx.typeUnion())

    def visitTypeVariable(self, ctx: GadaParser.TypeVariableContext):
        if ctx.operator:
            return typing.VariableType(self.visit(ctx.item))

        return self.visit(ctx.item)

    def visitType(self, ctx: GadaParser.TypeContext):
        if ctx.name:
            return {
                "any": typing.AnyType(),
                "int": typing.IntType(),
                "float": typing.FloatType(),
                "str": typing.StringType(),
                "bool": typing.BoolType(),
            }[ctx.name.text]

        if ctx.operator.text == "[":
            return typing.ListType(
                self.visit(ctx.listItem) if ctx.listItem else None
            )

        return typing.TupleType(self.visit(ctx.tupleItem))


def type(input: str, /) -> typing.Type:
    r"""Parse the textual representation of a Gada type.

    .. code-block:: python

        >>> from pygada_runtime import parser
        >>>
        >>> parser.type('any')
        AnyType()
        >>> parser.type('bool')
        BoolType()
        >>> parser.type('int')
        IntType()
        >>> parser.type('float')
        FloatType()
        >>> parser.type('str')
        StringType()
        >>> parser.type('[int]')
        ListType(IntType())
        >>> parser.type('*int')
        VariableType(IntType())
        >>> parser.type('(int, str)')
        TupleType([IntType(), StringType()])
        >>> parser.type('int | str')
        UnionType([IntType(), StringType()])
        >>>

    :param input: textual representation
    :return: represented type
    """
    # lexer
    lexer = GadaLexer(InputStream(input))
    stream = CommonTokenStream(lexer)
    # parser
    parser = GadaParser(stream)
    tree = parser.typeUnion()
    # evaluator
    visitor = Visitor()
    return visitor.visit(tree)
