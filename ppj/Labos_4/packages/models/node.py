from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Union


class Type(Enum):
    VOID = "VOID"
    INT = "INT"
    CHAR = "CHAR"
    ARRAY_INT = "ARRAY_INT"
    ARRAY_CHAR = "ARRAY_CHAR"
    ARRAY_CONST_CHAR = "ARRAY_CONST_CHAR"
    ARRAY_CONST_INT = "ARRAY_CONST_INT"
    FUNCTION = "FUNCTION"
    FUNCTION_DECLARATION = "FUNCTION_DECLARATION"


@dataclass
class FunctionType:
    return_type: Type
    argument_types: List[Type]
    only_declaration: bool


# klasa koja modelira čvor u stablu
@dataclass
class Node:
    name: str
    parent: int
    children: List[int]
    index: int

    production: Tuple[str, List[str]]

    type: Union[Type, FunctionType]
    ntype: Type
    number_of_elements: int
    const_type: bool
    const_ntype: bool
    l_expression: bool

    value: str
    types: List[Type]  # [atr1, atr2,...]
    names: List[str]

    def __init__(self, name: str, index: int, parent: int):
        self.name = name
        self.index = index
        self.parent = parent
        self.children = list()
        self.production = (self.name, [])
        self.l_expression = False
        self.const_type = False
        self.types = []
        self.names = []
        self.value = ""
        self.ntype = None
        self.const_ntype = False
        self.type = None
        self.number_of_elements = 0

    def bnf(self, tree):
        res = self.name + " ::="
        for child in self.children:
            child = next((x for x in tree.nodes if x.index == child), None)
            if child.value:
                name, line, value = child.name.split(" ")
                res += " " + name + "(" + line + "," + value + ")"
            else:
                res += " " + child.name
        return res

    def __str__(self):
        return self.name + ", Index: " + self.index.__str__() + ", Parent: " + self.parent.__str__() + \
               ", Children : " + self.children.__str__() + ", Production: " + self.production.__str__() + \
               ", Value:" + self.value.__str__()
