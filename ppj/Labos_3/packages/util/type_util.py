from ..models.node import Type


def has_implicit_cast(from_: Type, to: Type) -> bool:
    if from_ == to:
        return True
    if from_ == Type.CHAR:
        if to == Type.INT:
            return True
        return False
    if from_ == Type.ARRAY_INT:
        if to == Type.ARRAY_CONST_INT:
            return True
        return False
    if from_ == Type.ARRAY_CHAR:
        if to == Type.ARRAY_CONST_CHAR:
            return True
        return False
    return False


def has_explicit_cast(from_: Type, to: Type) -> bool:
    if has_implicit_cast(from_, to):
        return True
    if from_ == Type.INT:
        if to == Type.CHAR:
            return True
        return False
    return False


def check_type_range(type_: Type, value) -> bool:
    value = int(value)
    if type_ == Type.INT:
        return -2147483647 <= value <= 2147483647
    if type_ == Type.CHAR:
        return 0 <= value <= 255
    return False


