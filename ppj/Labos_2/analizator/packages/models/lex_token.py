from dataclasses import dataclass


@dataclass
class LexToken:
    name: str
    value: str
    line: int
