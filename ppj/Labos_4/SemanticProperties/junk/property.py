from dataclasses import dataclass
from typing import Set, List


@dataclass
class Symbol:
    name: str
    is_terminal: bool
    derived_property: str
    value: str
    type: str
    l_expression: bool


@dataclass
class Terminal(Symbol):
    derived_property: str
    type: str

    def __init__(self, name: str, derived_property: str, type: str):
        super().__init__(name, True)
        self.derived_property = derived_property
        self.type = type

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Terminal({self.name})"

    def __hash__(self):
        return hash((self.name, self.is_terminal))


@dataclass
class NonTerminal(Symbol):
    direct_first: Set[Symbol]
    first: Set[Terminal]
    inherited_property: str
    derived_property: str
    type: str
    l_expression: bool
    types: List[str]
    empty: bool = False

    def __init__(self, name: str, inherited_property: str, derived_property: str, type: str, l_expression: bool):
        super().__init__(name, False)
        self.direct_first = set()
        self.first = set()
        self.inherited_property = inherited_property
        self.derived_property = derived_property
        self.type = type
        self.l_expression = l_expression
        self.types = list()

    def __str__(self):
        return self.name

    def __repr__(self):
        if len(self.first):
            return f"NonTerminal({self.name}, first={self.first})"
        return f"NonTerminal({self.name})"

    def __hash__(self):
        return hash((self.name, self.is_terminal))


@dataclass
class Property:
    left_nonTerminal: NonTerminal
    right_symbols: List[Symbol]

    def __init__(self, left_nonTerminal: NonTerminal, right_symbols: List[Symbol]):
        self.right_symbols = list()
        self.left_nonTerminal = left_nonTerminal
        self.right_symbols = right_symbols
