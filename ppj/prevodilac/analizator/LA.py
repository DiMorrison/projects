"""
Modul za analizu ulaznog koda pomocu leksickog analizatora.
"""
import sys
from typing import List, Optional
from models import LexAnalizator, PraviloAnalizatora, TipAkcijeAnalizatora


def ucitaj_analizator(datoteka_tablice: str = 'prevodilac/analizator/tablica.txt') -> LexAnalizator:
    """
    Ucitava leksicki analizator iz datoteke.
    :param datoteka_tablice: Datoteka iz koje se ucitava leksicki analizator.
    :return: Ucitani leksicki analizator.
    """
    with open(datoteka_tablice, 'r') as file:
        return LexAnalizator.deserialize(file.read())


def pokreni_analizator(ulaz: str, analizator: LexAnalizator) -> List[str]:
    """
    Pokrece leksicki analizator nad ulaznim kodom.
    :param ulaz: Ulazni kod.
    :param analizator: Leksicki analizator.
    :return: Lista pravila koja su pokrenuta.
    """
    nka_runner = analizator.nka.inicijaliziraj_nka()
    p_zavrsetak = 0
    p_posljednji = 0
    p_pocetak = 0
    redak = 1
    pronadeno_pravilo: Optional[PraviloAnalizatora] = None
    state = None

    ispis: List[str] = []

    while p_zavrsetak < len(ulaz):
        znak = ulaz[p_zavrsetak]
        nka_runner.prijelaz(znak)
        testiranje_regexa = bool(next((filter(lambda x: x.startswith('r_'), nka_runner.current_states)), None))
        if not testiranje_regexa:
            try:
                ime_jedinke = pronadeno_pravilo.find_action(TipAkcijeAnalizatora.IME_JEDINKE).argument
                state = pronadeno_pravilo.find_action(TipAkcijeAnalizatora.UDJI_U_STANJE).argument
                vrati_se = pronadeno_pravilo.find_action(TipAkcijeAnalizatora.VRATI_SE)
                dodaj_novi_redak = bool(pronadeno_pravilo.find_action(TipAkcijeAnalizatora.NOVI_REDAK))

                redak += dodaj_novi_redak
                nka_runner = analizator.nka.inicijaliziraj_nka(state)


                if ime_jedinke != '-':
                    end = p_posljednji + 1
                    if vrati_se:
                        end = p_pocetak + int(vrati_se.argument)
                    ispis.append(f"{ime_jedinke} {redak} {ulaz[p_pocetak:end]}")

                if vrati_se:
                    p_pocetak = p_pocetak + int(vrati_se.argument)
                    p_zavrsetak = p_pocetak
                    p_posljednji = p_pocetak
                else:
                    p_pocetak = p_zavrsetak
                    p_posljednji = p_zavrsetak
                pronadeno_pravilo = None
            except:
                #print(f"[ERR] Line {redak} - '{ulaz[p_pocetak: p_zavrsetak + 1]}'", file=sys.stderr)
                p_pocetak += 1
                p_zavrsetak = p_pocetak
                p_posljednji = p_pocetak
                pronadeno_pravilo = None
                nka_runner = analizator.nka.inicijaliziraj_nka(state)
        else:
            trenutni_prihvacen = nka_runner.current_states & nka_runner.nka.prihvatljiva_stanja
            novo_pronadeno_pravilo = next(filter(lambda i: i.oznaka in trenutni_prihvacen, analizator.pravila), None)
            if novo_pronadeno_pravilo:
                pronadeno_pravilo = novo_pronadeno_pravilo
                p_posljednji = p_zavrsetak
            p_zavrsetak += 1
    return ispis  # + ['']


if __name__ == '__main__':
    analyzer = ucitaj_analizator('analizator/tablica.txt')
    result = pokreni_analizator(sys.stdin.read(), analyzer)
    for i in result:
        print(i)
