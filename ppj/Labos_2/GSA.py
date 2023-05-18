import sys
from json import dumps
from analizator.packages.syntax_generator import parse_syntax_definition_file, create_new_s0_production,\
    generate_enka, transform_to_dka, generate_tables

if __name__ == '__main__':
    sys.path.append('')
    definition = parse_syntax_definition_file(sys.stdin.read())
    create_new_s0_production(definition)
    enka = generate_enka(definition)
    dka = transform_to_dka(enka)
    table = generate_tables(dka, definition)
    with open('analizator/tablica.json', 'w') as file:
        file.write(dumps(table.serialize()))

