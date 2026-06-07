
import tkinter as tk
from tkinter import ttk
from config import C

class SectionHeader(ttk.Label):
    def __init__(self, master, text, **kwargs):
        super().__init__(master, text=text.upper(), 
                         font=("Segoe UI", 8, "bold"), 
                         foreground=C["subtext"],
                         padding=(0, 10, 0, 5),
                         **kwargs)

class Card(ttk.Frame):
    def __init__(self, master, padding=15, **kwargs):
        super().__init__(master, style='Card.TFrame', **kwargs)
        # Note: Card style needs to be defined in theme.py or here
        self.inner = ttk.Frame(self, padding=padding, style='Main.TFrame')
        self.inner.pack(fill="both", expand=True)

class PathPicker(ttk.Frame):
    def __init__(self, master, label, variable, browse_func, placeholder="", **kwargs):
        super().__init__(master, style='Main.TFrame', **kwargs)
        self.variable = variable
        self.browse_func = browse_func
        
        ttk.Label(self, text=label, font=("Segoe UI", 9), 
                  background=C["bg"], foreground=C["text"]).pack(anchor="w", pady=(0, 2))
        
        row = ttk.Frame(self, style='Main.TFrame')
        row.pack(fill="x")
        
        self.entry = ttk.Entry(row, textvariable=variable, style='TEntry')
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn = ttk.Button(row, text="Buscar...", style='Secondary.TButton', 
                             command=browse_func)
        self.btn.pack(side="right")

class ModernCheck(ttk.Checkbutton):
    def __init__(self, master, text, variable, **kwargs):
        super().__init__(master, text=text, variable=variable, **kwargs)
        # Standard TTK checkbutton is already styled by our theme
