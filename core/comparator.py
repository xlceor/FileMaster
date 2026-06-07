
import re
from utils.logger import logger

def preprocess_placas(name: str) -> str:
    """Extrae los caracteres antes del primer '-' o '_'."""
    val = re.split(r'[-_]', name)[0].strip()
    return val


def compare_files(expected: set, found_list: list, ignore_case: bool = False) -> dict:
    """Compara sets y devuelve encontrados, faltantes y sobrantes."""
    logger.debug(f"Ejecutando compare_files: {len(expected)} esperados, {len(found_list)} encontrados (ignorar_caso={ignore_case})")
    found = set(f.lower() if ignore_case else f for f in found_list)
    exp   = set(e.lower() if ignore_case else e for e in expected)
    
    res = {
        "found":   exp & found,
        "missing": exp - found,
        "extra":   found - exp,
    }
    logger.info(f"Resultado compare_files: {len(res['found'])} encontrados, {len(res['missing'])} faltantes, {len(res['extra'])} sobrantes")
    return res

def compare_dicts(master: dict, real: dict) -> dict:
    """Compara diccionarios y devuelve encontrados, faltantes y sobrantes."""
    logger.debug(f"Ejecutando compare_dicts: {len(master)} esperados, {len(real)} encontrados")
    ids_master = set(master.keys())
    ids_real = set(real.keys())

    ids_found = ids_master.intersection(ids_real)
    ids_missing = ids_master - ids_found
    ids_extra = ids_real - ids_master

    dict_found = {id: master[id] for id in ids_found}
    dict_missing = {id: master[id] for id in ids_missing}
    dict_extra = {id: real[id] for id in ids_extra}

    logger.info(f"Resultado compare_dicts: {len(dict_found)} encontrados, {len(dict_missing)} faltantes, {len(dict_extra)} sobrantes")
    return dict_found, dict_missing, dict_extra