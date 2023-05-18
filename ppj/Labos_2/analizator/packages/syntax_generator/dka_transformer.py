from typing import List, Tuple, Dict, Optional, Set
from collections import deque
from .enka_generator import find_symbol_after_dot
from ..models import SyntaxAnalyzerDefinition, Production, Terminal, NonTerminal, StackSymbol, \
    Symbol, Dot, NkaState, SyntaxNka, DkaState, SyntaxDka


def get_epsilon_closure(nka: SyntaxNka, state: NkaState) -> Set[NkaState]:
    closure = {state}
    next_closure = {}
    while len(next_closure) != len(closure):
        next_closure = closure.copy()
        for state in next_closure:
            for symbol, next_state in nka.transitions.get(state, []):
                if symbol.name == "$":
                    closure.add(next_state)
    return closure


def transform_to_dka(nka: SyntaxNka) -> SyntaxDka:
    states: List[DkaState] = []
    transitions: Dict[Tuple[DkaState, Symbol], DkaState] = {}

    dka_start_state = DkaState(get_epsilon_closure(nka, nka.start_state))
    states.append(dka_start_state)
    queue = deque([dka_start_state])
    while queue:
        dka_state = queue.popleft()
        next_states: Dict[Symbol, DkaState] = {}
        for nka_state in dka_state.nka_states:
            for symbol, next_nka_state in nka.transitions.get(nka_state, []):
                if symbol.name == "$":
                    continue
                if symbol not in next_states:
                    next_states[symbol] = DkaState()
                if isinstance(find_symbol_after_dot(next_nka_state.production), Terminal):
                    next_states[symbol].nka_states.update({next_nka_state})
                else:
                    next_states[symbol].nka_states.update(get_epsilon_closure(nka, next_nka_state))
        for symbol, next_state in next_states.items():
            if next_state not in states:
                states.append(next_state)
                queue.append(next_state)
            else:
                next_state = states[states.index(next_state)]
            transitions[(dka_state, symbol)] = next_state

    dka = SyntaxDka(states, dka_start_state, transitions)
    return dka
