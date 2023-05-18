from typing import List, Dict
from ..models.node import Type, Node, FunctionType, Union, Tuple
from ..models.tree import Tree
from ..semantic_analyser.production_parser import ProductionParser
from ..util.type_util import has_implicit_cast, has_explicit_cast, check_type_range
from ..util.semantic_error import SemanticError


"""
types_stack is a stack of types at each level of the tree until current
each element is a dictionary of name and its type
type is list because for example in function declaration we have return type and parameters
"""


class Analyzer:
    tree: Tree
    defined_main: bool
    failed_main: bool
    declared_functions: List[Tuple[str, FunctionType]] = []
    defined_functions: Dict[str, FunctionType] = {}


    def __init__(self, tree: Tree):
        self.tree = tree
        self.failed_main = False
        self.defined_main = False
        self.defined_functions = {}
        self.declared_functions = []

    def get_node(self, index):
        return next((x for x in self.tree.nodes if x.index == index), None)

    def start(self):
        self.step(self.tree.root, [{}])

    def step(self, node: Node, types_stack: List[Dict[str, Union[Type, FunctionType]]]) -> bool:
        if node.name == "<prijevodna_jedinica>":
            for child in node.children:
                child = self.get_node(child)
                res = self.step(child, types_stack)
                if not res:
                    return False
            return True
        if node.value and node.name.split()[0] == "IDN":
            for types in types_stack[::-1]:
                if node.value in types:
                    node.type = types[node.value]
                    if not node.const_type and (node.type == Type.CHAR or node.type == Type.INT):
                        node.l_expression = True
                    return True
            return False
        if node.value and node.name.split()[0] == "BROJ":
            return check_type_range(Type.INT, node.value)
        if node.value and node.name.split()[0] == "ZNAK":
            node.type = Type.CHAR
            value = node.value[1:-1]
            if len(value) == 1 and value != "\\":
                return True
            if value in ('\\t', '\\n', '\\0', "\\'", '\\"', '\\\\'):
                return True
            return False
        if node.value and node.name.split()[0] == "NIZ_ZNAKOVA":
            node.type = Type.ARRAY_CONST_CHAR
            value = node.value.replace("\\\\", "")
            for char, after in zip(value[1:], value[2:]):
                if char == "\\" and after not in ('t', 'n', '0', "'", '"', '\\'):
                    return False
            return True
        if node.value and node.name.split()[0] == "KR_VOID":
            node.type = Type.VOID
            return True
        if node.value and node.name.split()[0] == "KR_CHAR":
            node.type = Type.CHAR
            return True
        if node.value and node.name.split()[0] == "KR_INT":
            node.type = Type.INT
            return True
        if node.value and node.name.split()[0] in ('L_ZAGRADA', 'D_ZAGRADA', 'L_VIT_ZAGRADA', 'D_VIT_ZAGRADA', 'KR_RETURN', 'TOCKAZAREZ'):
            return True
        if node.production == ('<primarni_izraz>', ['IDN']):
            child_idn = self.get_node(node.children[0])
            if not self.step(child_idn, types_stack):
                raise SemanticError(node)
            node.type = child_idn.type
            node.l_expression = child_idn.l_expression
            return True
        if node.production == ('<primarni_izraz>', ['BROJ']):
            child_broj = self.get_node(node.children[0])
            node.type = Type.INT
            node.l_expression = False
            if not self.step(child_broj, types_stack):
                raise SemanticError(node)
            return True
        if node.production == ('<primarni_izraz>', ['ZNAK']):
            child_znak = self.get_node(node.children[0])
            node.type = Type.CHAR
            node.l_expression = False
            if not self.step(child_znak, types_stack):
                raise SemanticError(node)
            return True
        if node.production == ('<primarni_izraz>', ['NIZ_ZNAKOVA']):
            child_niz_znakova = self.get_node(node.children[0])
            node.type = Type.ARRAY_CONST_CHAR
            node.l_expression = False
            if not self.step(child_niz_znakova, types_stack):
                raise SemanticError(node)
            return True
        if node.production == ('<primarni_izraz>', ['L_ZAGRADA', '<izraz>', 'D_ZAGRADA']):
            child_izraz = self.get_node(node.children[1])
            if not self.step(child_izraz, types_stack):
                raise node.production
            node.type = child_izraz.type
            node.l_expression = child_izraz.l_expression
            return True
        if node.production == ('<postfiks_izraz>', ['<primarni_izraz>']):
            child_primarni_izraz = self.get_node(node.children[0])
            if not self.step(child_primarni_izraz, types_stack):
                raise node.production
            node.type = child_primarni_izraz.type
            node.l_expression = child_primarni_izraz.l_expression
            return True
        if node.production == ('<postfiks_izraz>', ['<postfiks_izraz>', 'L_UGL_ZAGRADA', '<izraz>', 'D_UGL_ZAGRADA']):
            child_postfiks_izraz = self.get_node(node.children[0])
            if not self.step(child_postfiks_izraz, types_stack):
                raise node.production
            if 'ARRAY' not in child_postfiks_izraz.type.value:
                raise SemanticError(node)

            child_izraz = self.get_node(node.children[2])
            if not self.step(child_izraz, types_stack):
                raise node.production
            if not has_implicit_cast(child_izraz.type, Type.INT):
                raise SemanticError(node)

            if child_postfiks_izraz.type == Type.ARRAY_CONST_CHAR:
                node.type = Type.CHAR
                node.const_type = True
            if child_postfiks_izraz.type == Type.ARRAY_CHAR:
                node.type = Type.CHAR
            if child_postfiks_izraz.type == Type.ARRAY_CONST_INT:
                node.type = Type.INT
                node.const_type = True
            if child_postfiks_izraz.type == Type.ARRAY_INT:
                node.type = Type.INT
            node.l_expression = not node.const_type

            return True
        if node.production == ('<postfiks_izraz>', ['<postfiks_izraz>', 'L_ZAGRADA', 'D_ZAGRADA']):
            child_postfiks_izraz = self.get_node(node.children[0])
            if not self.step(child_postfiks_izraz, types_stack):
                raise node.production
            # TO DO 2. <postfiks_izraz>.tip = funkcija(void → pov )
            # node.type = pov
            if not isinstance(child_postfiks_izraz.type, FunctionType):
                raise SemanticError(node)
            if child_postfiks_izraz.type.argument_types[0] != Type.VOID:
                raise SemanticError(node)
            node.type = child_postfiks_izraz.type.return_type
            node.l_expression = False
            return True
        if node.production == (
                '<postfiks_izraz>', ['<postfiks_izraz>', 'L_ZAGRADA', '<lista_argumenata>', 'D_ZAGRADA']):
            child_postfiks_izraz = self.get_node(node.children[0])
            child_lista_argumenata = self.get_node(node.children[2])
            if not self.step(child_postfiks_izraz, types_stack):
                raise node.production
            if not self.step(child_lista_argumenata, types_stack):
                raise node.production
            if not isinstance(child_postfiks_izraz.type, FunctionType):
                raise SemanticError(node)
            if len(child_postfiks_izraz.type.argument_types) != len(child_lista_argumenata.types):
                raise SemanticError(node)
            for arg, param in zip(child_lista_argumenata.types, child_postfiks_izraz.type.argument_types):
                if not has_implicit_cast(arg, param):
                    raise SemanticError(node)

            node.type = child_postfiks_izraz.type.return_type
            node.l_expression = False
            return True
        if node.production == ('<postfiks_izraz>', ['<postfiks_izraz>', 'OP_INC']):
            child_postfiks_izraz = self.get_node(node.children[0])
            if not self.step(child_postfiks_izraz, types_stack):
                raise node.production
            if not child_postfiks_izraz.l_expression:
                raise SemanticError(node)
            if not has_implicit_cast(child_postfiks_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<postfiks_izraz>', ['<postfiks_izraz>', 'OP_DEC']):
            child_postfiks_izraz = self.get_node(node.children[0])
            if not self.step(child_postfiks_izraz, types_stack):
                raise node.production
            if not child_postfiks_izraz.l_expression:
                raise SemanticError(node)
            if not has_implicit_cast(child_postfiks_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<lista_argumenata>', ['<izraz_pridruzivanja>']):
            child_izraz_pridruzivanja = self.get_node(node.children[0])
            if not self.step(child_izraz_pridruzivanja, types_stack):
                raise SemanticError(node)
            node.types.append(child_izraz_pridruzivanja.type)
            return True
        if node.production == ('<lista_argumenata>', ['<lista_argumenata>', 'ZAREZ', '<izraz_pridruzivanja>']):
            child_lista_argumenata = self.get_node(node.children[0])
            child_izraz_pridruzivanja = self.get_node(node.children[2])
            if not self.step(child_lista_argumenata, types_stack):
                raise SemanticError(node)
            if not self.step(child_izraz_pridruzivanja, types_stack):
                raise SemanticError(node)
            node.types = child_lista_argumenata.types + [child_izraz_pridruzivanja.type]
            return True
        if node.production == ('<unarni_izraz>', ['<postfiks_izraz>']):
            child_postfiks_izraz = self.get_node(node.children[0])
            if not self.step(child_postfiks_izraz, types_stack):
                raise SemanticError(node)
            node.type = child_postfiks_izraz.type
            node.l_expression = child_postfiks_izraz.l_expression
            return True
        if node.production == ('<unarni_izraz>', ['OP_INC', '<unarni_izraz>']):
            child_unarni_izraz = self.get_node(node.children[1])
            if not self.step(child_unarni_izraz, types_stack):
                raise SemanticError(node)
            if not child_unarni_izraz.l_expression:
                raise SemanticError(node)
            if not has_implicit_cast(child_unarni_izraz.type, Type.INT):
                raise SemanticError(node)
            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<unarni_izraz>', ['OP_DEC', '<unarni_izraz>']):
            child_unarni_izraz = self.get_node(node.children[1])
            if not self.step(child_unarni_izraz, types_stack):
                raise SemanticError(node)
            if not child_unarni_izraz.l_expression:
                raise SemanticError(node)
            if not has_implicit_cast(child_unarni_izraz.type, Type.INT):
                raise SemanticError(node)
            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<unarni_izraz>', ['<unarni_operator>', '<cast_izraz>']):
            child_cast_izraz = self.get_node(node.children[1])
            if not self.step(child_cast_izraz, types_stack):
                raise node.production
            if not has_implicit_cast(child_cast_izraz.type, Type.INT):
                raise SemanticError(node)
            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<unarni_operator>', ['PLUS']):
            return True
        if node.production == ('<unarni_operator>', ['MINUS']):
            return True
        if node.production == ('<unarni_operator>', ['OP_TILDA']):
            return True
        if node.production == ('<unarni_operator>', ['OP_NEG']):
            return True
        if node.production == ('<cast_izraz>', ['<unarni_izraz>']):
            child_unarni_izraz = self.get_node(node.children[0])
            if not self.step(child_unarni_izraz, types_stack):
                raise SemanticError(node)

            node.type = child_unarni_izraz.type
            node.l_expression = child_unarni_izraz.l_expression
            return True
        if node.production == ('<cast_izraz>', ['L_ZAGRADA', '<ime_tipa>', 'D_ZAGRADA', '<cast_izraz>']):
            child_ime_tipa = self.get_node(node.children[1])
            child_cast_izraz = self.get_node(node.children[3])
            if not self.step(child_ime_tipa, types_stack):
                raise SemanticError(node)
            if not self.step(child_cast_izraz, types_stack):
                raise SemanticError(node)
            if not has_explicit_cast(child_cast_izraz.type, child_ime_tipa.type):
                raise SemanticError(node)
            node.type = child_ime_tipa.type
            node.l_expression = False
            return True
        if node.production == ('<ime_tipa>', ['<specifikator_tipa>']):
            child_specifikator_tipa = self.get_node(node.children[0])
            if not self.step(child_specifikator_tipa, types_stack):
                raise SemanticError(node)
            node.type = child_specifikator_tipa.type
            return True
        if node.production == ('<ime_tipa>', ['KR_CONST', '<specifikator_tipa>']):
            child_specifikator_tipa = self.get_node(node.children[1])
            if not self.step(child_specifikator_tipa, types_stack):
                raise SemanticError(node)
            if child_specifikator_tipa.type == Type.VOID:
                raise SemanticError(node)
            node.type = child_specifikator_tipa.type
            node.const_type = True
            return True
        if node.production == ('<specifikator_tipa>', ['KR_VOID']):
            node.type = Type.VOID
            return True
        if node.production == ('<specifikator_tipa>', ['KR_CHAR']):
            node.type = Type.CHAR
            return True
        if node.production == ('<specifikator_tipa>', ['KR_INT']):
            node.type = Type.INT
            return True
        if node.production == ('<multiplikativni_izraz>', ['<cast_izraz>']):
            child_multiplikativni_izraz = self.get_node(node.children[0])
            if not self.step(child_multiplikativni_izraz, types_stack):
                raise SemanticError(node)
            node.type = child_multiplikativni_izraz.type
            node.l_expression = child_multiplikativni_izraz.l_expression
            return True
        if node.production == ('<multiplikativni_izraz>', ['<multiplikativni_izraz>', 'OP_PUTA', '<cast_izraz>']):
            child_multiplikativni_izraz = self.get_node(node.children[0])
            if not self.step(child_multiplikativni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_multiplikativni_izraz.type, Type.INT):
                raise SemanticError(node)

            child_cast_izraz = self.get_node(node.children[2])
            if not self.step(child_cast_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_cast_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<multiplikativni_izraz>', ['<multiplikativni_izraz>', 'OP_DIJELI', '<cast_izraz>']):
            child_multiplikativni_izraz = self.get_node(node.children[0])
            if not self.step(child_multiplikativni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_multiplikativni_izraz.type, Type.INT):
                raise SemanticError(node)

            child_cast_izraz = self.get_node(node.children[2])
            if not self.step(child_cast_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_cast_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<multiplikativni_izraz>', ['<multiplikativni_izraz>', 'OP_MOD', '<cast_izraz>']):
            child_multiplikativni_izraz = self.get_node(node.children[0])
            if not self.step(child_multiplikativni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_multiplikativni_izraz.type, Type.INT):
                raise SemanticError(node)

            child_cast_izraz = self.get_node(node.children[2])
            if not self.step(child_cast_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_cast_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<aditivni_izraz>', ['<multiplikativni_izraz>']):
            child_multiplikativni_izraz = self.get_node(node.children[0])
            if not self.step(child_multiplikativni_izraz, types_stack):
                raise SemanticError(node)

            node.type = child_multiplikativni_izraz.type
            node.l_expression = child_multiplikativni_izraz.l_expression
            return True
        if node.production == ('<aditivni_izraz>', ['<aditivni_izraz>', 'PLUS', '<multiplikativni_izraz>']):
            child_aditivni_izraz = self.get_node(node.children[0])
            if not self.step(child_aditivni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_aditivni_izraz.type, Type.INT):
                raise SemanticError(node)

            child_multiplikativni_izraz = self.get_node(node.children[2])
            if not self.step(child_multiplikativni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_multiplikativni_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<aditivni_izraz>', ['<aditivni_izraz>', 'MINUS', '<multiplikativni_izraz>']):
            child_aditivni_izraz = self.get_node(node.children[0])
            if not self.step(child_aditivni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_aditivni_izraz.type, Type.INT):
                raise SemanticError(node)

            child_multiplikativni_izraz = self.get_node(node.children[2])
            if not self.step(child_multiplikativni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_multiplikativni_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<odnosni_izraz>', ['<aditivni_izraz>']):
            child_aditivni_izraz = self.get_node(node.children[0])
            if not self.step(child_aditivni_izraz, types_stack):
                raise SemanticError(node)
            node.type = child_aditivni_izraz.type
            node.l_expression = child_aditivni_izraz.l_expression
            return True
        if node.production == ('<odnosni_izraz>', ['<odnosni_izraz>', 'OP_LT', '<aditivni_izraz>']):
            child_odnosni_izraz = self.get_node(node.children[0])
            if not self.step(child_odnosni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_odnosni_izraz.type, Type.INT):
                raise SemanticError(node)

            child_aditivni_izraz = self.get_node(node.children[2])
            if not self.step(child_aditivni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_aditivni_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<odnosni_izraz>', ['<odnosni_izraz>', 'OP_GT', '<aditivni_izraz>']):
            child_odnosni_izraz = self.get_node(node.children[0])
            if not self.step(child_odnosni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_odnosni_izraz.type, Type.INT):
                raise SemanticError(node)

            child_aditivni_izraz = self.get_node(node.children[2])
            if not self.step(child_aditivni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_aditivni_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<odnosni_izraz>', ['<odnosni_izraz>', 'OP_LTE', '<aditivni_izraz>']):
            child_odnosni_izraz = self.get_node(node.children[0])
            if not self.step(child_odnosni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_odnosni_izraz.type, Type.INT):
                raise SemanticError(node)

            child_aditivni_izraz = self.get_node(node.children[2])
            if not self.step(child_aditivni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_aditivni_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<odnosni_izraz>', ['<odnosni_izraz>', 'OP_GTE', '<aditivni_izraz>']):
            child_odnosni_izraz = self.get_node(node.children[0])
            if not self.step(child_odnosni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_odnosni_izraz.type, Type.INT):
                raise SemanticError(node)

            child_aditivni_izraz = self.get_node(node.children[2])
            if not self.step(child_aditivni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_aditivni_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<jednakosni_izraz>', ['<odnosni_izraz>']):
            child_odnosni_izraz = self.get_node(node.children[0])
            if not self.step(child_odnosni_izraz, types_stack):
                raise SemanticError(node)

            node.type = child_odnosni_izraz.type
            node.l_expression = child_odnosni_izraz.l_expression
            return True
        if node.production == ('<jednakosni_izraz>', ['<jednakosni_izraz>', 'OP_EQ', '<odnosni_izraz>']):
            child_jednakosni_izraz = self.get_node(node.children[0])
            child_odnosni_izraz = self.get_node(node.children[2])
            if not self.step(child_jednakosni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_jednakosni_izraz.type, Type.INT):
                raise SemanticError(node)

            if not self.step(child_odnosni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_odnosni_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<jednakosni_izraz>', ['<jednakosni_izraz>', 'OP_NEQ', '<odnosni_izraz>']):
            child_jednakosni_izraz = self.get_node(node.children[0])
            child_odnosni_izraz = self.get_node(node.children[2])
            if not self.step(child_jednakosni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_jednakosni_izraz.type, Type.INT):
                raise SemanticError(node)

            if not self.step(child_odnosni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_odnosni_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<bin_i_izraz>', ['<jednakosni_izraz>']):
            jednakosni_izraz = self.get_node(node.children[0])
            if not self.step(jednakosni_izraz, types_stack):
                raise SemanticError(node)
            node.type = jednakosni_izraz.type
            node.l_expression = jednakosni_izraz.l_expression
            return True
        if node.production == ('<bin_i_izraz>', ['<bin_i_izraz>', 'OP_BIN_I', '<jednakosni_izraz>']):
            child_bin_i_izraz = self.get_node(node.children[0])
            child_jednakosni_izraz = self.get_node(node.children[2])
            if not self.step(child_bin_i_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_bin_i_izraz.type, Type.INT):
                raise SemanticError(node)

            if not self.step(child_jednakosni_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_jednakosni_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<bin_xili_izraz>', ['<bin_i_izraz>']):
            child_bin_i_izraz = self.get_node(node.children[0])
            if not self.step(child_bin_i_izraz, types_stack):
                raise SemanticError(node)
            node.type = child_bin_i_izraz.type
            node.l_expression = child_bin_i_izraz.l_expression
            return True
        if node.production == ('<bin_xili_izraz>', ['<bin_xili_izraz>', 'OP_BIN_XILI', '<bin_i_izraz>']):
            child_bin_xili_izraz = self.get_node(node.children[0])
            child_bin_i_izraz = self.get_node(node.children[2])
            if not self.step(child_bin_xili_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_bin_xili_izraz.type, Type.INT):
                raise SemanticError(node)

            if not self.step(child_bin_i_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_bin_i_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<bin_ili_izraz>', ['<bin_xili_izraz>']):
            child_bin_xili_izraz = self.get_node(node.children[0])
            if not self.step(child_bin_xili_izraz, types_stack):
                raise SemanticError(node)
            node.type = child_bin_xili_izraz.type
            node.l_expression = child_bin_xili_izraz.l_expression
            return True
        if node.production == ('<bin_ili_izraz>', ['<bin_ili_izraz>', 'OP_BIN_ILI', '<bin_xili_izraz>']):
            child_bin_ili_izraz = self.get_node(node.children[0])
            child_bin_xili_izraz = self.get_node(node.children[2])
            if not self.step(child_bin_ili_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_bin_ili_izraz.type, Type.INT):
                raise SemanticError(node)

            if not self.step(child_bin_xili_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_bin_xili_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<log_i_izraz>', ['<bin_ili_izraz>']):
            child_bin_ili_izraz = self.get_node(node.children[0])
            if not self.step(child_bin_ili_izraz, types_stack):
                raise SemanticError(node)
            node.type = child_bin_ili_izraz.type
            node.l_expression = child_bin_ili_izraz.l_expression
            return True
        if node.production == ('<log_i_izraz>', ['<log_i_izraz>', 'OP_I', '<bin_ili_izraz>']):
            child_log_i_izraz = self.get_node(node.children[0])
            child_bin_ili_izraz = self.get_node(node.children[2])
            if not self.step(child_log_i_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_log_i_izraz.type, Type.INT):
                raise SemanticError(node)

            if not self.step(child_bin_ili_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_bin_ili_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<log_ili_izraz>', ['<log_i_izraz>']):
            child_log_i_izraz = self.get_node(node.children[0])
            if not self.step(child_log_i_izraz, types_stack):
                raise SemanticError(node)
            node.type = child_log_i_izraz.type
            node.l_expression = child_log_i_izraz.l_expression
            return True
        if node.production == ('<log_ili_izraz>', ['<log_ili_izraz>', 'OP_ILI', '<log_i_izraz>']):
            child_log_ili_izraz = self.get_node(node.children[0])
            child_log_i_izraz = self.get_node(node.children[2])
            if not self.step(child_log_ili_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_log_ili_izraz.type, Type.INT):
                raise SemanticError(node)

            if not self.step(child_log_i_izraz, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_log_i_izraz.type, Type.INT):
                raise SemanticError(node)

            node.type = Type.INT
            node.l_expression = False
            return True
        if node.production == ('<izraz_pridruzivanja>', ['<log_ili_izraz>']):
            child_log_ili_izraz = self.get_node(node.children[0])
            if not self.step(child_log_ili_izraz, types_stack):
                raise SemanticError(node)
            node.type = child_log_ili_izraz.type
            node.l_expression = child_log_ili_izraz.l_expression
            return True
        if node.production == ('<izraz_pridruzivanja>', ['<postfiks_izraz>', 'OP_PRIDRUZI', '<izraz_pridruzivanja>']):
            child_postfiks_izraz = self.get_node(node.children[0])
            child_izraz_pridruzivanja = self.get_node(node.children[2])
            if not self.step(child_postfiks_izraz, types_stack):
                raise SemanticError(node)
            if not child_postfiks_izraz.l_expression:
                raise SemanticError(node)

            if not self.step(child_izraz_pridruzivanja, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_izraz_pridruzivanja.type, child_postfiks_izraz.type):
                raise SemanticError(node)

            node.type = child_postfiks_izraz.type
            node.l_expression = False
            return True
        if node.production == ('<izraz>', ['<izraz_pridruzivanja>']):
            child_izraz_pridruzivanja = self.get_node(node.children[0])
            if not self.step(child_izraz_pridruzivanja, types_stack):
                raise SemanticError(node)
            node.type = child_izraz_pridruzivanja.type
            node.l_expression = child_izraz_pridruzivanja.l_expression
            return True
        if node.production == ('<izraz>', ['<izraz>', 'ZAREZ', '<izraz_pridruzivanja>']):
            child_izraz = self.get_node(node.children[0])
            child_izraz_pridruzivanja = self.get_node(node.children[2])
            if not self.step(child_izraz, types_stack):
                raise SemanticError(node)
            if not self.step(child_izraz_pridruzivanja, types_stack):
                raise SemanticError(node)
            node.type = child_izraz_pridruzivanja.type
            node.l_expression = False
            return True
        if node.production == ('<slozena_naredba>', ['L_VIT_ZAGRADA', '<lista_naredbi>', 'D_VIT_ZAGRADA']):
            child_lista_naredbi = self.get_node(node.children[1])
            new_types_stack = types_stack[:]
            if 'enter_function' not in types_stack[-1]:
                new_types_stack = new_types_stack + [{}]
            if not self.step(child_lista_naredbi, new_types_stack):
                raise SemanticError(node)
            return True
        if node.production == (
                '<slozena_naredba>', ['L_VIT_ZAGRADA', '<lista_deklaracija>', '<lista_naredbi>', 'D_VIT_ZAGRADA']):
            child_lista_deklaracija = self.get_node(node.children[1])
            child_lista_naredbi = self.get_node(node.children[2])
            new_types_stack = types_stack[:]
            if 'enter_function' not in types_stack[-1]:
                new_types_stack = new_types_stack + [{}]
            if not self.step(child_lista_deklaracija, new_types_stack):
                raise SemanticError(node)
            if not self.step(child_lista_naredbi, new_types_stack):
                raise SemanticError(node)
            return True
        if node.production == ('<lista_naredbi>', ['<naredba>']):
            child_naredba = self.get_node(node.children[0])
            if not self.step(child_naredba, types_stack):
                raise SemanticError(node)
            return True
        if node.production == ('<lista_naredbi>', ['<lista_naredbi>', '<naredba>']):
            child_lista_naredbi = self.get_node(node.children[0])
            child_naredba = self.get_node(node.children[1])
            if not self.step(child_lista_naredbi, types_stack):
                raise SemanticError(node)
            if not self.step(child_naredba, types_stack):
                raise SemanticError(node)
            return True
        if node.production == ('<naredba>', ['<slozena_naredba>']):
            child_slozena_naredba = self.get_node(node.children[0])
            if not self.step(child_slozena_naredba, types_stack):
                raise SemanticError(node)
            return True
        if node.production == ('<naredba>', ['<izraz_naredba>']):
            child_izraz_naredba = self.get_node(node.children[0])
            if not self.step(child_izraz_naredba, types_stack):
                raise SemanticError(node)
            return True
        if node.production == ('<naredba>', ['<naredba_grananja>']):
            child_naredba_grananja = self.get_node(node.children[0])
            if not self.step(child_naredba_grananja, types_stack + [{}]):
                raise SemanticError(node)
            return True
        if node.production == ('<naredba>', ['<naredba_petlje>']):
            child_naredba_petlje = self.get_node(node.children[0])
            if not self.step(child_naredba_petlje, types_stack + [{}]):
                raise SemanticError(node)
            return True
        if node.production == ('<naredba>', ['<naredba_skoka>']):
            child_naredba_skoka = self.get_node(node.children[0])
            if not self.step(child_naredba_skoka, types_stack):
                raise SemanticError(node)
            return True
        if node.production == ('<izraz_naredba>', ['TOCKAZAREZ']):
            node.type = Type.INT
            return True
        if node.production == ('<izraz_naredba>', ['<izraz>', 'TOCKAZAREZ']):
            child_izraz = self.get_node(node.children[0])
            if not self.step(child_izraz, types_stack):
                raise SemanticError(node)
            node.type = child_izraz.type
            return True
        if node.production == ('<naredba_grananja>', ['KR_IF', 'L_ZAGRADA', '<izraz>', 'D_ZAGRADA', '<naredba>']):
            child_izraz = self.get_node(node.children[2])
            child_naredba = self.get_node(node.children[4])
            if not self.step(child_izraz, types_stack):
                raise SemanticError(node)
            if not self.step(child_naredba, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_izraz.type, Type.INT):
                raise SemanticError(node)
            return True
        if node.production == (
                '<naredba_grananja>',
                ['KR_IF', 'L_ZAGRADA', '<izraz>', 'D_ZAGRADA', '<naredba>', 'KR_ELSE', '<naredba>']):
            child_izraz = self.get_node(node.children[2])
            child_naredba = self.get_node(node.children[4])
            child_naredba2 = self.get_node(node.children[6])
            if not self.step(child_izraz, types_stack):
                raise SemanticError(node)
            if not self.step(child_naredba, types_stack):
                raise SemanticError(node)
            if not self.step(child_naredba2, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_izraz.type, Type.INT):
                raise SemanticError(node)
        if node.production == ('<naredba_petlje>', ['KR_WHILE', 'L_ZAGRADA', '<izraz>', 'D_ZAGRADA', '<naredba>']):
            child_izraz = self.get_node(node.children[2])
            child_naredba = self.get_node(node.children[4])
            if not self.step(child_izraz, types_stack):
                raise SemanticError(node)
            if not self.step(child_naredba, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_izraz.type, Type.INT):
                raise SemanticError(node)
            return True
        if node.production == (
                '<naredba_petlje>',
                ['KR_FOR', 'L_ZAGRADA', '<izraz_naredba>', '<izraz_naredba>', 'D_ZAGRADA', '<naredba>']):
            child_izraz_naredba = self.get_node(node.children[2])
            child_izraz_naredba2 = self.get_node(node.children[3])
            child_naredba = self.get_node(node.children[5])
            if not self.step(child_izraz_naredba, types_stack):
                raise SemanticError(node)
            if not self.step(child_izraz_naredba2, types_stack):
                raise SemanticError(node)
            if not self.step(child_naredba, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_izraz_naredba2.type, Type.INT):
                raise SemanticError(node)
            return True
        if node.production == ('<naredba_petlje>',
                                 ['KR_FOR', 'L_ZAGRADA', '<izraz_naredba>', '<izraz_naredba>', '<izraz>', 'D_ZAGRADA',
                                  '<naredba>']):
            child_izraz_naredba = self.get_node(node.children[2])
            child_izraz_naredba2 = self.get_node(node.children[3])
            child_izraz = self.get_node(node.children[4])
            child_naredba = self.get_node(node.children[6])
            if not self.step(child_izraz_naredba, types_stack):
                raise SemanticError(node)
            if not self.step(child_izraz_naredba2, types_stack):
                raise SemanticError(node)
            if not self.step(child_izraz, types_stack):
                raise SemanticError(node)
            if not self.step(child_naredba, types_stack):
                raise SemanticError(node)
            if not has_implicit_cast(child_izraz_naredba2.type, Type.INT):
                raise SemanticError(node)
            return True
        if node.production == ('<naredba_skoka>', ['KR_CONTINUE', 'TOCKAZAREZ']):
            # naredba se nalazi unutar petlje ili unutar bloka koji je ugnijeˇzden u petl
            parent = self.get_node(node.parent)
            while parent is not None:
                if parent.name == '<naredba_petlje>':
                    return True
                parent = self.get_node(parent.parent)
            raise SemanticError(node)
        if node.production == ('<naredba_skoka>', ['KR_BREAK', 'TOCKAZAREZ']):
            parent = self.get_node(node.parent)
            while parent is not None:
                if parent.name == '<naredba_petlje>':
                    return True
                parent = self.get_node(parent.parent)
            raise SemanticError(node)
        if node.production == ('<naredba_skoka>', ['KR_RETURN', 'TOCKAZAREZ']):
            parent = self.get_node(node.parent)
            while parent is not None:
                if isinstance(parent.type, FunctionType):
                    if parent.type.return_type == Type.VOID:
                        return True
                    else:
                        raise SemanticError(node)
                parent = self.get_node(parent.parent)
            raise SemanticError(node)
        if node.production == ('<naredba_skoka>', ['KR_RETURN', '<izraz>', 'TOCKAZAREZ']):
            child_izraz = self.get_node(node.children[1])
            if not self.step(child_izraz, types_stack):
                raise SemanticError(node)
            parent = self.get_node(node.parent)
            while parent is not None:
                if isinstance(parent.type, FunctionType):
                    if not has_implicit_cast(child_izraz.type, parent.type.return_type):
                        raise SemanticError(node)
                    return True
                parent = self.get_node(parent.parent)
            raise SemanticError(node)
        if node.production == ('<prijevodna_jedinica>', ['<vanjska_deklaracija>']):
            child_vanjska_deklaracija = self.get_node(node.children[0])
            if not self.step(child_vanjska_deklaracija, types_stack):
                raise SemanticError(node)
            return True
        if node.production == ('<prijevodna_jedinica>', ['<prijevodna_jedinica>', '<vanjska_deklaracija>']):
            child_prijevodna_jedinica = self.get_node(node.children[0])
            child_vanjska_deklaracija = self.get_node(node.children[1])
            if not self.step(child_prijevodna_jedinica, types_stack):
                raise SemanticError(node)
            if not self.step(child_vanjska_deklaracija, types_stack):
                raise SemanticError(node)
            return True
        if node.production == ('<vanjska_deklaracija>', ['<definicija_funkcije>']):
            child_definicija_funkcije = self.get_node(node.children[0])
            if not self.step(child_definicija_funkcije, types_stack):
                raise SemanticError(node)
            return True
        if node.production == ('<vanjska_deklaracija>', ['<deklaracija>']):
            child_deklaracija = self.get_node(node.children[0])
            if not self.step(child_deklaracija, types_stack):
                raise SemanticError(node)
            return True
        if node.production == (
                '<definicija_funkcije>',
                ['<ime_tipa>', 'IDN', 'L_ZAGRADA', 'KR_VOID', 'D_ZAGRADA', '<slozena_naredba>']):
            child_ime_tipa = self.get_node(node.children[0])
            child_IDN = self.get_node(node.children[1])
            child_slozena_naredba = self.get_node(node.children[5])
            if not self.step(child_ime_tipa, types_stack):
                raise SemanticError(node)
            if child_ime_tipa.const_type:
                raise SemanticError(node)
            node.type = FunctionType(child_ime_tipa.type, [Type.VOID], False)
            self.defined_functions[child_IDN.value] = node.type
            if child_IDN.value == 'main':
                self.defined_main = True
                if node.type.return_type != Type.INT:
                    self.failed_main = True
                if child_ime_tipa.const_type:
                    self.failed_main = True
                if node.type.argument_types != [Type.VOID]:
                    self.failed_main = True
            for layer in types_stack[::-1]:
                if child_IDN.value in layer:
                    if isinstance(layer[child_IDN.value], FunctionType):
                        if layer[child_IDN.value].argument_types != [Type.VOID] or \
                                layer[child_IDN.value].return_type != node.type.return_type or \
                                not layer[child_IDN.value].only_declaration:
                            raise SemanticError(node)
                        else:
                            break
                    else:
                        raise SemanticError(node)

            types_stack[-1][child_IDN.value] = node.type
            if not self.step(child_slozena_naredba, types_stack + [{}]):
                raise SemanticError(node)
            return True
        if node.production == ('<definicija_funkcije>',
                                 ['<ime_tipa>', 'IDN', 'L_ZAGRADA', '<lista_parametara>', 'D_ZAGRADA',
                                  '<slozena_naredba>']):
            child_ime_tipa = self.get_node(node.children[0])
            child_IDN = self.get_node(node.children[1])
            child_lista_parametara = self.get_node(node.children[3])
            child_slozena_naredba = self.get_node(node.children[5])
            if not self.step(child_ime_tipa, types_stack):
                raise SemanticError(node)
            if child_ime_tipa.const_type:
                raise SemanticError(node)
            if not self.step(child_lista_parametara, types_stack):
                raise SemanticError(node)
            for layer in types_stack[::-1]:
                if child_IDN.value in layer:
                    if isinstance(layer[child_IDN.value], FunctionType) and layer[child_IDN.value].only_declaration:
                        if layer[child_IDN.value].argument_types != child_lista_parametara.types or \
                                layer[child_IDN.value].return_type != child_ime_tipa.type or \
                                not layer[child_IDN.value].only_declaration:
                            raise SemanticError(node)
                        else:
                            break
                    else:
                        raise SemanticError(node)
            node.type = FunctionType(child_ime_tipa.type, child_lista_parametara.types, False)
            self.defined_functions[child_IDN.value] = node.type
            if child_IDN.value == 'main':
                self.failed_main = True
            types_stack[-1][child_IDN.value] = node.type
            new_types_stack = types_stack + [{child_lista_parametara.names[i]: child_lista_parametara.types[i]
                                              for i in range(len(child_lista_parametara.names))}]
            new_types_stack[-1]['enter_function'] = True
            if not self.step(child_slozena_naredba, new_types_stack):
                raise SemanticError(node)

            return True
        if node.production == ('<lista_parametara>', ['<deklaracija_parametra>']):
            child_deklaracija_parametra = self.get_node(node.children[0])
            if not self.step(child_deklaracija_parametra, types_stack):
                raise SemanticError(node)
            node.types.append(child_deklaracija_parametra.type)
            node.names.append(child_deklaracija_parametra.name)
            return True
        if node.production == ('<lista_parametara>', ['<lista_parametara>', 'ZAREZ', '<deklaracija_parametra>']):
            child_lista_parametara = self.get_node(node.children[0])
            child_deklaracija_parametra = self.get_node(node.children[2])
            if not self.step(child_lista_parametara, types_stack):
                raise SemanticError(node)
            if not self.step(child_deklaracija_parametra, types_stack):
                raise SemanticError(node)
            if child_deklaracija_parametra.name in child_lista_parametara.names:
                raise SemanticError(node)

            node.types.extend(child_lista_parametara.types)
            node.types.append(child_deklaracija_parametra.type)
            node.names.extend(child_lista_parametara.names)
            node.names.append(child_deklaracija_parametra.name)
            return True
        if node.production == ('<deklaracija_parametra>', ['<ime_tipa>', 'IDN']):
            child_ime_tipa = self.get_node(node.children[0])
            child_IDN = self.get_node(node.children[1])
            if not self.step(child_ime_tipa, types_stack):
                raise SemanticError(node)
            if child_ime_tipa.type == Type.VOID:
                raise SemanticError(node)
            node.type = child_ime_tipa.type
            node.name = child_IDN.value
            return True
        if node.production == ('<deklaracija_parametra>', ['<ime_tipa>', 'IDN', 'L_UGL_ZAGRADA', 'D_UGL_ZAGRADA']):
            child_ime_tipa = self.get_node(node.children[0])
            child_IDN = self.get_node(node.children[1])
            if not self.step(child_ime_tipa, types_stack):
                raise SemanticError(node)
            if child_ime_tipa.type == Type.VOID:
                raise SemanticError(node)
            if child_ime_tipa.type == Type.CHAR and not child_ime_tipa.const_type:
                node.type = Type.ARRAY_CHAR
            if child_ime_tipa.type == Type.INT and not child_ime_tipa.const_type:
                node.type = Type.ARRAY_INT
            if child_ime_tipa.type == Type.CHAR and child_ime_tipa.const_type:
                node.type = Type.ARRAY_CONST_CHAR
            if child_ime_tipa.type == Type.INT and child_ime_tipa.const_type:
                node.type = Type.ARRAY_CONST_INT
            node.name = child_IDN.value
            return True
        if node.production == ('<lista_deklaracija>', ['<deklaracija>']):
            child_deklaracija = self.get_node(node.children[0])
            if not self.step(child_deklaracija, types_stack):
                raise SemanticError(node)
            return True
        if node.production == ('<lista_deklaracija>', ['<lista_deklaracija>', '<deklaracija>']):
            child_lista_deklaracija = self.get_node(node.children[0])
            child_deklaracija = self.get_node(node.children[1])
            if not self.step(child_lista_deklaracija, types_stack):
                raise SemanticError(node)
            if not self.step(child_deklaracija, types_stack):
                raise SemanticError(node)
            return True
        if node.production == ('<deklaracija>', ['<ime_tipa>', '<lista_init_deklaratora>', 'TOCKAZAREZ']):
            child_ime_tipa = self.get_node(node.children[0])
            child_lista_init_deklaratora = self.get_node(node.children[1])
            if not self.step(child_ime_tipa, types_stack):
                raise SemanticError(node)
            child_lista_init_deklaratora.ntype = child_ime_tipa.type
            child_lista_init_deklaratora.const_ntype = child_ime_tipa.const_type
            if not self.step(child_lista_init_deklaratora, types_stack):
                raise SemanticError(node)
            return True
        if node.production == ('<lista_init_deklaratora>', ['<init_deklarator>']):
            child_init_deklarator = self.get_node(node.children[0])
            child_init_deklarator.ntype = node.ntype
            child_init_deklarator.const_ntype = node.const_ntype
            if not self.step(child_init_deklarator, types_stack):
                raise SemanticError(node)
            return True
        if node.production == (
                '<lista_init_deklaratora>', ['<lista_init_deklaratora>', 'ZAREZ', '<init_deklarator>']):
            child_lista_init_deklaratora = self.get_node(node.children[0])
            child_init_deklarator = self.get_node(node.children[2])
            child_lista_init_deklaratora.ntype = node.ntype
            child_lista_init_deklaratora.const_ntype = node.const_ntype
            if not self.step(child_lista_init_deklaratora, types_stack):
                raise SemanticError(node)
            child_init_deklarator.ntype = node.ntype
            child_init_deklarator.const_ntype = node.const_ntype
            if not self.step(child_init_deklarator, types_stack):
                raise SemanticError(node)
            return True
        if node.production == ('<init_deklarator>', ['<izravni_deklarator>']):
            child_izravni_deklarator = self.get_node(node.children[0])
            child_izravni_deklarator.ntype = node.ntype
            child_izravni_deklarator.const_ntype = node.const_ntype
            if not self.step(child_izravni_deklarator, types_stack):
                raise SemanticError(node)
            if child_izravni_deklarator.const_type:
                raise SemanticError(node)
            if child_izravni_deklarator.type == Type.ARRAY_CONST_INT or \
                    child_izravni_deklarator.type == Type.ARRAY_CONST_CHAR:
                raise SemanticError(node)
            return True
        if node.production == ('<init_deklarator>', ['<izravni_deklarator>', 'OP_PRIDRUZI', '<inicijalizator>']):
            child_izravni_deklarator = self.get_node(node.children[0])
            child_inicijalizator = self.get_node(node.children[2])
            child_izravni_deklarator.ntype = node.ntype
            child_izravni_deklarator.const_ntype = node.const_ntype
            if not self.step(child_izravni_deklarator, types_stack):
                raise SemanticError(node)
            if not self.step(child_inicijalizator, types_stack):
                raise SemanticError(node)
            if child_izravni_deklarator.type == Type.INT or child_izravni_deklarator.type == Type.CHAR:
                if not has_implicit_cast(child_inicijalizator.type, child_izravni_deklarator.type):
                    raise SemanticError(node)
            elif child_izravni_deklarator.type == Type.ARRAY_INT or child_izravni_deklarator.type == Type.ARRAY_CHAR \
                    or child_izravni_deklarator.type == Type.ARRAY_CONST_INT or \
                    child_izravni_deklarator.type == Type.ARRAY_CONST_CHAR:
                if child_inicijalizator.number_of_elements > child_izravni_deklarator.number_of_elements:
                    raise SemanticError(node)
                if child_izravni_deklarator.type == Type.ARRAY_INT or child_izravni_deklarator.type == Type.ARRAY_CONST_INT:
                    array_type = Type.INT
                elif child_izravni_deklarator.type == Type.ARRAY_CHAR or child_izravni_deklarator.type == Type.ARRAY_CONST_CHAR:
                    array_type = Type.CHAR
                for type_ in child_inicijalizator.types:
                    if not has_implicit_cast(type_, array_type):
                        raise SemanticError(node)
            else:
                raise SemanticError(node)
            return True
        if node.production == ('<izravni_deklarator>', ['IDN']):
            child_IDN = self.get_node(node.children[0])
            node.type = node.ntype
            node.const_type = node.const_ntype
            if node.ntype == Type.VOID:
                raise SemanticError(node)
            if child_IDN.value in types_stack[-1]:
                raise SemanticError(node)
            types_stack[-1][child_IDN.value] = node.type
            return True
        if node.production == ('<izravni_deklarator>', ['IDN', 'L_UGL_ZAGRADA', 'BROJ', 'D_UGL_ZAGRADA']):
            child_IDN = self.get_node(node.children[0])
            child_BROJ = self.get_node(node.children[2])
            if node.ntype == Type.VOID:
                raise SemanticError(node)
            elif node.ntype == Type.INT and not node.const_ntype:
                node.type = Type.ARRAY_INT
            elif node.ntype == Type.CHAR and not node.const_ntype:
                node.type = Type.ARRAY_CHAR
            elif node.ntype == Type.INT and node.const_ntype:
                node.type = Type.ARRAY_CONST_INT
            elif node.ntype == Type.CHAR and node.const_ntype:
                node.type = Type.ARRAY_CONST_CHAR
            node.number_of_elements = int(child_BROJ.value)
            if child_IDN.value in types_stack[-1]:
                raise SemanticError(node)
            if not(0 < node.number_of_elements <= 1024):
                raise SemanticError(node)
            types_stack[-1][child_IDN.value] = node.type
            return True
        if node.production == ('<izravni_deklarator>', ['IDN', 'L_ZAGRADA', 'KR_VOID', 'D_ZAGRADA']):
            child_IDN = self.get_node(node.children[0])
            node.type = FunctionType(node.ntype, [Type.VOID], only_declaration=True)
            self.declared_functions.append((child_IDN.value, node.type))
            if child_IDN.value in types_stack[-1]:
                existing = types_stack[-1][child_IDN.value]
                if existing.return_type != node.type.return_type:
                    raise SemanticError(node)
                if existing.argument_types != node.type.argument_types:
                    raise SemanticError(node)
            else:
                types_stack[-1][child_IDN.value] = node.type
            return True
        if node.production == ('<izravni_deklarator>', ['IDN', 'L_ZAGRADA', '<lista_parametara>', 'D_ZAGRADA']):
            child_IDN = self.get_node(node.children[0])
            child_lista_parametara = self.get_node(node.children[2])
            node.type = FunctionType(node.ntype, child_lista_parametara.types, only_declaration=True)
            self.declared_functions.append((child_IDN.value, node.type))
            if not self.step(child_lista_parametara, types_stack):
                raise SemanticError(node)
            if child_IDN.value in types_stack[-1]:
                existing = types_stack[-1][child_IDN.value]
                if existing.return_type != node.type.return_type:
                    raise SemanticError(node)
                if existing.argument_types != node.type.argument_types:
                    raise SemanticError(node)
            else:
                types_stack[-1][child_IDN.value] = node.type
            return True
        if node.production == ('<inicijalizator>', ['<izraz_pridruzivanja>']):
            def search_for_NIZ_ZNAKOVA(current_node) -> int:
                for child in current_node.children:
                    child = self.get_node(child)
                    if child.production == ('<primarni_izraz>', ['NIZ_ZNAKOVA']):
                        child_NIZ_ZNAKOVA = self.get_node(child.children[0])
                        value = child_NIZ_ZNAKOVA.value[1:-1].replace('\\\\', 'a').replace('\\', '')
                        return len(value) + 1
                    if length := search_for_NIZ_ZNAKOVA(child):
                        return length
                return 0
            child_izraz_pridruzivanja = self.get_node(node.children[0])
            if not self.step(child_izraz_pridruzivanja, types_stack):
                raise SemanticError(node)
            if length := search_for_NIZ_ZNAKOVA(child_izraz_pridruzivanja):
                node.type = Type.ARRAY_CHAR
                node.number_of_elements = length
            else:
                node.type = child_izraz_pridruzivanja.type
            return True
        if node.production == (
                '<inicijalizator>', ['L_VIT_ZAGRADA', '<lista_izraza_pridruzivanja>', 'D_VIT_ZAGRADA']):
            child_lista_izraza_pridruzivanja = self.get_node(node.children[1])
            if not self.step(child_lista_izraza_pridruzivanja, types_stack):
                raise SemanticError(node)
            node.types = child_lista_izraza_pridruzivanja.types
            node.number_of_elements = child_lista_izraza_pridruzivanja.number_of_elements
            return True
        if node.production == ('<lista_izraza_pridruzivanja>', ['<izraz_pridruzivanja>']):
            child_izraz_pridruzivanja = self.get_node(node.children[0])
            if not self.step(child_izraz_pridruzivanja, types_stack):
                raise SemanticError(node)
            node.types = [child_izraz_pridruzivanja.type]
            node.number_of_elements = 1
            return True
        if node.production == (
                '<lista_izraza_pridruzivanja>', ['<lista_izraza_pridruzivanja>', 'ZAREZ', '<izraz_pridruzivanja>']):
            child_lista_izraza_pridruzivanja = self.get_node(node.children[0])
            child_izraz_pridruzivanja = self.get_node(node.children[2])
            if not self.step(child_lista_izraza_pridruzivanja, types_stack):
                raise SemanticError(node)
            if not self.step(child_izraz_pridruzivanja, types_stack):
                raise SemanticError(node)
            node.types = child_lista_izraza_pridruzivanja.types + [child_izraz_pridruzivanja.type]
            node.number_of_elements = child_lista_izraza_pridruzivanja.number_of_elements + 1
            return True
        raise Exception(f'Unknown production for node: {node}')