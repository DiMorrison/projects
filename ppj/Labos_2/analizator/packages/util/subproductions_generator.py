from typing import List
from ..models import Production, Dot


def generate_subproductions(old_production: Production) -> List[Production]:
    subproductions = []
    if old_production.right_side[0] is None:
        return [Production(
            old_production.left_side,
            [Dot()]
        )]
    for i in range(len(old_production.right_side) + 1):
        production = Production(
            old_production.left_side,
            old_production.right_side[:i] + [Dot()] + old_production.right_side[i:]
        )
        subproductions.append(production)
    # print(f"{old_production.left_side.name} -> `{''.join([symbol.name for symbol in old_production.right_side])}` into:")
    # for subproduction in subproductions:
    #     print(f"    {subproduction.left_side.name} -> {''.join([symbol.name for symbol in subproduction.right_side])}")
    return subproductions


def remove_dot(production: Production) -> Production:
    return Production(
        production.left_side,
        [symbol for symbol in production.right_side if not isinstance(symbol, Dot)] or [None]
    )