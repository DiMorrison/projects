"""
Modeli za ne-deterministički konačni automat (NKA).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Set, Dict, Tuple, Any, Optional
from collections import namedtuple


ParStanja = namedtuple('ParStanja', ['lijevo_stanje', 'desno_stanje'])
PrijelazIz = namedtuple('Prijelaz', ['stanje', 'znak'])


def get_next_letter_name(name: Optional[str]) -> str:
    """
    Vraća sljedeće slovo u abecedi.
    Ako je `name` None, vraća 'a'.
    Ako je `name` zadnje slovo u abecedi, povećava iduće slovo.
    """
    if name is None:
        return 'A'
    for index, char in enumerate(reversed(name)):
        if char != 'Z':
            return name[:-index - 1] + chr(ord(char) + 1) + 'A' * index
    return 'A' * (len(name) + 1)


@dataclass
class Nka:
    """
    Nedeterministički konačni automat.
    """
    stanja: Set[str] = field(default_factory=set)
    pocetno_stanje: Optional[str] = None
    prihvatljiva_stanja: Set[str] = field(default_factory=set)
    abeceda: Set[str] = field(default_factory=set)
    prijelazi: Dict[Tuple[str, str], Set[str]] = field(default_factory=dict)

    def dodaj_stanje(self, stanje: Any) -> str:
        """
        Dodaje novo stanje u automat.
        """
        new_state = str(stanje)
        self.stanja.add(new_state)
        return new_state

    def dodaj_prijelaz(self, par_stanja: ParStanja, znak: str):
        """
        Dodaje prijelaz iz jednog stanja u drugo za zadani znak.
        """
        key = PrijelazIz(par_stanja.lijevo_stanje, znak)
        if key not in self.prijelazi:
            self.prijelazi[key] = set()
        self.prijelazi[key].add(par_stanja.desno_stanje)
        if znak != '':
            self.abeceda.add(znak)

    def dodaj_epsilon_prijelaz(self, lijevo_stanje: str, desno_stanje: str):
        """
        Dodaje epsilon-prijelaz iz jednog stanja u drugo.
        """
        self.dodaj_prijelaz(ParStanja(lijevo_stanje, desno_stanje), '')

    def uljepsaj_imena_prijelaza(self):
        """
        Pretvori imena prijelaza u slova abecede, te ako je potrebno dodaj više slova u ime
        """
        transformacija_prijelaza = {"$": "$"}
        iduce_slovo = None
        for stanje in self.stanja:
            if stanje.startswith('S_') or stanje.startswith('P_') or stanje.startswith('r_'):
                transformacija_prijelaza[stanje] = stanje
                continue
            iduce_slovo = get_next_letter_name(iduce_slovo)
            transformacija_prijelaza[stanje] = iduce_slovo
        self.stanja = set(transformacija_prijelaza.values())
        self.pocetno_stanje = transformacija_prijelaza[self.pocetno_stanje]
        self.prihvatljiva_stanja = set(
            transformacija_prijelaza[stanje]
            for stanje in self.prihvatljiva_stanja
        )
        novi_prijelazi = dict()
        for prijelaz_iz, stanja in self.prijelazi.items():
            novi_prijelazi[PrijelazIz(
                transformacija_prijelaza[prijelaz_iz.stanje],
                prijelaz_iz.znak
            )] = {transformacija_prijelaza[stanje] for stanje in stanja}
        self.prijelazi = novi_prijelazi

    def spoji_nka(self, nka: Nka, from_state: str, to_state: str):
        """
        Spaja dva automata.
        """
        self.stanja |= nka.stanja
        self.prihvatljiva_stanja |= {to_state}
        self.abeceda |= nka.abeceda
        for key, value in nka.prijelazi.items():
            if key not in self.prijelazi:
                self.prijelazi[key] = set()
            self.prijelazi[key] |= value
        self.dodaj_epsilon_prijelaz(from_state, nka.pocetno_stanje)
        for prihvatljivo_stanje in nka.prihvatljiva_stanja:
            self.dodaj_epsilon_prijelaz(prihvatljivo_stanje, to_state)

    def inicijaliziraj_nka(self, state: Optional[str] = None):
        """
        Vraća novi NkaRunner, pokretač NKA za ovaj automat.
        :return:
        """
        runner = NkaRunner({self.pocetno_stanje}, self)
        if state is not None:
            runner.current_states = {state}
        runner.prijelaz_u_epsilon_stanja()
        return runner

    def serialize(self) -> Dict[str, Any]:
        return {
            'stanja': list(self.stanja),
            'pocetno_stanje': self.pocetno_stanje,
            'prihvatljiva_stanja': list(self.prihvatljiva_stanja),
            'abeceda': list(self.abeceda),
            'prijelazi': [
                {
                    'stanje': stanje,
                    'znak': znak,
                    'stanja': list(stanja),
                }
                for (stanje, znak), stanja in self.prijelazi.items()
            ]
        }

    @staticmethod
    def deserialize(data: Dict[str, Any]) -> Nka:
        nka = Nka()
        nka.stanja = set(data['stanja'])
        nka.pocetno_stanje = data['pocetno_stanje']
        nka.prihvatljiva_stanja = set(data['prihvatljiva_stanja'])
        nka.abeceda = set(data['abeceda'])
        nka.prijelazi = {
            PrijelazIz(prijelaz['stanje'], prijelaz['znak']): set(prijelaz['stanja'])
            for prijelaz in data['prijelazi']
        }
        return nka


@dataclass
class NkaRunner:
    """
    Pokretac koji pokrece automat nad ulazom, prateci trenutna stanja.
    """
    current_states: Set[str]
    nka: Nka

    def prihvatljiv(self) -> bool:
        """
        Provjerava je li automat trenutno u prihvatljivom stanju.
        """
        return len(self.current_states & self.nka.prihvatljiva_stanja) > 0

    def prijelaz_u_epsilon_stanja(self):
        """
        Pokrece epsilon-prijelaze iz trenutnih stanja.
        """
        new_states = self.current_states
        while True:
            next_new_states = set(self.current_states)
            for stanje in new_states:
                next_new_states |= self.nka.prijelazi.get((stanje, ''), set())
            if len(next_new_states) == len(new_states):
                break
            new_states = next_new_states
        self.current_states = new_states

    def prijelaz(self, znak: str):
        """
        Pokrece prijelaze za zadani znak iz trenutnih stanja, te pokrece
        epsilon-prijelaze iz novih stanja.
        """
        new_states = set()
        for stanje in self.current_states:
            new_states |= self.nka.prijelazi.get((stanje, znak), set())
        self.current_states = new_states
        self.prijelaz_u_epsilon_stanja()
