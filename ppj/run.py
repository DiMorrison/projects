"""
Testing runner for PPJ Compiler
"""
from prevodilac.analizator.util import RegexSimplifier, init_regex
from prevodilac.analizator.lexical_generator import analyser_definition_parser, lex_generator
from prevodilac.analizator.LA import ucitaj_analizator, pokreni_analizator

if __name__ == '__main__':
    REGEX_FORMAT = 'A|(B*|C).'
    regex = init_regex(REGEX_FORMAT)
    regex.uljepsaj_imena_prijelaza()
    print(f"Compile regex to NFA: '{REGEX_FORMAT}'")
    print("NKA(\n" +
          "\tstanja = " + str(regex.stanja) + ",\n" +
          "\tpocetno_stanje = '" + str(regex.pocetno_stanje) + "',\n" +
          "\tprihvatljiva_stanja = " + str(regex.prihvatljiva_stanja) + ",\n" +
          "\tabeceda = " + str(regex.abeceda) + ",\n" +
          "\tprijelazi = " + str(regex.prijelazi) + "\n" +
          ")")

    examples = [
        'A',
        'B',
        'C.',
        '',
        'AB',
        'AC',
        'BC',
        'BC.',
        'BB.',
        '.',
        'CC.'
    ]
    for example in examples:
        runner = regex.inicijaliziraj_nka()
        #print(f"Ulaz: '{example}'")
        #print("Stanja: " + str(runner.current_states))
        for znak in example:
            runner.prijelaz(znak)
            #print("Znak: " + znak + ", Stanja: " + str(runner.current_states))
        print(f"Primjer: '{example}' -> {runner.prihvatljiv()}")


    print("\n"*3)
    print("Simplify regexes")
    simplifier = RegexSimplifier()
    examples = {
        'hexKonstanta': '0x{hexZnamenka}{hexZnamenka}*',
        'hexZnamenka': '{znamenka}|A|B|C|D|E|F',
        'znamenka': '0|1|2|3|4|5|6|7|8|9',
        'malo_slovo': 'a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z',
        'veliko_slovo': 'A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z',
        'slovo': '{malo_slovo}|{veliko_slovo}',
    }
    for name, regex in examples.items():
        simplifier.simplify(regex, name)
    print(simplifier.known_regexes)

    print("\n"*3)
    print("Parse lex definition and generate nfa-s")
    with open('simplePpjLang.lan') as file:
        definition = analyser_definition_parser.parse_lex_definition(file.read())
        analizator = lex_generator.generate_lex_analyser(definition)
        with open('prevodilac/analizator/tablica.txt', 'w') as file:
            file.write(analizator.serialize())

    print("\n"*3)
    print("Use analyser to find regex matches in simplePpjLang.in")
    analizator = ucitaj_analizator()
    with open('simplePpjLang.in') as file:
        result = pokreni_analizator(file.read(), analizator)
        with open('simplePpjLang.myout', 'w') as file:
            file.write('\n'.join(result))
