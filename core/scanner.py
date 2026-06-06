
from pathlib import Path
from core.comparator import preprocess_placas

def scan_folder(folder: str, recursive: bool = False, ignore_ext: bool = False, preprocess: bool = False) -> list[str]:
    p = Path(folder)
    pattern = "**/*" if recursive else "*"
    files = []
    for f in p.glob(pattern):
        if f.is_file():
            name = f.stem if ignore_ext else f.name
            name = name.strip()
            if preprocess:
                name = preprocess_placas(name)
            if name:
                files.append(name)
    return sorted(list(set(files)))
