# Generated from gada\parser\dist\Gada.g4 by ANTLR 4.10.1
from antlr4 import *

if __name__ is not None and "." in __name__:
    from .GadaParser import GadaParser
else:
    from GadaParser import GadaParser

# This class defines a complete listener for a parse tree produced by GadaParser.
class GadaListener(ParseTreeListener):

    # Enter a parse tree produced by GadaParser#chunk.
    def enterChunk(self, ctx: GadaParser.ChunkContext):
        pass

    # Exit a parse tree produced by GadaParser#chunk.
    def exitChunk(self, ctx: GadaParser.ChunkContext):
        pass

    # Enter a parse tree produced by GadaParser#block.
    def enterBlock(self, ctx: GadaParser.BlockContext):
        pass

    # Exit a parse tree produced by GadaParser#block.
    def exitBlock(self, ctx: GadaParser.BlockContext):
        pass

    # Enter a parse tree produced by GadaParser#typeUnion.
    def enterTypeUnion(self, ctx: GadaParser.TypeUnionContext):
        pass

    # Exit a parse tree produced by GadaParser#typeUnion.
    def exitTypeUnion(self, ctx: GadaParser.TypeUnionContext):
        pass

    # Enter a parse tree produced by GadaParser#typeList.
    def enterTypeList(self, ctx: GadaParser.TypeListContext):
        pass

    # Exit a parse tree produced by GadaParser#typeList.
    def exitTypeList(self, ctx: GadaParser.TypeListContext):
        pass

    # Enter a parse tree produced by GadaParser#typeVariable.
    def enterTypeVariable(self, ctx: GadaParser.TypeVariableContext):
        pass

    # Exit a parse tree produced by GadaParser#typeVariable.
    def exitTypeVariable(self, ctx: GadaParser.TypeVariableContext):
        pass

    # Enter a parse tree produced by GadaParser#type.
    def enterType(self, ctx: GadaParser.TypeContext):
        pass

    # Exit a parse tree produced by GadaParser#type.
    def exitType(self, ctx: GadaParser.TypeContext):
        pass


del GadaParser
