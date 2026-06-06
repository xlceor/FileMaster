
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from core.scanner import scan_folder

import pandas as pd

def _style_header(cell, bg="5E35B1", fg="FFFFFF"):
    cell.font      = Font(name="Arial", bold=True, color=fg, size=11)
    cell.fill      = PatternFill("solid", start_color=bg.lstrip("#"))
    cell.alignment = Alignment(horizontal="center", vertical="center")
    thin = Side(style="thin", color="CCCCCC")
    cell.border    = Border(left=thin, right=thin, top=thin, bottom=thin)


def _style_cell(cell, color=None):
    thin = Side(style="thin", color="E0E0E0")
    cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    cell.font = Font(name="Arial", size=10)
    if color:
        cell.font = Font(name="Arial", size=10, color=color.lstrip("#"))


def _col_width(ws, col, width):
    ws.column_dimensions[get_column_letter(col)].width = width


def export_names_report(folder: str, recursive: bool, ignore_ext: bool, preprocess: bool, timestamp: str, output_path: str = None) -> str:
    """Genera Reporte_Nombres_<timestamp>.xlsx con los archivos de la carpeta."""
    files = scan_folder(folder, recursive, ignore_ext, preprocess)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Archivos"
    ws.row_dimensions[1].height = 22

    _style_header(ws["A1"], bg="5E35B1")
    ws["A1"] = "Archivo"
    _col_width(ws, 1, 40)

    for i, name in enumerate(files, start=2):
        ws.cell(row=i, column=1, value=name)
        _style_cell(ws.cell(row=i, column=1))
        if i % 2 == 0:
            ws.cell(row=i, column=1).fill = PatternFill("solid", start_color="F0F0F8")

    out = output_path if output_path else f"Reporte_Nombres_{timestamp}.xlsx"
    wb.save(out)
    return out


def comparison_report(
    source_path: str, master_path: str,
    recursive: bool, ignore_ext: bool, ignore_case: bool, preprocess: bool,
    timestamp: str, is_excel_source: bool = False,
    output_path: str = None
) -> str:
    """Genera un reporte profesional usando pandas con resultados y resumen."""
    from core.excel_loader import load_excel
    from core.comparator import compare_dicts, compare_files
    
    # Load master data as a dictionary for rich data preservation
    master_dict = load_excel(master_path, ignore_ext, ignore_case, preprocess)
    
    if is_excel_source:
        # Load source data as a dictionary
        source_dict = load_excel(source_path, ignore_ext, ignore_case, preprocess)
        found_dict, missing_dict, extra_dict = compare_dicts(master_dict, source_dict)
    else:
        # Scan folder (returns list of names)
        found_list = scan_folder(source_path, recursive, ignore_ext, preprocess)
        # We need to convert list to dict for report_excel
        # For folder scanning, we only have names, so we create empty dict values
        if ignore_case:
            found_list = [f.lower() for f in found_list]
        
        # Use existing compare_files to get sets of IDs
        expected_ids = set(master_dict.keys())
        results = compare_files(expected_ids, found_list, ignore_case)
        
        found_dict = {id: master_dict[id] for id in results["found"]}
        missing_dict = {id: master_dict[id] for id in results["missing"]}
        # For extra files in folder, we don't have extra columns, just the filename
        extra_dict = {f: {"Info": "Archivo extra en carpeta"} for f in results["extra"]}

    out = output_path if output_path else f"Reporte_Comparacion_{timestamp}.xlsx"
    report_excel(out, found_dict, missing_dict, extra_dict)
    
    # Add Summary Sheet to the existing file
    _add_summary_to_report(out, len(master_dict), len(found_dict), len(missing_dict), len(extra_dict))
    
    return out


def _add_summary_to_report(file_path: str, total: int, found: int, missing: int, extra: int) -> None:
    """Añade una hoja de resumen al final del archivo Excel generado por pandas."""
    import openpyxl
    wb = openpyxl.load_workbook(file_path)
    ws = wb.create_sheet("Resumen") # Append to the end
    
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 18

    _style_header(ws["A1"], bg="5E35B1")
    _style_header(ws["B1"], bg="5E35B1")
    ws["A1"] = "Métrica"
    ws["B1"] = "Valor"

    metrics = [
        ("Esperados",    total,         "1A237E"),
        ("Encontrados",  found,         "1B5E20"),
        ("Faltantes",    missing,       "C62828"),
        ("Sobrantes",    extra,         "E65100"),
        ("% Completitud",
         f"{found/total*100:.1f}%" if total > 0 else "N/A",
         "5E35B1"),
    ]

    for i, (label, val, color) in enumerate(metrics, start=2):
        ws.row_dimensions[i].height = 20
        lc = ws.cell(row=i, column=1, value=label)
        vc = ws.cell(row=i, column=2, value=val)
        _style_cell(lc)
        _style_cell(vc, color=color)
        lc.font = Font(name="Arial", bold=True, size=10)
    
    wb.save(file_path)


def report_excel(
    output_path: str, found: dict, missing: dict, extra: dict
) -> None:
    """Convierte los diccionarios a DataFrames, aplica estilos visuales profesionales
    (encabezados, bordes y colores temáticos) y los guarda en un Excel.
    """
    def prepare_df(data, index_name="placas"):
        if not data:
            return pd.DataFrame(columns=[index_name])
        df = pd.DataFrame.from_dict(data, orient="index")
        # If index_name is already a column, remove it from data part to avoid collision on reset_index
        if index_name in df.columns:
            df = df.drop(columns=[index_name])
        return df.rename_axis(index_name).reset_index()

    df_enc = prepare_df(found)
    df_fal = prepare_df(missing)
    df_sob = prepare_df(extra)

    try:
        header_style = {
            "selector": "th",
            "props": [
                ("background-color", "#1F4E78"),
                ("color", "white"),
                ("font-weight", "bold"),
                ("text-align", "center"),
                ("border", "1px solid #D9D9D9"),
                ("padding", "6px"),
            ],
        }

        cell_style = {
            "selector": "td",
            "props": [
                ("border", "1px solid #F2F2F2"),
                ("padding", "5px"),
                ("text-align", "left"),
            ],
        }

        style_enc = (
            df_enc.style.set_table_styles([header_style, cell_style])
            .set_properties(**{"background-color": "#E2EFDA"})
            .hide(axis="index")
        )

        style_fal = (
            df_fal.style.set_table_styles([header_style, cell_style])
            .set_properties(**{"background-color": "#FCE4D6"})
            .hide(axis="index")
        )

        style_sob = (
            df_sob.style.set_table_styles([header_style, cell_style])
            .set_properties(**{"background-color": "#F2F2F2"})
            .hide(axis="index")
        )

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            style_enc.to_excel(writer, sheet_name="Encontrados", index=False)
            style_fal.to_excel(writer, sheet_name="Faltantes", index=False)
            style_sob.to_excel(writer, sheet_name="Sobrantes", index=False)
    except Exception as e:
        print(f"Warning: Styling failed ({e}), saving without styles.")
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df_enc.to_excel(writer, sheet_name="Encontrados", index=False)
            df_fal.to_excel(writer, sheet_name="Faltantes", index=False)
            df_sob.to_excel(writer, sheet_name="Sobrantes", index=False)
