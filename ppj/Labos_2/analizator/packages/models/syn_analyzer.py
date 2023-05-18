from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Union
from ..models import Symbol, DkaState, Production, LexToken, Terminal


class ActionType(Enum):
    MOVE = 0
    REDUCE = 1
    PUSH = 2
    ACCEPT = 3


@dataclass
class StateAction:
    action: ActionType
    goto: int

    def short_name(self):
        if self.action == ActionType.MOVE:
            return f"P\033[94m{self.goto}\033[0m"
        if self.action == ActionType.REDUCE:
            return f"R\033[91m{self.goto}\033[0m"
        if self.action == ActionType.PUSH:
            return f"S\033[96m{self.goto}\033[0m"
        if self.action == ActionType.ACCEPT:
            return "\033[92mA\033[0m"

    def serialize(self) -> Dict:
        return {
            'action': self.action.value,
            'goto': self.goto
        }

    @staticmethod
    def deserialize(data: Dict) -> StateAction:
        return StateAction(
            action=ActionType(data['action']),
            goto=data['goto']
        )


@dataclass
class StateActions:
    state: DkaState
    actions: Dict[Symbol, StateAction] = field(default_factory=dict)

    def serialize(self) -> Dict:
        return {
            'state': {},
            'actions': {k.name: v.serialize() for k, v in self.actions.items()}
        }

    @staticmethod
    def deserialize(data: Dict, symbols: List[Symbol]) -> StateActions:
        return StateActions(
            state=DkaState(set()),
            actions={
                Symbol.deserialize({'name': k}, symbols): StateAction.deserialize(v)
                for k, v in data['actions'].items()
            }
        )


@dataclass
class LrTable:
    actions: List[StateActions] = field(default_factory=list)
    productions: List[Production] = field(default_factory=list)
    symbols: List[Symbol] = field(default_factory=list)
    synchronization_symbols: List[Terminal] = field(default_factory=list)

    def print_table(self):
        ordered_symbols = sorted(self.symbols, key=lambda x: (x.name.startswith('<') * 100, x.name))
        print("\033[95mState\033[0m|" + "|".join(['\033[1m ' + LrTable.__pad(symbol.name, 5) + '\033[0m' for symbol in ordered_symbols]) + "|")
        for index, state_actions in enumerate(self.actions):
            print(f"\033[1m{index:5}\033[0m|", end="")
            for symbol in ordered_symbols:
                column_length = len(LrTable.__pad(symbol.name, 5))
                if symbol in state_actions.actions:
                    action = state_actions.actions[symbol]
                    print(f" {LrTable.__pad(action.short_name(), column_length)}|", end="")
                else:
                    print(f" {LrTable.__pad('', column_length)}|", end="")
            print()
        print("\033[95mProductions\033[0m:")
        for index, production in enumerate(self.productions):
            print(f"\033[91m{index:5}\033[0m: {production.left_side} -> {' '.join(i.name if i is not None else '$' for i in production.right_side)}")

    @staticmethod
    def __pad(string: str, length: int) -> str:
        len_string = string.replace("\033[96m", "")
        len_string = len_string.replace("\033[95m", "")
        len_string = len_string.replace("\033[94m", "")
        len_string = len_string.replace("\033[92m", "")
        len_string = len_string.replace("\033[91m", "")
        len_string = len_string.replace("\033[1m", "")
        len_string = len_string.replace("\033[0m", "")
        return string + " " * (length - len(len_string))

    def get_symbol(self, name: str) -> Symbol:
        for symbol in self.symbols:
            if symbol.name == name:
                return symbol
        return None

    def serialize(self) -> Dict:
        return {
            'actions': [action.serialize() for action in self.actions],
            'productions': [production.serialize() for production in self.productions],
            'symbols': [symbol.serialize() for symbol in self.symbols],
            'synchronization_symbols': [symbol.serialize() for symbol in self.synchronization_symbols]
        }

    @staticmethod
    def deserialize(data: Dict) -> LrTable:
        deserialized_symbols = []
        symbols = [Symbol.deserialize(t, deserialized_symbols) for t in data['symbols']]
        productions = [Production.deserialize(t, deserialized_symbols) for t in data['productions']]
        actions = [StateActions.deserialize(t, deserialized_symbols) for t in data['actions']]
        synchronization_symbols = [Symbol.deserialize(t, deserialized_symbols) for t in data['synchronization_symbols']]
        return LrTable(
            actions=actions,
            productions=productions,
            symbols=symbols,
            synchronization_symbols=synchronization_symbols
        )


@dataclass
class LrNode:
    parent_symbol: Symbol
    nodes: List[Union[LrNode, LexToken]] = field(default_factory=list)

    def pretty_print(self, depth: int = 0, keep_parent: bool = False):
        if self.parent_symbol.name == "S'" and not keep_parent:
            if isinstance(self.nodes[0], LrNode):
                self.nodes[0].pretty_print(depth)
            else:
                print(self.nodes[0].name)
            return
        print(" " * depth, self.parent_symbol.name, sep="")
        if not self.nodes:
            print(" " * depth, "$")
        for node in self.nodes:
            if isinstance(node, LrNode):
                node.pretty_print(depth + 1, keep_parent)
            else:
                print(" " * depth, node.name, node.line, node.value)

    def short_repr(self, top=True):
        res = "LrNode" if top else ""
        res += f"({self.parent_symbol.name}:"
        res += ', '.join(t.short_repr(False) if isinstance(t, LrNode) else t.name for t in self.nodes)
        res += ")"
        return res
