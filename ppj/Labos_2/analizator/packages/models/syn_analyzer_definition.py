from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Set, Dict


@dataclass
class Symbol:
    name: str
    is_terminal: bool

    def serialize(self) -> Dict:
        return {
            'name': self.name,
            'is_terminal': self.is_terminal
        }

    @staticmethod
    def deserialize(data: Dict, symbols: List[Symbol]) -> Symbol:
        if '$' in data['name']:
            return None
        if '•' in data['name']:
            return Dot()
        elif '⊥' in data['name']:
            return StackSymbol()
        else:
            existing = next((t for t in symbols if t.name == data['name']), None)
            if existing is not None:
                return existing
            if data['is_terminal']:
                new_symbol = Terminal(data['name'])
            else:
                new_symbol = NonTerminal(data['name'])
            symbols.append(new_symbol)
            return new_symbol


@dataclass
class Terminal(Symbol):
    def __init__(self, name: str):
        super().__init__(name, True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Terminal({self.name})"

    def __hash__(self):
        return hash((self.name, self.is_terminal))


@dataclass
class StackSymbol(Terminal):
    def __init__(self):
        super().__init__('⊥')

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"⊥()"

    def __hash__(self):
        return hash((self.name, self.is_terminal))

    def __eq__(self, other):
        return isinstance(other, StackSymbol)


@dataclass
class NonTerminal(Symbol):
    direct_first: Set[Symbol]
    first: Set[Terminal]
    empty: bool = False

    def __init__(self, name: str):
        super().__init__(name, False)
        self.direct_first = set()
        self.first = set()

    def __str__(self):
        return self.name

    def __repr__(self):
        if len(self.first):
            return f"NonTerminal({self.name}, first={self.first})"
        return f"NonTerminal({self.name})"

    def __hash__(self):
        return hash((self.name, self.is_terminal))


@dataclass
class Dot(NonTerminal):
    def __init__(self):
        super().__init__("\033[92m•\033[0m")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Dot()"

    def __hash__(self):
        return hash((self.name + 'TERMINAL'))

    def __eq__(self, other):
        return isinstance(other, Dot)


@dataclass
class Production:
    left_side: NonTerminal
    right_side: List[Symbol]

    def find_suffix(self):
        for i in range(len(self.right_side)):
            if isinstance(self.right_side[i], Dot):
                return self.right_side[i + 1:]
        raise Exception("No dot in production")

    def __hash__(self):
        return hash((self.left_side, tuple(self.right_side)))

    def __eq__(self, other):
        if not isinstance(other, Production):
            return False
        return \
            self is other or \
            self.left_side == other.left_side and tuple(self.right_side) == tuple(other.right_side)

    def is_reduce(self):
        return isinstance(self.right_side[-1], Dot)

    def serialize(self) -> Dict:
        return {
            'left_side': self.left_side.serialize(),
            'right_side': [(symbol or Terminal("$")).serialize() for symbol in self.right_side]
        }

    @staticmethod
    def deserialize(data: Dict, symbols: List[Symbol]) -> Production:
        return Production(
            Symbol.deserialize(data['left_side'], symbols),
            [Symbol.deserialize(symbol, symbols) for symbol in data['right_side']]
        )

@dataclass
class SyntaxAnalyzerDefinition:
    start_symbol: NonTerminal
    non_terminals: List[NonTerminal]
    terminals: List[Terminal]
    syn_symbols: List[Terminal]
    productions: List[Production]
    start_production: Production = field(init=False)

    def find_symbol(self, name: str):
        for symbol in self.non_terminals + self.terminals:
            if symbol.name == name:
                return symbol
        raise Exception(f"Symbol {name} not found")

    def __repr__(self):
        return f"""SyntaxAnalyzerDefinition(
    start_symbol={self.start_symbol},
    non_terminals={self.non_terminals},
    terminals={self.terminals},
    syn_symbols={self.syn_symbols},
    productions=[
        """ + ",\n\t\t".join([f"{prod}" for prod in self.productions]) + """
    ]
)"""
