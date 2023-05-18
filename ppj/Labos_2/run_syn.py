from json import dumps
from Labos_2.analizator.packages.syntax_generator import parse_syntax_definition_file, create_new_s0_production, \
    generate_enka, transform_to_dka, generate_tables
from Labos_2.analizator.packages.lr_parser import load_analyzer, load_tokens, run_analyzer

TEST_FILE = "../tests/lab2/07_oporavak2/test"

if __name__ == '__main__':
    # Testing stuff
    with open(f'{TEST_FILE}.san') as file:
        content = file.read()
        definition = parse_syntax_definition_file(content)
        create_new_s0_production(definition)
        print(definition)

    print("\n"*3, "---")

    nka = generate_enka(definition)
    nka.pretty_print(print_states=False, print_transitions=False)

    dka = transform_to_dka(nka)
    dka.pretty_print(print_states=False, print_transitions=True)

    table = generate_tables(dka, definition)
    table.print_table()

    serialized = dumps(table.serialize())
    with open('analizator/tablica.json', 'w') as file:
        file.write(serialized)

    table = load_analyzer()
    with open(f'{TEST_FILE}.in') as f:
        tokens = load_tokens(f.read())
    tree = run_analyzer(tokens, table)
    print("\n"*3, "---")
    tree.pretty_print()
