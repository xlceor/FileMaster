# FileMaster - FileChecker

FileMaster is a robust desktop application designed to streamline the process of verifying files against a master list. It is particularly useful for auditing large sets of files, ensuring consistency between physical storage and database records (Excel), and generating detailed reports.

## 🚀 Key Features

- **Multi-Mode Operation**:
  - **Export Folder Names**: Quickly generate an Excel report listing all files in a specific directory.
  - **Compare Folder vs. Master Excel**: Audit a physical folder against an expected list provided in an Excel file.
  - **Compare Excel vs. Master Excel**: Compare two Excel lists to find discrepancies.
- **Advanced Filtering**:
  - **Recursive Search**: Scan subfolders deeply.
  - **Ignore Extensions**: Focus on filenames regardless of their format (e.g., comparing `document.pdf` vs `document.docx`).
  - **Case Insensitivity**: Ensure matches even if capitalization differs.
- **Specialized Processing (Placas)**: A dedicated mode for processing filenames with specific patterns (e.g., extracting prefixes before separators like `-` or `_`).
- **Professional Reports**: Generates beautifully styled Excel reports (`.xlsx`) with:
  - Color-coded results (Found, Missing, Extra).
  - Summary metrics (Completeness percentage, total counts).
  - Alternating row colors for readability.
- **Smart Persistence**: Remembers your last used paths and settings for a faster workflow.

## 📁 Project Architecture

The application follows a modular architecture for better maintainability:

```text
FileMaster/
│
├── main.py              # Application entry point
├── config.py            # Global constants and UI theme configuration
├── FileChecker.py       # Legacy entry point wrapper
│
├── core/                # Business logic
│   ├── scanner.py       # File system scanning utilities
│   ├── excel_loader.py  # Excel reading and parsing
│   ├── comparator.py    # Core comparison algorithms
│   └── reports.py       # Excel report generation and styling
│
├── ui/                  # User Interface
│   ├── app.py           # Main Tkinter application class
│   ├── dialogs.py       # Custom dialog windows (placeholder)
│   └── themes.py        # UI style definitions (placeholder)
│
├── utils/               # Utilities
│   ├── config_manager.py # JSON configuration persistence
│   └── helpers.py       # General helper functions
│
└── assets/              # Static assets
    └── icon.ico         # Application icon
```

## 🛠 Installation & Requirements

1. **Python 3.8+**: Ensure you have Python installed.
2. **Dependencies**:
   ```bash
   pip install openpyxl
   ```
3. **Run the App**:
   ```bash
   python main.py
   ```

## 📖 How to Use

1. **Select Operation**: Choose whether you want to export a list or compare files.
2. **Set Paths**:
   - Use **"Carpeta de Archivos"** to select a physical directory.
   - Use **"Excel de Entrada"** if you are comparing two lists.
   - Use **"Excel Maestro"** for your source of truth (the list of expected files).
3. **Configure Options**:
   - Toggle **Recursiva** if you want to include subfolders.
   - Use **Ignorar extensión** to match files like `img_01.jpg` with `img_01`.
4. **Generate**: Click **"⚡ GENERAR REPORTE"**. The app will process the data and ask if you want to open the resulting Excel file immediately.

## 📝 Notes on Excel Format
- For both Master and Input Excels, the application reads the **first column** starting from the **second row** (assuming the first row is a header).
- Ensure your Excel files are in `.xlsx` format.

---
*Developed for efficient file auditing and data integrity.*
