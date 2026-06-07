
import os
from pathlib import Path
import pandas as pd
from utils.logger import logger

def load_excel(path: str, ignore_ext: bool = False, ignore_case: bool = False, preprocess: bool = False):
    if not path or not os.path.exists(path):
        logger.warning(f"Intento de cargar Excel con ruta vacía o inexistente: {path}")
        return {}

    ext = Path(path).suffix.lower()
    try:
        if ext in [".xlsx", ".xls"]:
            names = pd.read_excel(path)
        elif ext == ".csv":
            try:
                # Automatically detect separator (comma, semicolon, tab)
                names = pd.read_csv(path, sep=None, engine='python', encoding='utf-8')
            except Exception:
                names = pd.read_csv(path, sep=',', encoding='utf-8')
        elif ext == ".json":
            names = pd.read_json(path, encoding='utf-8')
            if isinstance(names, pd.Series):
                names = names.to_frame()
        else:
            logger.error(f"Formato de archivo no soportado: {ext} en {path}")
            return {}
    except Exception as e:
        logger.error(f"Error cargando archivo {path}: {str(e)}", exc_info=True)
        return {}

    if names.empty:
        logger.info(f"El archivo Excel en {path} está vacío.")
        return {}

    # Rename unnamed columns (pandas reads empty headers as Unnamed: X)
    new_columns = []
    unnamed_count = 1
    for col in names.columns:
        if str(col).startswith("Unnamed:"):
            new_name = f"Info_{unnamed_count}" if unnamed_count > 1 else "Info"
            new_columns.append(new_name)
            unnamed_count += 1
        else:
            new_columns.append(col)
    names.columns = new_columns
    logger.debug(f"Columnas cargadas y saneadas en Excel: {list(names.columns)}")
        
    row_name = "placas"
    if row_name in names.columns:
        column_id = row_name
    else:
        column_id = names.columns[0]

    # Initialize clean_id from the source column and strip whitespace
    names['clean_id'] = names[column_id].astype(str).str.strip()

    # Filter out empty or invalid entries that often appear in processed reports
    names = names[names['clean_id'] != ""]
    names = names[names['clean_id'].notna()]
    names = names[names['clean_id'].str.lower() != "nan"]

    if ignore_ext:
        names['clean_id'] = names['clean_id'].str.replace(r'\.[^.]+$', '', regex=True)
        
    if preprocess:
        # Use regex to split by either - or _ and take the first part
        names['clean_id'] = names['clean_id'].str.split(r'[-_]', regex=True).str[0].str.strip()
        
    if ignore_case:
        names['clean_id'] = names['clean_id'].str.lower()

    # Drop duplicates to avoid ValueError: DataFrame index must be unique for orient='index'
    names = names.drop_duplicates(subset=['clean_id'], keep='first')

    dictionary = names.set_index('clean_id').to_dict(orient='index')
    logger.info(f"Cargados con éxito {len(dictionary)} registros de Excel desde {path}")
    return dictionary

