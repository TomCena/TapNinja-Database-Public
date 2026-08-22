"""
Elixir Tab module.
Includes Expected Time growth calculator, Datapoints log with CSV import conflict handling,
and interactive Tokyo Night dark-themed Matplotlib charts.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta
import math
import csv
from typing import Any, Optional, List, Tuple

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.dates as mdates
    import matplotlib.ticker as mticker
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from ui_components import CardFrame, ModernButton, ModernEntry, ModernScrollbar, ConflictDialog, setup_treeview_striping


class ElixirTab(tk.Frame):
    """Encapsulates Elixir calculations, historical tracking, and interactive growth charts."""

    def __init__(self, parent: tk.Widget, app: Any):
        super().__init__(parent, bg=app.theme.bg)
        self.app = app
        self.db = app.db
        self.theme = app.theme

        # State Variables
        self.elixir_sort_col = "Date"
        self.elixir_sort_reverse = True
        self.show_weekly_gain_var = tk.BooleanVar(value=True)
        self.show_future_projection_var = tk.BooleanVar(value=False)
        self.calculated_avg_growth = 0.0

        self.graph_dates: List[datetime] = []
        self.graph_values: List[float] = []
        self.graph_weekly_gains: List[float] = []

        self._build_ui()

    def _build_ui(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_expected = tk.Frame(self.notebook, bg=self.theme.bg)
        self.tab_datapoints = tk.Frame(self.notebook, bg=self.theme.bg)
        self.tab_graph = tk.Frame(self.notebook, bg=self.theme.bg)

        self.notebook.add(self.tab_expected, text="Growth Calculator")
        self.notebook.add(self.tab_datapoints, text="Datapoints Log")
        self.notebook.add(self.tab_graph, text="Analytics Chart")

        self._build_expected_ui()
        self._build_datapoints_ui()
        self._build_graph_ui()

    # ==========================================
    # --- GROWTH CALCULATOR SUB-TAB ---
    # ==========================================

    def _build_expected_ui(self) -> None:
        card_calc = CardFrame(self.tab_expected, self.theme, title="Target Time Projection Calculator", header_color=self.theme.green, padding=20)
        card_calc.pack(fill="x", padx=30, pady=30)

        grid = tk.Frame(card_calc.body, bg=self.theme.surface)
        grid.pack(pady=10)

        tk.Label(grid, text="Current Total Elixir:", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.fg).grid(row=0, column=0, sticky="e", padx=8, pady=8)
        self.entry_calc_current = ModernEntry(grid, self.theme, width=20)
        self.entry_calc_current.grid(row=0, column=1, padx=8, pady=8)

        tk.Label(grid, text="Target Total Elixir:", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.yellow).grid(row=1, column=0, sticky="e", padx=8, pady=8)
        self.entry_calc_target = ModernEntry(grid, self.theme, width=20)
        self.entry_calc_target.grid(row=1, column=1, padx=8, pady=8)

        tk.Label(grid, text="Weekly Growth Rate (%):", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.blue).grid(row=2, column=0, sticky="e", padx=8, pady=8)
        self.entry_calc_percent = ModernEntry(grid, self.theme, width=20)
        self.entry_calc_percent.grid(row=2, column=1, padx=8, pady=8)

        ModernButton(
            card_calc.body, self.theme, text="Calculate Projection", variant="success",
            command=self.calculate_expected_elixir, padx=20, pady=6
        ).pack(pady=15)

        self.lbl_calc_result = tk.Label(card_calc.body, text="", font=self.theme.fonts["section"], bg=self.theme.surface, fg=self.theme.green)
        self.lbl_calc_result.pack(pady=5)

    def calculate_expected_elixir(self) -> None:
        """Calculates estimated duration in weeks to reach a target elixir quantity."""
        try:
            curr_str = self.entry_calc_current.get().strip()
            if not curr_str:
                res = self.db.fetch_one("SELECT total_elixir FROM elixir_data ORDER BY date DESC LIMIT 1")
                if res:
                    current = float(res[0])
                    self.entry_calc_current.insert(0, f"{current:.2e}")
                else:
                    self.lbl_calc_result.config(text="No historical data available", fg=self.theme.red)
                    return
            else:
                current = float(curr_str)

            target = float(self.entry_calc_target.get().strip())
            pct_str = self.entry_calc_percent.get().strip()
            percent = float(pct_str) if pct_str else self.calculated_avg_growth

            if not pct_str:
                self.entry_calc_percent.insert(0, f"{percent:.2f}")

            if current <= 0 or target <= 0 or percent <= 0:
                self.lbl_calc_result.config(text="All values must be positive and non-zero.", fg=self.theme.red)
                return

            if current >= target:
                self.lbl_calc_result.config(text="Target already reached!", fg=self.theme.green)
                return

            rate = percent / 100.0
            weeks = math.log(target / current) / math.log(1.0 + rate)
            days = weeks * 7.0
            self.lbl_calc_result.config(
                text=f"Estimated Time: {weeks:.2f} weeks  ({days:.1f} days)",
                fg=self.theme.green
            )
        except ValueError:
            self.lbl_calc_result.config(text="Please enter valid numerical amounts.", fg=self.theme.red)

    # ==========================================
    # --- DATAPOINTS LOG SUB-TAB ---
    # ==========================================

    def _build_datapoints_ui(self) -> None:
        card_entry = CardFrame(self.tab_datapoints, self.theme, title="Elixir Datapoint Entry", header_color=self.theme.blue, padding=10)
        card_entry.pack(fill="x", padx=15, pady=(10, 4))

        row = tk.Frame(card_entry.body, bg=self.theme.surface)
        row.pack(fill="x", pady=4)

        tk.Label(row, text="Date (DD.MM.YYYY):", font=self.theme.fonts["body"], bg=self.theme.surface, fg=self.theme.fg).grid(row=0, column=0, padx=4)
        self.entry_elixir_date = ModernEntry(row, self.theme, width=14)
        self.entry_elixir_date.grid(row=0, column=1, padx=4)
        self.entry_elixir_date.insert(0, datetime.now().strftime("%d.%m.%Y"))

        tk.Label(row, text="Total Elixir:", font=self.theme.fonts["body"], bg=self.theme.surface, fg=self.theme.fg).grid(row=0, column=2, padx=4)
        self.entry_elixir_val = ModernEntry(row, self.theme, width=18)
        self.entry_elixir_val.grid(row=0, column=3, padx=4)
        self.entry_elixir_val.bind('<Return>', lambda e: self.add_elixir_record())

        ModernButton(row, self.theme, text="Add Point", variant="success", command=self.add_elixir_record).grid(row=0, column=4, padx=6)
        ModernButton(row, self.theme, text="Delete Selected", variant="danger", command=self.ask_delete_elixir).grid(row=0, column=5, padx=6)
        ModernButton(row, self.theme, text="Import CSV", variant="warning", command=self.import_elixir_csv).grid(row=0, column=6, padx=6)

        self.elixir_status_label = tk.Label(card_entry.body, text="", font=self.theme.fonts["body"], bg=self.theme.surface, fg=self.theme.fg)
        self.elixir_status_label.pack(anchor="w", pady=(4, 0))

        # Table Card
        tree_card = CardFrame(self.tab_datapoints, self.theme, padding=2)
        tree_card.pack(fill="both", expand=True, padx=15, pady=(4, 12))

        sb = ModernScrollbar(tree_card.body, self.theme)
        sb.pack(side="right", fill="y")

        cols = ("Date", "Total Elixir", "Bonus", "Daily Bonus", "%")
        self.tree_elixir = ttk.Treeview(tree_card.body, columns=cols, show="headings", yscrollcommand=sb.set)
        sb.config(command=self.tree_elixir.yview)

        for col in cols:
            self.tree_elixir.heading(col, text=col, command=lambda c=col: self.sort_elixir_column(c, False))
            self.tree_elixir.column(col, width=150, anchor="center")

        self.tree_elixir.pack(fill="both", expand=True)
        setup_treeview_striping(self.tree_elixir, self.theme)

    def show_elixir_status(self, message: str, color: Optional[str] = None) -> None:
        self.elixir_status_label.config(text=message, fg=color or self.theme.fg)

    def load_elixir_data(self) -> None:
        """Loads historical elixir log entries, calculates gains & % increases, and updates UI."""
        for r in self.tree_elixir.get_children():
            self.tree_elixir.delete(r)

        rows = self.db.fetch_all("SELECT id, date, total_elixir FROM elixir_data ORDER BY date ASC")
        if rows:
            last_val = rows[-1][2]
            self.entry_calc_current.delete(0, tk.END)
            self.entry_calc_current.insert(0, f"{last_val:.2e}")

        prev_elixir = 0.0
        prev_date_obj: Optional[datetime] = None
        percentages: List[float] = []

        for idx, (r_id, r_date, r_elixir) in enumerate(rows):
            bonus = 0.0
            daily_bonus = 0.0
            pct_increase = 0.0

            try:
                curr_date_obj = datetime.strptime(r_date, "%Y-%m-%d")
            except ValueError:
                curr_date_obj = None

            if prev_elixir > 0 and prev_date_obj and curr_date_obj:
                bonus = r_elixir - prev_elixir
                days = (curr_date_obj - prev_date_obj).days
                if days <= 0:
                    days = 1
                daily_bonus = bonus / days
                pct_increase = (bonus / prev_elixir) * 100.0
            elif prev_elixir > 0:
                bonus = r_elixir - prev_elixir
                pct_increase = (bonus / prev_elixir) * 100.0

            if prev_elixir > 0:
                percentages.append(pct_increase)

            fmt_elixir = f"{r_elixir:.2e}"
            fmt_bonus = f"{bonus:.2e}" if bonus != 0 else "-"
            fmt_daily = f"{daily_bonus:.2e}" if daily_bonus != 0 else "-"
            fmt_pct = f"{pct_increase:.2f}%" if pct_increase != 0 else "-"

            display_date = curr_date_obj.strftime("%d.%m.%Y") if curr_date_obj else r_date
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree_elixir.insert("", "end", iid=r_id, values=(display_date, fmt_elixir, fmt_bonus, fmt_daily, fmt_pct), tags=(tag,))

            prev_elixir = r_elixir
            prev_date_obj = curr_date_obj

        if percentages:
            last_5 = percentages[-5:]
            avg_pct = sum(last_5) / len(last_5)
            self.entry_calc_percent.delete(0, tk.END)
            self.entry_calc_percent.insert(0, f"{avg_pct:.2f}")
            self.calculated_avg_growth = avg_pct
        else:
            self.calculated_avg_growth = 0.0

        if self.elixir_sort_col:
            self.sort_elixir_column(self.elixir_sort_col, self.elixir_sort_reverse)

        self.update_elixir_graph()

    def add_elixir_record(self, _event: Optional[tk.Event] = None) -> None:
        """Adds or updates an elixir record for a specific date."""
        date_str = self.entry_elixir_date.get().strip()
        elixir_str = self.entry_elixir_val.get().strip()

        if not date_str or not elixir_str:
            self.show_elixir_status("Please enter both Date and Total Elixir.", self.theme.yellow)
            return

        try:
            dt = datetime.strptime(date_str, "%d.%m.%Y")
            iso_date = dt.strftime("%Y-%m-%d")
            elixir_val = float(elixir_str)

            existing = self.db.fetch_one("SELECT id, total_elixir FROM elixir_data WHERE date = ?", (iso_date,))
            if existing:
                existing_id, existing_val = existing
                if messagebox.askyesno("Duplicate Date", f"Date {date_str} exists with value {existing_val:.2e}.\nOverwrite with {elixir_val:.2e}?"):
                    self.db.run_query("UPDATE elixir_data SET total_elixir = ? WHERE id = ?", (elixir_val, existing_id))
                    self.show_elixir_status("Datapoint updated.", self.theme.green)
                    self.entry_elixir_val.delete(0, tk.END)
                    self.load_elixir_data()
                    self.app.update_global_data()
            else:
                self.db.run_query("INSERT INTO elixir_data (date, total_elixir) VALUES (?, ?)", (iso_date, elixir_val))
                self.entry_elixir_val.delete(0, tk.END)
                self.load_elixir_data()
                self.show_elixir_status("Datapoint added.", self.theme.green)
                self.app.update_global_data()
        except ValueError:
            self.show_elixir_status("Invalid Date (DD.MM.YYYY) or number.", self.theme.red)

    def ask_delete_elixir(self, _event: Optional[tk.Event] = None) -> None:
        selected = self.tree_elixir.selection()
        if not selected:
            self.show_elixir_status("Please select a row to delete.", self.theme.yellow)
            return
        for item in selected:
            self.db.run_query("DELETE FROM elixir_data WHERE id = ?", (item,))
        self.load_elixir_data()
        self.show_elixir_status("Selected record(s) deleted.", self.theme.green)
        self.app.update_global_data()

    def import_elixir_csv(self) -> None:
        """Imports elixir history from CSV, invoking ConflictDialog on duplicates."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            count_added, count_updated, count_skipped = 0, 0, 0
            action_all = None

            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if not row or len(row) < 2:
                        continue
                    d_str, e_str = row[0].strip(), row[1].strip()
                    if d_str.lower() == "date":
                        continue
                    try:
                        dt = datetime.strptime(d_str, "%d.%m.%Y")
                        iso_date = dt.strftime("%Y-%m-%d")
                        elixir_val = float(e_str)

                        existing = self.db.fetch_one("SELECT id, total_elixir FROM elixir_data WHERE date = ?", (iso_date,))
                        if existing:
                            existing_id, existing_val = existing
                            action = action_all
                            if action is None:
                                dlg = ConflictDialog(self.winfo_toplevel(), self.theme, d_str, f"{existing_val:.2e}", f"{elixir_val:.2e}")
                                action = dlg.result
                                if action in ['overwrite_all', 'skip_all']:
                                    action_all = action

                            if action in ['overwrite', 'overwrite_all']:
                                self.db.run_query("UPDATE elixir_data SET total_elixir = ? WHERE id = ?", (elixir_val, existing_id))
                                count_updated += 1
                            else:
                                count_skipped += 1
                        else:
                            self.db.run_query("INSERT INTO elixir_data (date, total_elixir) VALUES (?, ?)", (iso_date, elixir_val))
                            count_added += 1
                    except ValueError:
                        continue

            self.load_elixir_data()
            self.app.update_global_data()
            self.show_elixir_status(f"Imported: {count_added} added, {count_updated} updated, {count_skipped} skipped.", self.theme.green)
        except Exception as e:
            self.show_elixir_status(f"Import failed: {e}", self.theme.red)

    def sort_elixir_column(self, col: str, reverse: bool) -> None:
        self.elixir_sort_col, self.elixir_sort_reverse = col, reverse
        items = [(self.tree_elixir.set(k, col), k) for k in self.tree_elixir.get_children('')]

        def sort_key(val: str) -> Any:
            if val == "-":
                return -float('inf')
            try:
                return datetime.strptime(val, "%d.%m.%Y").timestamp()
            except ValueError:
                pass
            if val.endswith('%'):
                try:
                    return float(val[:-1])
                except ValueError:
                    pass
            try:
                return float(val)
            except ValueError:
                pass
            return val.lower()

        items.sort(key=lambda t: sort_key(t[0]), reverse=reverse)
        for index, (_val, k) in enumerate(items):
            self.tree_elixir.move(k, '', index)
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree_elixir.item(k, tags=(tag,))

        for c in ("Date", "Total Elixir", "Bonus", "Daily Bonus", "%"):
            self.tree_elixir.heading(c, text=c)
        arrow = " ▼" if reverse else " ▲"
        self.tree_elixir.heading(col, text=col + arrow, command=lambda: self.sort_elixir_column(col, not reverse))

    # ==========================================
    # --- ANALYTICS CHART SUB-TAB ---
    # ==========================================

    def _build_graph_ui(self) -> None:
        if not MATPLOTLIB_AVAILABLE:
            tk.Label(
                self.tab_graph,
                text="Matplotlib is required for interactive charts.\nInstall with: pip install matplotlib",
                font=self.theme.fonts["section"],
                bg=self.theme.bg,
                fg=self.theme.fg
            ).pack(expand=True)
            return

        # Controls Card
        ctrl_card = CardFrame(self.tab_graph, self.theme, padding=8)
        ctrl_card.pack(side="top", fill="x", padx=10, pady=(10, 4))

        ctrl_row = tk.Frame(ctrl_card.body, bg=self.theme.surface)
        ctrl_row.pack(fill="x")

        tk.Checkbutton(
            ctrl_row, text="Show Weekly Gain", variable=self.show_weekly_gain_var,
            command=self.update_elixir_graph, bg=self.theme.surface, fg=self.theme.fg,
            selectcolor=self.theme.bg, activebackground=self.theme.surface, activeforeground=self.theme.fg,
            font=self.theme.fonts["body"]
        ).pack(side="left", padx=6)

        tk.Checkbutton(
            ctrl_row, text="Show Projection (6m)", variable=self.show_future_projection_var,
            command=self.update_elixir_graph, bg=self.theme.surface, fg=self.theme.fg,
            selectcolor=self.theme.bg, activebackground=self.theme.surface, activeforeground=self.theme.fg,
            font=self.theme.fonts["body"]
        ).pack(side="left", padx=6)

        tk.Label(ctrl_row, text="Time Filter:", font=self.theme.fonts["body"], bg=self.theme.surface, fg=self.theme.text_dim).pack(side="left", padx=(12, 4))
        self.graph_filter_var = tk.StringVar(value="All Time")
        self.cmb_graph_filter = ttk.Combobox(
            ctrl_row, textvariable=self.graph_filter_var,
            values=["All Time", "2025", "2026", "Past 3 Months", "Past 6 Months"],
            state="readonly", width=14
        )
        self.cmb_graph_filter.pack(side="left", padx=4)
        self.cmb_graph_filter.bind("<<ComboboxSelected>>", lambda e: self.update_elixir_graph())

        ModernButton(ctrl_row, self.theme, text="Reset Filter", variant="neutral", command=self.reset_graph_filter).pack(side="left", padx=4)
        ModernButton(ctrl_row, self.theme, text="Save PNG", variant="success", command=self.save_graph_image).pack(side="left", padx=4)

        self.lbl_avg_gain = tk.Label(ctrl_row, text="Avg Weekly Gain: -", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.yellow)
        self.lbl_avg_gain.pack(side="left", padx=12)

        self.lbl_dist_stats = tk.Label(ctrl_row, text="", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.blue)
        self.lbl_dist_stats.pack(side="left", padx=12)

        # Plot Frame
        chart_card = CardFrame(self.tab_graph, self.theme, padding=4)
        chart_card.pack(fill="both", expand=True, padx=10, pady=(4, 10))

        self.fig, (self.ax, self.ax_dist) = plt.subplots(1, 2, figsize=(8, 4), dpi=100, gridspec_kw={'width_ratios': [3.2, 1]})
        self.ax2 = None
        self.fig.patch.set_facecolor(self.theme.bg)
        self.ax.set_facecolor(self.theme.bg)
        self.ax_dist.set_facecolor(self.theme.bg)

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_card.body)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.canvas.mpl_connect("motion_notify_event", self.on_graph_hover)
        self.canvas.mpl_connect("motion_notify_event", self.on_dist_hover)

        self.sc = None
        self.sc2 = None
        self.annot = None
        self.annot2 = None
        self.annot_dist = None
        self.bp_dict = None

    def reset_graph_filter(self) -> None:
        self.graph_filter_var.set("All Time")
        self.update_elixir_graph()

    def save_graph_image(self) -> None:
        if not MATPLOTLIB_AVAILABLE:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            try:
                self.fig.savefig(file_path, facecolor=self.theme.surface)
                self.show_elixir_status(f"Chart saved to {file_path}", self.theme.green)
            except Exception as e:
                self.show_elixir_status(f"Failed to save chart: {e}", self.theme.red)

    def update_elixir_graph(self) -> None:
        """Renders the Total Elixir trend line, secondary weekly gain axis, and projection."""
        if not MATPLOTLIB_AVAILABLE:
            return

        rows = self.db.fetch_all("SELECT date, total_elixir FROM elixir_data ORDER BY date ASC")
        all_dates, all_values, all_gains = [], [], []
        prev_d, prev_v = None, None

        for r_date, r_val in rows:
            try:
                dt = datetime.strptime(r_date, "%Y-%m-%d")
                all_dates.append(dt)
                all_values.append(r_val)
                if prev_d is not None and prev_v is not None:
                    days = (dt - prev_d).days
                    gain = r_val - prev_v
                    all_gains.append((gain / days) * 7.0 if days > 0 else 0.0)
                else:
                    all_gains.append(0.0)
                prev_d, prev_v = dt, r_val
            except ValueError:
                continue

        self.graph_dates, self.graph_values, self.graph_weekly_gains = [], [], []
        filter_opt = self.graph_filter_var.get()
        now = datetime.now()
        start_dt, end_dt = None, None

        if filter_opt == "2025":
            start_dt, end_dt = datetime(2025, 1, 1), datetime(2025, 12, 31, 23, 59, 59)
        elif filter_opt == "2026":
            start_dt, end_dt = datetime(2026, 1, 1), datetime(2026, 12, 31, 23, 59, 59)
        elif filter_opt == "Past 3 Months":
            start_dt = now - timedelta(days=90)
        elif filter_opt == "Past 6 Months":
            start_dt = now - timedelta(days=180)

        valid_gains_for_avg = []
        for i, (d, v, g) in enumerate(zip(all_dates, all_values, all_gains)):
            if start_dt and d < start_dt: continue
            if end_dt and d > end_dt: continue
            self.graph_dates.append(d)
            self.graph_values.append(v)
            self.graph_weekly_gains.append(g)
            if i > 0:
                valid_gains_for_avg.append(g)

        avg_gain = sum(valid_gains_for_avg) / len(valid_gains_for_avg) if valid_gains_for_avg else 0.0
        self.lbl_avg_gain.config(text=f"Avg Weekly Gain: {avg_gain:.2e}" if valid_gains_for_avg else "Avg Weekly Gain: -")

        self.ax.clear()
        if self.ax2 is not None:
            try:
                self.ax2.remove()
            except Exception:
                pass
            self.ax2 = None

        self.sc, self.sc2 = None, None
        self.annot, self.annot2 = None, None

        if self.graph_dates:
            p1, = self.ax.plot(self.graph_dates, self.graph_values, marker='o', linestyle='-', color=self.theme.blue, markersize=4, label="Total Elixir", linewidth=2)
            self.sc = self.ax.scatter(self.graph_dates, self.graph_values, s=50, alpha=0)
            lines = [p1]

            if self.show_weekly_gain_var.get():
                self.ax2 = self.ax.twinx()
                color_gain = "#4cc2ff"
                p2, = self.ax2.plot(self.graph_dates, self.graph_weekly_gains, marker='x', linestyle='--', color=color_gain, markersize=4, label="Weekly Gain", linewidth=1.5)
                self.sc2 = self.ax2.scatter(self.graph_dates, self.graph_weekly_gains, s=50, alpha=0)

                self.annot2 = self.ax2.annotate(
                    "", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.5", fc=self.theme.surface, ec=self.theme.border, lw=1),
                    color=self.theme.fg,
                    arrowprops=dict(arrowstyle="->", color=color_gain, lw=1.2),
                    zorder=10,
                    fontsize=8
                )
                self.annot2.set_visible(False)

                self.ax2.tick_params(axis='y', colors=color_gain, labelsize=8)
                for spine_k in ['bottom', 'top', 'left']:
                    self.ax2.spines[spine_k].set_visible(False)
                self.ax2.spines['right'].set_color(color_gain)
                self.ax2.set_ylabel("Weekly Gain", color=color_gain, fontsize=8)
                self.ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _p: f"{x:.0e}".replace('+', '')))
                lines.append(p2)

            if self.show_future_projection_var.get() and avg_gain > 0:
                last_d, last_v = self.graph_dates[-1], self.graph_values[-1]
                future_dates = [last_d + timedelta(weeks=i) for i in range(27)]
                future_values = [last_v + (avg_gain * i) for i in range(27)]
                p_proj, = self.ax.plot(future_dates, future_values, linestyle=':', color=self.theme.purple, label="Projected (6m)", linewidth=2)
                lines.append(p_proj)

            self.annot = self.ax.annotate(
                "", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.5", fc=self.theme.surface, ec=self.theme.border, lw=1),
                color=self.theme.fg,
                arrowprops=dict(arrowstyle="->", color=self.theme.blue, lw=1.2),
                zorder=10,
                fontsize=8
            )
            self.annot.set_visible(False)

            self.ax.grid(True, color="#2d2d2d", linestyle='--', linewidth=0.5)
            self.ax.set_facecolor(self.theme.bg)
            self.ax.tick_params(axis='x', colors=self.theme.fg, labelsize=8, rotation=45)
            self.ax.tick_params(axis='y', colors=self.theme.fg, labelsize=8)
            for spine_k, spine in self.ax.spines.items():
                if spine_k == 'right' and self.show_weekly_gain_var.get():
                    spine.set_visible(False)
                else:
                    spine.set_color(self.theme.border)

            self.ax.set_title("Total Elixir & Growth Trends", color=self.theme.fg, fontsize=10, fontweight="bold")
            self.ax.set_xlabel("Date", color=self.theme.text_dim, fontsize=8)
            self.ax.set_ylabel("Total Elixir", color=self.theme.text_dim, fontsize=8)

            labels = [l.get_label() for l in lines]
            self.ax.legend(lines, labels, loc='upper left', facecolor=self.theme.surface, edgecolor=self.theme.border, labelcolor=self.theme.fg, fontsize=8)

            self.ax.xaxis.set_major_locator(mdates.MonthLocator())
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
            self.ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _p: f"{x:.2e}".replace('+', '')))
            self.fig.autofmt_xdate()

        self.canvas.draw()
        self.update_elixir_distribution()

    def update_elixir_distribution(self) -> None:
        """Renders the % growth distribution boxplot."""
        if not MATPLOTLIB_AVAILABLE:
            return

        rows = self.db.fetch_all("SELECT date, total_elixir FROM elixir_data ORDER BY date ASC")
        percentages = []
        prev_v = None

        for r_date, r_val in rows:
            try:
                dt = datetime.strptime(r_date, "%Y-%m-%d")
                val = float(r_val)
                if prev_v is not None and prev_v > 0:
                    percentages.append((dt, ((val - prev_v) / prev_v) * 100.0))
                prev_v = val
            except ValueError:
                continue

        filter_opt = self.graph_filter_var.get()
        now = datetime.now()
        start_dt, end_dt = None, None
        if filter_opt == "2025":
            start_dt, end_dt = datetime(2025, 1, 1), datetime(2025, 12, 31, 23, 59, 59)
        elif filter_opt == "2026":
            start_dt, end_dt = datetime(2026, 1, 1), datetime(2026, 12, 31, 23, 59, 59)
        elif filter_opt == "Past 3 Months":
            start_dt = now - timedelta(days=90)
        elif filter_opt == "Past 6 Months":
            start_dt = now - timedelta(days=180)

        filtered_pcts = [p for d, p in percentages if (not start_dt or d >= start_dt) and (not end_dt or d <= end_dt)]

        self.ax_dist.clear()
        self.bp_dict = None

        if filtered_pcts:
            avg_val = sum(filtered_pcts) / len(filtered_pcts)
            self.lbl_dist_stats.config(text=f"Avg: {avg_val:.2f}% | Min: {min(filtered_pcts):.2f}% | Max: {max(filtered_pcts):.2f}%")

            self.bp_dict = self.ax_dist.boxplot(
                filtered_pcts, vert=True, patch_artist=True,
                boxprops=dict(facecolor=self.theme.blue, color=self.theme.fg),
                capprops=dict(color=self.theme.fg),
                whiskerprops=dict(color=self.theme.fg),
                flierprops=dict(markeredgecolor=self.theme.yellow),
                medianprops=dict(color=self.theme.yellow, lw=2)
            )
        else:
            self.lbl_dist_stats.config(text="No data")

        self.ax_dist.set_facecolor(self.theme.bg)
        self.ax_dist.tick_params(axis='x', colors=self.theme.fg)
        self.ax_dist.tick_params(axis='y', colors=self.theme.fg, labelsize=8)
        for spine in self.ax_dist.spines.values():
            spine.set_color(self.theme.border)

        self.ax_dist.set_title("Growth %", color=self.theme.fg, fontsize=10, fontweight="bold")
        self.ax_dist.set_ylabel("% Growth Rate", color=self.theme.text_dim, fontsize=8)
        self.ax_dist.set_xticks([])
        self.ax_dist.yaxis.set_major_formatter(mticker.PercentFormatter())
        self.ax_dist.grid(True, color="#2d2d2d", linestyle='--', linewidth=0.5, alpha=0.5)

        self.annot_dist = self.ax_dist.annotate(
            "", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.5", fc=self.theme.surface, ec=self.theme.border, lw=1),
            color=self.theme.fg,
            arrowprops=dict(arrowstyle="->", color=self.theme.blue, lw=1.2),
            zorder=10,
            fontsize=8
        )
        self.annot_dist.set_visible(False)

        self.fig.tight_layout()
        self.canvas.draw()

    def on_graph_hover(self, event: Any) -> None:
        if not self.sc or not self.annot:
            return
        found = False
        if event.inaxes in [self.ax, self.ax2]:
            if self.sc2 and self.annot2:
                cont, ind = self.sc2.contains(event)
                if cont:
                    self._update_annot_data(ind, self.sc2, self.annot2)
                    self.annot2.set_visible(True)
                    self.annot.set_visible(False)
                    self.canvas.draw_idle()
                    found = True
            if not found and self.sc:
                cont, ind = self.sc.contains(event)
                if cont:
                    self._update_annot_data(ind, self.sc, self.annot)
                    self.annot.set_visible(True)
                    if self.annot2: self.annot2.set_visible(False)
                    self.canvas.draw_idle()
                    found = True
        if not found:
            if self.annot.get_visible():
                self.annot.set_visible(False)
                self.canvas.draw_idle()
            if self.annot2 and self.annot2.get_visible():
                self.annot2.set_visible(False)
                self.canvas.draw_idle()

    def _update_annot_data(self, ind: Any, sc: Any, annot: Any) -> None:
        idx = ind["ind"][0]
        annot.xy = sc.get_offsets()[idx]
        d_val = self.graph_dates[idx]
        e_val = self.graph_values[idx]
        g_val = self.graph_weekly_gains[idx]
        annot.set_text(f"Date: {d_val.strftime('%d.%m.%Y')}\nTotal: {e_val:.2e}\nWeekly: {g_val:.2e}")

    def on_dist_hover(self, event: Any) -> None:
        if not self.bp_dict or not self.annot_dist or event.inaxes != self.ax_dist:
            if self.annot_dist and self.annot_dist.get_visible():
                self.annot_dist.set_visible(False)
                self.canvas.draw_idle()
            return
        found = False
        for flier in self.bp_dict.get('fliers', []):
            cont, ind = flier.contains(event)
            if cont:
                idx = ind['ind'][0]
                val = flier.get_ydata()[idx]
                self.annot_dist.xy = (flier.get_xdata()[idx], val)
                self.annot_dist.set_text(f"Outlier: {val:.2f}%")
                self.annot_dist.set_visible(True)
                self.canvas.draw_idle()
                found = True
                break
        if not found:
            for box in self.bp_dict.get('boxes', []):
                cont, _ = box.contains(event)
                if cont:
                    extent = box.get_path().get_extents()
                    medians = self.bp_dict.get('medians', [])
                    median = medians[0].get_ydata()[0] if medians else (extent.ymin + extent.ymax) / 2
                    self.annot_dist.xy = (event.xdata, event.ydata)
                    self.annot_dist.set_text(f"Q1: {extent.ymin:.2f}%\nMedian: {median:.2f}%\nQ3: {extent.ymax:.2f}%")
                    self.annot_dist.set_visible(True)
                    self.canvas.draw_idle()
                    found = True
                    break
        if not found and self.annot_dist.get_visible():
            self.annot_dist.set_visible(False)
            self.canvas.draw_idle()
