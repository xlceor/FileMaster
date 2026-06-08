import tkinter as tk
from tkinter import ttk
from config import C
from utils.translator import t

class ResultsView(ttk.Frame):
    def __init__(self, master, on_export, **kwargs):
        super().__init__(master, style='Main.TFrame', **kwargs)
        self.on_export = on_export
        self.trees = {}
        self.lbl_frames = {}
        self.filter_entries = {}
        self.raw_data_cache = {
            "encontrados": {},
            "faltantes": {},
            "sobrantes": {}
        }
        self.last_results_data = None
        self._build_ui()

    def _build_ui(self):
        # Summary Area
        self.summary_card = ttk.Frame(self, style='Card.TFrame', padding=15)
        self.summary_card.pack(fill="x", pady=(0, 20))
        
        self.summary_label = ttk.Label(self.summary_card, 
                                     text=t("results_no_data"),
                                     font=("Segoe UI", 11), background=C["surface"], foreground=C["subtext"])
        self.summary_label.pack()

        # Tables Container
        tables_frame = ttk.Frame(self, style='Main.TFrame')
        tables_frame.pack(fill="both", expand=True)
        
        # Columns configuration
        self.cols_config = [
            ("results_col_found", "encontrados", C["green"]),
            ("results_col_missing", "faltantes", C["red"]),
            ("results_col_extra", "sobrantes", "#E65100")
        ]
        
        for i, (title_key, key, color) in enumerate(self.cols_config):
            frame = ttk.Frame(tables_frame, style='Main.TFrame', padding=5)
            frame.grid(row=0, column=i, sticky="nsew")
            tables_frame.grid_columnconfigure(i, weight=1)
            
            lbl = ttk.Label(frame, text=t(title_key).upper(), font=("Segoe UI", 9, "bold"), foreground=color, background=C["bg"])
            lbl.pack(anchor="w", pady=(0, 5))
            self.lbl_frames[key] = (lbl, title_key)

            # Filter Entry
            filter_var = tk.StringVar()
            filter_entry = ttk.Entry(frame, textvariable=filter_var, style='TEntry')
            filter_entry.pack(fill="x", pady=(0, 5))
            filter_entry.bind("<KeyRelease>", lambda event, k=key: self._filter_treeview(event, k))
            self.filter_entries[key] = (filter_entry, filter_var)
            
            # Treeview Container with scrollbar
            tree_container = ttk.Frame(frame, style='Card.TFrame')
            tree_container.pack(fill="both", expand=True)
            
            tree = ttk.Treeview(tree_container, columns=("ID",), show="headings", height=10, style='Treeview')
            tree.heading("ID", text=t("results_col_header"), command=lambda: self._sort_column(tree, "ID", False))
            tree.column("ID", anchor="w")
            
            sb = ttk.Scrollbar(tree_container, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=sb.set)
            
            tree.pack(side="left", fill="both", expand=True)
            sb.pack(side="right", fill="y")
            
            self.trees[key] = tree

        # Export Button
        self.btn_export = ttk.Button(self, text=t("btn_export_excel"), 
                                    style='Accent.TButton', command=self.on_export)
        self.btn_export.pack(fill="x", pady=(20, 0))
        self.btn_export.state(['disabled'])

    def update_results(self, master_count, found, missing, extra):
        """Actualiza la interfaz con los resultados de la comparación."""
        self.last_results_data = (master_count, len(found), len(missing), len(extra))
        
        # Update Summary with localized label
        self.summary_label.configure(
            text=t("results_summary", total=master_count, found=len(found), missing=len(missing), extra=len(extra)),
            foreground=C["text"]
        )
        
        # Store raw data for filtering
        self.raw_data_cache["encontrados"] = found
        self.raw_data_cache["faltantes"] = missing
        self.raw_data_cache["sobrantes"] = extra
        
        # Clear and fill trees (applying filters if any)
        for key, tree in self.trees.items():
            filter_text = self.filter_entries[key][1].get().lower()
            
            for item in tree.get_children():
                tree.delete(item)
            
            data = self.raw_data_cache[key]
            filtered_identifiers = []
            for identifier in sorted(data.keys()):
                if not filter_text or filter_text in identifier.lower():
                    filtered_identifiers.append(identifier)

            for identifier in filtered_identifiers:
                tree.insert("", "end", values=(identifier,))
        
        self.btn_export.state(['!disabled'])

    def _filter_treeview(self, event, key):
        """Filtra los elementos del Treeview según el texto del Entry."""
        tree = self.trees[key]
        filter_text = self.filter_entries[key][1].get().lower()
        
        # Clear current view
        for item in tree.get_children():
            tree.delete(item)
            
        # Re-insert filtered items from raw data
        data = self.raw_data_cache[key]
        filtered_identifiers = []
        for identifier in sorted(data.keys()):
            if not filter_text or filter_text in identifier.lower():
                filtered_identifiers.append(identifier)
        
        for identifier in filtered_identifiers:
            tree.insert("", "end", values=(identifier,))

    def _sort_column(self, tree, col, reverse):
        """Ordena los datos de una columna del Treeview."""
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        data.sort(key=lambda x: x[0].lower(), reverse=reverse)
        for index, item in enumerate(data):
            tree.move(item[1], '', index)
        tree.heading(col, command=lambda: self._sort_column(tree, col, not reverse))

    def refresh_translations(self):
        """Actualiza los textos de los resultados según el idioma activo."""
        # Update Summary Label
        if self.last_results_data:
            total, found, missing, extra = self.last_results_data
            self.summary_label.configure(text=t("results_summary", total=total, found=found, missing=missing, extra=extra))
        else:
            self.summary_label.configure(text=t("results_no_data"))
            
        # Update Table Titles and Headers
        for key, (lbl, title_key) in self.lbl_frames.items():
            lbl.configure(text=t(title_key).upper())
            
        for tree in self.trees.values():
            tree.heading("ID", text=t("results_col_header"))
            
        self.btn_export.configure(text=t("btn_export_excel"))
