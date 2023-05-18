"""
A module with methods for parsing the analyser definition file content.
"""
from ..models import \
    DefinicijaLexAnalizatora, PraviloDefinicijeAnalizatora, TipAkcijeAnalizatora, AkcijaAnalizatora, NamedRegex


def parse_lex_definition(content: str) -> DefinicijaLexAnalizatora:
    """
    Parses the analyser definition file content.
    :param content: The content of the analyser definition file.
    :return: The analyser definition.
    """
    lines = iter(content.splitlines())
    definition = DefinicijaLexAnalizatora()
    line_state = 'regex'
    for line in lines:
        line = line.strip()
        if line.startswith('%X'):
            line_state = 'states'
        if line.startswith('%L'):
            line_state = 'tokens'
        if line.startswith('<'):
            line_state = 'rules'
        if line_state == 'regex':
            name, regex = line[1:].split('} ', maxsplit=1)
            definition.regexi.add(NamedRegex(name, regex))
        elif line_state == 'states':
            states = line[2:].split()
            definition.pocetno_stanje = states[0]
            definition.stanja.update(states)
        elif line_state == 'tokens':
            definition.jedinke.update(line[2:].split())
        elif line_state == 'rules':
            state, regex = line[1:].split('>', maxsplit=1)
            line = next(lines).strip()
            assert line.startswith('{'), 'Expected { in line: ' + line
            line = next(lines).strip()
            actions = [AkcijaAnalizatora(TipAkcijeAnalizatora.IME_JEDINKE, line)]
            while True:
                line = next(lines).strip()
                if line == '}':
                    break
                action, *args = line.split()
                if action == 'VRATI_SE':
                    actions.append(AkcijaAnalizatora(TipAkcijeAnalizatora.VRATI_SE, int(args[0])))
                elif action == 'UDJI_U_STANJE':
                    actions.append(AkcijaAnalizatora(TipAkcijeAnalizatora.UDJI_U_STANJE, args[0]))
                elif action == 'NOVI_REDAK':
                    actions.append(AkcijaAnalizatora(TipAkcijeAnalizatora.NOVI_REDAK))
            udji_u_stanje = next((a for a in actions if a.tip == TipAkcijeAnalizatora.UDJI_U_STANJE), None)
            if not udji_u_stanje:
                udji_u_stanje = AkcijaAnalizatora(TipAkcijeAnalizatora.UDJI_U_STANJE, state)
                actions.append(udji_u_stanje)
            definition.pravila.append(PraviloDefinicijeAnalizatora(state, regex, actions))
    return definition
