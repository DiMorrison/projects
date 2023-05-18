from ..models import Terminal, NonTerminal, Production, SyntaxAnalyzerDefinition, StackSymbol


def parse_syntax_definition_file(content: str) -> SyntaxAnalyzerDefinition:
    """
    Parses syntax definition file and returns SyntaxAnalyzerDefinition object.
    """

    lines = content.splitlines()

    non_terminals = []
    terminals = []
    find_non_terminal = lambda name: next((t for t in non_terminals if t.name == name), None)
    find_terminal = lambda name: next((t for t in terminals if t.name == name), None)
    syn_symbols = []
    productions = []
    current_left_side: NonTerminal = None

    for i, line in enumerate(lines):
        if line.startswith("%V"):
            non_terminals = [NonTerminal(name.strip()) for name in line.split("%V ", maxsplit=1)[1].split()]
            continue
        elif line.startswith("%T"):
            terminals = [Terminal(name.strip()) for name in line.split("%T ", maxsplit=1)[1].split()]
            continue
        elif line.startswith("%Syn"):
            syn_symbols = [Terminal(name.strip()) for name in line.split("%Syn ", maxsplit=1)[1].split()]
            continue
        elif line.startswith("<"):
            current_left_side = find_non_terminal(line[:line.index(">") + 1])
            continue

        if current_left_side is None:
            raise Exception(f"Production without left side on line {i + 1}")

        right_side = line.strip().split(' ')
        production = Production(
            current_left_side,
            [find_terminal(name) or find_non_terminal(name) for name in right_side]
        )
        productions.append(production)

        if line == '':
            break

    return SyntaxAnalyzerDefinition(
        non_terminals[0],
        non_terminals,
        terminals + [Terminal('$')],
        syn_symbols,
        productions)


def create_new_s0_production(definition: SyntaxAnalyzerDefinition):
    s0 = NonTerminal("S'")
    s0_production = Production(s0, [definition.start_symbol])
    definition.start_production = s0_production
    definition.non_terminals.append(s0)
    definition.productions.append(s0_production)
    # s0.first = [StackSymbol()]
    definition.start_symbol = s0
