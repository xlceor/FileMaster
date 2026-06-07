
import tkinter as tk
from tkinter import ttk, filedialog
from config import C
from ui.components.common import SectionHeader, PathPicker, ModernCheck

class ConfigView(ttk.Frame):
    def __init__(self, master, vars, on_run, **kwargs):
        super().__init__(master, style='Main.TFrame', **kwargs)
        self.vars = vars
        self.on_run = on_run
        self._build_ui()

    def _build_ui(self):
        # Scrollable container
        canvas = tk.Canvas(self, bg=C["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = ttk.Frame(canvas, style='Main.TFrame')

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=800)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Layout inside scroll_frame
        container = ttk.Frame(self.scroll_frame, style='Main.TFrame', padding=10)
        container.pack(fill="both", expand=True)

        # 1. Operación
        SectionHeader(container, "1. Tipo de Operación").pack(anchor="w")
        mode_card = ttk.Frame(container, style='Card.TFrame', padding=15)
        mode_card.pack(fill="x", pady=(0, 15))
        
        modes = [
            ("📤  Exportar nombres de carpeta", "export"),
            ("🔍  Comparar carpeta vs Excel maestro", "compare"),
            ("📊  Comparar Excel vs Excel maestro", "compare_excel")
        ]
        for text, val in modes:
            rb = tk.Radiobutton(mode_card, text=text, variable=self.vars["mode"], value=val,
                               bg=C["surface"], fg=C["text"], selectcolor=C["panel"],
                               activebackground=C["surface"], activeforeground=C["text"],
                               font=("Segoe UI", 10), command=self._toggle_fields)
            rb.pack(anchor="w", pady=5)

        # 2. Orígenes de Datos
        SectionHeader(container, "2. Orígenes de Datos").pack(anchor="w")
        data_card = ttk.Frame(container, style='Card.TFrame', padding=15)
        data_card.pack(fill="x", pady=(0, 15))

        self.path_folder = PathPicker(data_card, "Carpeta de Archivos", self.vars["folder"], self._browse_folder)
        self.path_folder.pack(fill="x", pady=(0, 15))

        self.path_source_excel = PathPicker(data_card, "Excel de Entrada", self.vars["source_excel"], self._browse_source_excel)
        self.path_source_excel.pack(fill="x", pady=(0, 15))

        self.path_master_excel = PathPicker(data_card, "Excel Maestro", self.vars["excel"], self._browse_excel)
        self.path_master_excel.pack(fill="x")

        # 3. Destino
        SectionHeader(container, "3. Destino de Reportes").pack(anchor="w")
        dest_card = ttk.Frame(container, style='Card.TFrame', padding=15)
        dest_card.pack(fill="x", pady=(0, 15))
        PathPicker(dest_card, "Carpeta de Salida", self.vars["output"], self._browse_output).pack(fill="x")

        # 4. Opciones Avanzadas
        SectionHeader(container, "4. Opciones de Procesamiento").pack(anchor="w")
        opts_card = ttk.Frame(container, style='Card.TFrame', padding=15)
        opts_card.pack(fill="x", pady=(0, 20))

        ModernCheck(opts_card, "🔁 Búsqueda recursiva (subcarpetas)", self.vars["recursive"]).pack(anchor="w", pady=5)
        ModernCheck(opts_card, "🔤 Ignorar extensión al comparar", self.vars["ignore_ext"]).pack(anchor="w", pady=5)
        ModernCheck(opts_card, "🔡 Ignorar mayúsculas/minúsculas", self.vars["ignore_case"]).pack(anchor="w", pady=5)
        ModernCheck(opts_card, "🛠 Procesamiento especial (Placas)", self.vars["preprocess"]).pack(anchor="w", pady=5)

        # Action Button
        self.run_btn = ttk.Button(container, text="⚡ INICIAR PROCESAMIENTO", style='Accent.TButton', command=self.on_run)
        self.run_btn.pack(fill="x", pady=10)

        self._toggle_fields()

    def _toggle_fields(self):
        m = self.vars["mode"].get()
        
        # Folder is needed for 'export' and 'compare' (folder vs excel)
        if m in ["export", "compare"]:
            self.path_folder.state(['!disabled'])
        else:
            self.path_folder.state(['disabled'])

        # Source Excel is only for 'compare_excel'
        if m == "compare_excel":
            self.path_source_excel.state(['!disabled'])
        else:
            self.path_source_excel.state(['disabled'])

        # Master Excel is for both 'compare' modes
        if m in ["compare", "compare_excel"]:
            self.path_master_excel.state(['!disabled'])
        else:
            self.path_master_excel.state(['disabled'])

    def _browse_folder(self):
        d = filedialog.askdirectory()
        if d: self.vars["folder"].set(d)

    def _browse_source_excel(self):
        f = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xls")])
        if f: self.vars["source_excel"].set(f)

    def _browse_excel(self):
        f = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xls")])
        if f: self.vars["excel"].set(f)

    def _browse_output(self):
        d = filedialog.askdirectory()
        if d: self.vars["output"].set(d)
