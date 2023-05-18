from dataclasses import dataclass
from typing import List, Dict, Tuple

from .node import Node


# na osnovu ulazne datoteke stvaram stablo, tj pretvaram indent zapis u čvorove
@dataclass
class Tree:
    nodes: List[Node]
    root: Node
    counter: int
    lastOnLevel: List[int]  # id čvora koji se pojavio kao zadnji na nekoj razini

    def __init__(self, input_data: str):
        self.nodes = list()
        self.root = Node("<prijevodna_jedinica>", 0, -1)
        self.counter = 0
        self.load_tree(input_data)

    def find_node(self, index: int):
        for n in self.nodes:
            if n.index == index:
                return n

    def load_tree(self, input_data: str):
        lines: List[str] = list()
        levels: Dict[int, List[str]] = dict()
        counter: int = 0
        last_on_level: Dict[int, Node] = dict()

        for line in input_data.splitlines():
            lines.append(line)

        #print(lines)

        for line in lines:
            indent: int = len(line) - len(line.lstrip(' ')) + 1  # po ovome gledam dubinu čvora u stablu
            counter += 1  # counter kako bih pridruzio jedinstven index svakom cvoru - efektivno dobijem depth first search kad bih slijedno pratio indexe

            if indent not in levels:
                levels.update({indent: []})

            if line == "<prijevodna_jedinica>":  # slucaj kada pocnemo citati stablo, inicijalizacija korjena - uvijek pocinje s ovim
                self.root.name = "<prijevodna_jedinica>"
                self.root.index = counter
                last_on_level.update({indent: self.root})
                self.nodes.append(self.root)
            else:
                # stvaram novi cvor - na osnovu indenta/dubine pridruzujem roditelja
                new_node: Node = Node(line.strip(), counter, last_on_level.get(indent - 1).index)
                last_on_level.get(indent - 1).children.append(new_node.index)
                self.nodes.append(new_node)
                last_on_level.update({indent: new_node})
                # ako je list tj u formatu npr "IDN 3 c" (tip, linija, vrijednost) postavi vrijednost
                if len(new_node.name.split(" ")) > 1:
                    new_node.value = new_node.name.split(" ")[2]

            levels[indent].append(line.strip())

        for node in self.nodes:
            if len(node.children) > 0:
                for child in node.children:
                    node.production[1].append(self.find_node(child).name.split(" ")[0].strip())