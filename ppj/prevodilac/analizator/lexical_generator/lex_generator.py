"""
Modul za generiranje leksickog analizatora iz njegove definice.
"""
from typing import List
from ..util.simplify_regex import RegexSimplifier
from ..util.regex import init_regex
from ..models import DefinicijaLexAnalizatora, NamedRegex, Nka, LexAnalizator, PraviloAnalizatora


def generate_lex_analyser(definition: DefinicijaLexAnalizatora) -> LexAnalizator:
    """
    Generira leksicki analizator iz definicije.
    :param definition: Definicija leksickog analizatora.
    :return: Izvorni kod leksickog analizatora.
    """
    regex_simplifier = RegexSimplifier()
    for regex in definition.regexi:
        regex_simplifier.simplify(regex.regex, regex.name)
    jednostavni_regexi: List[NamedRegex] = [
        NamedRegex(regex.name, regex_simplifier.simplify(regex.regex, regex.name))
        for regex in definition.regexi
    ]
    definition.regexi = jednostavni_regexi
    for rule in definition.pravila:
        rule.regex = regex_simplifier.simplify(rule.regex)
        rule.nka = init_regex(rule.regex)
    analizator = combine_nka(definition)
    return analizator


def combine_nka(definition: DefinicijaLexAnalizatora) -> LexAnalizator:
    """
    Spaja sve NKA regexa i stanja analizatora u jedan
    :param definition: Definicija leksickog analizatora.
    """
    nka = Nka()
    analizator = LexAnalizator(nka, [])
    nka.pocetno_stanje = nka.dodaj_stanje(definition.pocetno_stanje)
    for index, rule in enumerate(definition.pravila):
        if rule.stanje not in nka.stanja:
            nka.dodaj_stanje(rule.stanje)
        final_state = nka.dodaj_stanje(f'P_{index}')
        processing_state = nka.dodaj_stanje(f'r_{index}')
        for state in rule.nka.stanja:
            if state == processing_state:
                continue
            nka.dodaj_epsilon_prijelaz(state, processing_state)
        nka.spoji_nka(rule.nka, rule.stanje, final_state)
        analizator.pravila.append(PraviloAnalizatora(final_state, rule.akcije))
    nka.uljepsaj_imena_prijelaza()
    return analizator
