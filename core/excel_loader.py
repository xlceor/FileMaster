
import os
from pathlib import Path
import pandas as pd

def load_excel(path: str, ignore_ext: bool = False, ignore_case: bool = False, preprocess: bool = False):
    if not path or not os.path.exists(path):
        return {}

    try:
        names = pd.read_excel(path)
    except Exception:
        return {}

    if names.empty:
        return {}
        
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
    return dictionary
