import tkinter as tk
from utils.logger import logger

# Try importing and initializing tkinterdnd2 with fallback
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    
    # Dry-run check: verify if the native tkdnd Tcl library can actually be loaded
    # interpreter uses incompatible stubs mechanism is caught here!
    root_check = tk.Tk()
    try:
        root_check.tk.call('package', 'require', 'tkdnd')
        HAS_DND = True
        logger.info("tkinterdnd2 y biblioteca tkdnd nativa cargados con éxito. Soporte de arrastrar y soltar activado.")
    except Exception as tcl_err:
        HAS_DND = False
        TkinterDnD = None
        DND_FILES = None
        logger.warning(f"La biblioteca native tkdnd no es compatible con este intérprete Tcl/Tk: {str(tcl_err)}. Desactivando arrastrar y soltar.")
    finally:
        root_check.destroy()
        
except Exception as e:
    TkinterDnD = None
    DND_FILES = None
    HAS_DND = False
    logger.warning(f"No se pudo cargar tkinterdnd2: {str(e)}. Se usará entrada tradicional de archivos.")


def parse_dnd_path(data: str) -> str:
    """Sanea la ruta de archivo recibida desde DnD.
    En macOS, los nombres con espacios pueden venir entre llaves, p.ej. {/path/to/my file.xlsx}
    """
    path = data.strip()
    if path.startswith('{') and path.endswith('}'):
        path = path[1:-1]
    return path


def make_drop_target(widget, variable, is_folder: bool = False):
    """Registra un widget entry/label como destino de arrastrar y soltar si DnD está disponible y cargado."""
    if not HAS_DND:
        return
        
    try:
        widget.drop_target_register(DND_FILES)
        
        def handle_drop(event):
            clean_path = parse_dnd_path(event.data)
            variable.set(clean_path)
            logger.debug(f"Arrastrado y soltado: {clean_path} en widget {widget}")
            
        widget.dnd_bind('<<Drop>>', handle_drop)
    except Exception as e:
        logger.error(f"Error registrando drop target en widget {widget}: {e}")
