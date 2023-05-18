from Labos_4.packages.semantic_analyser.better_analyzer import Analyzer
from Labos_4.packages.models.tree import Tree

tree = Tree(open("../../tests/2011-12/37_global_var_param/test.in").read())

analyzer = Analyzer(tree)
analyzer.start()
