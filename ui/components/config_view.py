import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from config import C
from ui.components.common import SectionHeader, PathPicker, ModernCheck, ToolTip
from utils.translator import t

class ConfigView(ttk.Frame):
    def __init__(self, master, vars, on_run, **kwargs):
        super().__init__(master, style='Main.TFrame', **kwargs)
        self.vars = vars
        self.on_run = on_run
        
        # Lists for translation updates
        self.headers = []
        self.radio_btns = []
        self.check_btns = []
        self.path_pickers = []
        
        self._build_ui()

    def _build_ui(self):
        # Scrollable container
        self.canvas = tk.Canvas(self, bg=C["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas, style='Main.TFrame')

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=800)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Layout inside scroll_frame
        container = ttk.Frame(self.scroll_frame, style='Main.TFrame', padding=10)
        container.pack(fill="both", expand=True)

        # 1. Operación
        sec1 = SectionHeader(container, "section_operation")
        sec1.pack(anchor="w")
        self.headers.append(sec1)
        
        mode_card = ttk.Frame(container, style='Card.TFrame', padding=15)
        mode_card.pack(fill="x", pady=(0, 15))
        
        modes = [
            ("mode_export", "export"),
            ("mode_compare", "compare"),
            ("mode_compare_excel", "compare_excel")
        ]
        for text_key, val in modes:
            rb = tk.Radiobutton(mode_card, text=t(text_key), variable=self.vars["mode"], value=val,
                               bg=C["surface"], fg=C["text"], selectcolor=C["panel"],
                               activebackground=C["surface"], activeforeground=C["text"],
                               font=("Segoe UI", 10), command=self._toggle_fields)
            rb.pack(anchor="w", pady=5)
            self.radio_btns.append((rb, text_key))

        # 2. Orígenes de Datos (with Help lightbulb)
        header_row = ttk.Frame(container, style='Main.TFrame')
        header_row.pack(fill="x")
        
        sec2 = SectionHeader(header_row, "section_sources")
        sec2.pack(side="left")
        self.headers.append(sec2)
        
        self.help_btn = ttk.Button(header_row, text="💡", style='Secondary.TButton', width=3,
                              command=self._show_help_dialog)
        self.help_btn.pack(side="right", padx=5)
        ToolTip(self.help_btn, "help_title")
        
        data_card = ttk.Frame(container, style='Card.TFrame', padding=15)
        data_card.pack(fill="x", pady=(0, 15))

        self.path_folder = PathPicker(data_card, "lbl_folder", self.vars["folder"], self._browse_folder)
        self.path_folder.pack(fill="x", pady=(0, 15))
        self.path_pickers.append(self.path_folder)

        self.path_source_excel = PathPicker(data_card, "lbl_source_excel", self.vars["source_excel"], self._browse_source_excel)
        self.path_source_excel.pack(fill="x", pady=(0, 15))
        self.path_pickers.append(self.path_source_excel)

        self.path_master_excel = PathPicker(data_card, "lbl_master_excel", self.vars["excel"], self._browse_excel)
        self.path_master_excel.pack(fill="x")
        self.path_pickers.append(self.path_master_excel)

        # 3. Destino
        sec3 = SectionHeader(container, "section_destination")
        sec3.pack(anchor="w")
        self.headers.append(sec3)
        
        dest_card = ttk.Frame(container, style='Card.TFrame', padding=15)
        dest_card.pack(fill="x", pady=(0, 15))
        
        self.path_output = PathPicker(dest_card, "lbl_output_folder", self.vars["output"], self._browse_output)
        self.path_output.pack(fill="x")
        self.path_pickers.append(self.path_output)

        # 4. Opciones Avanzadas (with modern ToolTips)
        sec4 = SectionHeader(container, "section_options")
        sec4.pack(anchor="w")
        self.headers.append(sec4)
        
        opts_card = ttk.Frame(container, style='Card.TFrame', padding=15)
        opts_card.pack(fill="x", pady=(0, 20))

        chk1 = ModernCheck(opts_card, "opt_recursive", self.vars["recursive"], "help_tooltip_recursive")
        chk1.pack(anchor="w", pady=5)
        self.check_btns.append(chk1)
        
        chk2 = ModernCheck(opts_card, "opt_ignore_ext", self.vars["ignore_ext"], "help_tooltip_ignore_ext")
        chk2.pack(anchor="w", pady=5)
        self.check_btns.append(chk2)
        
        chk3 = ModernCheck(opts_card, "opt_ignore_case", self.vars["ignore_case"], "help_tooltip_ignore_case")
        chk3.pack(anchor="w", pady=5)
        self.check_btns.append(chk3)
        
        chk4 = ModernCheck(opts_card, "opt_preprocess", self.vars["preprocess"], "help_tooltip_preprocess")
        chk4.pack(anchor="w", pady=5)
        self.check_btns.append(chk4)

        # Action Button
        self.run_btn = ttk.Button(container, text=t("btn_run"), style='Accent.TButton', command=self.on_run)
        self.run_btn.pack(fill="x", pady=10)

        self._toggle_fields()

    def _toggle_fields(self):
        m = self.vars["mode"].get()
        
        if m in ["export", "compare"]:
            self.path_folder.state(['!disabled'])
        else:
            self.path_folder.state(['disabled'])

        if m == "compare_excel":
            self.path_source_excel.state(['!disabled'])
        else:
            self.path_source_excel.state(['disabled'])

        if m in ["compare", "compare_excel"]:
            self.path_master_excel.state(['!disabled'])
        else:
            self.path_master_excel.state(['disabled'])

    def _browse_folder(self):
        d = filedialog.askdirectory()
        if d: self.vars["folder"].set(d)

    def _browse_source_excel(self):
        f = filedialog.askopenfilename(filetypes=[("Data Files", "*.xlsx *.xls *.csv *.json"), ("Excel", "*.xlsx *.xls"), ("CSV", "*.csv"), ("JSON", "*.json")])
        if f: self.vars["source_excel"].set(f)

    def _browse_excel(self):
        f = filedialog.askopenfilename(filetypes=[("Data Files", "*.xlsx *.xls *.csv *.json"), ("Excel", "*.xlsx *.xls"), ("CSV", "*.csv"), ("JSON", "*.json")])
        if f: self.vars["excel"].set(f)

    def _browse_output(self):
        d = filedialog.askdirectory()
        if d: self.vars["output"].set(d)

    def _show_help_dialog(self):
        messagebox.showinfo(t("help_title"), t("help_desc"))

    def refresh_translations(self):
        """Actualiza todos los textos de la vista de configuración según el idioma activo."""
        for header in self.headers:
            header.refresh_translations()
            
        for picker in self.path_pickers:
            picker.refresh_translations()
            
        for chk in self.check_btns:
            chk.refresh_translations()
            
        for rb, text_key in self.radio_btns:
            rb.configure(text=t(text_key))
            
        self.run_btn.configure(text=t("btn_run"))

    def refresh_theme(self):
        """Actualiza los colores de los widgets tradicionales (Canvas, Radiobuttons) al cambiar de tema."""
        self.canvas.configure(bg=C["bg"])
        for rb, _ in self.radio_btns:
            rb.configure(bg=C["surface"], fg=C["text"], selectcolor=C["panel"],
                         activebackground=C["surface"], activeforeground=C["text"])
