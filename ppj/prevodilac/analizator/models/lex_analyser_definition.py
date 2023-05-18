"""
Definicija leksičkog analizatora, predstavlja ulaz u generator leksičkog analizatora.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Set, List, Optional, Dict, Any
from collections import namedtuple
from enum import Enum
from .nka import Nka
from json import loads, dumps

NamedRegex = namedtuple('NamedRegex', ['name', 'regex'])


class TipAkcijeAnalizatora(Enum):
    """
    Akcije koje se mogu izvršiti na leksičkom analizatoru.
    """
    IME_JEDINKE = 'IME_JEDINKE'
    NOVI_REDAK = 'NOVI_REDAK'
    VRATI_SE = 'VRATI_SE'
    UDJI_U_STANJE = 'UDJI_U_STANJE'


@dataclass
class AkcijaAnalizatora:
    """
    Akcija koja se izvršava na leksičkom analizatoru.
    """
    tip: TipAkcijeAnalizatora
    argument: Optional[str] = field(default_factory=lambda: None)

    def serialize(self) -> Dict[str, Any]:
        """
        Serijalizira akciju u JSON.
        """
        return {
            'tip': self.tip.value,
            'argument': self.argument
        }

    @staticmethod
    def deserialize(data: Dict[str, Any]) -> AkcijaAnalizatora:
        """
        Deserijalizira akciju iz JSON-a.
        """
        return AkcijaAnalizatora(
            tip=TipAkcijeAnalizatora(data['tip']),
            argument=data['argument']
        )


@dataclass
class PraviloDefinicijeAnalizatora:
    """
    Akcija koja se izvršava kada se pronade token.
    """
    stanje: str
    regex: str
    akcije: List[AkcijaAnalizatora]
    nka: Optional[Nka] = None


@dataclass
class DefinicijaLexAnalizatora:
    """
    Definicija leksičkog analizatora.
    Sadrži pravila za leksički analizator, te akcije koje se izvršavaju kada
    se pronade token.
    """
    regexi: Set[NamedRegex] = field(default_factory=set)
    stanja: Set[str] = field(default_factory=set)
    jedinke: Set[str] = field(default_factory=set)
    pravila: List[PraviloDefinicijeAnalizatora] = field(default_factory=list)
    pocetno_stanje: Optional[str] = None


@dataclass
class PraviloAnalizatora:
    """
    Pravilo gotovog leksickog analizatora, koji ima NKA
    Ne mora znati regex svog pravila
    """
    oznaka: str
    akcije: List[AkcijaAnalizatora]

    def find_action(self, action_type: TipAkcijeAnalizatora) -> Optional[AkcijaAnalizatora]:
        """
        Pronalazi akciju određenog tipa.
        """
        for action in self.akcije:
            if action.tip == action_type:
                return action
        return None

    def serialize(self) -> Dict[str, Any]:
        return {
            'oznaka': self.oznaka,
            'akcije': [a.serialize() for a in self.akcije]
        }

    @staticmethod
    def deserialize(data: Dict[str, Any]) -> PraviloAnalizatora:
        return PraviloAnalizatora(
            oznaka=data['oznaka'],
            akcije=[AkcijaAnalizatora.deserialize(a) for a in data['akcije']]
        )


@dataclass
class LexAnalizator:
    """
    Gotov leksicki analizator, ima NKA i pravila za njega.
    """
    nka: Nka
    pravila: List[PraviloAnalizatora]

    def serialize(self) -> str:
        return dumps({
            'nka': self.nka.serialize(),
            'pravila': [p.serialize() for p in self.pravila]
        })

    @staticmethod
    def deserialize(json: str) -> LexAnalizator:
        data: Dict[str, Any] = loads(json)
        return LexAnalizator(
            nka=Nka.deserialize(data['nka']),
            pravila=[PraviloAnalizatora.deserialize(p) for p in data['pravila']]
        )