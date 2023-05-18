from typing import List, Set, Dict, Union
from json import loads
from sys import stderr
from ..models import LrTable, LexToken, LrNode, ActionType, NonTerminal, StackSymbol


def load_analyzer(file: str = "analizator/tablica.json") -> LrTable:
    with open(file) as f:
        table = LrTable.deserialize(loads(f.read()))
    return table


def load_tokens(data: str) -> List[LexToken]:
    tokens: List[LexToken] = []
    for line in data.splitlines():
        name, line, value = line.split(maxsplit=2)
        tokens.append(LexToken(name, value, int(line)))
    return tokens


def run_analyzer(tokens: List[LexToken], analyzer: LrTable) -> LrNode:
    first_non_terminal = NonTerminal("S'")
    lr_tree = LrNode(first_non_terminal)
    stack = [first_non_terminal, 0]
    current_token = 0
    while True:
        current_state = stack[-1]
        current_symbol = tokens[current_token] if current_token < len(tokens) else StackSymbol()
        action = analyzer.actions[current_state].actions.get(analyzer.get_symbol(current_symbol.name), None)
        if action is None:
            error_row = tokens[current_token].line
            error_expected = '[' + ''.join(map(lambda t: t.name, analyzer.actions[current_state].actions.keys())) + ']'
            error_read_token = tokens[current_token].name + "('" + tokens[current_token].value + "')"
            error_message = f"Error at line {error_row}: expected one of {error_expected}, read {error_read_token}"
            print(error_message, file=stderr)
            while current_token < len(tokens):
                current_symbol = tokens[current_token]
                if analyzer.get_symbol(current_symbol.name) in analyzer.synchronization_symbols:
                    break
                current_token += 1
            syn_symbol = analyzer.get_symbol(current_symbol.name)
            while True:
                current_state = stack[-1]
                action = analyzer.actions[current_state].actions.get(syn_symbol, None)
                if action is not None:
                    break
                if len(lr_tree.nodes) == 0 or len(stack) == 0:
                    return lr_tree
                stack.pop(-1)
                stack.pop(-1)
                lr_tree.nodes.pop(-1)
        if action.action == ActionType.MOVE:
            if current_symbol.name == '⊥':
                break
            stack.append(current_symbol)
            stack.append(action.goto)
            lr_tree.nodes.append(current_symbol)
            current_token += 1
        elif action.action == ActionType.REDUCE:
            production = analyzer.productions[action.goto]
            new_node = LrNode(production.left_side)
            if production.right_side[0]:
                for i in range(len(production.right_side)):
                    _ = stack.pop(-1)
                    _ = stack.pop(-1)
                    new_node.nodes.append(lr_tree.nodes.pop(-1))
            new_node.nodes.reverse()
            lr_tree.nodes.append(new_node)
            stack.append(production.left_side)
            stack.append(analyzer.actions[stack[-2]].actions[production.left_side].goto)
        elif action.action == ActionType.PUSH:
            stack.append(current_symbol)
            stack.append(action.goto)
            lr_tree.add_child(current_symbol, None)
        elif action.action == ActionType.ACCEPT:
            return lr_tree
        else:
            raise Exception("Invalid syntax")