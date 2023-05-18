from dataclasses import dataclass
from typing import List

from property import Symbol, NonTerminal, Terminal, Property


# pdf potpoglavlje 4.4.4 preslikavam pravila
@dataclass
class PrimarniIzraz(Property):

    def __init__(self, right_symbols: List[Symbol]):
        super().__init__(NonTerminal("<primarni_izraz>", "", "", "", False), right_symbols)
        if len(self.right_symbols) == 1:
            self.left_nonTerminal.l_expression = False
            if self.right_symbols[0].name == "IDN":
                self.left_nonTerminal.type = "int"
                # TODO provjera je li broj u INT rasponu
                self.left_nonTerminal.derived_property = int(self.right_symbols[0].value)
            if self.right_symbols[0].name == "ZNAK":
                self.left_nonTerminal.type = "char"
                # TODO implementirati provjeru u 4.3.2
            if self.right_symbols[0].name == "NIZ_ZNAKOVA":
                self.left_nonTerminal.type = "niz(const(char))"
                # TODO implementirati provjeru u 4.3.2
        elif self.right_symbols[0].name == "L_ZAGRADA" and self.right_symbols[1].name == "<izraz>" and \
                self.right_symbols[2].name == "D_ZAGRADA":
            self.left_nonTerminal.type = self.right_symbols[1].type
            self.left_nonTerminal.l_expression = self.right_symbols[1].l_expression
            # TODO provjeri(<izraz>)


@dataclass
class PostfiksIzraz(Property):
    def __init__(self, right_symbols: List[Symbol]):
        super().__init__(NonTerminal("<postfiks_izraz>", "", "", "", False), right_symbols)
        if self.right_symbols[0].name == "<primarni_izraz>":
            self.left_nonTerminal.type = self.right_symbols[0].type
            self.left_nonTerminal.l_expression = self.right_symbols[0].l_expression
        if self.right_symbols[0].name == "<postfiks_izraz>" and self.right_symbols[1].name == "L_UGL_ZAGRADA" and \
                self.right_symbols[2].name == "<izraz>" and self.right_symbols[3].name == "D_UGL_ZAGRADA":
            print()
            # TODO provjeri(<postfix_izraz)
            # <postfiks_izraz>.tip = niz (X )
            # provjeri (<izraz>)
            # <izraz>.tip ∼ int
        if self.right_symbols[0].name == "<postfiks_izraz>" and self.right_symbols[1].name == "L_ZAGRADA" and \
                self.right_symbols[2].name == "D_ZAGRADA":
            # TODO provjeri (<postfiks_izraz>)
            self.left_nonTerminal.type = "funkcija(void -> pov)"  # prepraviti
        if self.right_symbols[0].name == "<postfiks_izraz>" and self.right_symbols[1].name == "L_ZAGRADA" and \
                self.right_symbols[2].name == "<lista_argumenata>" and self.right_symbols[3].name == "D_ZAGRADA":
            # TODO provjeri (<postfiks_izraz>)
            # TODO provjeri (<lista_argumenata>)
            self.left_nonTerminal.type = "funkcija(void -> pov)"  # TODO prepraviti IMA PRAVILO KAKO PROVJERITI
        if self.right_symbols[0].name == "<postfiks_izraz>" and self.right_symbols[1].name == "OP_INC" or \
                self.right_symbols[1].name == "OP_DEC":
            # TODO provjeri (<postfiks_izraz>)
            self.left_nonTerminal.l_expression = True
            self.left_nonTerminal.type = "int"


@dataclass
class ListaArgumenata(Property):

    def __init__(self, right_symbols: List[Symbol]):
        super().__init__(NonTerminal("<lista_argumenata>", "", "", "", False), right_symbols)
        if self.right_symbols[0].name == "<izraz_pridruzivanja>":
            # TODO provjeri (<izraz_pridruzivanja>)
            self.left_nonTerminal.types.append(self.right_symbols[0].type)
        if self.right_symbols[0].name == "<lista_argumenata>" and self.right_symbols[1].name == "ZAREZ" and \
                self.right_symbols[2].name == "<izraz_pridruzivanja>":
            # TODO provjeri (<lista_argumenata>)
            # TODO provjeri (<izraz_pridruzivanja>)
            self.left_nonTerminal.types.append(self.right_symbols[0].types)
            self.left_nonTerminal.types.append(self.right_symbols[2].type)


@dataclass
class UnarniIzraz(Property):
    def __init__(self, right_symbols: List[Symbol]):
        super().__init__(NonTerminal("<unarni_izraz>", "", "", "", False), right_symbols)
        if self.right_symbols[0].name == "<postfiks_izraz>":
            self.left_nonTerminal.type = self.right_symbols[0].type
            self.left_nonTerminal.l_expression = self.right_symbols[0].l_expression
            # TODO provjeri (<postfiks_izraz>)
        if (self.right_symbols[0].name == "OP_INC" or self.right_symbols[0].name == "OP_DEC") and \
                self.right_symbols[1].name == "<unarni_izraz>":
            self.left_nonTerminal.type = "int"
            self.left_nonTerminal.l_expression = False
            # TODO 1. provjeri (<unarni_izraz>)
            # TODO 2. <unarni_izraz>.l-izraz = 1 i <unarni_izraz>.tip ∼ int

        if self.right_symbols[0].name == "<unarni_operator>" and self.right_symbols[1].name == "<cast_izraz>":
            self.left_nonTerminal.type = "int"
            self.left_nonTerminal.l_expression = False
            # TODO 1. provjeri (<cast_izraz>)
            # TODO 2. <cast_izraz>.tip ∼ int


@dataclass
class CastIzraz(Property):
    def __init__(self, right_symbols: List[Symbol]):
        super().__init__(NonTerminal("<cast_izraz>", "", "", "", False), right_symbols)

        if self.right_symbols[0].name == "<unarni_izraz>":
            self.left_nonTerminal.type = self.right_symbols[0].type
            self.left_nonTerminal.l_expression = self.right_symbols[0].l_expression
            # TODO 1. provjeri (<unarni_izraz)
