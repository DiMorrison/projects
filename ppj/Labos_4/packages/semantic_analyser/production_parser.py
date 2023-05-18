from dataclasses import dataclass
from typing import List, Tuple


# parsira sve produkcije iz filea, u bnf notaciji
# odvaja lijevu stranu, i sprema za nju listu znakova koji su na desnoj strani
@dataclass
class ProductionParser:
    productions: List[Tuple[str, List[str]]]
    path: str

    def __init__(self, path: str):
        self.path = path
        self.productions = list()

    def parse_productions(self):
        file = open(self.path, "r")
        last_left_side: str = ""
        right_side: List[str] = list()
        for line in file:
            line = line.strip()
            right_side = list()

            if line.startswith("<"):
                split = line.split(" ")
                last_left_side = split[0]
                for i in range(2, len(split)):
                    right_side.append(split[i])
                self.productions.append((last_left_side, right_side))

            elif line.startswith("|"):
                split = line.split(" ")
                for i in range(1, len(split)):
                    right_side.append(split[i])
                self.productions.append((last_left_side, right_side))

        # for prod in productions:
        #    print(prod)

    # provjera je li produkcija u zadanoj gramatici
    def check_production(self, production: Tuple[str, List[str]]):
        if len(self.productions) == 0:
            self.parse_productions()
        if production in self.productions:
            return True
        return False

# par = ProductionParser("bnf.txt")
# par.parse_productions()
# for prod in par.productions:
#    print(prod)
