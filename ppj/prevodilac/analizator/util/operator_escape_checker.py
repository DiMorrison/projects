"""
Metode za provjeru je li operator na poziciji unescaped
"""


def is_operator(regex_format: str, i: int) -> bool:
    """
    Vraca True ako je karakter na poziciji i operator, inace False.
    """
    n_of_backslashes = 0
    while i - 1 >= 0 and regex_format[i - 1] == '\\':
        n_of_backslashes = n_of_backslashes + 1
        i = i - 1
    return n_of_backslashes % 2 == 0
