
import tkinter as tk
from tkinter import ttk
from config import C

class Sidebar(ttk.Frame):
    def __init__(self, master, on_nav_change, **kwargs):
        super().__init__(master, style='Sidebar.TFrame', **kwargs)
        self.on_nav_change = on_nav_change
        self._build_ui()

    def _build_ui(self):
        # Logo / Title
        header = ttk.Label(self, text="📁 FileChecker", style='Sidebar.TLabel', padding=(20, 30))
        header.pack(fill="x")
        
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20, pady=10)

        # Nav Buttons
        self.btn_config = self._nav_button("⚙  Configuración", "config")
        self.btn_results = self._nav_button("📊  Resultados", "results")
        
        # Footer / Version
        footer = ttk.Label(self, text="v1.2 Enterprise", 
                          background=C["accent"], foreground="#BDBDBD",
                          font=("Segoe UI", 8))
        footer.pack(side="bottom", pady=20)

    def _nav_button(self, text, target):
        btn = tk.Button(self, text=text, 
                       bg=C["accent"], fg="#FFFFFF",
                       activebackground=C["accent2"], activeforeground="#FFFFFF",
                       font=("Segoe UI", 10, "bold"),
                       relief="flat", anchor="w", padx=20, pady=12,
                       cursor="hand2", command=lambda: self.on_nav_change(target))
        btn.pack(fill="x")
        return btn
