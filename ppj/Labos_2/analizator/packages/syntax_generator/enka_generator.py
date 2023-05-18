from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, field
from collections import deque
from ..models import SyntaxAnalyzerDefinition, Production, Terminal, NonTerminal, StackSymbol,\
    Symbol, Dot, NkaState, SyntaxNka
from ..util import mark_empty_nonterminals, find_direct_firsts, find_firsts,\
    generate_subproductions, find_firsts_for_suffix


def prepare_definition(definition: SyntaxAnalyzerDefinition):
    mark_empty_nonterminals(definition)
    find_direct_firsts(definition)
    find_firsts(definition)


def find_symbol_after_dot(production: Production) -> Optional[Symbol]:
    for symbol, next_symbol in zip(production.right_side, production.right_side[1:]):
        if isinstance(symbol, Dot):
            return next_symbol
    return None


def find_suffix_second_after_dot(production: Production) -> List[Symbol]:
    for index in range(len(production.right_side) - 1):
        if isinstance(production.right_side[index], Dot):
            return production.right_side[index + 2:]


@dataclass
class QueueItem:
    previous: NkaState
    next: NkaState
    is_epsilon: bool


def generate_enka(definition: SyntaxAnalyzerDefinition) -> SyntaxNka:
    prepare_definition(definition)
    epsilon = definition.find_symbol('$')
    states: List[NkaState] = []
    transitions: Dict[NkaState, List[Tuple[Symbol, NkaState]]] = {}
    start_state = NkaState(None, follows={StackSymbol()}, is_start_state=True)
    states.append(start_state)

    start_subproductions = generate_subproductions(definition.start_production)
    queue = deque([QueueItem(previous=start_state, next=NkaState(start_subproductions[0]), is_epsilon=False)])
    for item in start_subproductions[1:]:
        queue.append(QueueItem(previous=queue[-1].next, next=NkaState(item), is_epsilon=False))
    while queue:
        state = queue.popleft()
        if not state.is_epsilon:
            state.next.follows = state.previous.follows.copy()
        else:
            suffix_after_dot = find_suffix_second_after_dot(state.previous.production)
            starts_with, can_be_empty = find_firsts_for_suffix(suffix_after_dot)
            state.next.follows = starts_with
            if can_be_empty:
                state.next.follows.update(state.previous.follows.copy())
        state.next.freeze()
        if state.previous not in transitions:
            transitions[state.previous] = []
        if state.next not in states:
            states.append(state.next)
            if state.previous.is_start_state or state.is_epsilon:
                transitions[state.previous].append((epsilon, state.next))
            else:
                transitions[state.previous].append((find_symbol_after_dot(state.previous.production), state.next))
        else:
            existing_state = states[states.index(state.next)]
            if state.previous.is_start_state or state.is_epsilon:
                transitions[state.previous].append((epsilon, existing_state))
            else:
                transitions[state.previous].append((find_symbol_after_dot(state.previous.production), existing_state))
            continue

        next_symbol = find_symbol_after_dot(state.next.production)
        if next_symbol is None:
            continue
        if isinstance(next_symbol, NonTerminal):
            # find all productions for this nonterminal
            next_productions = []
            for production in definition.productions:
                if production.left_side == next_symbol:
                    next_productions.append(production)
            for production in next_productions:
                subproductions = generate_subproductions(production)
                queue.append(QueueItem(previous=state.next, next=NkaState(subproductions[0]), is_epsilon=True))
                for item in subproductions[1:]:
                    queue.append(QueueItem(previous=queue[-1].next, next=NkaState(item), is_epsilon=False))

    return SyntaxNka(states, start_state, transitions)
