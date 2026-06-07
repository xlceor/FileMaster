import tkinter as tk
from tkinter import ttk
from config import C

# Define Light and Dark Palettes
PALETTES = {
    "light": {
        "bg":       "#F8F9FA",
        "surface":  "#FFFFFF",
        "panel":    "#E9ECEF",
        "accent":   "#5E35B1",
        "accent2":  "#7E57C2",
        "green":    "#2E7D32",
        "red":      "#C62828",
        "yellow":   "#F9A825",
        "cyan":     "#00838F",
        "text":     "#212529",
        "subtext":  "#6C757D",
        "border":   "#DEE2E6",
    },
    "dark": {
        "bg":       "#121212",
        "surface":  "#1E1E1E",
        "panel":    "#2D2D2D",
        "accent":   "#7E57C2",
        "accent2":  "#9575CD",
        "green":    "#81C784",
        "red":      "#E57373",
        "yellow":   "#FBC02D",
        "cyan":     "#00ACC1",
        "text":     "#E0E0E0",
        "subtext":  "#9E9E9E",
        "border":   "#333333",
    }
}

def apply_theme(root, mode: str = "light"):
    """Aplica y reconfigura los estilos TTK modernos basados en el tema activo (light/dark)."""
    style = ttk.Style(root)
    
    # Force clam theme as base for custom styling
    try:
        style.theme_use('clam')
    except Exception:
        pass
        
    # Update global config color dictionary C in-place
    palette = PALETTES.get(mode, PALETTES["light"])
    for k, v in palette.items():
        C[k] = v
        
    # Configure base elements
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
    
    # Main Content Area & Card Frames
    style.configure('Main.TFrame', background=C["bg"])
    style.configure('Card.TFrame', background=C["surface"], relief="flat", borderwidth=0)
    
    # Custom Frame for grouping with a subtle border
    style.configure('Group.TLabelframe', background=C["bg"], foreground=C["subtext"], font=("Segoe UI", 9, "bold"))
    style.configure('Group.TLabelframe.Label', background=C["bg"], foreground=C["subtext"])
    
    # Accent Buttons (Primary)
    style.configure('Accent.TButton', 
        padding=(20, 10), 
        background=C["accent"], 
        foreground="#FFFFFF",
        font=("Segoe UI", 10, "bold")
    )
    style.map('Accent.TButton',
        background=[('active', C["accent2"]), ('disabled', C["border"])],
        foreground=[('disabled', C["subtext"])]
    )
    
    # Secondary Buttons
    style.configure('Secondary.TButton', 
        padding=(10, 5), 
        background=C["surface"], 
        foreground=C["text"],
        bordercolor=C["border"],
        font=("Segoe UI", 9)
    )
    style.map('Secondary.TButton',
        background=[('active', C["panel"])],
        foreground=[('active', C["text"])]
    )

    # Treeview (Results Tables)
    style.configure('Treeview',
        background=C["surface"],
        foreground=C["text"],
        rowheight=30,
        fieldbackground=C["surface"],
        font=("Segoe UI", 9),
        borderwidth=0
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

    # Tabs (Notebook)
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
        foreground=C["text"],
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
