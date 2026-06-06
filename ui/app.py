
import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

from config import C
from core.reports import (
    export_names_report, 
    comparison_report, 
    run_comparison, 
    report_excel, 
    _add_summary_to_report
)
from utils.config_manager import load_config, save_config

class FileCheckerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FileChecker v1.1")

        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        if '_MEIPASS' not in sys.__dict__:
            base_path = os.path.dirname(base_path)

        icon_path = os.path.join(base_path, "assets", "icon.ico")
        try:
            self.iconbitmap(icon_path)
        except Exception:
            pass

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
        self.preprocess         = tk.BooleanVar(value=self.cfg.get("preprocess", False))
        self.status_var         = tk.StringVar(value="Listo")
        self.summary_var        = tk.StringVar(value="Esperados: 0   Encontrados: 0   Faltantes: 0   Sobrantes: 0")

        # Cache for results
        self.last_results = None

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
        body.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(body)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        self.tab_std = tk.Frame(self.notebook, bg=C["bg"])
        self.tab_res = tk.Frame(self.notebook, bg=C["bg"])
        
        self.notebook.add(self.tab_std, text="  CONFIGURACIÓN  ")
        self.notebook.add(self.tab_res, text="  RESULTADOS  ")
        
        self._build_tab_config(self.tab_std)
        self._build_tab_results(self.tab_res)

        # Bottom Summary Bar
        summary_f = tk.Frame(self, bg=C["accent"], pady=6)
        summary_f.pack(fill="x", side="bottom")
        tk.Label(summary_f, textvariable=self.summary_var,
                 bg=C["accent"], fg="#FFFFFF",
                 font=("Arial", 10, "bold")).pack()

        self.progress = ttk.Progressbar(self, mode="indeterminate", length=400)
        self.progress.pack(fill="x", side="bottom")

        status_f = tk.Frame(self, bg=C["panel"], pady=6, padx=10)
        status_f.pack(fill="x", side="bottom")
        tk.Label(status_f, textvariable=self.status_var,
                 bg=C["panel"], fg=C["cyan"],
                 font=("Arial", 9, "italic")).pack(anchor="w")

        self._toggle_excel_field()

    def _build_tab_config(self, parent):
        # Canvas and scrollbar for scrolling
        canvas = tk.Canvas(parent, bg=C["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=C["bg"])

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=700)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel support
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        container = tk.Frame(scroll_frame, bg=C["bg"], padx=20, pady=10)
        container.pack(fill="both", expand=True)

        self._section(container, "OPERACIÓN")
        mode_f = tk.Frame(container, bg=C["surface"], pady=8, padx=12)
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

        self.folder_section = self._section(container, "CARPETA DE ARCHIVOS")
        self.folder_frame = self._path_row(container, self.folder_var, self._browse_folder)

        self.source_excel_section = self._section(container, "EXCEL DE ENTRADA")
        self.source_excel_frame = self._path_row(container, self.source_excel_var, self._browse_source_excel, placeholder="Selecciona el Excel de entrada...")

        self.excel_section_label = self._section(container, "EXCEL MAESTRO")
        self.excel_frame = self._path_row(container, self.excel_var, self._browse_excel, placeholder="Selecciona el archivo Excel maestro...")

        self._section(container, "CARPETA DE DESTINO (REPORTES)")
        self._path_row(container, self.output_var, self._browse_output, placeholder="Donde se guardarán los reportes...")

        self._section(container, "OPCIONES")
        opts = tk.Frame(container, bg=C["surface"], padx=12, pady=8)
        opts.pack(fill="x", pady=(0, 10))

        for text, var in [
            ("🔁  Búsqueda recursiva (subcarpetas)", self.recursive),
            ("🔤  Ignorar extensión al comparar", self.ignore_ext),
            ("🔡  Ignorar mayúsculas/minúsculas", self.ignore_case),
            ("🛠  Procesamiento especial (Placas)", self.preprocess),
        ]:
            tk.Checkbutton(opts, text=text, variable=var,
                           bg=C["surface"], fg=C["text"], selectcolor=C["panel"],
                           activebackground=C["surface"], activeforeground=C["text"],
                           font=("Arial", 10)).pack(anchor="w", pady=2)

        btn = tk.Button(container, text="⚡  GENERAR / PREVISUALIZAR",
                        command=self._run,
                        bg=C["accent"], fg="#FFFFFF",
                        font=("Arial", 12, "bold"),
                        relief="flat", cursor="hand2",
                        pady=10, padx=20)
        btn.pack(fill="x", pady=(4, 10))
        btn.bind("<Enter>", lambda e: btn.configure(bg=C["accent2"]))
        btn.bind("<Leave>", lambda e: btn.configure(bg=C["accent"]))

    def _build_tab_results(self, parent):
        container = tk.Frame(parent, bg=C["bg"])
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        cols = ["Encontrados", "Faltantes", "Sobrantes"]
        colors = [C["green"], C["red"], "#E65100"] 
        
        self.trees = {}
        
        for i, (col_name, color) in enumerate(zip(cols, colors)):
            frame = tk.LabelFrame(container, text=f"  {col_name.upper()}  ", 
                                 bg=C["bg"], fg=color, font=("Arial", 10, "bold"))
            frame.grid(row=0, column=i, sticky="nsew", padx=5)
            container.grid_columnconfigure(i, weight=1)
            
            tree = ttk.Treeview(frame, columns=("ID",), show="headings", height=12)
            tree.heading("ID", text="Identificador")
            tree.column("ID", width=150)
            
            sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=sb.set)
            
            tree.pack(side="left", fill="both", expand=True)
            sb.pack(side="right", fill="y")
            
            self.trees[col_name.lower()] = tree

        btn_frame = tk.Frame(parent, bg=C["bg"])
        btn_frame.pack(fill="x", pady=10)
        
        self.btn_export = tk.Button(btn_frame, text="📥  EXPORTAR A EXCEL",
                                   command=self._export_results,
                                   bg=C["accent"], fg="#FFFFFF",
                                   font=("Arial", 11, "bold"),
                                   relief="flat", cursor="hand2",
                                   pady=8, padx=20, state="disabled")
        self.btn_export.pack()
        self.btn_export.bind("<Enter>", lambda e: self.btn_export.configure(bg=C["accent2"]))
        self.btn_export.bind("<Leave>", lambda e: self.btn_export.configure(bg=C["accent"]))

    def _section(self, parent, text):
        lbl = tk.Label(parent, text=text, bg=C["bg"], fg=C["subtext"],
                       font=("Arial", 8, "bold"))
        lbl.pack(anchor="w", pady=(6, 2))
        return lbl

    def _path_row(self, parent, var, cmd, placeholder="Selecciona carpeta..."):
        f = tk.Frame(parent, bg=C["bg"])
        f.pack(fill="x", pady=(0, 4))
        entry = tk.Entry(f, textvariable=var, width=15,
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
        # Adjusted for a narrower, more balanced look
        w, h = 810, 750
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _run(self):
        mode = self.mode.get()
        is_placas = (self.notebook.index("current") == 1) # This needs update as tabs changed
        # We can use mode or just check if it's "compare"
        
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
            pre = self.preprocess.get()
            out_dir = self.output_var.get().strip()

            if mode == "export":
                filename = f"Reporte_Nombres_{ts}.xlsx"
                out_path = os.path.join(out_dir, filename) if out_dir else filename
                out = export_names_report(source_path, rec, iex, pre, ts, output_path=out_path)
                self.progress.stop()
                self.status_var.set(f"✔ Reporte generado: {out}")
                if messagebox.askyesno("Listo", f"Reporte generado:\n{out}\n\n¿Abrir ahora?"):
                    self._open_file(out)
            else:
                # Comparison mode
                results = run_comparison(
                    source_path, excel_master, 
                    rec, iex, ica, pre, 
                    is_excel_source=(mode == "compare_excel")
                )
                self.last_results = results
                self._update_results_ui(results)
                self.notebook.select(self.tab_res)
                self.btn_export.configure(state="normal")
                self.progress.stop()
                self.status_var.set("✔ Comparación finalizada. Revisa la pestaña de resultados.")

        except Exception as ex:
            self.progress.stop()
            self.status_var.set(f"✖ Error: {ex}")
            messagebox.showerror("Error", str(ex))

    def _update_results_ui(self, results):
        master, found, missing, extra = results
        
        # Clear trees
        for tree in self.trees.values():
            for item in tree.get_children():
                tree.delete(item)
        
        # Fill trees
        for tree_name, data in zip(["encontrados", "faltantes", "sobrantes"], [found, missing, extra]):
            tree = self.trees[tree_name]
            for key in sorted(data.keys()):
                tree.insert("", "end", values=(key,))
        
        # Update summary bar
        self.summary_var.set(
            f"Esperados: {len(master)}   Encontrados: {len(found)}   "
            f"Faltantes: {len(missing)}   sobrantes: {len(extra)}"
        )

    def _export_results(self):
        if not self.last_results: return
        
        try:
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
            out_dir = self.output_var.get().strip()
            filename = f"Reporte_Comparacion_{ts}.xlsx"
            out_path = os.path.join(out_dir, filename) if out_dir else filename
            
            master, found, missing, extra = self.last_results
            
            report_excel(out_path, found, missing, extra)
            _add_summary_to_report(out_path, len(master), len(found), len(missing), len(extra))
            
            self.status_var.set(f"✔ Reporte exportado: {out_path}")
            if messagebox.askyesno("Listo", f"Reporte exportado:\n{out_path}\n\n¿Abrir ahora?"):
                self._open_file(out_path)
        except Exception as ex:
            messagebox.showerror("Error al exportar", str(ex))

    def _open_file(self, path):
        import platform
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            os.system(f'open "{path}"')
        else:
            os.system(f'xdg-open "{path}"')

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
            "preprocess":        self.preprocess.get()
        })
