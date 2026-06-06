# 🔍 Technical Details: FileMaster Implementation

This document provides a deep dive into the code for developers. It explains the flow of execution, the responsibility of each module, and how data moves through the system.

---

## 🏗️ The Execution Flow

The application follows a linear flow from user input to report generation:

1.  **Entry Point (`main.py`)**:
    - Initializes the `FileCheckerApp` class from `ui/app.py`.
    - Starts the Tkinter event loop (`mainloop()`).

2.  **UI Initialization (`ui/app.py`)**:
    - `__init__`: Loads previous user settings via `utils/config_manager.py`.
    - `_build_ui`: Constructs the interface using colors defined in `config.py`.
    - `_toggle_excel_field`: Dynamically hides/shows input fields based on the selected mode (Export vs. Compare Folder vs. Compare Excel).

3.  **User Trigger (`_run` method)**:
    - When the user clicks "GENERAR REPORTE", the `_run` method performs:
        - **Validation**: Checks if paths exist and are valid.
        - **State Saving**: Saves current UI selections to the JSON config file.
        - **Orchestration**: Calls the appropriate high-level function from `core/reports.py`.

4.  **Core Processing (`core/`)**:
    - **`reports.py`**: Acts as the "Chef". It calls the "Ingredients":
        - `scanner.py`: Scans the disk for files.
        - `excel_loader.py`: Reads the Master Excel file.
        - `comparator.py`: Compares the two lists.
    - **Result**: `reports.py` then uses `openpyxl` to create a new workbook, styles it, and saves it to disk.

5.  **Finalization**:
    - The UI stops the progress bar.
    - It shows a success message and offers to open the file using system-native commands (via `os.startfile` or `open`).

---

## 📂 Module-by-Module Breakdown

### 🎨 `config.py`
Contains the `C` dictionary (Theme Colors) and the `CONFIG_FILE` name. This centralizes the "look and feel" so you can change the UI palette in one place.

### ⚙️ `core/` (Business Logic)
- **`comparator.py`**:
    - `preprocess_placas(name)`: A string manipulation function that extracts prefixes.
    - `compare_files(expected, found_list)`: The logic heart. It uses Python `set` operations (`&`, `-`) to find intersections and differences instantly.
- **`scanner.py`**:
    - `scan_folder(...)`: Uses `pathlib.Path.glob`. If `recursive` is True, it uses `**/*`. It filters out directories and only returns filenames.
- **`excel_loader.py`**:
    - Uses `openpyxl` in `read_only=True` mode for speed. It always targets the first column (`row[0]`) and skips the header (`min_row=2`).
- **`reports.py`**:
    - Contains complex logic for `openpyxl` styling (`Font`, `Fill`, `Border`). 
    - `comparison_report`: Orchestrates the full comparison and creates two sheets: "Resultados" (detailed list) and "Resumen" (metrics).

### 🖥️ `ui/app.py`
- Inherits from `tk.Tk`.
- Uses `tk.StringVar` and `tk.BooleanVar` to bind UI elements to data.
- **Dynamic UI**: The `_set_state` helper recursively enables/disables widgets within frames, ensuring the user can't interact with irrelevant fields.

### 🛠️ `utils/config_manager.py`
- Simple wrapper around `json.dump` and `json.load`.
- It ensures that when you reopen the app, your previous work folder and Excel paths are already there.

---

## 💡 Key Design Decisions

- **Set Operations**: We convert lists to `set()` before comparison. This makes the tool extremely fast even for 100,000+ files, as set operations are O(n) while list searching is O(n^2).
- **Styling with OpenPyXL**: We manually define borders and fills in `core/reports.py` to ensure the reports are "client-ready" immediately after generation.
- **Decoupled Logic**: Notice that `core/` functions (scanner, loader, comparator) **never** import `tkinter`. They are pure Python logic, which makes them easy to unit test.

---

## 🛠️ How to start making changes
1. **To change the UI colors**: Edit `config.py`.
2. **To add a new comparison rule**: Add a function to `core/comparator.py` and call it from `core/reports.py`.
3. **To support a new file format**: Add a loader in `core/excel_loader.py` (or rename to `data_loader.py`).
4. **To change Excel styles**: Modify the `_style_header` and `_style_cell` functions in `core/reports.py`.
