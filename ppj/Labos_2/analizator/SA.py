import sys
from packages.lr_parser import load_analyzer, load_tokens, run_analyzer

if __name__ == '__main__':
    analyzer = load_analyzer('analizator/tablica.json')
    tokens = load_tokens(sys.stdin.read())
    result = run_analyzer(tokens, analyzer)
    result.pretty_print()
