
import tkinter as tk
from tkinter import ttk
from config import C

def apply_theme(root):
    """Aplica el estilo moderno y minimalista a la aplicación."""
    style = ttk.Style(root)
    
    # Base configuration
    style.theme_use('clam') # Use 'clam' as a base for customization
    
    # Configure Colors
    style.configure('.',
        background=C["bg"],
        foreground=C["text"],
        fieldbackground=C["surface"],
        troughcolor=C["panel"],
        font=("Segoe UI", 10)
    )

    # Sidebar Style
    style.configure('Sidebar.TFrame', background=C["accent"])
    style.configure('Sidebar.TLabel', 
        background=C["accent"], 
        foreground="#FFFFFF",
        font=("Segoe UI", 11, "bold")
    )
    
    # Main Content Area
    style.configure('Main.TFrame', background=C["bg"])
    style.configure('Card.TFrame', background=C["surface"], relief="flat", borderwidth=0)
    
    # Custom Frame for grouping with a subtle border
    style.configure('Group.TLabelframe', background=C["bg"], foreground=C["subtext"], font=("Segoe UI", 9, "bold"))
    style.configure('Group.TLabelframe.Label', background=C["bg"], foreground=C["subtext"])
    
    # Buttons
    style.configure('Accent.TButton', 
        padding=(20, 10), 
        background=C["accent"], 
        foreground="#FFFFFF",
        font=("Segoe UI", 10, "bold")
    )
    style.map('Accent.TButton',
        background=[('active', C["accent2"]), ('disabled', C["border"])]
    )
    
    style.configure('Secondary.TButton', 
        padding=(10, 5), 
        background=C["surface"], 
        foreground=C["text"],
        bordercolor=C["border"],
        font=("Segoe UI", 9)
    )
    style.map('Secondary.TButton',
        background=[('active', C["panel"])]
    )

    # Treeview (Results)
    style.configure('Treeview',
        background=C["surface"],
        foreground=C["text"],
        rowheight=30,
        fieldbackground=C["surface"],
        font=("Segoe UI", 9)
    )
    style.map('Treeview',
        background=[('selected', C["accent"])],
        foreground=[('selected', "#FFFFFF")]
    )
    style.configure('Treeview.Heading',
        background=C["panel"],
        foreground=C["text"],
        font=("Segoe UI", 10, "bold"),
        relief="flat"
    )

    # Notebook (if still used) or Tabs
    style.configure('TNotebook', background=C["bg"], borderwidth=0)
    style.configure('TNotebook.Tab', 
        padding=(15, 5), 
        background=C["panel"], 
        foreground=C["subtext"],
        font=("Segoe UI", 9)
    )
    style.map('TNotebook.Tab',
        background=[('selected', C["surface"])],
        foreground=[('selected', C["accent"])],
        expand=[('selected', [1, 1, 1, 0])]
    )

    # Entry fields
    style.configure('TEntry',
        fieldbackground=C["surface"],
        bordercolor=C["border"],
        lightcolor=C["border"],
        darkcolor=C["border"],
        relief="flat",
        padding=5
    )

    # Progressbar
    style.configure('TProgressbar',
        background=C["accent"],
        troughcolor=C["panel"],
        thickness=4
    )

    return style
