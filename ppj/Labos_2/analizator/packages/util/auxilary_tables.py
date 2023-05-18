from typing import List, Set, Dict
from ..models import SyntaxAnalyzerDefinition, Production, Terminal, NonTerminal, StackSymbol, Symbol


def mark_empty_nonterminals(definiton: SyntaxAnalyzerDefinition):
    for production in definiton.productions:
        if len(production.right_side) == 1 and production.right_side[0] is None:
            production.left_side.empty = True

    changed = True
    while changed:
        changed = False
        for production in definiton.productions:
            if not production.left_side.empty:
                production.left_side.empty = True
                for symbol in production.right_side:
                    if isinstance(symbol, NonTerminal) and not symbol.empty or symbol.name != '$':
                        production.left_side.empty = False
                        break
                else:
                    changed = True


def find_direct_firsts(definition: SyntaxAnalyzerDefinition):
    for production in definition.productions:
        for symbol in production.right_side:
            if isinstance(symbol, Terminal) and symbol.name != '$':
                production.left_side.direct_first.add(symbol)
                break
            if isinstance(symbol, NonTerminal):
                production.left_side.direct_first.add(symbol)
                if not symbol.empty:
                    break


def find_firsts(definition: SyntaxAnalyzerDefinition):
    changed = True
    while changed:
        changed = False
        for production in definition.productions:
            for direct_first in production.left_side.direct_first:
                if isinstance(direct_first, Terminal):
                    if direct_first not in production.left_side.first:
                        production.left_side.first.add(direct_first)
                        changed = True
                elif isinstance(direct_first, NonTerminal):
                    for first in direct_first.first:
                        if first not in production.left_side.first:
                            production.left_side.first.add(first)
                            changed = True


def find_firsts_for_suffix(
        suffix: List[Symbol]) -> (Set[Terminal], bool):
    firsts = set()
    can_be_empty = False

    for next_symbol in suffix:
        if isinstance(next_symbol, Terminal) and next_symbol.name != '$':
            firsts.add(next_symbol)
            break
        elif isinstance(next_symbol, NonTerminal):
            sub_firsts = next_symbol.first
            firsts.update(sub_firsts)
            if not next_symbol.empty:
                break
    else:
        can_be_empty = True

    return firsts, can_be_empty or len(suffix) == 0
