"""
Seasonal Tab module.
Provides full multi-season resource tracking, modern bulk season editor,
CSV import/export, and interactive Matplotlib resource growth analytics.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Any, Dict, List, Optional

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.ticker as mticker
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from constants import (
    SEASONAL_RESOURCES, parse_resource_value, format_resource_value
)
from ui_components import CardFrame, ModernButton, ModernEntry, ModernScrollbar, setup_treeview_striping


class SeasonalTab(tk.Frame):
    """Encapsulates Seasonal progression management, bulk editing, and resource analytics charts."""

    def __init__(self, parent: tk.Widget, app: Any):
        super().__init__(parent, bg=app.theme.bg)
        self.app = app
        self.db = app.db
        self.theme = app.theme

        # State Variables
        self.seasonal_season_var = tk.StringVar()
        self.seasonal_entry_widgets: Dict[str, ModernEntry] = {}
        self.active_edit_season: Optional[int] = None

        # Analytics Graph State
        self.graph_resource_var = tk.StringVar(value="Gold")
        self.graph_type_var = tk.StringVar(value="Line Chart")
        self.fig: Optional[Any] = None
        self.canvas_plot: Optional[Any] = None

        self._build_ui()

    def _build_ui(self) -> None:
        # Sub-tab Navigation Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(6, 10))

        self.tab_data = tk.Frame(self.notebook, bg=self.theme.bg)
        self.tab_graphs = tk.Frame(self.notebook, bg=self.theme.bg)

        self.notebook.add(self.tab_data, text="Data & Bulk Editor")
        self.notebook.add(self.tab_graphs, text="Resource Analytics / Graphs")

        self._build_data_ui()
        self._build_graphs_ui()

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

    # ==========================================
    # --- SUB-TAB 1: DATA & BULK EDITOR ---
    # ==========================================

    def _build_data_ui(self) -> None:
        # Top Controls Card
        card_controls = CardFrame(self.tab_data, self.theme, title="Seasonal Controls & Actions", header_color=self.theme.blue, padding=6)
        card_controls.pack(fill="x", padx=10, pady=(8, 4))

        ctrl_row = tk.Frame(card_controls.body, bg=self.theme.surface)
        ctrl_row.pack(fill="x", pady=2)

        tk.Label(
            ctrl_row, text="Active Season:", font=self.theme.fonts["body_bold"],
            bg=self.theme.surface, fg=self.theme.fg
        ).pack(side="left", padx=(4, 6))

        self.cmb_seasonal_season = ttk.Combobox(
            ctrl_row, textvariable=self.seasonal_season_var, state="readonly", width=8
        )
        self.cmb_seasonal_season.pack(side="left", padx=(0, 12))
        self.cmb_seasonal_season.bind("<<ComboboxSelected>>", lambda _e: self._on_season_select())

        ModernButton(ctrl_row, self.theme, text="➕ Create New Season", variant="success", command=self.create_new_season).pack(side="left", padx=3)
        ModernButton(ctrl_row, self.theme, text="✏️ Bulk Edit Season", variant="primary", command=self.open_bulk_edit_ui).pack(side="left", padx=3)
        ModernButton(ctrl_row, self.theme, text="🗑️ Clear Season Data", variant="danger", command=self.clear_season_data).pack(side="left", padx=3)
        ModernButton(ctrl_row, self.theme, text="🧹 Purge Empty Seasons", variant="neutral", command=self.purge_empty_seasons).pack(side="left", padx=3)
        ModernButton(ctrl_row, self.theme, text="📥 Import CSV", variant="neutral", command=self.import_seasonal_csv).pack(side="left", padx=3)
        ModernButton(ctrl_row, self.theme, text="📤 Export CSV", variant="neutral", command=self.export_seasonal_csv).pack(side="left", padx=3)

        self.status_label = tk.Label(
            card_controls.body, text="", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.green
        )
        self.status_label.pack(anchor="w", padx=6, pady=(4, 0))

        # Dynamic Bulk Edit Container (Card-based UI)
        self.edit_container = tk.Frame(self.tab_data, bg=self.theme.bg)
        self.edit_container.pack(fill="x", padx=10, pady=(0, 4))

        # Seasonal Data Table Card
        table_card = CardFrame(self.tab_data, self.theme, padding=2)
        table_card.pack(fill="both", expand=True, padx=10, pady=(4, 8))

        scrollbar_y = ModernScrollbar(table_card.body, self.theme)
        scrollbar_y.pack(side="right", fill="y")

        scrollbar_x = ModernScrollbar(table_card.body, self.theme, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")

        self.tree_seasonal = ttk.Treeview(
            table_card.body,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        scrollbar_y.config(command=self.tree_seasonal.yview)
        scrollbar_x.config(command=self.tree_seasonal.xview)
        self.tree_seasonal.pack(fill="both", expand=True)

        setup_treeview_striping(self.tree_seasonal, self.theme)

        self._update_season_selector()
        self.load_seasonal_data()

    def show_status(self, message: str, color: Optional[str] = None) -> None:
        """Displays user feedback in the Seasonal status bar."""
        self.status_label.config(text=message, fg=color or self.theme.green)

    def _get_existing_seasons(self) -> List[int]:
        return self.db.get_existing_seasons(auto_cleanup=True)

    def _update_season_selector(self) -> None:
        """Updates the season combobox with existing seasons."""
        seasons = self._get_existing_seasons()
        self.cmb_seasonal_season['values'] = seasons
        if seasons:
            if not self.seasonal_season_var.get() or int(self.seasonal_season_var.get()) not in seasons:
                self.seasonal_season_var.set(str(seasons[-1]))
        else:
            self.seasonal_season_var.set('')

    def _on_season_select(self) -> None:
        if self.active_edit_season is not None:
            self.open_bulk_edit_ui()

    def create_new_season(self) -> None:
        """Creates a new, incremental season column in SQLite and switches to it."""
        try:
            next_num = self.db.create_new_season()
            self.show_status(f"Season {next_num} created successfully!", self.theme.green)
            self._update_season_selector()
            self.seasonal_season_var.set(str(next_num))
            self.load_seasonal_data()
            self.open_bulk_edit_ui()
        except Exception as e:
            self.show_status(f"Error creating season: {e}", self.theme.red)

    def open_bulk_edit_ui(self) -> None:
        """Renders an improved, clean card-based bulk editor for the selected season."""
        season_str = self.seasonal_season_var.get()
        if not season_str:
            self.show_status("Please select or create a season to edit.", self.theme.yellow)
            return

        season_num = int(season_str)
        self.active_edit_season = season_num

        for w in self.edit_container.winfo_children():
            w.destroy()
        self.seasonal_entry_widgets.clear()

        edit_card = CardFrame(
            self.edit_container,
            self.theme,
            title=f"Bulk Editor — Season {season_num}",
            header_color=self.theme.yellow,
            padding=8
        )
        edit_card.pack(fill="x", pady=4)

        # Query existing data for this season
        col_name = f"season_{season_num}"
        self.db.ensure_season_column_exists(col_name)
        rows = self.db.fetch_all(f"SELECT resource, {col_name} FROM seasonal_data ORDER BY resource ASC")
        current_data = dict(rows)

        grid_frame = tk.Frame(edit_card.body, bg=self.theme.surface)
        grid_frame.pack(fill="x", pady=4)

        num_cols = 4
        for i, resource in enumerate(SEASONAL_RESOURCES):
            row_idx, col_idx = divmod(i, num_cols)

            tile = tk.Frame(
                grid_frame,
                bg=self.theme.bg,
                bd=1,
                relief="groove",
                padx=8,
                pady=6
            )
            tile.grid(row=row_idx, column=col_idx, padx=4, pady=4, sticky="nsew")

            tk.Label(
                tile,
                text=f"● {resource}",
                font=self.theme.fonts["small_bold"],
                bg=self.theme.bg,
                fg=self.theme.blue
            ).pack(anchor="w", pady=(0, 2))

            entry = ModernEntry(tile, self.theme, width=16)
            entry.pack(fill="x")

            curr_val = current_data.get(resource, "-")
            if curr_val and curr_val != "-":
                entry.insert(0, str(curr_val))

            self.seasonal_entry_widgets[resource] = entry

        for c in range(num_cols):
            grid_frame.columnconfigure(c, weight=1)

        # Action Buttons for Editor
        btn_bar = tk.Frame(edit_card.body, bg=self.theme.surface)
        btn_bar.pack(fill="x", pady=(8, 2))

        ModernButton(
            btn_bar, self.theme, text=f"💾 Save Season {season_num} Data",
            variant="success", command=self._save_bulk_edit_data
        ).pack(side="left", padx=4)

        ModernButton(
            btn_bar, self.theme, text="Cancel",
            variant="neutral", command=self._cancel_bulk_edit
        ).pack(side="left", padx=4)

    def _save_bulk_edit_data(self) -> None:
        """Saves all values from the bulk editor to the active season column."""
        if self.active_edit_season is None:
            return

        try:
            data = {}
            for res_name, entry_widget in self.seasonal_entry_widgets.items():
                val = entry_widget.get().strip()
                data[res_name] = val if val else "-"

            self.db.save_seasonal_bulk(self.active_edit_season, data)
            self._update_season_selector()
            self.load_seasonal_data()
            self.show_status(f"Season {self.active_edit_season} data saved successfully!", self.theme.green)

            # Close edit card
            self._cancel_bulk_edit()
            self.update_graphs()
        except Exception as e:
            self.show_status(f"Error saving data: {e}", self.theme.red)

    def _cancel_bulk_edit(self) -> None:
        """Closes the bulk edit panel and cleans up any abandoned empty seasons."""
        for w in self.edit_container.winfo_children():
            w.destroy()
        self.seasonal_entry_widgets.clear()
        self.active_edit_season = None
        self.db.cleanup_empty_seasons()
        self._update_season_selector()
        self.load_seasonal_data()

    def purge_empty_seasons(self) -> None:
        """Removes all empty seasons from the database schema and table."""
        try:
            remaining = self.db.cleanup_empty_seasons()
            self._update_season_selector()
            self.load_seasonal_data()
            self.update_graphs()
            self.show_status(f"Purged empty seasons. Active seasons: {remaining}", self.theme.green)
        except Exception as e:
            self.show_status(f"Error purging seasons: {e}", self.theme.red)

    def clear_season_data(self) -> None:
        """Clears all logged resource entries for the selected season and removes it from the database."""
        season_str = self.seasonal_season_var.get()
        if not season_str:
            self.show_status("Please select a season to clear.", self.theme.yellow)
            return

        season_num = int(season_str)
        if not messagebox.askyesno("Confirm Remove", f"Are you sure you want to remove Season {season_num} from the database?"):
            return

        try:
            self.db.clear_season_data(season_num)
            self._update_season_selector()
            self.load_seasonal_data()
            self.show_status(f"Season {season_num} removed from database.", self.theme.green)
            self.update_graphs()
        except Exception as e:
            self.show_status(f"Error removing season: {e}", self.theme.red)

    def export_seasonal_csv(self) -> None:
        """Exports seasonal records to CSV."""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            self.db.export_seasonal_csv(file_path)
            self.show_status("Seasonal data exported successfully!", self.theme.green)
        except Exception as e:
            self.show_status(f"Export failed: {e}", self.theme.red)

    def import_seasonal_csv(self) -> None:
        """Imports seasonal records from CSV."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            self.db.import_seasonal_csv(file_path)
            self._update_season_selector()
            self.load_seasonal_data()
            self.show_status("Seasonal CSV imported successfully!", self.theme.green)
            self.update_graphs()
        except Exception as e:
            self.show_status(f"Import failed: {e}", self.theme.red)

    def load_seasonal_data(self) -> None:
        """Clears and reloads the seasonal matrix in Treeview, dynamically showing all existing season columns."""
        for row in self.tree_seasonal.get_children():
            self.tree_seasonal.delete(row)

        try:
            rows = self.db.fetch_all("SELECT * FROM seasonal_data ORDER BY resource ASC")
            if not rows:
                return

            seasons = self._get_existing_seasons()
            if not seasons:
                seasons = [1]
                self.db.ensure_season_column_exists("season_1")
                rows = self.db.fetch_all("SELECT * FROM seasonal_data ORDER BY resource ASC")

            # Column headers
            visible_columns = ["Resource"] + [f"Season {s}" for s in seasons]
            self.tree_seasonal["columns"] = visible_columns
            self.tree_seasonal["displaycolumns"] = visible_columns

            self.tree_seasonal.heading("Resource", text="Resource")
            self.tree_seasonal.column("Resource", width=160, anchor="w")

            for s in seasons:
                col_name = f"Season {s}"
                self.tree_seasonal.heading(col_name, text=col_name)
                self.tree_seasonal.column(col_name, width=120, anchor="center")

            # Column mapping
            for idx, r_row in enumerate(rows):
                res_name = r_row[0]
                row_vals = [res_name]
                for s in seasons:
                    col_key = f"season_{s}"
                    s_val = "-"
                    col_names = [info[1] for info in self.db.fetch_all("PRAGMA table_info(seasonal_data)")]
                    if col_key in col_names:
                        c_idx = col_names.index(col_key)
                        if c_idx < len(r_row):
                            s_val = r_row[c_idx]
                    row_vals.append(s_val if s_val else "-")

                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.tree_seasonal.insert("", "end", values=row_vals, tags=(tag,))

        except Exception as e:
            self.show_status(f"Error loading seasonal data: {e}", self.theme.red)

    # ==========================================
    # --- SUB-TAB 2: RESOURCE GRAPHS ---
    # ==========================================

    def _build_graphs_ui(self) -> None:
        # Top Selector Card
        card_sel = CardFrame(self.tab_graphs, self.theme, title="Resource Analytics Configuration", header_color=self.theme.blue, padding=6)
        card_sel.pack(fill="x", padx=10, pady=(8, 4))

        sel_row = tk.Frame(card_sel.body, bg=self.theme.surface)
        sel_row.pack(fill="x", pady=2)

        tk.Label(
            sel_row, text="Select Resource:", font=self.theme.fonts["body_bold"],
            bg=self.theme.surface, fg=self.theme.fg
        ).pack(side="left", padx=(4, 6))

        self.cmb_graph_res = ttk.Combobox(
            sel_row,
            textvariable=self.graph_resource_var,
            values=SEASONAL_RESOURCES,
            state="readonly",
            width=16
        )
        self.cmb_graph_res.pack(side="left", padx=(0, 16))
        self.cmb_graph_res.bind("<<ComboboxSelected>>", lambda _e: self.update_graphs())

        tk.Label(
            sel_row, text="Chart Style:", font=self.theme.fonts["body_bold"],
            bg=self.theme.surface, fg=self.theme.fg
        ).pack(side="left", padx=(4, 6))

        self.cmb_graph_type = ttk.Combobox(
            sel_row,
            textvariable=self.graph_type_var,
            values=["Line Chart", "Bar Chart"],
            state="readonly",
            width=12
        )
        self.cmb_graph_type.pack(side="left", padx=(0, 16))
        self.cmb_graph_type.bind("<<ComboboxSelected>>", lambda _e: self.update_graphs())

        ModernButton(sel_row, self.theme, text="🔄 Refresh Chart", variant="primary", command=self.update_graphs).pack(side="left", padx=4)

        # Plot Canvas Card
        self.chart_card = CardFrame(self.tab_graphs, self.theme, title="Progression Over Seasons (Amount vs. Season #)", header_color=self.theme.purple, padding=4)
        self.chart_card.pack(fill="both", expand=True, padx=10, pady=(4, 4))

        # Performance Summary Metrics Card
        self.metrics_card = CardFrame(self.tab_graphs, self.theme, padding=6)
        self.metrics_card.pack(fill="x", padx=10, pady=(2, 8))

        m_row = tk.Frame(self.metrics_card.body, bg=self.theme.surface)
        m_row.pack(fill="x")

        self.lbl_metric_total = tk.Label(m_row, text="Total Acquired: 0", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.yellow)
        self.lbl_metric_total.pack(side="left", expand=True)

        self.lbl_metric_avg = tk.Label(m_row, text="Average / Season: 0", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.green)
        self.lbl_metric_avg.pack(side="left", expand=True)

        self.lbl_metric_peak = tk.Label(m_row, text="Peak Season: -", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.blue)
        self.lbl_metric_peak.pack(side="left", expand=True)

        self.lbl_metric_latest = tk.Label(m_row, text="Latest Season: -", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.purple)
        self.lbl_metric_latest.pack(side="left", expand=True)

        self._init_plot()

    def _init_plot(self) -> None:
        """Initializes the Matplotlib Figure and Canvas."""
        if not MATPLOTLIB_AVAILABLE:
            tk.Label(
                self.chart_card.body,
                text="Matplotlib is not installed. Visual graphs are unavailable.",
                font=self.theme.fonts["body_bold"],
                bg=self.theme.surface,
                fg=self.theme.red
            ).pack(expand=True)
            return

        self.fig, self.ax = plt.subplots(figsize=(9, 4.5), dpi=100)
        self.fig.patch.set_facecolor(self.theme.surface)
        self.ax.set_facecolor(self.theme.bg)

        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=self.chart_card.body)
        self.canvas_plot.get_tk_widget().pack(fill="both", expand=True)

    def _on_tab_change(self, _event: Optional[tk.Event] = None) -> None:
        selected_index = self.notebook.index(self.notebook.select())
        if selected_index == 1:
            self.update_graphs()

    def update_graphs(self) -> None:
        """Plots the selected resource amounts across all seasons."""
        if not MATPLOTLIB_AVAILABLE or self.fig is None:
            return

        self.ax.clear()
        self.fig.patch.set_facecolor(self.theme.surface)
        self.ax.set_facecolor(self.theme.bg)

        res_name = self.graph_resource_var.get()
        chart_type = self.graph_type_var.get()

        seasons = self._get_existing_seasons()
        if not seasons:
            seasons = [1]

        # Fetch resource values across seasons
        season_cols = [f"season_{s}" for s in seasons]
        cols_query = ", ".join(season_cols)

        # Ensure columns exist
        for sc in season_cols:
            self.db.ensure_season_column_exists(sc)

        row = self.db.fetch_one(f"SELECT {cols_query} FROM seasonal_data WHERE resource = ?", (res_name,))
        
        amounts: List[float] = []
        season_labels: List[str] = []

        if row:
            for s_num, val_str in zip(seasons, row):
                num_val = parse_resource_value(str(val_str))
                amounts.append(num_val)
                season_labels.append(f"S{s_num}")
        else:
            amounts = [0.0] * len(seasons)
            season_labels = [f"S{s}" for s in seasons]

        x_indices = list(range(len(seasons)))

        accent_color = self.theme.blue
        fill_color = "#60cdff"

        if chart_type == "Bar Chart":
            bars = self.ax.bar(
                x_indices, amounts,
                color=accent_color,
                edgecolor="#ffffff",
                linewidth=0.8,
                width=0.55,
                alpha=0.85
            )
            for bar in bars:
                h = bar.get_height()
                if h > 0:
                    self.ax.annotate(
                        format_resource_value(h),
                        xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 4),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=9, fontweight='bold',
                        color=self.theme.fg
                    )
        else:
            # Line Chart
            self.ax.plot(
                x_indices, amounts,
                color=accent_color,
                linewidth=2.5,
                marker='o',
                markersize=7,
                markerfacecolor='#ffffff',
                markeredgecolor=accent_color,
                markeredgewidth=2,
                label=res_name
            )
            # Fill under curve
            self.ax.fill_between(x_indices, amounts, color=fill_color, alpha=0.15)

            for x, y in zip(x_indices, amounts):
                if y > 0:
                    self.ax.annotate(
                        format_resource_value(y),
                        xy=(x, y),
                        xytext=(0, 6),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=9, fontweight='bold',
                        color=self.theme.fg
                    )

        # Configure Axes & Styling
        self.ax.set_xticks(x_indices)
        self.ax.set_xticklabels(season_labels, fontsize=10, fontweight='bold', color=self.theme.fg)
        self.ax.set_xlabel("Season Number", fontsize=11, fontweight='bold', color=self.theme.blue, labelpad=8)
        self.ax.set_ylabel(f"{res_name} Acquired", fontsize=11, fontweight='bold', color=self.theme.blue, labelpad=8)
        self.ax.set_title(f"{res_name} Acquired Progression (By Season)", fontsize=13, fontweight='bold', color=self.theme.yellow, pad=12)

        self.ax.tick_params(axis='x', colors=self.theme.fg)
        self.ax.tick_params(axis='y', colors=self.theme.fg)

        # Formatter for Y-axis numbers
        def y_fmt(val, _pos):
            return format_resource_value(val)

        self.ax.yaxis.set_major_formatter(mticker.FuncFormatter(y_fmt))

        self.ax.grid(True, linestyle="--", alpha=0.25, color="#555555")

        # Spine Styling
        for spine in self.ax.spines.values():
            spine.set_color(self.theme.border)
            spine.set_linewidth(1.0)

        # Dynamic Y-axis limits
        max_val = max(amounts) if amounts else 0
        if max_val > 0:
            self.ax.set_ylim(0, max_val * 1.22)
        else:
            self.ax.set_ylim(0, 10)

        try:
            self.fig.tight_layout()
        except Exception:
            pass
        self.canvas_plot.draw()

        # Update Metrics Summary Cards
        total_sum = sum(amounts)
        avg_val = total_sum / len(amounts) if amounts else 0.0
        peak_idx = amounts.index(max_val) if max_val > 0 else 0
        peak_season = seasons[peak_idx] if seasons else 1
        latest_val = amounts[-1] if amounts else 0.0
        latest_season = seasons[-1] if seasons else 1

        self.lbl_metric_total.config(text=f"Total Acquired: {format_resource_value(total_sum)}")
        self.lbl_metric_avg.config(text=f"Average / Season: {format_resource_value(avg_val)}")
        self.lbl_metric_peak.config(text=f"Peak Season: Season {peak_season} ({format_resource_value(max_val)})")
        self.lbl_metric_latest.config(text=f"Latest Season: Season {latest_season} ({format_resource_value(latest_val)})")
