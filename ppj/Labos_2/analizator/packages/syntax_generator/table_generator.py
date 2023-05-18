from typing import List
from ..models import StackSymbol, \
    SyntaxDka, LrTable, StateAction, StateActions, ActionType, Terminal, SyntaxAnalyzerDefinition
from ..util import remove_dot


def generate_tables(dka: SyntaxDka, definition: SyntaxAnalyzerDefinition) -> LrTable:
    table = LrTable()
    table.synchronization_symbols = definition.syn_symbols
    for dka_state in dka.states:
        action_list = StateActions(dka_state)

        for symbol in dka.find_transitions(dka_state):
            if symbol.is_terminal:
                action = StateAction(ActionType.MOVE, dka.states.index(dka.transitions[(dka_state, symbol)]))
            else:
                action = StateAction(ActionType.PUSH, dka.states.index(dka.transitions[(dka_state, symbol)]))
            action_list.actions[symbol] = action
            if symbol not in table.symbols:
                table.symbols.append(symbol)

        for nka_state in dka_state.nka_states:
            if nka_state.production and nka_state.production.is_reduce():
                base_production = remove_dot(nka_state.production)
                if base_production not in table.productions:
                    table.productions.append(base_production)
                base_production_index = table.productions.index(base_production)
                try:
                    base_production_def_index = definition.productions.index(base_production)
                except:
                    print(base_production)
                    print(definition.productions)
                    print("FAIL")
                for follow in nka_state.follows:
                    if follow not in action_list.actions or \
                            action_list.actions[follow].action == ActionType.REDUCE and \
                            base_production_def_index < definition.productions.index(
                                table.productions[action_list.actions[follow].goto]):
                        action_list.actions[follow] = StateAction(ActionType.REDUCE, base_production_index)
                        if follow not in table.symbols:
                            table.symbols.append(follow)
                        if base_production.left_side.name == "S'" and follow.name == StackSymbol().name:
                            action_list.actions[follow].action = ActionType.ACCEPT
        table.actions.append(action_list)
    return table
