from dataclasses import dataclass, field
from typing import List, Dict

from ..models.node import Type, Node
from ..models.tree import Tree
from ..semantic_analyser.production_parser import ProductionParser
from ..util.type_util import has_implicit_cast, has_explicit_cast, check_type_range
from ..util.semantic_error import SemanticError


@dataclass
class Walker:
    tree: Tree

    def __init__(self, tree: Tree):
        self.tree = tree

    def walk(self, root: int = 1):
        self.step(root, [{}])

    def leaf(self, node: Node, sign_table: List[Dict[str, Type]]):
        pass

    def step(self, node_index: int, sign_table: List[Dict[str, Type]]):
        node = self.tree.find_node(node_index)

        if node.name == "<prijevodna_jedinica>":
            for child in node.children:
                self.step(child)
                return

        print("Step at node: " + node.name)

        production_parser: ProductionParser = ProductionParser("bnf.txt")
        # TO DO implementirati provjeru mogucnosti pretvaranja u izraz npr. A ∼ B
        if node.production == ('<primarni_izraz>', ['IDN']):
            child_IDN = self.tree.find_node(node.children[0])
            # provjera izraza
            if not self.step(child_IDN.index):
                raise SemanticError(node.production)
            node.type = child_IDN.type
            node.l_expression = child_IDN.l_expression

            return True
        elif node.production == ('<primarni_izraz>', ['BROJ']):
            child_BROJ = self.tree.find_node(node.children[0])
            node.type = Type.INT
            node.l_expression = False
            if not check_type_range(child_BROJ.value):
                raise SemanticError(node.production)
            return True
        elif node.production == ('<primarni_izraz>', ['ZNAK']):
            node.type = Type.CHAR
            node.l_expression = False
            # TO DO provjeriti isravnost znaka
            return True
        elif node.production == ('<primarni_izraz>', ['NIZ_ZNAKOVA']):
            node.type = Type.ARRAY_CONST_CHAR
            node.l_expression = False
            # TO DO provjeriti isravnost znakovnog niza
            return True
        elif node.production == ('<primarni_izraz>', ['L_ZAGRADA', '<izraz>', 'D_ZAGRADA']):
            izraz = self.tree.find_node(node.children[1])
            if not self.step(izraz.index, sign_table):
                raise node.production
            node.type = izraz.type
            node.l_expression = izraz.l_expression
            return True
        elif node.production == ('<postfiks_izraz>', ['<primarni_izraz>']):
            primarni_izraz = self.tree.find_node(node.children[0])
            if not self.step(primarni_izraz.index, sign_table):
                raise node.production
            node.type = primarni_izraz.type
            node.l_expression = primarni_izraz.l_expression
            return True
        elif node.production == ('<postfiks_izraz>', ['<postfiks_izraz>', 'L_UGL_ZAGRADA', '<izraz>', 'D_UGL_ZAGRADA']):
            postfiks_izraz = self.tree.find_node(node.children[0])
            if not self.step(postfiks_izraz.index, sign_table):
                raise node.production
            postfiks_izraz.type = Type.ARRAY_X
            izraz = self.tree.find_node(node.children[2])
            if not self.step(izraz.index, sign_table):
                raise node.production
            izraz.type = Type.INT

            node.type = Type.X  # PREPRAVITI LOGIKU S X NIJE DOBRO
            node.l_expression = node.type != Type.CONST_T

            return True
        elif node.production == ('<postfiks_izraz>', ['<postfiks_izraz>', 'L_ZAGRADA', 'D_ZAGRADA']):
            if not self.step(self.tree.find_node(node.children[0]).index, sign_table):
                raise node.production
            # TO DO 2. <postfiks_izraz>.tip = funkcija(void → pov )
            # node.type = pov
            node.l_expression = False
            return True
        elif node.production == (
                '<postfiks_izraz>', ['<postfiks_izraz>', 'L_ZAGRADA', '<lista_argumenata>', 'D_ZAGRADA']):
            if not self.step(self.tree.find_node(node.children[0]).index, sign_table):
                raise node.production
            if not self.step(self.tree.find_node(node.children[2]).index, sign_table):
                raise node.production

            # 3. <postfiks_izraz>.tip = funkcija(params → pov ) i redom po elementima
            # arg-tip iz <lista_argumenata>.tipovi i param-tip iz params vrijedi arg-tip
            # ∼ param-tip

            node.l_expression = False
            return True
        elif node.production == ('<postfiks_izraz>', ['<postfiks_izraz>', 'OP_INC']):
            postfiks_izraz = self.tree.find_node(node.children[0])
            if not self.step(postfiks_izraz.index, sign_table):
                raise node.production
            postfiks_izraz.l_expression = True
            postfiks_izraz.type = Type.INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<postfiks_izraz>', ['<postfiks_izraz>', 'OP_DEC']):
            postfiks_izraz = self.tree.find_node(node.children[0])
            if not self.step(postfiks_izraz.index, sign_table):
                raise node.production
            postfiks_izraz.l_expression = True
            postfiks_izraz.type = Type.INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<lista_argumenata>', ['<izraz_pridruzivanja>']):
            if not self.step(self.tree.find_node(node.children[0]).index, sign_table):
                raise node.production
            node.types.append(self.tree.find_node(node.children[0]).type)
            return True
        elif node.production == ('<lista_argumenata>', ['<lista_argumenata>', 'ZAREZ', '<izraz_pridruzivanja>']):
            if not self.step(self.tree.find_node(node.children[0]).index, sign_table):
                raise node.production
            if not self.step(self.tree.find_node(node.children[2]).index, sign_table):
                raise node.production
            node.types.append(self.tree.find_node(node.children[2]).type)
            return True
        elif node.production == ('<unarni_izraz>', ['<postfiks_izraz>']):
            postfiks_izraz = self.tree.find_node(node.children[0])
            if not self.step(postfiks_izraz.index, sign_table):
                raise node.production
            node.type = postfiks_izraz.type
            node.l_expression = postfiks_izraz.l_expression
            return True
        elif node.production == ('<unarni_izraz>', ['OP_INC', '<unarni_izraz>']):
            unarni_izraz = self.tree.find_node(node.children[1])
            unarni_izraz.l_expression = 1
            unarni_izraz.type = Type.INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<unarni_izraz>', ['OP_DEC', '<unarni_izraz>']):
            unarni_izraz = self.tree.find_node(node.children[1])
            unarni_izraz.l_expression = 1
            unarni_izraz.type = Type.INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<unarni_izraz>', ['<unarni_operator>', '<cast_izraz>']):
            cast_izraz = self.tree.find_node(node.children[1])
            if not self.step(cast_izraz.index, sign_table):
                raise node.production
            cast_izraz.type = Type.INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<unarni_operator>', ['PLUS']):
            return True
        elif node.production == ('<unarni_operator>', ['MINUS']):
            return True
        elif node.production == ('<unarni_operator>', ['OP_TILDA']):
            return True
        elif node.production == ('<unarni_operator>', ['OP_NEG']):
            return True
        elif node.production == ('<cast_izraz>', ['<unarni_izraz>']):
            unarni_izraz = self.tree.find_node(node.children[0])
            if not self.step(unarni_izraz.index, sign_table):
                raise node.production

            node.type = unarni_izraz.type
            node.l_expression = unarni_izraz.l_expression
            return True
        elif node.production == ('<cast_izraz>', ['L_ZAGRADA', '<ime_tipa>', 'D_ZAGRADA', '<cast_izraz>']):
            ime_tipa = self.tree.find_node(node.children[0])
            if not self.step(ime_tipa.index, sign_table):
                raise node.production
            if not self.step(self.tree.find_node(node.children[3]).index, sign_table):
                raise node.production
            # 3. <cast_izraz>.tip se moˇze pretvoriti u <ime_tipa>.tip po poglavlju 4.3.1

            node.type = ime_tipa.type
            node.l_expression = False
            return True
        elif node.production == ('<ime_tipa>', ['<specifikator_tipa>']):
            specifikator_tipa = self.tree.find_node(node.children[0])
            if not self.step(specifikator_tipa.index, sign_table):
                raise node.production
            node.type = specifikator_tipa.type
            return True
        elif node.production == ('<ime_tipa>', ['KR_CONST', '<specifikator_tipa>']):
            specifikator_tipa = self.tree.find_node(node.children[0])
            if not self.step(specifikator_tipa.index, sign_table):
                raise node.production
            if specifikator_tipa.type == Type.VOID:
                raise node.production
            node.type = specifikator_tipa.type
            node.const = True
            return True
        elif node.production == ('<specifikator_tipa>', ['KR_VOID']):
            node.type = Type.VOID
            return True
        elif node.production == ('<specifikator_tipa>', ['KR_CHAR']):
            node.type = Type.CHAR
            return True
        elif node.production == ('<specifikator_tipa>', ['KR_INT']):
            node.type = Type.INT
            return True
        elif node.production == ('<multiplikativni_izraz>', ['<cast_izraz>']):
            multiplikativni_izraz = self.tree.find_node(node.children[0])
            if not self.step(multiplikativni_izraz.index, sign_table):
                raise node.production
            node.type = multiplikativni_izraz.type
            node.l_expression = multiplikativni_izraz.l_expression
            return True
        elif node.production == ('<multiplikativni_izraz>', ['<multiplikativni_izraz>', 'OP_PUTA', '<cast_izraz>']):
            multiplikativni_izraz = self.tree.find_node(node.children[0])
            if not self.step(multiplikativni_izraz.index, sign_table):
                raise node.production

            # to do provjera multiplikativni_izraz.type se moze pretvoriti u INT

            cast_izraz = self.tree.find_node(node.children[2])
            if not self.step(cast_izraz.index, sign_table):
                raise node.production

            # to do provjera cast_izraz.type se moze pretvoriti u INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<multiplikativni_izraz>', ['<multiplikativni_izraz>', 'OP_DIJELI', '<cast_izraz>']):
            multiplikativni_izraz = self.tree.find_node(node.children[0])
            if not self.step(multiplikativni_izraz.index, sign_table):
                raise node.production

            # to do provjera multiplikativni_izraz.type se moze pretvoriti u INT

            cast_izraz = self.tree.find_node(node.children[2])
            if not self.step(cast_izraz.index, sign_table):
                raise node.production

            # to do provjera cast_izraz.type se moze pretvoriti u INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<multiplikativni_izraz>', ['<multiplikativni_izraz>', 'OP_MOD', '<cast_izraz>']):
            multiplikativni_izraz = self.tree.find_node(node.children[0])
            if not self.step(multiplikativni_izraz.index, sign_table):
                raise node.production

            # to do provjera multiplikativni_izraz.type se moze pretvoriti u INT

            cast_izraz = self.tree.find_node(node.children[2])
            if not self.step(cast_izraz.index, sign_table):
                raise node.production

            # to do provjera cast_izraz.type se moze pretvoriti u INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<aditivni_izraz>', ['<multiplikativni_izraz>']):
            multiplikativni_izraz = self.tree.find_node(node.children[0])
            if not self.step(multiplikativni_izraz.index, sign_table):
                raise node.production

            node.type = multiplikativni_izraz.type
            node.l_expression = multiplikativni_izraz.l_expression
            return True
        elif node.production == ('<aditivni_izraz>', ['<aditivni_izraz>', 'PLUS', '<multiplikativni_izraz>']):
            aditivni_izraz = self.tree.find_node(node.children[0])
            if not self.step(aditivni_izraz.index, sign_table):
                raise node.production

            # to do provjera aditivni_izraz.type se moze pretvoriti u INT

            multiplikativni_izraz = self.tree.find_node(node.children[2])
            if not self.step(multiplikativni_izraz.index, sign_table):
                raise node.production

            # to do provjera cast_izraz.type se moze pretvoriti u INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<aditivni_izraz>', ['<aditivni_izraz>', 'MINUS', '<multiplikativni_izraz>']):
            aditivni_izraz = self.tree.find_node(node.children[0])
            if not self.step(aditivni_izraz.index, sign_table):
                raise node.production

            # to do provjera aditivni_izraz.type se moze pretvoriti u INT

            multiplikativni_izraz = self.tree.find_node(node.children[2])
            if not self.step(multiplikativni_izraz.index, sign_table):
                raise node.production

            # to do provjera cast_izraz.type se moze pretvoriti u INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<odnosni_izraz>', ['<aditivni_izraz>']):
            aditivni_izraz = self.tree.find_node(node.children[0])
            if not self.step(aditivni_izraz.index, sign_table):
                raise node.production
            node.type = aditivni_izraz.type
            node.l_expression = aditivni_izraz.l_expression
            return True
        elif node.production == ('<odnosni_izraz>', ['<odnosni_izraz>', 'OP_LT', '<aditivni_izraz>']):
            odnosni_izraz = self.tree.find_node(node.children[0])
            if not self.step(odnosni_izraz.index, sign_table):
                raise node.production
            # to do provjera odnosni_izraz.type se moze pretvoriti u INT

            aditivni_izraz = self.tree.find_node(node.children[2])
            if not self.step(aditivni_izraz.index, sign_table):
                raise node.production
            # to do provjera aditivni_izraz.type se moze pretvoriti u INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<odnosni_izraz>', ['<odnosni_izraz>', 'OP_GT', '<aditivni_izraz>']):
            odnosni_izraz = self.tree.find_node(node.children[0])
            if not self.step(odnosni_izraz.index, sign_table):
                raise node.production
            # to do provjera odnosni_izraz.type se moze pretvoriti u INT

            aditivni_izraz = self.tree.find_node(node.children[2])
            if not self.step(aditivni_izraz.index, sign_table):
                raise node.production
            # to do provjera aditivni_izraz.type se moze pretvoriti u INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<odnosni_izraz>', ['<odnosni_izraz>', 'OP_LTE', '<aditivni_izraz>']):
            odnosni_izraz = self.tree.find_node(node.children[0])
            if not self.step(odnosni_izraz.index, sign_table):
                raise node.production
            # to do provjera odnosni_izraz.type se moze pretvoriti u INT

            aditivni_izraz = self.tree.find_node(node.children[2])
            if not self.step(aditivni_izraz.index, sign_table):
                raise node.production
            # to do provjera aditivni_izraz.type se moze pretvoriti u INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<odnosni_izraz>', ['<odnosni_izraz>', 'OP_GTE', '<aditivni_izraz>']):
            odnosni_izraz = self.tree.find_node(node.children[0])
            if not self.step(odnosni_izraz.index, sign_table):
                raise node.production
            # to do provjera odnosni_izraz.type se moze pretvoriti u INT

            aditivni_izraz = self.tree.find_node(node.children[2])
            if not self.step(aditivni_izraz.index, sign_table):
                raise node.production
            # to do provjera aditivni_izraz.type se moze pretvoriti u INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<jednakosni_izraz>', ['<odnosni_izraz>']):
            odnosni_izraz = self.tree.find_node(node.children[0])
            if not self.step(odnosni_izraz.index, sign_table):
                raise node.production
            node.type = odnosni_izraz.type
            node.l_expression = odnosni_izraz.l_expression
            return True
        elif node.production == ('<jednakosni_izraz>', ['<jednakosni_izraz>', 'OP_EQ', '<odnosni_izraz>']):
            jednakosni_izraz = self.tree.find_node(node.children[0])
            if not self.step(jednakosni_izraz.index, sign_table):
                raise node.production
            # to do provjera jednakosni_izraz.type se moze pretvoriti u INT

            odnosni_izraz = self.tree.find_node(node.children[2])
            if not self.step(odnosni_izraz.index, sign_table):
                raise node.production
            # to do provjera odnosni_izraz.type se moze pretvoriti u INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<jednakosni_izraz>', ['<jednakosni_izraz>', 'OP_NEQ', '<odnosni_izraz>']):
            jednakosni_izraz = self.tree.find_node(node.children[0])
            if not self.step(jednakosni_izraz.index, sign_table):
                raise node.production
            # to do provjera jednakosni_izraz.type se moze pretvoriti u INT

            odnosni_izraz = self.tree.find_node(node.children[2])
            if not self.step(odnosni_izraz.index, sign_table):
                raise node.production
            # to do provjera odnosni_izraz.type se moze pretvoriti u INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<bin_i_izraz>', ['<jednakosni_izraz>']):
            jednakosni_izraz = self.tree.find_node(node.children[0])
            if not self.step(jednakosni_izraz.index, sign_table):
                raise node.production
            node.type = jednakosni_izraz.type
            node.l_expression = jednakosni_izraz.l_expression
            return True
        elif node.production == ('<bin_i_izraz>', ['<bin_i_izraz>', 'OP_BIN_I', '<jednakosni_izraz>']):
            bin_i_izraz = self.tree.find_node(node.children[0])
            if not self.step(bin_i_izraz.index, sign_table):
                raise node.production
            # to do provjera bin_i_izraz.type se moze pretvoriti u INT

            jednakosni_izraz = self.tree.find_node(node.children[2])
            if not self.step(jednakosni_izraz.index, sign_table):
                raise node.production
            # to do provjera jednakosni_izraz.type se moze pretvoriti u INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<bin_xili_izraz>', ['<bin_i_izraz>']):
            bin_i_izraz = self.tree.find_node(node.children[0])
            if not self.step(bin_i_izraz.index, sign_table):
                raise node.production
            node.type = bin_i_izraz.type
            node.l_expression = bin_i_izraz.l_expression
            return True
        elif node.production == ('<bin_xili_izraz>', ['<bin_xili_izraz>', 'OP_BIN_XILI', '<bin_i_izraz>']):
            bin_xili_izraz = self.tree.find_node(node.children[0])
            if not self.step(bin_xili_izraz.index, sign_table):
                raise node.production
            # to do provjera bin_xili_izraz.type se moze pretvoriti u INT

            bin_i_izraz = self.tree.find_node(node.children[2])
            if not self.step(bin_i_izraz.index, sign_table):
                raise node.production
            # to do provjera bin_i_izraz.type se moze pretvoriti u INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<bin_ili_izraz>', ['<bin_xili_izraz>']):
            bin_xili_izraz = self.tree.find_node(node.children[0])
            if not self.step(bin_xili_izraz.index, sign_table):
                raise node.production
            node.type = bin_xili_izraz.type
            node.l_expression = bin_xili_izraz.l_expression
            return True
        elif node.production == ('<bin_ili_izraz>', ['<bin_ili_izraz>', 'OP_BIN_ILI', '<bin_xili_izraz>']):
            bin_ili_izraz = self.tree.find_node(node.children[0])
            if not self.step(bin_ili_izraz.index, sign_table):
                raise node.production
            # to do provjera bin_ili_izraz.type se moze pretvoriti u INT

            bin_xili_izraz = self.tree.find_node(node.children[2])
            if not self.step(bin_xili_izraz.index, sign_table):
                raise node.production
            # to do provjera bin_xili_izraz.type se moze pretvoriti u INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<log_i_izraz>', ['<bin_ili_izraz>']):
            bin_ili_izraz = self.tree.find_node(node.children[0])
            if not self.step(bin_ili_izraz.index, sign_table):
                raise node.production
            node.type = bin_ili_izraz.type
            node.l_expression = bin_ili_izraz.l_expression
            return True
        elif node.production == ('<log_i_izraz>', ['<log_i_izraz>', 'OP_I', '<bin_ili_izraz>']):
            log_i_izraz = self.tree.find_node(node.children[0])
            if not self.step(log_i_izraz.index, sign_table):
                raise node.production
            # to do provjera log_i_izraz.type se moze pretvoriti u INT

            bin_ili_izraz = self.tree.find_node(node.children[2])
            if not self.step(bin_ili_izraz.index, sign_table):
                raise node.production
            # to do provjera bin_ili_izraz.type se moze pretvoriti u INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<log_ili_izraz>', ['<log_i_izraz>']):
            log_i_izraz = self.tree.find_node(node.children[0])
            if not self.step(log_i_izraz.index, sign_table):
                raise node.production
            node.type = log_i_izraz.type
            node.l_expression = log_i_izraz.l_expression
            return True
        elif node.production == ('<log_ili_izraz>', ['<log_ili_izraz>', 'OP_ILI', '<log_i_izraz>']):
            log_ili_izraz = self.tree.find_node(node.children[0])
            if not self.step(log_ili_izraz.index, sign_table):
                raise node.production
            # to do provjera log_ili_izraz.type se moze pretvoriti u INT

            log_i_izraz = self.tree.find_node(node.children[2])
            if not self.step(log_i_izraz.index, sign_table):
                raise node.production
            # to do provjera log_i_izraz.type se moze pretvoriti u INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<izraz_pridruzivanja>', ['<log_ili_izraz>']):
            log_ili_izraz = self.tree.find_node(node.children[0])
            if not self.step(log_ili_izraz.index, sign_table):
                raise node.production
            node.type = log_ili_izraz.type
            node.l_expression = log_ili_izraz.l_expression
            return True
        elif node.production == ('<izraz_pridruzivanja>', ['<postfiks_izraz>', 'OP_PRIDRUZI', '<izraz_pridruzivanja>']):
            postfiks_izraz = self.tree.find_node(node.children[0])
            if (not self.step(postfiks_izraz.index, sign_table)) or (not postfiks_izraz.l_expression):
                raise node.production

            izraz_pridruzivanja = self.tree.find_node(node.children[2])
            if not self.step(izraz_pridruzivanja.index, sign_table):
                raise node.production
            # to do provjera izraz_pridruzivanja.type se moze pretvoriti u INT

            node.type = Type.INT
            node.l_expression = False
            return True
        elif node.production == ('<izraz>', ['<izraz_pridruzivanja>']):
            izraz_pridruzivanja = self.tree.find_node(node.children[0])
            if not self.step(izraz_pridruzivanja.index, sign_table):
                raise node.production
            node.type = izraz_pridruzivanja.type
            node.l_expression = izraz_pridruzivanja.l_expression
            return True
        elif node.production == ('<izraz>', ['<izraz>', 'ZAREZ', '<izraz_pridruzivanja>']):
            izraz = self.tree.find_node(node.children[0])
            if not self.step(izraz.index, sign_table):
                raise node.production
            izraz_pridruzivanja = self.tree.find_node(node.children[2])
            if not self.step(izraz_pridruzivanja.index, sign_table):
                raise node.production
            node.type = izraz_pridruzivanja.type
            node.l_expression = False
            return True
        elif node.production == ('<slozena_naredba>', ['L_VIT_ZAGRADA', '<lista_naredbi>', 'D_VIT_ZAGRADA']):
            lista_naredbi = self.tree.find_node(node.children[1])
            if not self.step(lista_naredbi.index, sign_table):
                raise node.production
            return True
        elif node.production == (
                '<slozena_naredba>', ['L_VIT_ZAGRADA', '<lista_deklaracija>', '<lista_naredbi>', 'D_VIT_ZAGRADA']):
            lista_deklaracija = self.tree.find_node(node.children[1])
            if not self.step(lista_deklaracija.index, sign_table):
                raise node.production
            lista_naredbi = self.tree.find_node(node.children[2])
            if not self.step(lista_naredbi.index, sign_table):
                raise node.production
            return True
        elif node.production == ('<lista_naredbi>', ['<naredba>']):
            naredba = self.tree.find_node(node.children[0])
            if not self.step(naredba.index, sign_table):
                raise node.production
            return True
        elif node.production == ('<lista_naredbi>', ['<lista_naredbi>', '<naredba>']):
            lista_naredbi = self.tree.find_node(node.children[0])
            if not self.step(lista_naredbi.index, sign_table):
                raise node.production
            naredba = self.tree.find_node(node.children[1])
            if not self.step(naredba.index, sign_table):
                raise node.production
            return True
        elif node.production == ('<naredba>', ['<slozena_naredba>']):
            slozena_naredba = self.tree.find_node(node.children[0])
            if not self.step(slozena_naredba.index, sign_table):
                raise node.production
            return True
        elif node.production == ('<naredba>', ['<izraz_naredba>']):
            izraz_naredba = self.tree.find_node(node.children[0])
            if not self.step(izraz_naredba.index, sign_table):
                raise node.production
            return True
        elif node.production == ('<naredba>', ['<naredba_grananja>']):
            naredba_grananja = self.tree.find_node(node.children[0])
            if not self.step(naredba_grananja.index, sign_table):
                raise node.production
            return True
        elif node.production == ('<naredba>', ['<naredba_petlje>']):
            naredba_petlje = self.tree.find_node(node.children[0])
            if not self.step(naredba_petlje.index, sign_table):
                raise node.production
            return True
        elif node.production == ('<naredba>', ['<naredba_skoka>']):
            naredba_skoka = self.tree.find_node(node.children[0])
            if not self.step(naredba_skoka.index, sign_table):
                raise node.production
            return True
        elif node.production == ('<izraz_naredba>', ['TOCKAZAREZ']):
            node.type = Type.INT
            return True
        elif node.production == ('<izraz_naredba>', ['<izraz>', 'TOCKAZAREZ']):
            izraz = self.tree.find_node(node.children[0])
            if not self.step(izraz.index, sign_table):
                raise node.production
            node.type = izraz.type
            return True
        elif node.production == ('<naredba_grananja>', ['KR_IF', 'L_ZAGRADA', '<izraz>', 'D_ZAGRADA', '<naredba>']):
            izraz = self.tree.find_node(node.children[2])
            if not self.step(izraz.index, sign_table):
                raise node.production
            # to do provjeriti moze li se izraz.type pretvoriti u INT

            naredba = self.tree.find_node(node.children[4])
            if not self.step(naredba.index, sign_table):
                raise node.production
            return True
        elif node.production == (
                '<naredba_grananja>',
                ['KR_IF', 'L_ZAGRADA', '<izraz>', 'D_ZAGRADA', '<naredba>', 'KR_ELSE', '<naredba>']):
            izraz = self.tree.find_node(node.children[2])
            if not self.step(izraz.index, sign_table):
                raise node.production
            # to do provjeriti moze li se izraz.type pretvoriti u INT

            naredba = self.tree.find_node(node.children[4])
            if not self.step(naredba.index, sign_table):
                raise node.production

            naredba_1 = self.tree.find_node(node.children[6])
            if not self.step(naredba_1.index, sign_table):
                raise node.production

            return True
        elif node.production == ('<naredba_petlje>', ['KR_WHILE', 'L_ZAGRADA', '<izraz>', 'D_ZAGRADA', '<naredba>']):
            izraz = self.tree.find_node(node.children[2])
            if not self.step(izraz.index, sign_table):
                raise node.production
            # to do provjeriti moze li se izraz.type pretvoriti u INT

            naredba = self.tree.find_node(node.children[4])
            if not self.step(naredba.index, sign_table):
                raise node.production
            return True
        elif node.production == (
                '<naredba_petlje>',
                ['KR_FOR', 'L_ZAGRADA', '<izraz_naredba>', '<izraz_naredba>', 'D_ZAGRADA', '<naredba>']):
            izraz_naredba_1 = self.tree.find_node(node.children[2])
            if not self.step(izraz_naredba_1.index, sign_table):
                raise node.production

            izraz_naredba_2 = self.tree.find_node(node.children[3])
            if not self.step(izraz_naredba_2.index, sign_table):
                raise node.production
            # to do provjeriti moze li se izraz_naredba_2.type pretvoriti u INT

            naredba = self.tree.find_node(node.children[5])
            if not self.step(naredba.index, sign_table):
                raise node.production
            return True
        elif node.production == ('<naredba_petlje>',
                                 ['KR_FOR', 'L_ZAGRADA', '<izraz_naredba>', '<izraz_naredba>', '<izraz>', 'D_ZAGRADA',
                                  '<naredba>']):
            izraz_naredba_1 = self.tree.find_node(node.children[2])
            if not self.step(izraz_naredba_1.index, sign_table):
                raise node.production

            izraz_naredba_2 = self.tree.find_node(node.children[3])
            if not self.step(izraz_naredba_2.index, sign_table):
                raise node.production
            # to do provjeriti moze li se izraz_naredba_2.type pretvoriti u INT

            izraz = self.tree.find_node(node.children[4])
            if not self.step(izraz.index, sign_table):
                raise node.production

            naredba = self.tree.find_node(node.children[6])
            if not self.step(naredba.index, sign_table):
                raise node.production
            return True
        elif node.production == ('<naredba_skoka>', ['KR_CONTINUE', 'TOCKAZAREZ']):
            # naredba se nalazi unutar petlje ili unutar bloka koji je ugnijeˇzden u petl
            parent = self.tree.find_node(node.parent)
            while True:
                if parent.name == "<naredba_petlje>":
                    return True
                elif parent.name == "<prijevodna_jedinica>":
                    raise node.production
                else:
                    parent = self.tree.find_node(parent.parent)
        elif node.production == ('<naredba_skoka>', ['KR_BREAK', 'TOCKAZAREZ']):
            parent = self.tree.find_node(node.parent)
            while True:
                if parent.name == "<naredba_petlje>":
                    return True
                elif parent.name == "<prijevodna_jedinica>":
                    raise node.production
                else:
                    parent = self.tree.find_node(parent.parent)
        elif node.production == ('<naredba_skoka>', ['KR_RETURN', 'TOCKAZAREZ']):
            # to do 1. naredba se nalazi unutar funkcije tipa funkcija(params → void)
            parent = self.tree.find_node(node.parent)
            while True:
                if parent.type == "funkcija(params → void)":  # POSSIBLE PROBLEM
                    return True
                elif parent.name == "<prijevodna_jedinica>":
                    raise node.production
                else:
                    parent = self.tree.find_node(parent.parent)
        elif node.production == ('<naredba_skoka>', ['KR_RETURN', '<izraz>', 'TOCKAZAREZ']):
            izraz = self.tree.find_node(node.children[1])
            if not self.step(izraz.index, sign_table):
                raise node.production
            # to do provjeriti moze li se izraz.type pretvoriti u INT

            while True:
                if parent.type == "funkcija(params → pov )":  # POSSIBLE PROBLEM
                    return True
                elif parent.name == "<prijevodna_jedinica>":
                    raise node.production
                else:
                    parent = self.tree.find_node(parent.parent)
        elif node.production == ('<prijevodna_jedinica>', ['<vanjska_deklaracija>']):
            vanjska_deklaracija = self.tree.find_node(node.children[0])
            if not self.step(vanjska_deklaracija.index, sign_table):
                raise node.production
            return True
        elif node.production == ('<prijevodna_jedinica>', ['<prijevodna_jedinica>', '<vanjska_deklaracija>']):
            prijevodna_jedinica = self.tree.find_node(node.children[0])
            if not self.step(prijevodna_jedinica.index, sign_table):
                raise node.production
            vanjska_deklaracija = self.tree.find_node(node.children[1])
            if not self.step(vanjska_deklaracija.index, sign_table):
                raise node.production
            return True
        elif node.production == ('<vanjska_deklaracija>', ['<definicija_funkcije>']):
            definicija_funkcije = self.tree.find_node(node.children[0])
            if not self.step(definicija_funkcije.index, sign_table):
                raise node.production
            return True
        elif node.production == ('<vanjska_deklaracija>', ['<deklaracija>']):
            deklaracija = self.tree.find_node(node.children[0])
            if not self.step(deklaracija.index, sign_table):
                raise node.production
            return True
        elif node.production == (
                '<definicija_funkcije>',
                ['<ime_tipa>', 'IDN', 'L_ZAGRADA', 'KR_VOID', 'D_ZAGRADA', '<slozena_naredba>']):
            ime_tipa = self.tree.find_node(node.children[0])
            if not self.step(ime_tipa.index, sign_table):
                raise node.production
            if ime_tipa.type == Type.T and ime_tipa.const:
                raise node.production
            # to do 3. ne postoji prije definirana funkcija imena IDN.ime
            # 4. ako postoji deklaracija imena IDN.ime u globalnom djelokrugu onda je pripadni
            # tip te deklaracije funkcija(void → <ime_tipa>.tip)
            # 5. zabiljeˇzi definiciju i deklaraciju funkcije

            slozena_naredba = self.tree.find_node(node.children[5])
            if not self.step(slozena_naredba.index, sign_table):
                raise node.production
            return True
        elif node.production == ('<definicija_funkcije>',
                                 ['<ime_tipa>', 'IDN', 'L_ZAGRADA', '<lista_parametara>', 'D_ZAGRADA',
                                  '<slozena_naredba>']):
            ime_tipa = self.tree.find_node(node.children[0])
            if not self.step(ime_tipa.index, sign_table):
                raise node.production
            if ime_tipa.type == Type.T and ime_tipa.const:
                raise node.production
            # to do 3. ne postoji prije definirana funkcija imena IDN.ime
            lista_parametara = self.tree.find_node(node.children[3])
            if not self.step(lista_parametara.index, sign_table):
                raise node.production
            # to do 5. ako postoji deklaracija imena IDN.ime u globalnom djelokrugu onda je pripadni
            # tip te deklaracije funkcija(<lista_parametara>.tipovi → <ime_tipa>.tip)
            # 6. zabiljeˇzi definiciju i deklaraciju funkcije
            # 7. provjeri (<slozena_naredba>) uz parametre funkcije koriste ́ci <lista_parametara>.tipovi
            # i <lista_parametara>.imena
            return True
        elif node.production == ('<lista_parametara>', ['<deklaracija_parametra>']):
            deklaracija_parametra = self.tree.find_node(node.children[0])
            if not self.step(deklaracija_parametra.index, sign_table):
                raise node.production
            node.types.append(deklaracija_parametra.type)
            node.names.append(deklaracija_parametra.name)
            return True
        elif node.production == ('<lista_parametara>', ['<lista_parametara>', 'ZAREZ', '<deklaracija_parametra>']):
            lista_parametara = self.tree.find_node(node.children[0])
            if not self.step(lista_parametara.index, sign_table):
                raise node.production
            deklaracija_parametra = self.tree.find_node(node.children[2])
            if not self.step(deklaracija_parametra.index, sign_table):
                raise node.production
            if deklaracija_parametra.name in lista_parametara.names:
                raise node.production

            node.types.append(lista_parametara.types)
            node.types.append(deklaracija_parametra.types)
            node.names.append(lista_parametara.names)
            node.names.append(deklaracija_parametra.name)
            return True
        elif node.production == ('<deklaracija_parametra>', ['<ime_tipa>', 'IDN']):
            ime_tipa = self.tree.find_node(node.children[0])
            if (not self.step(ime_tipa.index, sign_table)) or (ime_tipa.type == Type.VOID):
                raise node.production
            node.type = ime_tipa.type
            node.name = self.tree.find_node(node.children[1]).name
            return True
        elif node.production == ('<deklaracija_parametra>', ['<ime_tipa>', 'IDN', 'L_UGL_ZAGRADA', 'D_UGL_ZAGRADA']):
            ime_tipa = self.tree.find_node(node.children[0])
            if (not self.step(ime_tipa.index, sign_table)) or (ime_tipa.type == Type.VOID):
                raise node.production
            node.type = "ARRAY_" + ime_tipa.type
            node.name = self.tree.find_node(node.children[1]).name
            return True
        elif node.production == ('<lista_deklaracija>', ['<deklaracija>']):
            deklaracija = self.tree.find_node(node.children[0])
            if not self.step(deklaracija.index, sign_table):
                raise node.production
            return True
        elif node.production == ('<lista_deklaracija>', ['<lista_deklaracija>', '<deklaracija>']):
            lista_deklaracija = self.tree.find_node(node.children[0])
            if not self.step(lista_deklaracija.index, sign_table):
                raise node.production
            deklaracija = self.tree.find_node(node.children[1])
            if not self.step(deklaracija.index, sign_table):
                raise node.production
            return True
        elif node.production == ('<deklaracija>', ['<ime_tipa>', '<lista_init_deklaratora>', 'TOCKAZAREZ']):
            ime_tipa = self.tree.find_node(node.children[0])
            if not self.step(ime_tipa.index, sign_table):
                raise node.production
            lista_init_deklaratora = self.tree.find_node(node.children[1])
            # provjeri (<lista_init_deklaratora>) to do uz nasljedno svojstvo <lista_init_deklaratora>.ntip ← <ime_tipa>.tip
            if not self.step(lista_init_deklaratora.index, sign_table):
                raise node.production
            return True
        elif node.production == ('<lista_init_deklaratora>', ['<init_deklarator>']):
            return True
        elif node.production == (
                '<lista_init_deklaratora>', ['<lista_init_deklaratora>', 'ZAREZ', '<init_deklarator>']):
            return True
        elif node.production == ('<init_deklarator>', ['<izravni_deklarator>']):
            return True
        elif node.production == ('<init_deklarator>', ['<izravni_deklarator>', 'OP_PRIDRUZI', '<inicijalizator>']):
            return True
        elif node.production == ('<izravni_deklarator>', ['IDN']):
            return True
        elif node.production == ('<izravni_deklarator>', ['IDN', 'L_UGL_ZAGRADA', 'BROJ', 'D_UGL_ZAGRADA']):
            return True
        elif node.production == ('<izravni_deklarator>', ['IDN', 'L_ZAGRADA', 'KR_VOID', 'D_ZAGRADA']):
            return True
        elif node.production == ('<izravni_deklarator>', ['IDN', 'L_ZAGRADA', '<lista_parametara>', 'D_ZAGRADA']):
            return True
        elif node.production == ('<inicijalizator>', ['<izraz_pridruzivanja>']):
            return True
        elif node.production == (
                '<inicijalizator>', ['L_VIT_ZAGRADA', '<lista_izraza_pridruzivanja>', 'D_VIT_ZAGRADA']):
            return True
        elif node.production == ('<lista_izraza_pridruzivanja>', ['<izraz_pridruzivanja>']):
            return True
        elif node.production == (
                '<lista_izraza_pridruzivanja>', ['<lista_izraza_pridruzivanja>', 'ZAREZ', '<izraz_pridruzivanja>']):
            return True
