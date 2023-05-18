"""
Pojednostavljanje regularnih izraza.
"""
from typing import Dict, Set, Optional
from .bracket_finder import find_closing_bracket


class RegexSimplifier:
    """
    Klasa koja predstavlja regularne izraze, zamjenjujući aliase drugih
    regularnih izraza koji su već poznati.
    """
    def __init__(self):
        self.known_regexes: Dict[str, str] = dict()
        self.waiting_for_regex: Dict[str, Set[str]] = dict()

    def simplify(self, regex: str, regex_name: Optional[str] = None) -> str:
        """
        Pojednostavljuje regularni izraz i dodaje ga u listu poznatih regularnih izraza.
        """
        regex = self._simplify(regex_name, regex)
        if regex_name:
            self.known_regexes[regex_name] = regex
            self._fix_waiting_regexes(regex_name)

        return regex

    def _fix_waiting_regexes(self, regex_name, depth=0):
        if depth == 10:
            return
        if self.waiting_for_regex.get(regex_name):
            waiting_for_regex = self.waiting_for_regex[regex_name]
            self.waiting_for_regex[regex_name] = set()
            for waiting_regex in waiting_for_regex:
                if self.known_regexes.get(waiting_regex):
                    self.known_regexes[waiting_regex] = self._simplify(
                        waiting_regex,
                        self.known_regexes[waiting_regex])
                    self._fix_waiting_regexes(regex_name, depth + 1)

    def _simplify(self, regex_name: str, regex: Optional[str]) -> str:
        """
        Pojednostavljuje regularni izraz.
        """
        new_regex = ""
        i = 0
        escaping = False
        while i < len(regex):
            char = regex[i]
            if char == '\\' and not escaping:
                escaping = True
                new_regex += char
                i += 1
                continue
            if escaping:
                escaping = False
                new_regex += char
                i += 1
                continue
            if char == '{':
                end_bracket_index = find_closing_bracket(regex, i, '{}')
                sub_regex_name = regex[i + 1:end_bracket_index]
                if sub_regex_name in self.known_regexes:
                    new_regex += '(' + self.known_regexes[sub_regex_name] + ')'
                    if regex_name and sub_regex_name in [j for k in self.waiting_for_regex.values() for j in k]:
                        if sub_regex_name not in self.waiting_for_regex:
                            self.waiting_for_regex[sub_regex_name] = set()
                        self.waiting_for_regex[sub_regex_name].add(regex_name)
                else:
                    new_regex += regex[i:end_bracket_index + 1]
                    if regex_name:
                        if sub_regex_name not in self.waiting_for_regex:
                            self.waiting_for_regex[sub_regex_name] = set()
                        self.waiting_for_regex[sub_regex_name].add(regex_name)
                i = end_bracket_index + 1
                continue
            new_regex += char
            i += 1
        return new_regex
