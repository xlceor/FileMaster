
import re

def preprocess_placas(name: str) -> str:
    """Extrae los caracteres antes del primer '-' o '_'."""
    return re.split(r'[-_]', name)[0].strip()


def compare_files(expected: set, found_list: list, ignore_case: bool = False) -> dict:
    """Compara sets y devuelve encontrados, faltantes y sobrantes."""
    found = set(f.lower() if ignore_case else f for f in found_list)
    exp   = set(e.lower() if ignore_case else e for e in expected)
    return {
        "found":   exp & found,
        "missing": exp - found,
        "extra":   found - exp,
    }

def compare_dicts(master: dict, real: dict) -> dict:
    """Compara diccionarios y devuelve encontrados, faltantes y sobrantes."""
    ids_master = set(master.keys())
    ids_real = set(real.keys())

    ids_found = ids_master.intersection(ids_real)
    ids_missing = ids_master - ids_found
    ids_extra = ids_real - ids_master

    dict_found = {id: master[id] for id in ids_found}
    dict_missing = {id: master[id] for id in ids_missing}
    dict_extra = {id: real[id] for id in ids_extra}

    return dict_found, dict_missing, dict_extra