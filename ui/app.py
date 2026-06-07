import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import platform

from config import C
from ui.theme import apply_theme
from ui.components.sidebar import Sidebar
from ui.components.config_view import ConfigView
from ui.components.results_view import ResultsView
from utils.config_manager import load_config, save_config
from utils.logger import logger
from utils.translator import t, translator
from utils.dnd_helper import TkinterDnD, HAS_DND

# Import Core Logic
from core.reports import (
    export_names_report, 
    run_comparison, 
    report_excel, 
    _add_summary_to_report
)

class FileCheckerApp(TkinterDnD.Tk if HAS_DND else tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FileChecker Enterprise")
        self.geometry("1200x850")
        
        # Load Config & Initialize Language/Theme
        self.cfg = load_config()
        self.current_theme = self.cfg.get("theme", "light")
        self.current_lang = self.cfg.get("lang", "es")
        
        # Configure Translator
        translator.set_lang(self.current_lang)
        
        self._init_vars()
        
        # UI Setup
        self._setup_resources()
        self.style = apply_theme(self, self.current_theme)
        self.configure(bg=C["bg"]) # Set root bg to match theme
        
        # Views Cache
        self.views = {}
        self.last_results = None
        self.is_running = False
        self.active_view = "config"
        
        self._build_main_layout()
        self.navigate("config")
        self._center_window()

    def _init_vars(self):
        self.vars = {
            "mode":         tk.StringVar(value=self.cfg.get("mode", "export")),
            "folder":       tk.StringVar(value=self.cfg.get("last_folder", "")),
            "source_excel": tk.StringVar(value=self.cfg.get("last_source_excel", "")),
            "excel":        tk.StringVar(value=self.cfg.get("last_excel", "")),
            "output":       tk.StringVar(value=self.cfg.get("last_output", "")),
            "recursive":    tk.BooleanVar(value=self.cfg.get("recursive", False)),
            "ignore_ext":   tk.BooleanVar(value=self.cfg.get("ignore_ext", False)),
            "ignore_case":  tk.BooleanVar(value=self.cfg.get("ignore_case", True)),
            "preprocess":   tk.BooleanVar(value=self.cfg.get("preprocess", False)),
            "status":       tk.StringVar(value=t("status_ready")),
        }

    def _setup_resources(self):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_path, "assets", "icon.ico")
        try:
            self.iconbitmap(icon_path)
        except Exception:
            pass

    def _build_main_layout(self):
        # Sidebar with nav and i18n/theme callbacks
        self.sidebar = Sidebar(
            self, 
            on_nav_change=self.navigate,
            on_lang_change=self._handle_lang_change,
            on_theme_toggle=self._handle_theme_toggle,
            width=240
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.refresh_translations() # Initialize buttons highlighting
        
        # Main Content Area
        self.container = ttk.Frame(self, style='Main.TFrame')
        self.container.pack(side="right", fill="both", expand=True)
        
        # Header
        self.header = ttk.Frame(self.container, style='Main.TFrame', padding=(30, 20))
        self.header.pack(fill="x")
        self.header_title = ttk.Label(self.header, text=t("header_config"), 
                                     font=("Segoe UI", 20, "bold"), 
                                     background=C["bg"], foreground=C["text"])
        self.header_title.pack(anchor="w")
        
        # View Container
        self.view_area = ttk.Frame(self.container, style='Main.TFrame', padding=(30, 0, 30, 30))
        self.view_area.pack(fill="both", expand=True)
        
        # Footer / Status Bar
        self.footer = ttk.Frame(self.container, style='Card.TFrame', padding=(20, 10))
        self.footer.pack(side="bottom", fill="x")
        
        self.progress = ttk.Progressbar(self.footer, mode="indeterminate", style='TProgressbar')
        self.progress.pack(fill="x", pady=(0, 5))
        
        status_lbl = ttk.Label(self.footer, textvariable=self.vars["status"], 
                               font=("Segoe UI", 9, "italic"), background=C["surface"], foreground=C["cyan"])
        status_lbl.pack(side="left")

    def navigate(self, target):
        """Maneja la navegación entre vistas."""
        if self.is_running and target != "results":
            pass

        # Hide current views
        for widget in self.view_area.winfo_children():
            widget.pack_forget()

        self.active_view = target

        if target == "config":
            self.header_title.configure(text=t("header_config"))
            if "config" not in self.views:
                self.views["config"] = ConfigView(self.view_area, self.vars, on_run=self._handle_run)
            self.views["config"].pack(fill="both", expand=True)
            self.views["config"].refresh_theme() # Ensure themes match if toggled while hidden
            
        elif target == "results":
            self.header_title.configure(text=t("header_results"))
            if "results" not in self.views:
                self.views["results"] = ResultsView(self.view_area, on_export=self._handle_export)
            self.views["results"].pack(fill="both", expand=True)

    def _handle_run(self):
        if self.is_running: return
        
        # Validation
        mode = self.vars["mode"].get()
        if mode in ["export", "compare"]:
            folder = self.vars["folder"].get().strip()
            if not folder or not os.path.isdir(folder):
                messagebox.showerror(t("err_val_title"), t("err_val_folder"))
                return
        
        if mode == "compare_excel":
            source = self.vars["source_excel"].get().strip()
            if not source or not os.path.isfile(source):
                messagebox.showerror(t("err_val_title"), t("err_val_source_excel"))
                return
        
        if mode in ["compare", "compare_excel"]:
            excel = self.vars["excel"].get().strip()
            if not excel or not os.path.isfile(excel):
                messagebox.showerror(t("err_val_title"), t("err_val_master_excel"))
                return

        self._save_state()
        self._start_task(self._task_processing)

    def _task_processing(self):
        try:
            logger.info("Iniciando procesamiento de tarea...")
            mode = self.vars["mode"].get()
            ts  = datetime.now().strftime("%Y-%m-%d_%H-%M")
            rec = self.vars["recursive"].get()
            iex = self.vars["ignore_ext"].get()
            ica = self.vars["ignore_case"].get()
            pre = self.vars["preprocess"].get()
            out_dir = self.vars["output"].get().strip()
            
            source_path = self.vars["source_excel"].get() if mode == "compare_excel" else self.vars["folder"].get()

            if mode == "export":
                filename = f"Reporte_Nombres_{ts}.xlsx"
                out_path = os.path.join(out_dir, filename) if out_dir else filename
                out = export_names_report(source_path, rec, iex, pre, ts, output_path=out_path)
                
                self.after(0, lambda: self._on_task_complete(t("status_complete"), out))
            else:
                excel_master = self.vars["excel"].get()
                results = run_comparison(
                    source_path, excel_master, 
                    rec, iex, ica, pre, 
                    is_excel_source=(mode == "compare_excel")
                )
                self.last_results = results
                self.after(0, lambda: self._update_results_and_navigate(results))

        except Exception as e:
            logger.error(f"Error procesando tarea principal: {str(e)}", exc_info=True)
            self.after(0, lambda: self._on_task_error(str(e)))

    def _update_results_and_navigate(self, results):
        if "results" not in self.views:
            self.navigate("results")
        
        self.views["results"].update_results(len(results[0]), results[1], results[2], results[3])
        self.navigate("results")
        self._on_task_complete(t("msg_success_compare"))

    def _handle_export(self):
        if not self.last_results: return
        self._start_task(self._task_export)

    def _task_export(self):
        try:
            logger.info("Iniciando exportación de resultados...")
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
            out_dir = self.vars["output"].get().strip()
            filename = f"Reporte_Comparacion_{ts}.xlsx"
            out_path = os.path.join(out_dir, filename) if out_dir else filename
            
            master, found, missing, extra = self.last_results
            report_excel(out_path, found, missing, extra, master_count=len(master))
            
            self.after(0, lambda: self._on_task_complete(t("msg_success_exported", path=out_path), out_path))
        except Exception as e:
            logger.error(f"Error exportando reporte: {str(e)}", exc_info=True)
            self.after(0, lambda: self._on_task_error(str(e)))

    def _start_task(self, target):
        self.is_running = True
        self.progress.start(10)
        self.vars["status"].set(t("status_processing"))
        if "config" in self.views: self.views["config"].run_btn.state(['disabled'])
        threading.Thread(target=target, daemon=True).start()

    def _on_task_complete(self, msg, file_to_open=None):
        self.is_running = False
        self.progress.stop()
        self.vars["status"].set(t("status_complete"))
        if "config" in self.views: self.views["config"].run_btn.state(['!disabled'])
        
        if file_to_open:
            if messagebox.askyesno(t("msg_success_title"), t("msg_success_export", path=file_to_open)):
                self._open_file(file_to_open)
        else:
            messagebox.showinfo(t("msg_success_title"), msg)

    def _on_task_error(self, error_msg):
        self.is_running = False
        self.progress.stop()
        self.vars["status"].set(t("status_error", error=error_msg))
        if "config" in self.views: self.views["config"].run_btn.state(['!disabled'])
        
        msg = t("msg_err_desc", error=error_msg)
        if messagebox.askyesno(t("msg_err_title"), msg):
            self._open_file("filemaster.log")

    def _open_file(self, path):
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')
        except Exception as e:
            messagebox.showwarning("Aviso", f"No se pudo abrir el archivo automáticamente: {e}")

    def _handle_lang_change(self, lang):
        if lang == self.current_lang:
            return
        self.current_lang = lang
        translator.set_lang(lang)
        
        # Refresh widgets texts
        self.sidebar.refresh_translations()
        if "config" in self.views:
            self.views["config"].refresh_translations()
        if "results" in self.views:
            self.views["results"].refresh_translations()
            
        self._refresh_app_translations()
        self._save_state()

    def _handle_theme_toggle(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        apply_theme(self, self.current_theme)
        
        # Update app colors
        self.configure(bg=C["bg"])
        self.header_title.configure(background=C["bg"], foreground=C["text"])
        
        # Refresh non-ttk parts of widgets
        self.sidebar.refresh_theme()
        if "config" in self.views:
            self.views["config"].refresh_theme()
            
        self._save_state()

    def _refresh_app_translations(self):
        # Update dynamic header title
        if self.active_view == "config":
            self.header_title.configure(text=t("header_config"))
        else:
            self.header_title.configure(text=t("header_results"))
            
        # Update status bar label if it represents ready/processing
        status_val = self.vars["status"].get()
        if status_val in ["Sistema Listo", "System Ready"]:
            self.vars["status"].set(t("status_ready"))
        elif status_val in ["Procesando operación... por favor espere.", "Processing operation... please wait."]:
            self.vars["status"].set(t("status_processing"))
        elif status_val in ["✔ Operación finalizada.", "✔ Operation finished."]:
            self.vars["status"].set(t("status_complete"))

    def _save_state(self):
        save_config({
            "mode":              self.vars["mode"].get(),
            "last_folder":       self.vars["folder"].get(),
            "last_source_excel": self.vars["source_excel"].get(),
            "last_excel":        self.vars["excel"].get(),
            "last_output":       self.vars["output"].get(),
            "recursive":         self.vars["recursive"].get(),
            "ignore_ext":        self.vars["ignore_ext"].get(),
            "ignore_case":       self.vars["ignore_case"].get(),
            "preprocess":        self.vars["preprocess"].get(),
            "lang":              self.current_lang,
            "theme":             self.current_theme
        })

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f'+{x}+{y}')

if __name__ == "__main__":
    app = FileCheckerApp()
    app.mainloop()
