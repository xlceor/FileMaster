import tkinter as tk
from tkinter import ttk
from config import C
from utils.translator import t

class Sidebar(ttk.Frame):
    def __init__(self, master, on_nav_change, on_lang_change, on_theme_toggle, **kwargs):
        super().__init__(master, style='Sidebar.TFrame', **kwargs)
        self.on_nav_change = on_nav_change
        self.on_lang_change = on_lang_change
        self.on_theme_toggle = on_theme_toggle
        self._build_ui()

    def _build_ui(self):
        # Logo / Title
        self.header = ttk.Label(self, text="📁 FileChecker", style='Sidebar.TLabel', padding=(20, 30))
        self.header.pack(fill="x")
        
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20, pady=10)

        # Nav Buttons
        self.btn_config = self._nav_button(t("nav_config"), "config")
        self.btn_results = self._nav_button(t("nav_results"), "results")
        
        # Footer Container
        footer_container = ttk.Frame(self, style='Sidebar.TFrame')
        footer_container.pack(side="bottom", fill="x", pady=20)
        
        # Language Selector (ES | EN)
        lang_frame = ttk.Frame(footer_container, style='Sidebar.TFrame')
        lang_frame.pack(pady=5)
        
        self.btn_es = tk.Button(lang_frame, text="ES", bg=C["accent"], fg="#FFFFFF",
                                activebackground=C["accent2"], activeforeground="#FFFFFF",
                                font=("Segoe UI", 9, "bold"), relief="flat", padx=8, pady=3,
                                cursor="hand2", command=lambda: self.on_lang_change("es"))
        self.btn_es.pack(side="left", padx=5)
        
        self.btn_en = tk.Button(lang_frame, text="EN", bg=C["accent"], fg="#FFFFFF",
                                activebackground=C["accent2"], activeforeground="#FFFFFF",
                                font=("Segoe UI", 9, "bold"), relief="flat", padx=8, pady=3,
                                cursor="hand2", command=lambda: self.on_lang_change("en"))
        self.btn_en.pack(side="left", padx=5)
        
        # Theme Toggle Button
        self.btn_theme = tk.Button(footer_container, text="☀️ / 🌙", bg=C["accent"], fg="#FFFFFF",
                                   activebackground=C["accent2"], activeforeground="#FFFFFF",
                                   font=("Segoe UI", 10), relief="flat", padx=10, pady=5,
                                   cursor="hand2", command=self.on_theme_toggle)
        self.btn_theme.pack(pady=5)
        
        # Version
        self.version_lbl = ttk.Label(footer_container, text="v1.2 Enterprise", 
                                    background=C["accent"], foreground="#BDBDBD",
                                    font=("Segoe UI", 8))
        self.version_lbl.pack(pady=(5, 0))

    def _nav_button(self, text, target):
        btn = tk.Button(self, text=text, 
                       bg=C["accent"], fg="#FFFFFF",
                       activebackground=C["accent2"], activeforeground="#FFFFFF",
                       font=("Segoe UI", 10, "bold"),
                       relief="flat", anchor="w", padx=20, pady=12,
                       cursor="hand2", command=lambda: self.on_nav_change(target))
        btn.pack(fill="x")
        return btn

    def refresh_translations(self):
        """Actualiza los textos traducibles de la barra lateral."""
        self.btn_config.configure(text=t("nav_config"))
        self.btn_results.configure(text=t("nav_results"))
        # Highlight active language button
        from utils.translator import translator
        current = translator.current_lang
        if current == "es":
            self.btn_es.configure(bg=C["accent2"], relief="sunken")
            self.btn_en.configure(bg=C["accent"], relief="flat")
        else:
            self.btn_en.configure(bg=C["accent2"], relief="sunken")
            self.btn_es.configure(bg=C["accent"], relief="flat")
