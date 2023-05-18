import sys

from packages.models.tree import Tree, Node
from packages.semantic_analyser.better_analyzer import Analyzer
from packages.util.semantic_error import SemanticError

if __name__ == '__main__':
    file = sys.stdin
    # file = open("../tests/lab3/30_const_init/test.in")
    tree = Tree(file.read())
    analyzer = Analyzer(tree)
    try:
        analyzer.start()
    except SemanticError as e:
        if isinstance(e.inner_object, Node):
            print(e.inner_object.bnf(tree))
        else:
            print(e.inner_object)
        # raise e
    else:
        if analyzer.failed_main or not analyzer.defined_main:
            print("main")
        else:
            for function, declared in analyzer.declared_functions:
                if function not in analyzer.defined_functions:
                    print("funkcija")
                    break
                defined = analyzer.defined_functions[function]
                if declared.return_type != defined.return_type:
                    print("funkcija")
                    break
                if declared.argument_types != defined.argument_types:
                    print("funkcija")
                    break
