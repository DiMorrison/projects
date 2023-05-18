"""
Modul sa funkcijom init_regex koja prima regularni izraz i vraca NKA koji
prepoznaje taj regularni izraz.
Modul također sadrži funkcije koje se koriste u init_regex.
"""

from typing import List
from uuid import uuid4 as Guid
from ..models import Nka, ParStanja
from .bracket_finder import find_closing_bracket, is_operator


def init_regex(regex_format: str) -> Nka:
    """
    Inicijalizacija automata koji prepoznaje regularni izraz.
    """
    nka = Nka()
    start, accepted = convert_to_nfa(regex_format, nka)
    nka.pocetno_stanje = start
    nka.prihvatljiva_stanja = {accepted}
    return nka


def convert_to_nfa(regex_format: str, nfa: Nka) -> ParStanja:
    """
    Pretvara regularni izraz u NKA.
    """
    izbori = split_on_or_operator(regex_format)
    lijevo_stanje = nfa.dodaj_stanje(Guid())
    desno_stanje = nfa.dodaj_stanje(Guid())
    if len(izbori) > 1:
        for izbor in izbori:
            privremeno = convert_to_nfa(izbor, nfa)
            nfa.dodaj_epsilon_prijelaz(lijevo_stanje, privremeno.lijevo_stanje)
            nfa.dodaj_epsilon_prijelaz(privremeno.desno_stanje, desno_stanje)
        return ParStanja(lijevo_stanje, desno_stanje)
    escaped = False
    zadnje_stanje = lijevo_stanje
    i = 0
    while i < len(regex_format):
        char = regex_format[i]
        if escaped:
            escaped = False
            prijelazni_znak = unescape_symbol(char)
            start = nfa.dodaj_stanje(Guid())
            end = nfa.dodaj_stanje(Guid())
            nfa.dodaj_prijelaz(ParStanja(start, end), prijelazni_znak)
        else:
            if char == '\\':
                escaped = True
                i = i + 1
                continue

            if char != '(':
                start = nfa.dodaj_stanje(Guid())
                end = nfa.dodaj_stanje(Guid())
                if char == '$':
                    nfa.dodaj_epsilon_prijelaz(start, end)
                else:
                    nfa.dodaj_prijelaz(ParStanja(start, end), char)
            else:
                j = find_closing_bracket(regex_format, i)
                privremeno = convert_to_nfa(regex_format[i + 1:j], nfa)
                start = privremeno.lijevo_stanje
                end = privremeno.desno_stanje
                i = j

        # provjera ponavljanja
        if i + 1 < len(regex_format) and regex_format[i + 1] == '*':
            new_start = start
            new_end = end
            start = nfa.dodaj_stanje(Guid())
            end = nfa.dodaj_stanje(Guid())
            nfa.dodaj_epsilon_prijelaz(start, new_start)
            nfa.dodaj_epsilon_prijelaz(new_end, end)
            nfa.dodaj_epsilon_prijelaz(start, end)
            nfa.dodaj_epsilon_prijelaz(new_end, new_start)
            i = i + 1

        # povezivanje s prethodnim podizrazon
        nfa.dodaj_epsilon_prijelaz(zadnje_stanje, start)
        zadnje_stanje = end
        i = i + 1
    nfa.dodaj_epsilon_prijelaz(zadnje_stanje, desno_stanje)
    return ParStanja(lijevo_stanje, desno_stanje)


def split_on_or_operator(regex_format: str) -> List[str]:
    """
    Vraca listu podizraza regularnog izraza razdvojenih operatorom ili '|'.
    """
    depth = 0
    result = []
    current_index = 0
    for i, char in enumerate(regex_format):
        if char == '(' and is_operator(regex_format, i):
            depth = depth + 1
        elif char == ')' and is_operator(regex_format, i):
            depth = depth - 1
        if char == '|' and depth == 0 and is_operator(regex_format, i):
            result.append(regex_format[current_index:i])
            current_index = i + 1
    rest = regex_format[current_index:]
    if rest:
        result.append(rest)
    return result


def unescape_symbol(char: str) -> str:
    """
    Vraca znak koji se dobije izbacivanjem escape znaka.
    """
    if char == 't':
        return '\t'
    if char == 'n':
        return '\n'
    if char == '_':
        return ' '
    return char
