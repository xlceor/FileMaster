
import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

from config import C
from core.reports import export_names_report, comparison_report
from utils.config_manager import load_config, save_config

class FileCheckerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FileChecker v1.0")

        
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        if '_MEIPASS' not in sys.__dict__:
            base_path = os.path.dirname(base_path)

        icon_path = os.path.join(base_path, "assets", "icon.ico")
        self.iconbitmap(icon_path)

        self.resizable(False, False)
        self.configure(bg=C["bg"])

        self.cfg = load_config()

        self.mode               = tk.StringVar(value=self.cfg.get("mode", "export"))
        self.folder_var         = tk.StringVar(value=self.cfg.get("last_folder", ""))
        self.source_excel_var   = tk.StringVar(value=self.cfg.get("last_source_excel", ""))
        self.excel_var          = tk.StringVar(value=self.cfg.get("last_excel", ""))
        self.output_var         = tk.StringVar(value=self.cfg.get("last_output", ""))
        self.recursive          = tk.BooleanVar(value=self.cfg.get("recursive", False))
        self.ignore_ext         = tk.BooleanVar(value=self.cfg.get("ignore_ext", False))
        self.ignore_case        = tk.BooleanVar(value=self.cfg.get("ignore_case", True))
        self.status_var         = tk.StringVar(value="Listo")

        self._build_ui()
        self._center_window()


    def _build_ui(self):
        hdr = tk.Frame(self, bg=C["accent"], pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📁  FileChecker", font=("Arial", 17, "bold"),
                 bg=C["accent"], fg="#FFFFFF").pack()
        tk.Label(hdr, text="Verificador de archivos contra lista maestra",
                 font=("Arial", 9), bg=C["accent"], fg="#E0E0E0").pack()

        body = tk.Frame(self, bg=C["bg"], padx=20, pady=14)
        body.pack(fill="both")

        self.notebook = ttk.Notebook(body)
        self.notebook.pack(fill="x", pady=(0, 10))
        
        self.tab_std = tk.Frame(self.notebook, bg=C["bg"])
        self.tab_plc = tk.Frame(self.notebook, bg=C["bg"])
        
        self.notebook.add(self.tab_std, text="  ESTÁNDAR  ")
        self.notebook.add(self.tab_plc, text="  PLACAS  ")
        
        if self.cfg.get("tab") == "placas":
            self.notebook.select(1)

        self._section(body, "OPERACIÓN")
        mode_f = tk.Frame(body, bg=C["surface"], pady=8, padx=12)
        mode_f.pack(fill="x", pady=(0, 10))

        modes = [
            ("📤  Exportar nombres de carpeta", "export"),
            ("🔍  Comparar carpeta vs Excel maestro", "compare"),
            ("📊  Comparar Excel vs Excel maestro", "compare_excel")
        ]
        for text, val in modes:
            tk.Radiobutton(mode_f, text=text, variable=self.mode, value=val,
                           command=self._toggle_excel_field,
                           bg=C["surface"], fg=C["text"], selectcolor=C["panel"],
                           activebackground=C["surface"], activeforeground=C["text"],
                           font=("Arial", 10)).pack(anchor="w", pady=2)

        self.folder_section = self._section(body, "CARPETA DE ARCHIVOS")
        self.folder_frame = self._path_row(body, self.folder_var, self._browse_folder)

        self.source_excel_section = self._section(body, "EXCEL DE ENTRADA")
        self.source_excel_frame = self._path_row(body, self.source_excel_var, self._browse_source_excel, placeholder="Selecciona el Excel de entrada...")

        self.excel_section_label = self._section(body, "EXCEL MAESTRO")
        self.excel_frame = self._path_row(body, self.excel_var, self._browse_excel, placeholder="Selecciona el archivo Excel maestro...")

        self._section(body, "CARPETA DE DESTINO (REPORTES)")
        self._path_row(body, self.output_var, self._browse_output, placeholder="Donde se guardarán los reportes...")

        self._section(body, "OPCIONES")
        opts = tk.Frame(body, bg=C["surface"], padx=12, pady=8)
        opts.pack(fill="x", pady=(0, 10))

        for text, var in [
            ("🔁  Búsqueda recursiva (subcarpetas)", self.recursive),
            ("🔤  Ignorar extensión al comparar", self.ignore_ext),
            ("🔡  Ignorar mayúsculas/minúsculas", self.ignore_case),
        ]:
            tk.Checkbutton(opts, text=text, variable=var,
                           bg=C["surface"], fg=C["text"], selectcolor=C["panel"],
                           activebackground=C["surface"], activeforeground=C["text"],
                           font=("Arial", 10)).pack(anchor="w", pady=2)

        btn = tk.Button(body, text="⚡  GENERAR REPORTE",
                        command=self._run,
                        bg=C["accent"], fg="#FFFFFF",
                        font=("Arial", 12, "bold"),
                        relief="flat", cursor="hand2",
                        pady=10, padx=20)
        btn.pack(fill="x", pady=(4, 10))
        btn.bind("<Enter>", lambda e: btn.configure(bg=C["accent2"]))
        btn.bind("<Leave>", lambda e: btn.configure(bg=C["accent"]))

        self.progress = ttk.Progressbar(body, mode="indeterminate", length=400)
        self.progress.pack(fill="x", pady=(0, 6))

        status_f = tk.Frame(body, bg=C["panel"], pady=6, padx=10)
        status_f.pack(fill="x")
        tk.Label(status_f, textvariable=self.status_var,
                 bg=C["panel"], fg=C["cyan"],
                 font=("Arial", 9, "italic")).pack(anchor="w")

        self._toggle_excel_field()

    def _section(self, parent, text):
        lbl = tk.Label(parent, text=text, bg=C["bg"], fg=C["subtext"],
                       font=("Arial", 8, "bold"))
        lbl.pack(anchor="w", pady=(6, 2))
        return lbl

    def _path_row(self, parent, var, cmd, placeholder="Selecciona carpeta..."):
        f = tk.Frame(parent, bg=C["bg"])
        f.pack(fill="x", pady=(0, 4))
        entry = tk.Entry(f, textvariable=var, width=44,
                         bg=C["panel"], fg=C["text"], insertbackground=C["text"],
                         relief="flat", font=("Arial", 9), bd=4)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        btn = tk.Button(f, text="Examinar…", command=cmd,
                        bg=C["surface"], fg=C["text"],
                        relief="flat", cursor="hand2",
                        font=("Arial", 9), padx=8)
        btn.pack(side="right")
        btn.bind("<Enter>", lambda e: btn.configure(bg=C["accent"], fg="#FFFFFF"))
        btn.bind("<Leave>", lambda e: btn.configure(bg=C["surface"], fg=C["text"]))
        return f


    def _toggle_excel_field(self):
        m = self.mode.get()
        is_export = (m == "export")
        is_compare_folder = (m == "compare")
        is_compare_excel = (m == "compare_excel")

        folder_state = "normal" if (is_export or is_compare_folder) else "disabled"
        self._set_state(self.folder_frame, folder_state)
        self.folder_section.configure(fg=C["subtext"] if folder_state == "normal" else C["border"])

        source_state = "normal" if is_compare_excel else "disabled"
        self._set_state(self.source_excel_frame, source_state)
        self.source_excel_section.configure(fg=C["subtext"] if source_state == "normal" else C["border"])

        master_state = "normal" if (is_compare_folder or is_compare_excel) else "disabled"
        self._set_state(self.excel_frame, master_state)
        self.excel_section_label.configure(fg=C["subtext"] if master_state == "normal" else C["border"])

    def _set_state(self, frame, state):
        for w in frame.winfo_children():
            try:
                w.configure(state=state)
                for child in w.winfo_children():
                    child.configure(state=state)
            except Exception:
                pass

    def _browse_folder(self):
        d = filedialog.askdirectory(title="Seleccionar carpeta")
        if d:
            self.folder_var.set(d)

    def _browse_source_excel(self):
        f = filedialog.askopenfilename(
            title="Seleccionar Excel de entrada",
            filetypes=[("Excel", "*.xlsx *.xlsm *.xls"), ("Todos", "*.*")]
        )
        if f:
            self.source_excel_var.set(f)

    def _browse_excel(self):
        f = filedialog.askopenfilename(
            title="Seleccionar Excel maestro",
            filetypes=[("Excel", "*.xlsx *.xlsm *.xls"), ("Todos", "*.*")]
        )
        if f:
            self.excel_var.set(f)

    def _browse_output(self):
        d = filedialog.askdirectory(title="Seleccionar carpeta de destino")
        if d:
            self.output_var.set(d)

    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

    def _run(self):
        mode = self.mode.get()
        is_placas = (self.notebook.index("current") == 1)
        
        if mode in ["export", "compare"]:
            folder = self.folder_var.get().strip()
            if not folder or not os.path.isdir(folder):
                messagebox.showerror("Error", "Selecciona una carpeta válida.")
                return
        
        if mode == "compare_excel":
            source_path = self.source_excel_var.get().strip()
            if not source_path or not os.path.isfile(source_path):
                messagebox.showerror("Error", "Selecciona un Excel de entrada válido.")
                return
        else:
            source_path = self.folder_var.get().strip()

        if mode in ["compare", "compare_excel"]:
            excel_master = self.excel_var.get().strip()
            if not excel_master or not os.path.isfile(excel_master):
                messagebox.showerror("Error", "Selecciona un Excel maestro válido.")
                return

        self._save_state()
        self.progress.start(10)
        self.status_var.set("Procesando…")
        self.update()

        try:
            ts  = datetime.now().strftime("%Y-%m-%d_%H-%M")
            rec = self.recursive.get()
            iex = self.ignore_ext.get()
            ica = self.ignore_case.get()
            out_dir = self.output_var.get().strip()

            if mode == "export":
                filename = f"Reporte_Nombres_{ts}.xlsx"
                out_path = os.path.join(out_dir, filename) if out_dir else filename
                out = export_names_report(source_path, rec, iex, is_placas, ts, output_path=out_path)
            else:
                filename = f"Reporte_Comparacion_{ts}.xlsx"
                out_path = os.path.join(out_dir, filename) if out_dir else filename
                out = comparison_report(
                    source_path, excel_master, 
                    rec, iex, ica, is_placas, ts, 
                    is_excel_source=(mode == "compare_excel"),
                    output_path=out_path
                )

            self.progress.stop()
            self.status_var.set(f"✔ Reporte generado: {out}")
            if messagebox.askyesno("Listo", f"Reporte generado:\n{out}\n\n¿Abrir ahora?"):
                import platform
                if platform.system() == "Windows":
                    os.startfile(out)
                elif platform.system() == "Darwin":
                    os.system(f'open "{out}"')
                else:
                    os.system(f'xdg-open "{out}"')

        except Exception as ex:
            self.progress.stop()
            self.status_var.set(f"✖ Error: {ex}")
            messagebox.showerror("Error", str(ex))

    def _save_state(self):
        save_config({
            "mode":              self.mode.get(),
            "last_folder":       self.folder_var.get(),
            "last_source_excel": self.source_excel_var.get(),
            "last_excel":        self.excel_var.get(),
            "last_output":       self.output_var.get(),
            "recursive":         self.recursive.get(),
            "ignore_ext":        self.ignore_ext.get(),
            "ignore_case":       self.ignore_case.get(),
            "tab":               "placas" if self.notebook.index("current") == 1 else "standard"
        })
