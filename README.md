# FileMaster

### Professional file auditing — from days to seconds.

**Verify, compare and reconcile thousands of files against your official records, and generate auditable executive reports with a single click.**

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![UI](https://img.shields.io/badge/UI-Tkinter%20%2B%20ttk-5E35B1)
![Data](https://img.shields.io/badge/Data-pandas%20%2B%20openpyxl-150458)
![License](https://img.shields.io/badge/License-Proprietary-2E7D32)
![Tests](https://img.shields.io/badge/Tests-pytest-F9A825)

---

## What is FileMaster?

**FileMaster** is an enterprise desktop application for **file auditing and reconciliation** against structured records (Excel, CSV, JSON). It is built for organizations that need to guarantee that their physical or digital files match their master records — and to prove it with professional, presentation-ready reports.

> **The problem it solves:** manually auditing thousands of files against a spreadsheet takes **days — sometimes over a week** — is error-prone, and leaves no auditable evidence. FileMaster does it in **seconds** and produces a formatted executive report.

---

## 💰 Savings: on average, **~$230 USD/week**

The calculation is grounded in the real cost of the manual work that FileMaster eliminates.

### Calculation basis

| Variable | Value |
|---|---|
| Assumed salary | **$8,000 USD/month** |
| Estimated hourly rate | **~$46 USD/h** *(based on 173 h/month)* |
| Manual process per cycle | **3–7+ days** *(24–56+ h)* |
| With FileMaster per cycle | **< 15 minutes** |
| Time reduction | **> 95 %** |

### Amortized weekly savings

```
Recovered manual work:           ~5 h/week (conservative estimate
                                 already net of preparation and verification)
Hourly rate:                     ~$46 USD/h
─────────────────────────────────────────────────
Weekly savings:                  ~$230 USD/week
Annual savings per user:         ~$11,960 USD/year
```

> **Transparency note:** actual savings **scale with file volume, audit frequency and your organization's hourly cost**. The $230 USD/week figure is a conservative estimate; error reduction and the value of auditable evidence are additional, unquantified benefits.

---

## ✨ Features

### 🔍 File reconciliation — 5 operating modes

- **Folder → Excel export**
- **Folder vs Master Excel**
- **Excel vs Master Excel**
- **CSV vs Master Excel**
- **JSON vs Master Excel**

### 🧩 Smart matching engine

Normalization strategies that eliminate false negatives:

- Recursive subfolder scanning
- Case-insensitive comparisons
- Extension-agnostic matching
- Filename prefix extraction
- Automatic data cleaning and normalization

**Examples:**

| Physical file | Master record | Match |
|---|---|---|
| `ABC123.pdf` | `ABC123` | ✅ |
| `DOC-001.JPG` | `doc-001` | ✅ |
| `AB123_photo.jpg` | `AB123` | ✅ |
| `file (1).txt` | `file` | ✅ |

### ⚡ High-performance engine

Built on **Python set algebra**:

```python
found   = expected & actual   # intersection
missing = expected - actual   # difference
extra   = actual - expected   # reverse difference
```

**O(1)** lookups that let FileMaster process tens or hundreds of thousands of records in seconds.

| Volume | Comparison time |
|---|---|
| 10,000 records | **< 2 s** |
| 100,000 records | **< 10 s** |
| 1,000,000 records | **< 60 s** *(with optimizations)* |

### 📊 Professional Excel reports

Generated with **OpenPyXL**, with optional injection into corporate templates.

**Included sheets:**

- **Resumen (Summary)** — executive dashboard: expected records, found, missing, extra and **completion percentage**.
- **Encontrados (Found)** — matching records.
- **Faltantes (Missing)** — expected records not found.
- **Sobrantes (Extra)** — files present but unregistered.

**Styling:** themed headers · zebra rows · color-coded categories · auto column sizing · consistent borders and alignment.

### 🎨 Modern interface

- **Light / Dark themes** with hot-swapping (affects widgets, tables, charts, scrollbars and dashboard).
- **Drag & Drop** for folders and files (`.xlsx`, `.csv`, `.json`).
- **Analytics dashboard** with a completion donut chart and a distribution bar chart.
- **Tabbed navigation:** Configuration · Results · Dashboard.

### 🌐 Internationalization (i18n)

- Supported languages: **Spanish · English**.
- **Instant language switching**, no restart required.

---

## 🚀 Installation

### Requirements

- **Python 3.13+**
- Windows 10/11, macOS or Linux

### From source

```bash
# 1. Clone the repository
git clone <repository-url>
cd FileMaster

# 2. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python filemaster_launcher.py
```

### Main dependencies

```txt
pandas          # Tabular data manipulation
openpyxl        # Advanced Excel manipulation
tkinterdnd2     # Drag & Drop for Tkinter
cryptography    # License cryptography
pyjwt           # JSON Web Tokens for licensing
psutil          # System fingerprinting
requests        # License validation via API
pytest          # Testing framework
```

### Precompiled binary

End users are provided with a binary packaged via **PyInstaller** (`--onefile --windowed`), with no Python installation required.

---

## ⚡ Quick start

```
1. Open FileMaster and activate your license.
2. Select the operating mode (e.g. "Folder vs Master Excel").
3. Drag the folder to audit and your master record (.xlsx).
4. Click "Compare".
5. Review the dashboard and export the Excel report.
```

**Programmatic usage:**

```python
from core.scanner import scan_folder
from core.excel_loader import load_excel
from core.comparator import compare

# 1. Recursively scan a folder
actual = scan_folder("/path/to/folder", recursive=True)

# 2. Load the master record
expected = load_excel("/path/to/master.xlsx")

# 3. Reconcile
result = compare(expected, actual)
print(f"Found:   {len(result.found)}")
print(f"Missing: {len(result.missing)}")
print(f"Extra:   {len(result.extra)}")
```

---

## 🏗️ Architecture

### Core components

| Module | Responsibility |
|---|---|
| `core/scanner.py` | Recursive file scanning |
| `core/excel_loader.py` | Dataset loading and normalization |
| `core/comparator.py` | High-performance reconciliation engine |
| `core/reports.py` | Excel report generation |
| `core/exceptions.py` | Custom exception definitions |
| `utils/licensing.py` | License validation and JWT verification |
| `utils/translator.py` | Internationalization system |
| `utils/config_manager.py` | Configuration persistence |
| `utils/usage_tracker.py` | Usage monitoring for trial limits |
| `ui/` | Interface, views and dashboard |
| `ui/components/` | Reusable widgets (sidebar, config, results, dashboard) |

### Project structure

```text
FileMaster/
├── core/                    # Business logic
│   ├── scanner.py
│   ├── excel_loader.py
│   ├── comparator.py
│   ├── reports.py
│   └── exceptions.py
├── ui/                      # Tkinter interface
│   ├── app.py
│   ├── license_prompt.py
│   ├── theme.py
│   └── components/
├── utils/                   # Utilities
│   ├── licensing.py
│   ├── translator.py
│   ├── config_manager.py
│   ├── dnd_helper.py
│   ├── logger.py
│   └── usage_tracker.py
├── assets/i18n/             # en.json · es.json
├── tests/                   # pytest (scanner, excel_loader, comparator)
├── docs/                    # Technical documentation
│   └── license-server.md
├── .github/workflows/       # CI/CD (PyInstaller)
├── filemaster_launcher.py   # Entry point
├── main.py                  # Alternative entry point
├── config.py                # UI color palette
└── requirements.txt
```

**Code graph:** 558 nodes · 1,572 connections · 26 Python modules · 1 main entry point.

---

## 🔐 Licensing system

**Lifetime Single-Machine** model.

### Activation flow

1. The user enters their license key.
2. On first activation, a **hardware fingerprint** (SHA-256) is generated.
3. The fingerprint is permanently bound to the license.
4. The server issues a **signed JWT lease**.
5. The client verifies the token **offline** and operates without connectivity.

### Security features

- **RSA-2048 cryptography**
- **RS256-signed JWTs**
- **Multi-source hardware fingerprinting** (CPU, motherboard, disk)
- **Offline verification** with configurable expiration
- **License revocation** support
- **Machine migration** support
- **Rate-limited** validation API

---

## 🧪 Testing

```bash
pytest tests/ -v
```

| Module | Coverage |
|---|---|
| `test_scanner.py` | Recursive scanning |
| `test_excel_loader.py` | Data loading and normalization |
| `test_comparator.py` | Reconciliation algorithm |

**Strategy:** unit tests for *core*, integration tests for complete flows, mocking of external dependencies, and edge-case validation.

---

## 📦 Build & distribution

The project includes a **GitHub Actions** workflow that packages with PyInstaller (`--onefile --windowed`) on `windows-latest` and publishes the `FileChecker-Windows` artifact.

```bash
pyinstaller --onefile --windowed --name FileMaster filemaster_launcher.py
```

> For commercial distribution, **PyArmor obfuscation** is recommended.

---

## 🛠️ Tech stack

### Desktop application

- **Python 3.13** · **Tkinter + ttk**
- **pandas** · **OpenPyXL** · **TkinterDnD2**
- **pathlib / os** for filesystem operations

### Licensing server

- **Next.js** (App Router)
- **Supabase** (PostgreSQL)
- **JWT (RS256)**
- **Vercel**
- **Rate limiting** against abuse

---

## 🗺️ Roadmap

- [ ] Support for additional input formats
- [ ] Cloud API integration
- [ ] PDF report export
- [ ] Advanced dashboard with time series
- [ ] Multithreaded processing
- [ ] Plugin system

---

## 📚 Additional documentation

Licensing server architecture, API contracts, database schemas and deployment requirements:

```text
docs/license-server.md
```

---

## 📄 License

**Proprietary software.**

© FileMaster. All rights reserved.

Use is subject to the terms of the acquired **Lifetime Single-Machine** license. See `LICENSE` or contact the commercial team for details.

---

<p align="center"><strong>FileMaster</strong> — Turn days of manual auditing into seconds of auditable results.<br/><sub>Estimated average savings: <strong>~$230 USD/week</strong> · ~$11,960 USD/year per user.</sub></p>

---
