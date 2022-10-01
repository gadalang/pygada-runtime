# Generated from gada\parser\dist\Gada.g4 by ANTLR 4.10.1
from antlr4 import *

if __name__ is not None and "." in __name__:
    from .GadaParser import GadaParser
else:
    from GadaParser import GadaParser

# This class defines a complete generic visitor for a parse tree produced by GadaParser.


class GadaVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by GadaParser#chunk.
    def visitChunk(self, ctx: GadaParser.ChunkContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GadaParser#block.
    def visitBlock(self, ctx: GadaParser.BlockContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GadaParser#typeUnion.
    def visitTypeUnion(self, ctx: GadaParser.TypeUnionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GadaParser#typeList.
    def visitTypeList(self, ctx: GadaParser.TypeListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GadaParser#typeVariable.
    def visitTypeVariable(self, ctx: GadaParser.TypeVariableContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GadaParser#type.
    def visitType(self, ctx: GadaParser.TypeContext):
        return self.visitChildren(ctx)


del GadaParser
