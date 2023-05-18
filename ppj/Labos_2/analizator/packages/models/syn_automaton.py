from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set
from .syn_analyzer_definition import Symbol, Terminal, NonTerminal, StackSymbol, Dot,\
    Production, SyntaxAnalyzerDefinition


@dataclass
class NkaState:
    production: Production
    follows: Set[Terminal] = field(default_factory=set)
    is_start_state: bool = False
    frozen_hash: int = None

    def __init__(self, production: Optional[Production], follows: Set[Terminal] = None, is_start_state: bool = False):
        if not is_start_state and production is None:
            raise ValueError("Production must be provided for non-start state")
        self.production = production
        self.follows = follows or set()
        self.is_start_state = is_start_state
        self.frozen_hash = None

    def __hash__(self):
        if self.frozen_hash is not None:
            return self.frozen_hash
        return hash((self.production, tuple(self.follows), self.is_start_state))

    def __eq__(self, other):
        if not isinstance(other, NkaState):
            return False
        return \
            self is other or \
            (not self.frozen_hash or not other.frozen_hash or self.frozen_hash == other.frozen_hash) and \
            self.production == other.production and \
            self.follows == other.follows and \
            self.is_start_state == other.is_start_state

    def freeze(self):
        self.frozen_hash = hash(self)

    def pretty_print(self) -> str:
        if self.is_start_state:
            res = f"(START), " \
                "{" + "|".join([str(follow) for follow in self.follows]) + "}"
        else:
            res = \
                f"{self.production.left_side.name} -> " + \
                f"{''.join([str(symbol) for symbol in self.production.right_side])}, " + \
                "{" + "|".join([str(follow) for follow in self.follows]) + "}"
        return res


@dataclass
class DkaState:
    nka_states: Set[NkaState] = field(default_factory=set)

    def __hash__(self):
        return hash(tuple(self.nka_states))

    def __eq__(self, other):
        return tuple(self.nka_states) == tuple(other.nka_states)

    def pretty_print(self) -> str:
        return f"{{" + ", ".join([nka_state.pretty_print() for nka_state in self.nka_states]) + "}"

    def __str__(self):
        return self.pretty_print()

    def __eq__(self, other):
        if not isinstance(other, DkaState):
            return False
        return self.nka_states == other.nka_states

    def combine_follows(self) -> DkaState:
        follows: Dict[Production, Set[Terminal]] = {}
        for nka_state in self.nka_states:
            if nka_state.production not in follows:
                follows[nka_state.production] = set()
            follows[nka_state.production].update(nka_state.follows)
        return DkaState({NkaState(production, follows[production]) for production in follows})


@dataclass
class SyntaxNka:
    states: List[NkaState]
    start_state: NkaState
    transitions: Dict[NkaState, List[Tuple[Symbol, NkaState]]]

    def pretty_print(self, print_states: bool = True, print_transitions: bool = True):
        print(f"NKA, transitions: {len(self.transitions)}, states: {len(self.states)}, start state: {self.start_state}")
        if print_states:
            print("\tStates:")
            states_to_print = self.states if len(self.states) < 100 else self.states[:50] + self.states[-50:]
            for state in states_to_print:
                print(f"\t\t[{state.pretty_print()}]")
        if print_transitions:
            print("\tTransitions:")
            trans_to_print = list(self.transitions.items())
            trans_to_print = trans_to_print if len(trans_to_print) < 100 else trans_to_print[:50] + trans_to_print[-50:]
            for index, (state, transitions) in enumerate(trans_to_print):
                for symbol, next_state in transitions:
                    print(f"\t\t{index}. [{state.pretty_print()}] \033[94m--\033[96m{symbol.name}\033[94m-->\033[0m [{next_state.pretty_print()}]")
        print()

    def __hash__(self):
        return hash(0)


@dataclass
class SyntaxDka:
    states: List[DkaState]
    start_state: DkaState
    transitions: Dict[Tuple[DkaState, Symbol], DkaState]

    def pretty_print(self, print_states: bool = True, print_transitions: bool = True):
        print(f"DKA, transitions: {len(self.transitions)}, states: {len(self.states)},\nstart state: {self.start_state.pretty_print()}")
        if print_states:
            print("\tStates:")
            states_to_print = self.states if len(self.states) < 100 else self.states[:50] + self.states[-50:]
            for state in states_to_print:
                print(f"\t\t[{state.pretty_print()}]", end="\t")
            print()
        if print_transitions:
            print("\tTransitions:")
            trans_to_print = list(self.transitions.items())
            trans_to_print = trans_to_print if len(trans_to_print) < 100 else trans_to_print[:50] + trans_to_print[-50:]
            for index, ((state, symbol), next_state) in enumerate(trans_to_print):
                print(f"\t\t{index}. [{state.pretty_print()}] \033[94m--\033[96m{symbol.name}\033[94m-->\033[0m [{next_state.pretty_print()}]")
        print()

    def find_transitions(self, state: DkaState) -> List[Symbol]:
        return [symbol for (s, symbol) in self.transitions.keys() if s == state]
