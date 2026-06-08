# FileMaster

Professional desktop auditing software for reconciling files stored on disk against structured records from Excel, CSV, or JSON datasets.

FileMaster is designed for organizations that need to verify that physical or digital files match their official records, generating detailed reports, discrepancy analysis, and executive summaries in seconds.

---

## Features

### File Reconciliation

Compare thousands of files against database records with multiple operating modes:

- Folder → Excel Export
- Folder vs Master Excel
- Excel vs Master Excel
- CSV vs Master Excel
- JSON vs Master Excel

### Smart Matching Engine

FileMaster includes several normalization strategies to reduce false mismatches:

- Recursive folder scanning
- Case-insensitive comparisons
- Extension-agnostic matching
- Filename prefix extraction
- Automatic data cleaning and normalization

Examples:

| Physical File | Master Record | Match |
|--------------|--------------|--------|
| `ABC123.pdf` | `ABC123` | ✅ |
| `DOC-001.JPG` | `doc-001` | ✅ |
| `AB123_photo.jpg` | `AB123` | ✅ |

---

## Performance

The comparison engine is built around Python Set Algebra.

Operations are performed using:

```python
found = expected & actual
missing = expected - actual
extra = actual - expected
```

This provides near O(1) lookup performance and allows FileMaster to process datasets containing tens or hundreds of thousands of records efficiently.

---

## Supported Formats

### Input

- XLSX
- XLS
- CSV
- JSON

### Output

- Styled XLSX Reports

---

## Generated Reports

FileMaster automatically generates professional Excel reports using OpenPyXL.

### Included Sheets

#### Resumen

Executive dashboard containing:

- Expected Records
- Found Records
- Missing Records
- Extra Records
- Completion Percentage

#### Encontrados

Records successfully matched.

#### Faltantes

Records expected but not found.

#### Sobrantes

Files found but not registered.

### Report Features

- Automatic column sizing
- Zebra row styling
- Color-coded categories
- Corporate template support
- Executive summary dashboard

---

## User Interface

### Modern Theme System

FileMaster includes fully integrated:

- Light Mode
- Dark Mode

Theme switching updates:

- Widgets
- Tables
- Graphs
- Scrollbars
- Dashboard components

### Drag & Drop

Users can drag:

- Folders
- Excel files
- CSV files
- JSON files

directly into the application.

### Internationalization

Languages currently supported:

- English
- Spanish

Language changes are applied instantly without restarting the application.

---

## Analytical Dashboard

FileMaster includes a built-in analytics panel featuring:

### Completion Donut Chart

Visual representation of:

- Found Records
- Missing Records

### Distribution Bar Chart

Comparison of:

- Found
- Missing
- Extra

with automatic scaling and theme integration.

---

## Architecture

### Core Components

| Module | Responsibility |
|----------|---------------|
| `core/scanner.py` | Recursive file scanning |
| `core/excel_loader.py` | Dataset loading and normalization |
| `core/comparator.py` | High-performance reconciliation engine |
| `core/reports.py` | Excel report generation |
| `utils/licensing.py` | License validation and JWT verification |
| `ui/` | Application interface and dashboards |

---

## Licensing System

FileMaster uses a Lifetime Single-Machine licensing model.

### How It Works

1. User purchases a license key.
2. First activation generates a hardware fingerprint.
3. Fingerprint is bound permanently to the license.
4. Server issues a signed JWT lease token.
5. Client verifies the token locally and can operate offline.

### Security Features

- RSA-2048 cryptography
- RS256 signed JWT leases
- Hardware fingerprint locking
- Offline verification
- License revocation support
- License migration support
- Rate-limited API verification

---

## Technology Stack

### Desktop Application

- Python
- Tkinter
- OpenPyXL
- Pandas
- TkinterDnD2

### Licensing Server

- Next.js
- Supabase
- PostgreSQL
- JWT (RS256)
- Vercel

---

## Project Structure

```text
FileMaster/
│
├── core/
│   ├── scanner.py
│   ├── excel_loader.py
│   ├── comparator.py
│   └── reports.py
│
├── ui/
│
├── utils/
│
├── assets/
│
└── docs/
    └── license-server.md
```

---

## Documentation

Detailed backend architecture, licensing infrastructure, API contracts, database schemas, and deployment requirements are available in:

```text
docs/license-server.md
```

---

## License

Proprietary Software

© FileMaster. All rights reserved.