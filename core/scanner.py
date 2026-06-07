
from pathlib import Path
from core.comparator import preprocess_placas
from utils.logger import logger

def scan_folder(folder: str, recursive: bool = False, ignore_ext: bool = False, preprocess: bool = False) -> list[str]:
    logger.info(f"Iniciando escaneo de carpeta: {folder} (recursivo={recursive}, ignorar_ext={ignore_ext}, preprocesar={preprocess})")
    p = Path(folder)
    if not p.exists() or not p.is_dir():
        logger.error(f"Carpeta no existe o no es un directorio válido: {folder}")
        return []
        
    pattern = "**/*" if recursive else "*"
    files = []
    try:
        for f in p.glob(pattern):
            if f.is_file():
                name = f.stem if ignore_ext else f.name
                name = name.strip()
                if preprocess:
                    name = preprocess_placas(name)
                if name:
                    files.append(name)
    except Exception as e:
        logger.error(f"Error durante el escaneo de archivos: {str(e)}", exc_info=True)
        return []
        
    unique_files = sorted(list(set(files)))
    logger.info(f"Escaneo finalizado. Encontrados {len(unique_files)} archivos únicos.")
    return unique_files
