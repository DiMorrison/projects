"""
Metode za traženje zagrada u regexima
"""
from ..exceptions.invalid_regex_exception import InvalidRegexException
from .operator_escape_checker import is_operator


def find_closing_bracket(regex_format: str, i: int, bracket_type='()') -> int:
    """
    Vraca indeks zatvarajuce zagrade za zagradu na poziciji i unutar regularnog izraza.
    """
    depth = 1
    for index, j in enumerate(regex_format[i + 1:]):
        if j == bracket_type[0] and is_operator(regex_format, i + index + 1):
            depth = depth + 1
        elif j == bracket_type[1] and is_operator(regex_format, i + index + 1):
            depth = depth - 1
            if depth == 0:
                return index + i + 1
    raise InvalidRegexException(
        "Missing closing bracket:\n" +
        f"'{regex_format}'\n" +
        f" {' '*i}^\n" +
        f" {' '*i}| this bracket doesn't have a closing pair\n")
