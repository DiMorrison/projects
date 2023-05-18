import sys
from analizator.lexical_generator import analyser_definition_parser, lex_generator

if __name__ == '__main__':
    sys.path.append('')
    definition = analyser_definition_parser.parse_lex_definition(sys.stdin.read())
    analizator = lex_generator.generate_lex_analyser(definition)
    with open('analizator/tablica.txt', 'w') as file:
        file.write(analizator.serialize())
