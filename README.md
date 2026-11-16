# FileMaster

### Audit thousands of files against your master records in seconds, and get an auditable report.

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![UI](https://img.shields.io/badge/UI-Tkinter%20%2B%20ttk-5E35B1)
![Data](https://img.shields.io/badge/Data-pandas%20%2B%20openpyxl-150458)

<p align="center">
<img width="850" alt="Captura de pantalla 2026-06-26 113314" src="https://github.com/user-attachments/assets/ad0fdc00-9a5a-46c3-9131-4fd7eaf66761" />
</p>




---

## The problem

Organizations that keep physical or digital files (invoices, contracts, records) need to prove those files match their official spreadsheet. Doing this by hand means opening a folder and a spreadsheet side by side and checking row by row. It takes days, it is easy to get wrong, and it leaves no evidence behind.

## The solution

FileMaster is a desktop application that reconciles a folder (or another dataset) against a **master record** and produces a formatted Excel report with three answers:

| Result | Meaning |
|---|---|
| **Found** | The record exists in both places |
| **Missing** | The master lists it, but no file exists |
| **Extra** | A file exists, but the master doesn't list it |

**Real run (from the screenshot above):** 1,815 expected records → **1,606 found · 209 missing · 185 extra → 88.5% completion**, reconciled and reported in a single click.

---

## Features

### Three operating modes

1. **Export folder names**: scan a folder and export its file names to Excel (recursive, extension-agnostic options).
2. **Compare folder vs Master Excel**: check files on disk against the official record.
3. **Compare Excel vs Master Excel**: reconcile two datasets against each other.

**Supported input formats:** `.xlsx`, `.xls`, `.csv`, `.json`. **Output:** formatted `.xlsx`.

### Smart matching

Real-world file names are messy, so FileMaster normalizes both sides before comparing: case-insensitive, extension-agnostic, prefix extraction and cleanup of copy suffixes.

| Physical file | Master record | Match |
|---|---|---|
| `ABC123.pdf` | `ABC123` | ✅ |
| `DOC-001.JPG` | `doc-001` | ✅ |
| `AB123_photo.jpg` | `AB123` | ✅ |
| `file (1).txt` | `file` | ✅ |

### Professional Excel reports

Generated with OpenPyXL, with optional injection into corporate templates.

- **Resumen**: executive summary (expected, found, missing, extra, completion %)
- **Encontrados / Faltantes / Sobrantes**: one sheet per category
- Themed headers, zebra rows, color-coded categories and auto-sized columns

### Interface

- Light / Dark themes, switchable live
- Spanish / English, switchable live, no restart
- Drag & Drop for folders and files
- Dashboard with a completion donut chart and a distribution bar chart

---

## Engineering highlights

This project is as much about design decisions as features.

- **Set algebra for reconciliation.** Once both sides are normalized into sets, the whole comparison is three operations:
  ```python
  found   = expected & actual   # intersection
  missing = expected - actual   # difference
  extra   = actual - expected   # reverse difference
  ```
  Membership checks are O(1) on average; building and normalizing the sets is O(n), which is where the real time goes.
- **Separation of concerns.** `core/` has zero UI dependencies, so the engine is testable and reusable on its own (see the programmatic example below).
- **Offline-capable licensing.** The server issues an RS256-signed JWT lease bound to a hardware fingerprint (SHA-256 over CPU, motherboard and disk identifiers). The client verifies the signature locally with an embedded public key, so the app works without connectivity. Supports revocation and machine migration; the validation API is rate-limited.
- **Hot-swappable i18n and themes.** A global `t(key, **kwargs)` translator and a theme layer update every widget live, including the charts.
- **Automated builds.** GitHub Actions packages a standalone Windows binary with PyInstaller.

---

## Quick start

### Pre-built binary

Download the Windows executable (no Python required), launch it and activate your license.

### From source

Requires **Python 3.13+**.

```bash
git clone <repository-url>
cd FileMaster

python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows

pip install -r requirements.txt
python filemaster_launcher.py
```

### Using the engine programmatically

```python
from core.scanner import scan_folder
from core.excel_loader import load_excel
from core.comparator import compare

actual   = scan_folder("/path/to/folder", recursive=True)
expected = load_excel("/path/to/master.xlsx")

result = compare(expected, actual)
print(f"Found:   {len(result.found)}")
print(f"Missing: {len(result.missing)}")
print(f"Extra:   {len(result.extra)}")
```

---

## Architecture

```text
FileMaster/
├── core/                  # Business logic (no UI imports)
│   ├── scanner.py         # Recursive file scanning
│   ├── excel_loader.py    # Dataset loading and normalization
│   ├── comparator.py      # Reconciliation engine
│   ├── reports.py         # Excel report generation
│   └── exceptions.py
├── ui/                    # Tkinter interface
│   ├── app.py
│   ├── theme.py
│   ├── license_prompt.py
│   └── components/        # sidebar, config, results, dashboard widgets
├── utils/                 # licensing, translator, config, drag & drop, logging, usage tracking
├── assets/i18n/           # en.json · es.json
├── tests/                 # pytest suite
├── docs/license-server.md # Licensing server architecture and API
├── .github/workflows/     # CI build (PyInstaller)
├── filemaster_launcher.py # Entry point
└── requirements.txt
```

**Desktop stack:** Python 3.13 · Tkinter/ttk · pandas · OpenPyXL · TkinterDnD2 · cryptography · PyJWT · psutil

**Licensing server:** Next.js (App Router) · Supabase (PostgreSQL) · RS256 JWT · Vercel. Details in [`docs/license-server.md`](docs/license-server.md).

---

## Business case (illustrative)

The value comes from replacing recurring manual work. The estimate below is a model, not a measurement. Plug in your own numbers.

| Variable | Assumption |
|---|---|
| Fully loaded cost | $8,000 USD/month ≈ **$46 USD/h** (173 h/month) |
| Manual audit cycle | 24–56+ hours |
| With FileMaster | < 15 minutes |

```
Savings per audit cycle = hours saved × hourly cost
Example: 24 h × $46 ≈ $1,100 per audit
```

Actual savings scale with file volume, audit frequency and local labor cost. Error reduction and the auditable evidence trail are additional benefits that this model does not price.

---

## Testing

```bash
pytest tests/ -v
```

Unit tests cover the scanner, the Excel loader and the comparator. Test coverage for `reports.py` and `licensing.py` is on the roadmap.

---

## Roadmap

- [ ] Tests for report generation and licensing
- [ ] PDF report export
- [ ] Multithreaded scanning for very large folders
- [ ] Time-series dashboard (compare audits over time)
- [ ] Cloud API integration
- [ ] Plugin system

---

## Build

```bash
pyinstaller --onefile --windowed --name FileMaster filemaster_launcher.py
```

---

## License

Proprietary software. © FileMaster. All rights reserved. Use is subject to the Lifetime Single-Machine license terms.

---

## Author

**Carlos Osorio**: Systems Alchemist
