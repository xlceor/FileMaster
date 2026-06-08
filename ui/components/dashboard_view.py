import tkinter as tk
from tkinter import ttk
from config import C
from utils.translator import t

class DashboardView(ttk.Frame):
    def __init__(self, master, results_data=None, **kwargs):
        super().__init__(master, style='Main.TFrame', **kwargs)
        self.results_data = results_data
        
        # Elements to update dynamically
        self.metric_cards = []
        self.metric_values = {}
        self.chart_canvases = {}
        self.chart_titles = []
        
        self._build_ui()

    def _build_ui(self):
        # Clear existing elements if any (for rebuilds)
        for widget in self.winfo_children():
            widget.destroy()
            
        self.metric_cards.clear()
        self.metric_values.clear()
        self.chart_canvases.clear()
        self.chart_titles.clear()

        # Canvas with scrollbar for vertical responsiveness
        self.scroll_canvas = tk.Canvas(self, bg=C["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.scroll_canvas.yview)
        self.container = ttk.Frame(self.scroll_canvas, style='Main.TFrame', padding=10)

        self.container.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        )
        self.scroll_canvas.create_window((0, 0), window=self.container, anchor="nw", width=880)
        self.scroll_canvas.configure(yscrollcommand=scrollbar.set)

        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Check if we have data to display
        if not self.results_data or not any(self.results_data):
            self._build_no_data_state()
            return

        self._build_dashboard_state()

    def _build_no_data_state(self):
        card = ttk.Frame(self.container, style='Card.TFrame', padding=40)
        card.pack(fill="both", expand=True, pady=40, padx=20)


        no_data_lbl = ttk.Label(card, text=t("db_no_data"), font=("Segoe UI", 12),
                                background=C["surface"], foreground=C["subtext"],
                                wraplength=600, justify="center")
        no_data_lbl.pack()

    def _build_dashboard_state(self):
        master_dict, found_dict, missing_dict, extra_dict = self.results_data
        
        total_expected = len(master_dict)
        total_found = len(found_dict)
        total_missing = len(missing_dict)
        total_extra = len(extra_dict)

        # 1. Row of Metric Cards
        metrics_frame = ttk.Frame(self.container, style='Main.TFrame')
        metrics_frame.pack(fill="x", pady=(0, 20))
        metrics_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="group1")

        metrics_config = [
            ("db_summary_expected", total_expected, C["text"], 0),
            ("db_summary_found", total_found, C["green"], 1),
            ("db_summary_missing", total_missing, C["red"], 2),
            ("db_summary_extra", total_extra, C["yellow"], 3)
        ]

        for key, val, color, col_idx in metrics_config:
            card = ttk.Frame(metrics_frame, style='Card.TFrame', padding=15)
            card.grid(row=0, column=col_idx, padx=5, sticky="nsew")
            self.metric_cards.append(card)

            # Title
            title_lbl = ttk.Label(card, text=t(key), font=("Segoe UI", 9, "bold"),
                                  background=C["surface"], foreground=color)
            title_lbl.pack(anchor="w", pady=(0, 5))
            self.metric_values[key] = (title_lbl, val)

            # Value
            val_lbl = ttk.Label(card, text=f"{val:,}", font=("Segoe UI", 24, "bold"),
                                background=C["surface"], foreground=C["text"])
            val_lbl.pack(anchor="w")

        # 2. Row of Charts (Donut + Bar Chart)
        charts_frame = ttk.Frame(self.container, style='Main.TFrame')
        charts_frame.pack(fill="both", expand=True)
        charts_frame.columnconfigure((0, 1), weight=1, uniform="group2")

        # Donut Frame
        donut_card = ttk.Frame(charts_frame, style='Card.TFrame', padding=15)
        donut_card.grid(row=0, column=0, padx=5, sticky="nsew")
        self.metric_cards.append(donut_card)

        donut_title = ttk.Label(donut_card, text=t("db_completion_rate"), font=("Segoe UI", 11, "bold"),
                                background=C["surface"], foreground=C["accent"])
        donut_title.pack(anchor="w", pady=(0, 10))
        self.chart_titles.append((donut_title, "db_completion_rate"))

        self.donut_canvas = tk.Canvas(donut_card, width=320, height=280, bg=C["surface"], highlightthickness=0)
        self.donut_canvas.pack(fill="both", expand=True)
        self.chart_canvases["donut"] = self.donut_canvas

        # Bar Frame
        bar_card = ttk.Frame(charts_frame, style='Card.TFrame', padding=15)
        bar_card.grid(row=0, column=1, padx=5, sticky="nsew")
        self.metric_cards.append(bar_card)

        bar_title = ttk.Label(bar_card, text=t("db_distribution"), font=("Segoe UI", 11, "bold"),
                              background=C["surface"], foreground=C["accent"])
        bar_title.pack(anchor="w", pady=(0, 10))
        self.chart_titles.append((bar_title, "db_distribution"))

        self.bar_canvas = tk.Canvas(bar_card, width=320, height=280, bg=C["surface"], highlightthickness=0)
        self.bar_canvas.pack(fill="both", expand=True)
        self.chart_canvases["bar"] = self.bar_canvas

        # Draw content
        self._draw_charts()

    def _draw_charts(self):
        if not self.results_data:
            return
            
        master_dict, found_dict, missing_dict, extra_dict = self.results_data
        total_expected = len(master_dict)
        total_found = len(found_dict)
        total_missing = len(missing_dict)
        total_extra = len(extra_dict)

        # ----------------- DRAW DONUT CHART -----------------
        canvas = self.donut_canvas
        canvas.delete("all")
        
        # Center coordinates
        cx, cy = 160, 110
        r = 80
        
        # Calculations
        tot = total_found + total_missing
        pct_found = (total_found / tot * 100) if tot > 0 else 0
        pct_missing = (total_missing / tot * 100) if tot > 0 else 0

        # Donut Slices
        if tot == 0:
            # Draw gray empty ring
            canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="", outline=C["border"], width=15)
            canvas.create_text(cx, cy, text="0%", font=("Segoe UI", 22, "bold"), fill=C["subtext"])
        else:
            # Found Arc (green)
            span_found = 360 * (total_found / tot)
            if span_found > 0:
                canvas.create_arc(cx - r, cy - r, cx + r, cy + r, start=90, extent=-span_found,
                                  fill=C["green"], outline="")
            
            # Missing Arc (red)
            span_missing = 360 * (total_missing / tot)
            if span_missing > 0:
                canvas.create_arc(cx - r, cy - r, cx + r, cy + r, start=90 - span_found, extent=-span_missing,
                                  fill=C["red"], outline="")

            # Center Hole (to make it a donut)
            r_hole = 55
            canvas.create_oval(cx - r_hole, cy - r_hole, cx + r_hole, cy + r_hole, fill=C["surface"], outline="")
            
            # Center Percentage Text
            canvas.create_text(cx, cy, text=f"{pct_found:.1f}%", font=("Segoe UI", 20, "bold"), fill=C["text"])
        
        # Legends
        ly = 215
        # Legend Found
        canvas.create_rectangle(40, ly, 52, ly + 12, fill=C["green"], outline="")
        canvas.create_text(60, ly + 6, text=t("db_found_percent", percent=f"{pct_found:.1f}"),
                           font=("Segoe UI", 9), fill=C["text"], anchor="w")
        
        # Legend Missing
        canvas.create_rectangle(180, ly, 192, ly + 12, fill=C["red"], outline="")
        canvas.create_text(200, ly + 6, text=t("db_missing_percent", percent=f"{pct_missing:.1f}"),
                           font=("Segoe UI", 9), fill=C["text"], anchor="w")

        # ----------------- DRAW BAR CHART -----------------
        canvas_bar = self.bar_canvas
        canvas_bar.delete("all")

        # Graph parameters
        gx, gy = 45, 20
        gw, gh = 250, 180
        
        # Draw dynamic horizontal grid lines
        max_val = max(total_found, total_missing, total_extra)
        if max_val == 0: max_val = 1
        
        # Round max_val up to something nice
        import math
        magnitude = 10 ** int(math.log10(max_val)) if max_val > 0 else 1
        if magnitude == 0: magnitude = 1
        nice_max = math.ceil(max_val / magnitude) * magnitude
        if nice_max == 0: nice_max = 1
        
        # Draw Grid Lines
        grid_steps = 4
        for idx in range(grid_steps + 1):
            val_step = int((nice_max / grid_steps) * idx)
            y_step = gy + gh - (gh * (val_step / nice_max))
            canvas_bar.create_line(gx, y_step, gx + gw, y_step, fill=C["border"], dash=(2, 2))
            canvas_bar.create_text(gx - 8, y_step, text=f"{val_step}", font=("Segoe UI", 8),
                                   fill=C["subtext"], anchor="e")

        # Bar specs
        bars = [
            (total_found, C["green"], t("results_col_found")),
            (total_missing, C["red"], t("results_col_missing")),
            (total_extra, C["yellow"], t("results_col_extra"))
        ]
        
        num_bars = len(bars)
        bar_gap = 25
        total_gaps_width = bar_gap * (num_bars + 1)
        bar_width = (gw - total_gaps_width) / num_bars

        # Draw Bars
        for idx, (b_val, b_color, b_label) in enumerate(bars):
            bx = gx + bar_gap + idx * (bar_width + bar_gap)
            bar_h = gh * (b_val / nice_max)
            by = gy + gh - bar_h
            
            # Draw bar rectangle
            canvas_bar.create_rectangle(bx, by, bx + bar_width, gy + gh, fill=b_color, outline="")
            
            # Value on top
            canvas_bar.create_text(bx + bar_width / 2, by - 8, text=f"{b_val}",
                                   font=("Segoe UI", 9, "bold"), fill=C["text"])
            
            # X Axis Label
            # Wrap text to avoid long label truncation
            short_label = b_label if len(b_label) < 12 else b_label[:10] + "..."
            canvas_bar.create_text(bx + bar_width / 2, gy + gh + 12, text=short_label,
                                   font=("Segoe UI", 8, "bold"), fill=C["text"])

    def update_data(self, results_data):
        """Updates the results data and completely rebuilds the UI to reflect changes."""
        self.results_data = results_data
        self._build_ui()

    def refresh_translations(self):
        """Updates all translated strings dynamically."""
        # Re-build UI to update texts and metrics properly
        self._build_ui()

    def refresh_theme(self):
        """Updates all theme colors for canvas background and shapes."""
        self.configure(style='Main.TFrame')
        self.scroll_canvas.configure(bg=C["bg"])
        
        # Re-build and redraw charts to ensure colors match theme completely
        self._build_ui()
