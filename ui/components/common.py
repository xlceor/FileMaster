import tkinter as tk
from tkinter import ttk
from config import C
from utils.translator import t

class ToolTip:
    """Clase para mostrar tooltips flotantes elegantes con soporte de traducción dinámica."""
    def __init__(self, widget, text_key):
        self.widget = widget
        self.text_key = text_key
        self.tip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hide()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(400, self.show)

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show(self):
        if self.tip_window or not self.text_key:
            return
        
        # Calculate tooltip position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True) # Remove windows frames
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=t(self.text_key), justify='left',
                         background="#212529", fg="#FFFFFF", relief='flat',
                         font=("Segoe UI", 9), padx=8, pady=5)
        label.pack(ipadx=1)

    def hide(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


class SectionHeader(ttk.Label):
    def __init__(self, master, text_key, **kwargs):
        self.text_key = text_key
        super().__init__(master, text=t(self.text_key).upper(), 
                         font=("Segoe UI", 9, "bold"), 
                         foreground=C["subtext"],
                         padding=(0, 10, 0, 5),
                         **kwargs)

    def refresh_translations(self):
        self.configure(text=t(self.text_key).upper())


class Card(ttk.Frame):
    def __init__(self, master, padding=15, **kwargs):
        super().__init__(master, style='Card.TFrame', **kwargs)
        self.inner = ttk.Frame(self, padding=padding, style='Main.TFrame')
        self.inner.pack(fill="both", expand=True)


class PathPicker(ttk.Frame):
    def __init__(self, master, label_key, variable, browse_func, **kwargs):
        super().__init__(master, style='Main.TFrame', **kwargs)
        self.label_key = label_key
        self.variable = variable
        self.browse_func = browse_func
        
        self.lbl = ttk.Label(self, text=t(label_key), font=("Segoe UI", 9), 
                             background=C["bg"], foreground=C["text"])
        self.lbl.pack(anchor="w", pady=(0, 2))
        
        row = ttk.Frame(self, style='Main.TFrame')
        row.pack(fill="x")
        
        self.entry = ttk.Entry(row, textvariable=variable, style='TEntry')
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Integrate Drag and Drop support
        from utils.dnd_helper import make_drop_target
        make_drop_target(self.entry, variable)
        
        self.btn = ttk.Button(row, text=t("btn_browse"), style='Secondary.TButton', 
                              command=browse_func)
        self.btn.pack(side="right")

    def refresh_translations(self):
        self.lbl.configure(text=t(self.label_key))
        self.btn.configure(text=t("btn_browse"))


class ModernCheck(ttk.Checkbutton):
    def __init__(self, master, text_key, variable, tooltip_key=None, **kwargs):
        self.text_key = text_key
        super().__init__(master, text=t(text_key), variable=variable, **kwargs)
        if tooltip_key:
            ToolTip(self, tooltip_key)

    def refresh_translations(self):
        self.configure(text=t(self.text_key))
