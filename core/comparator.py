
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
