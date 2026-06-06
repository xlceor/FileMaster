
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from core.scanner import scan_folder
from core.excel_loader import load_names_from_excel, load_master_excel
from core.comparator import compare_files

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


def export_names_report(folder: str, recursive: bool, ignore_ext: bool, preprocess: bool, timestamp: str) -> str:
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

    out = f"Reporte_Nombres_{timestamp}.xlsx"
    wb.save(out)
    return out


def comparison_report(
    source_path: str, master_path: str,
    recursive: bool, ignore_ext: bool, ignore_case: bool, preprocess: bool,
    timestamp: str, is_excel_source: bool = False
) -> str:
    """Genera Reporte_Comparacion_<timestamp>.xlsx con resultados y resumen."""
    expected = load_master_excel(master_path, ignore_ext, ignore_case, preprocess)
    
    if is_excel_source:
        found_list = load_names_from_excel(source_path, ignore_ext, preprocess)
    else:
        found_list = scan_folder(source_path, recursive, ignore_ext, preprocess)
    
    if ignore_case:
        found_list = [f.lower() for f in found_list]

    result = compare_files(expected, found_list, ignore_case)

    found_sorted   = sorted(result["found"])
    missing_sorted = sorted(result["missing"])
    extra_sorted   = sorted(result["extra"])
    max_rows       = max(len(found_sorted), len(missing_sorted), len(extra_sorted), 1)

    wb = openpyxl.Workbook()

    ws1 = wb.active
    ws1.title = "Resultados"
    ws1.row_dimensions[1].height = 24

    headers = ["✔ Encontrados", "✖ Faltantes", "⚠ Sobrantes"]
    colors  = ["2E7D32", "C62828", "E65100"]
    widths  = [35, 35, 35]

    for col, (h, c, w) in enumerate(zip(headers, colors, widths), start=1):
        cell = ws1.cell(row=1, column=col, value=h)
        _style_header(cell, bg=c)
        _col_width(ws1, col, w)

    lists = [found_sorted, missing_sorted, extra_sorted]
    txt_c = ["1B5E20", "B71C1C", "BF360C"]

    for row in range(max_rows):
        ws1.row_dimensions[row + 2].height = 18
        for col, (lst, tc) in enumerate(zip(lists, txt_c), start=1):
            val  = lst[row] if row < len(lst) else ""
            cell = ws1.cell(row=row + 2, column=col, value=val)
            _style_cell(cell, color=tc if val else None)
            bg = "F9FBE7" if col == 1 else ("FFEBEE" if col == 2 else "FFF3E0")
            if row % 2 == 0:
                cell.fill = PatternFill("solid", start_color=bg)

    ws2 = wb.create_sheet("Resumen")
    ws2.column_dimensions["A"].width = 28
    ws2.column_dimensions["B"].width = 18

    _style_header(ws2["A1"], bg="5E35B1")
    _style_header(ws2["B1"], bg="5E35B1")
    ws2["A1"] = "Métrica"
    ws2["B1"] = "Valor"

    metrics = [
        ("Esperados",    len(expected),         "1A237E"),
        ("Encontrados",  len(found_sorted),      "1B5E20"),
        ("Faltantes",    len(missing_sorted),    "B71C1C"),
        ("Sobrantes",    len(extra_sorted),      "BF360C"),
        ("% Completitud",
         f"{len(found_sorted)/len(expected)*100:.1f}%" if expected else "N/A",
         "5E35B1"),
    ]

    for i, (label, val, color) in enumerate(metrics, start=2):
        ws2.row_dimensions[i].height = 20
        lc = ws2.cell(row=i, column=1, value=label)
        vc = ws2.cell(row=i, column=2, value=val)
        _style_cell(lc)
        _style_cell(vc, color=color)
        lc.font = Font(name="Arial", bold=True, size=10)

    out = f"Reporte_Comparacion_{timestamp}.xlsx"
    wb.save(out)
    return out
