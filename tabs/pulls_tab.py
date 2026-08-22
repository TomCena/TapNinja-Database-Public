"""
Pulls Tab module.
Provides Hero Scroll & Pet Egg pull tracking, live luck analytics with Matplotlib,
breakdown menus, and pull history logs with CSV import.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import csv
from typing import Any, Optional, Dict, List

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from constants import (
    HERO_NAMES, PET_NAMES, EGG_STAR_CHANCES, SCROLL_STAR_CHANCES, HERO_DETAILS_MAP,
    calculate_pulls_pacing
)
from ui_components import CardFrame, ModernButton, ModernEntry, ModernScrollbar, setup_treeview_striping


class PullsTab(tk.Frame):
    """Encapsulates Pulls logging, probability graphs, luck statistics, and history tables."""

    def __init__(self, parent: tk.Widget, app: Any):
        super().__init__(parent, bg=app.theme.bg)
        self.app = app
        self.db = app.db
        self.theme = app.theme

        # State Variables
        self.selected_scroll_id: Optional[str] = None
        self.selected_egg_id: Optional[str] = None
        self.scroll_sort_col = "Date"
        self.scroll_sort_reverse = True
        self.egg_sort_col = "Date"
        self.egg_sort_reverse = True

        self.scroll_dist_map: Dict[int, int] = {}
        self.egg_dist_map: Dict[int, int] = {}
        self.user_scroll_probs: List[float] = [0.0] * 12
        self.user_egg_probs: List[float] = [0.0] * 12

        # Pacing State (Two Starting Dates: Scrolls = 07.Jan.2024, Eggs = 07.Nov.2022)
        start_date_scrolls = datetime(2024, 1, 7)
        calc_days_scrolls = max(1, (datetime.now() - start_date_scrolls).days)
        self.pacing_scrolls_days_var = tk.StringVar(
            value=self.db.get_setting("pacing_scrolls_days_elapsed", str(calc_days_scrolls))
        )

        start_date_eggs = datetime(2022, 11, 7)
        calc_days_eggs = max(1, (datetime.now() - start_date_eggs).days)
        self.pacing_eggs_days_var = tk.StringVar(
            value=self.db.get_setting("pacing_eggs_days_elapsed", self.db.get_setting("pulls_days_elapsed", str(calc_days_eggs)))
        )

        # Pacing User Inputs
        self.pacing_rare_scrolls_var = tk.StringVar(value=self.db.get_setting("pacing_rare_scrolls_opened", "2316"))
        self.pacing_rare_target1_var = tk.StringVar(value=self.db.get_setting("pacing_rare_target1", "1500"))
        self.pacing_rare_target2_var = tk.StringVar(value=self.db.get_setting("pacing_rare_target2", "3000"))

        self.pacing_epic_scrolls_var = tk.StringVar(value=self.db.get_setting("pacing_epic_scrolls_opened", "1158"))
        self.pacing_epic_target1_var = tk.StringVar(value=self.db.get_setting("pacing_epic_target1", "1500"))
        self.pacing_epic_target2_var = tk.StringVar(value=self.db.get_setting("pacing_epic_target2", "3000"))

        self.pacing_eggs_var = tk.StringVar(value=self.db.get_setting("pacing_eggs_opened", "4623"))
        self.pacing_egg_target1_var = tk.StringVar(value=self.db.get_setting("pacing_egg_target1", "2500"))
        self.pacing_egg_target2_var = tk.StringVar(value=self.db.get_setting("pacing_egg_target2", "5000"))

        self._build_ui()

    def _build_ui(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_main = tk.Frame(self.notebook, bg=self.theme.bg)
        self.tab_luck = tk.Frame(self.notebook, bg=self.theme.bg)
        self.tab_pacing = tk.Frame(self.notebook, bg=self.theme.bg)
        self.tab_dp_scrolls = tk.Frame(self.notebook, bg=self.theme.bg)
        self.tab_dp_eggs = tk.Frame(self.notebook, bg=self.theme.bg)

        self.notebook.add(self.tab_main, text="Pull Entry")
        self.notebook.add(self.tab_luck, text="Luck Analytics")
        self.notebook.add(self.tab_pacing, text="Pacing & Achievements")
        self.notebook.add(self.tab_dp_scrolls, text="Scrolls History")
        self.notebook.add(self.tab_dp_eggs, text="Eggs History")

        self.notebook.bind("<<NotebookTabChanged>>", self._on_subtab_change)

        self._build_main_ui()
        self._build_luck_ui()
        self._build_pacing_ui()
        self._build_history_scrolls_ui()
        self._build_history_eggs_ui()

    def _on_subtab_change(self, _event: tk.Event) -> None:
        selected = self.notebook.select()
        if selected == str(self.tab_luck):
            self.update_luck_stats()
        elif selected == str(self.tab_pacing):
            self.update_pacing_stats()

    # ==========================================
    # --- MAIN PULL ENTRY SUB-TAB ---
    # ==========================================

    def _build_main_ui(self) -> None:
        container = tk.Frame(self.tab_main, bg=self.theme.bg)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        container.columnconfigure(0, weight=1, uniform="pull_card")
        container.columnconfigure(1, weight=1, uniform="pull_card")

        # 1. Scrolls Pull Card
        card_scroll = CardFrame(container, self.theme, title="Hero Scroll Pull", header_color=self.theme.blue, padding=16)
        card_scroll.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        s_form = tk.Frame(card_scroll.body, bg=self.theme.surface)
        s_form.pack(pady=10)

        tk.Label(s_form, text="Hero Name (Optional):", font=self.theme.fonts["body"], bg=self.theme.surface, fg=self.theme.fg).grid(row=0, column=0, sticky="w", pady=6)
        self.entry_scroll_name = ModernEntry(s_form, self.theme, width=20)
        self.entry_scroll_name.grid(row=0, column=1, padx=8, pady=6)

        tk.Label(s_form, text="Stars Pulled (1-12):", font=self.theme.fonts["body"], bg=self.theme.surface, fg=self.theme.fg).grid(row=1, column=0, sticky="w", pady=6)
        self.entry_scroll_stars = ModernEntry(s_form, self.theme, width=20)
        self.entry_scroll_stars.grid(row=1, column=1, padx=8, pady=6)

        ModernButton(
            card_scroll.body, self.theme, text="Record Scroll Pull", variant="primary",
            command=self.process_scroll_pull, padx=16, pady=6
        ).pack(pady=15)

        self.entry_scroll_name.bind('<Return>', lambda e: self.process_scroll_pull())
        self.entry_scroll_stars.bind('<Return>', lambda e: self.process_scroll_pull())

        # 2. Eggs Pull Card
        card_egg = CardFrame(container, self.theme, title="Pet Egg Pull", header_color=self.theme.yellow, padding=16)
        card_egg.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        e_form = tk.Frame(card_egg.body, bg=self.theme.surface)
        e_form.pack(pady=10)

        tk.Label(e_form, text="Pet Name (Optional):", font=self.theme.fonts["body"], bg=self.theme.surface, fg=self.theme.fg).grid(row=0, column=0, sticky="w", pady=6)
        self.entry_egg_name = ModernEntry(e_form, self.theme, width=20)
        self.entry_egg_name.grid(row=0, column=1, padx=8, pady=6)

        tk.Label(e_form, text="Stars Pulled (1-12):", font=self.theme.fonts["body"], bg=self.theme.surface, fg=self.theme.fg).grid(row=1, column=0, sticky="w", pady=6)
        self.entry_egg_stars = ModernEntry(e_form, self.theme, width=20)
        self.entry_egg_stars.grid(row=1, column=1, padx=8, pady=6)

        ModernButton(
            card_egg.body, self.theme, text="Record Egg Pull", variant="warning",
            command=self.process_egg_pull, padx=16, pady=6
        ).pack(pady=15)

        self.entry_egg_name.bind('<Return>', lambda e: self.process_egg_pull())
        self.entry_egg_stars.bind('<Return>', lambda e: self.process_egg_pull())

        # Pulls Status Bar
        self.pulls_status_label = tk.Label(self.tab_main, text="", font=self.theme.fonts["body_bold"], bg=self.theme.bg, fg=self.theme.fg)
        self.pulls_status_label.pack(side="bottom", pady=10)

    def show_pulls_status(self, message: str, color: Optional[str] = None) -> None:
        self.pulls_status_label.config(text=message, fg=color or self.theme.fg)

    def process_scroll_pull(self, _event: Optional[tk.Event] = None) -> None:
        """Processes and logs a hero scroll pull, upgrading hero stars if higher."""
        name = self.entry_scroll_name.get().strip().title()
        sterne = self.entry_scroll_stars.get().strip()

        if not sterne:
            self.show_pulls_status("Please enter stars pulled.", self.theme.yellow)
            return

        if name and name not in HERO_NAMES:
            self.show_pulls_status(f"Hero '{name}' is not in the allowed list.", self.theme.yellow)
            return

        try:
            sterne_val = int(sterne)
            if not (0 <= sterne_val <= 12):
                self.show_pulls_status("Stars must be between 0 and 12.", self.theme.yellow)
                return

            msg = "Logged Scroll Pull (Stars only)"
            if name:
                existing = self.db.fetch_one("SELECT id, sterne FROM daten WHERE name = ?", (name,))
                if existing:
                    curr_s = -1 if existing[1] == "-" else int(existing[1])
                    if sterne_val > curr_s:
                        self.db.run_query("UPDATE daten SET sterne = ? WHERE id = ?", (sterne_val, existing[0]))
                        msg = f"Updated Hero: {name} (Now {sterne_val}★)"
                    else:
                        msg = f"Logged Pull for {name} (Current: {existing[1]}★)"
                else:
                    rarity = self.db.get_rarity(name)
                    faction, cls = HERO_DETAILS_MAP.get(name, ("-", "-"))
                    self.db.run_query(
                        "INSERT INTO daten (name, sterne, xp_level, dust_used, dust_needed, rarity, faction, class) VALUES (?, ?, '-', '-', '-', ?, ?, ?)",
                        (name, sterne_val, rarity, faction, cls)
                    )
                    msg = f"Added Hero: {name} ({sterne_val}★)"

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.db.run_query("INSERT INTO pulls_scrolls (name, stars, date) VALUES (?, ?, ?)", (name, sterne_val, timestamp))

            self.entry_scroll_name.delete(0, tk.END)
            self.entry_scroll_stars.delete(0, tk.END)
            self.load_pulls_history()
            self.app.update_global_data()
            self.show_pulls_status(msg, self.theme.green)

        except ValueError:
            self.show_pulls_status("Stars must be a valid integer.", self.theme.red)

    def process_egg_pull(self, _event: Optional[tk.Event] = None) -> None:
        """Processes and logs a pet egg pull, upgrading pet stars if higher."""
        name = self.entry_egg_name.get().strip().title()
        sterne = self.entry_egg_stars.get().strip()

        if not sterne:
            self.show_pulls_status("Please enter stars pulled.", self.theme.yellow)
            return

        if name and name not in PET_NAMES:
            self.show_pulls_status(f"Pet '{name}' is not in the allowed list.", self.theme.yellow)
            return

        try:
            sterne_val = int(sterne)
            if not (0 <= sterne_val <= 12):
                self.show_pulls_status("Stars must be between 0 and 12.", self.theme.yellow)
                return

            msg = "Logged Egg Pull (Stars only)"
            if name:
                existing = self.db.fetch_one("SELECT id, sterne FROM pets WHERE name = ?", (name,))
                if existing:
                    curr_s = -1 if existing[1] == "-" else int(existing[1])
                    if sterne_val > curr_s:
                        self.db.run_query("UPDATE pets SET sterne = ? WHERE id = ?", (sterne_val, existing[0]))
                        msg = f"Updated Pet: {name} (Now {sterne_val}★)"
                    else:
                        msg = f"Logged Pull for {name} (Current: {existing[1]}★)"
                else:
                    self.db.run_query(
                        "INSERT INTO pets (name, sterne, bond_level, feathers_used, feathers_needed) VALUES (?, ?, '-', '-', '-')",
                        (name, sterne_val)
                    )
                    msg = f"Added Pet: {name} ({sterne_val}★)"

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.db.run_query("INSERT INTO pulls_eggs (name, stars, date) VALUES (?, ?, ?)", (name, sterne_val, timestamp))

            self.entry_egg_name.delete(0, tk.END)
            self.entry_egg_stars.delete(0, tk.END)
            self.load_pulls_history()
            self.app.update_global_data()
            self.show_pulls_status(msg, self.theme.green)

        except ValueError:
            self.show_pulls_status("Stars must be a valid integer.", self.theme.red)

    # ==========================================
    # --- LUCK ANALYTICS SUB-TAB ---
    # ==========================================

    def _build_luck_ui(self) -> None:
        container = tk.Frame(self.tab_luck, bg=self.theme.bg)
        container.pack(fill="both", expand=True, padx=15, pady=15)
        container.columnconfigure(0, weight=1, uniform="luck")
        container.columnconfigure(1, weight=1, uniform="luck")

        # 1. Scrolls Luck Card
        card_s_luck = CardFrame(container, self.theme, title="Scrolls Luck & Probabilities", header_color=self.theme.blue)
        card_s_luck.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        stats_s = tk.Frame(card_s_luck.body, bg=self.theme.surface)
        stats_s.pack(fill="x", pady=4)

        self.lbl_avg_scroll_stars = tk.Label(stats_s, text="Average Stars: -", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.fg)
        self.lbl_avg_scroll_stars.pack(anchor="w", pady=1)

        self.lbl_total_scrolls = tk.Label(
            stats_s, text="Total Pulled: - (Click for breakdown)",
            font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.blue, cursor="hand2"
        )
        self.lbl_total_scrolls.pack(anchor="w", pady=1)
        self.lbl_total_scrolls.bind("<Button-1>", self.show_scroll_breakdown)

        self.lbl_weighted_scroll_luck = tk.Label(stats_s, text="Weighted Luck: -", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.green)
        self.lbl_weighted_scroll_luck.pack(anchor="w", pady=1)

        # 2. Eggs Luck Card
        card_e_luck = CardFrame(container, self.theme, title="Eggs Luck & Probabilities", header_color=self.theme.yellow)
        card_e_luck.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        stats_e = tk.Frame(card_e_luck.body, bg=self.theme.surface)
        stats_e.pack(fill="x", pady=4)

        self.lbl_avg_egg_stars = tk.Label(stats_e, text="Average Stars: -", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.fg)
        self.lbl_avg_egg_stars.pack(anchor="w", pady=1)

        self.lbl_total_eggs = tk.Label(
            stats_e, text="Total Pulled: - (Click for breakdown)",
            font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.yellow, cursor="hand2"
        )
        self.lbl_total_eggs.pack(anchor="w", pady=1)
        self.lbl_total_eggs.bind("<Button-1>", self.show_egg_breakdown)

        self.lbl_weighted_egg_luck = tk.Label(stats_e, text="Weighted Luck: -", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.green)
        self.lbl_weighted_egg_luck.pack(anchor="w", pady=1)

        # Matplotlib Figures
        if MATPLOTLIB_AVAILABLE:
            # Scroll Plot
            self.fig_scroll, self.ax_scroll = plt.subplots(figsize=(4.5, 3.2), dpi=100)
            self.fig_scroll.patch.set_facecolor(self.theme.bg)
            self.canvas_scroll = FigureCanvasTkAgg(self.fig_scroll, master=card_s_luck.body)
            self.canvas_scroll.get_tk_widget().pack(fill="both", expand=True, pady=4)
            self.canvas_scroll.mpl_connect("motion_notify_event", self._on_scroll_hover)

            # Egg Plot
            self.fig_egg, self.ax_egg = plt.subplots(figsize=(4.5, 3.2), dpi=100)
            self.fig_egg.patch.set_facecolor(self.theme.bg)
            self.canvas_egg = FigureCanvasTkAgg(self.fig_egg, master=card_e_luck.body)
            self.canvas_egg.get_tk_widget().pack(fill="both", expand=True, pady=4)
            self.canvas_egg.mpl_connect("motion_notify_event", self._on_egg_hover)

            self.sc_scroll = None
            self.annot_scroll = None
            self.sc_egg = None
            self.annot_egg = None

        # 3. Reference Tables Frame Below Graphs
        ref_frame = tk.Frame(container, bg=self.theme.bg)
        ref_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ref_frame.columnconfigure(0, weight=1)
        ref_frame.columnconfigure(1, weight=1)

        # Scroll Odds Card
        card_scroll_odds = CardFrame(ref_frame, self.theme, title="ℹ️ Official Scroll Chances & Quality Rates", header_color=self.theme.blue, padding=10)
        card_scroll_odds.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        tk.Label(
            card_scroll_odds.body,
            text="● Quality: Rare Scroll: 2% Leg / 38% Epic / 60% Rare | Epic Scroll: 15% Leg / 85% Epic",
            font=self.theme.fonts["small_bold"],
            bg=self.theme.surface,
            fg=self.theme.blue
        ).pack(anchor="w", pady=(0, 4))

        s_stars_row1 = " | ".join([f"{s}★: {SCROLL_STAR_CHANCES[s-1]:.2f}%" for s in range(1, 7)])
        s_stars_row2 = " | ".join([f"{s}★: {SCROLL_STAR_CHANCES[s-1]:.3f}%" for s in range(7, 13)])
        tk.Label(
            card_scroll_odds.body,
            text=f"{s_stars_row1}\n{s_stars_row2}",
            font=self.theme.fonts["small"],
            bg=self.theme.surface,
            fg=self.theme.fg,
            justify="left"
        ).pack(anchor="w")

        # Egg Odds Card
        card_egg_odds = CardFrame(ref_frame, self.theme, title="ℹ️ Official Egg Star Probability Rates", header_color=self.theme.yellow, padding=10)
        card_egg_odds.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        e_stars_row1 = " | ".join([f"{s}★: {EGG_STAR_CHANCES[s-1]:.2f}%" for s in range(1, 7)])
        e_stars_row2 = " | ".join([f"{s}★: {EGG_STAR_CHANCES[s-1]:.3f}%" for s in range(7, 13)])
        tk.Label(
            card_egg_odds.body,
            text=f"{e_stars_row1}\n{e_stars_row2}",
            font=self.theme.fonts["small"],
            bg=self.theme.surface,
            fg=self.theme.fg,
            justify="left"
        ).pack(anchor="w", pady=(4, 0))

    # ==========================================
    # --- PACING & ACHIEVEMENTS SUB-TAB ---
    # ==========================================

    def _build_pacing_ui(self) -> None:
        """Builds the Pulls Pacing and Milestone Achievement tracker interface for Rare Scrolls, Epic Scrolls, and Eggs."""
        pacing_container = tk.Frame(self.tab_pacing, bg=self.theme.bg)
        pacing_container.pack(fill="both", expand=True, padx=20, pady=16)

        # 1. Days Elapsed Config Card (Two Timelines: Scrolls = 07.Jan.2024, Eggs = 07.Nov.2022)
        card_config = CardFrame(
            pacing_container,
            self.theme,
            title="⏱️ Pacing Timelines & Starting Dates",
            header_color=self.theme.blue,
            padding=10
        )
        card_config.pack(fill="x", pady=(0, 10))

        cfg_grid = tk.Frame(card_config.body, bg=self.theme.surface)
        cfg_grid.pack(fill="x", pady=2)
        cfg_grid.columnconfigure(0, weight=1, uniform="pacing_timeline")
        cfg_grid.columnconfigure(1, weight=1, uniform="pacing_timeline")

        # Left Timeline: Scrolls (07.Jan.2024)
        tl_scrolls = tk.Frame(cfg_grid, bg=self.theme.surface)
        tl_scrolls.grid(row=0, column=0, sticky="w", padx=(0, 15))

        tk.Label(
            tl_scrolls, text="📜 Scrolls Days (Since 07.Jan.2024):",
            font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.blue
        ).pack(side="left", padx=(0, 6))

        entry_scrolls_days = ModernEntry(tl_scrolls, self.theme, textvariable=self.pacing_scrolls_days_var, width=8)
        entry_scrolls_days.pack(side="left", padx=(0, 8))
        entry_scrolls_days.bind("<KeyRelease>", lambda _e: self.on_pacing_change())
        entry_scrolls_days.bind("<FocusOut>", lambda _e: self.on_pacing_change())

        ModernButton(
            tl_scrolls, self.theme, text="📅 Reset", variant="neutral",
            command=self.reset_pacing_scrolls_days_to_today, padx=8, pady=2
        ).pack(side="left")

        # Right Timeline: Eggs (07.Nov.2022)
        tl_eggs = tk.Frame(cfg_grid, bg=self.theme.surface)
        tl_eggs.grid(row=0, column=1, sticky="w", padx=(15, 0))

        tk.Label(
            tl_eggs, text="🥚 Eggs Days (Since 07.Nov.2022):",
            font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.yellow
        ).pack(side="left", padx=(0, 6))

        entry_eggs_days = ModernEntry(tl_eggs, self.theme, textvariable=self.pacing_eggs_days_var, width=8)
        entry_eggs_days.pack(side="left", padx=(0, 8))
        entry_eggs_days.bind("<KeyRelease>", lambda _e: self.on_pacing_change())
        entry_eggs_days.bind("<FocusOut>", lambda _e: self.on_pacing_change())

        ModernButton(
            tl_eggs, self.theme, text="📅 Reset", variant="neutral",
            command=self.reset_pacing_eggs_days_to_today, padx=8, pady=2
        ).pack(side="left")

        # 2. 3-Column Dashboards Grid (Rare Scrolls | Epic Scrolls | Pet Eggs)
        dash_container = tk.Frame(pacing_container, bg=self.theme.bg)
        dash_container.pack(fill="both", expand=True)
        for c in range(3):
            dash_container.columnconfigure(c, weight=1, uniform="pacing_dash")

        # --- 1. Rare Scrolls Dashboard ---
        card_rare = CardFrame(dash_container, self.theme, title="📜 Rare Scrolls Pacing", header_color=self.theme.blue, padding=12)
        card_rare.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # Rare Inputs
        r_in = tk.Frame(card_rare.body, bg=self.theme.surface)
        r_in.pack(fill="x", pady=(0, 8))

        tk.Label(r_in, text="Opened:", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.blue).grid(row=0, column=0, sticky="w", pady=2)
        e_ro = ModernEntry(r_in, self.theme, textvariable=self.pacing_rare_scrolls_var, width=10)
        e_ro.grid(row=0, column=1, sticky="w", padx=(4, 0), pady=2)
        e_ro.bind("<KeyRelease>", lambda _e: self.on_pacing_change())

        tk.Label(r_in, text="Goal 1 Target:", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.text_dim).grid(row=1, column=0, sticky="w", pady=2)
        e_rg1 = ModernEntry(r_in, self.theme, textvariable=self.pacing_rare_target1_var, width=10)
        e_rg1.grid(row=1, column=1, sticky="w", padx=(4, 0), pady=2)
        e_rg1.bind("<KeyRelease>", lambda _e: self.on_pacing_change())

        tk.Label(r_in, text="Goal 2 Target:", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.text_dim).grid(row=2, column=0, sticky="w", pady=2)
        e_rg2 = ModernEntry(r_in, self.theme, textvariable=self.pacing_rare_target2_var, width=10)
        e_rg2.grid(row=2, column=1, sticky="w", padx=(4, 0), pady=2)
        e_rg2.bind("<KeyRelease>", lambda _e: self.on_pacing_change())

        self.lbl_rare_rates = tk.Label(card_rare.body, text="● Velocity: -", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.fg)
        self.lbl_rare_rates.pack(anchor="w", pady=(4, 6))

        self.lbl_rare_g1 = tk.Label(card_rare.body, text="🎯 Goal 1: -", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.fg, justify="left")
        self.lbl_rare_g1.pack(anchor="w", pady=2)

        self.lbl_rare_g2 = tk.Label(card_rare.body, text="🎯 Goal 2: -", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.fg, justify="left")
        self.lbl_rare_g2.pack(anchor="w", pady=2)

        # --- 2. Epic Scrolls Dashboard ---
        card_epic = CardFrame(dash_container, self.theme, title="📜 Epic Scrolls Pacing", header_color=self.theme.purple, padding=12)
        card_epic.grid(row=0, column=1, sticky="nsew", padx=5)

        # Epic Inputs
        ep_in = tk.Frame(card_epic.body, bg=self.theme.surface)
        ep_in.pack(fill="x", pady=(0, 8))

        tk.Label(ep_in, text="Opened:", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.purple).grid(row=0, column=0, sticky="w", pady=2)
        e_eo = ModernEntry(ep_in, self.theme, textvariable=self.pacing_epic_scrolls_var, width=10)
        e_eo.grid(row=0, column=1, sticky="w", padx=(4, 0), pady=2)
        e_eo.bind("<KeyRelease>", lambda _e: self.on_pacing_change())

        tk.Label(ep_in, text="Goal 1 Target:", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.text_dim).grid(row=1, column=0, sticky="w", pady=2)
        e_eg1 = ModernEntry(ep_in, self.theme, textvariable=self.pacing_epic_target1_var, width=10)
        e_eg1.grid(row=1, column=1, sticky="w", padx=(4, 0), pady=2)
        e_eg1.bind("<KeyRelease>", lambda _e: self.on_pacing_change())

        tk.Label(ep_in, text="Goal 2 Target:", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.text_dim).grid(row=2, column=0, sticky="w", pady=2)
        e_eg2 = ModernEntry(ep_in, self.theme, textvariable=self.pacing_epic_target2_var, width=10)
        e_eg2.grid(row=2, column=1, sticky="w", padx=(4, 0), pady=2)
        e_eg2.bind("<KeyRelease>", lambda _e: self.on_pacing_change())

        self.lbl_epic_rates = tk.Label(card_epic.body, text="● Velocity: -", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.fg)
        self.lbl_epic_rates.pack(anchor="w", pady=(4, 6))

        self.lbl_epic_g1 = tk.Label(card_epic.body, text="🎯 Goal 1: -", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.fg, justify="left")
        self.lbl_epic_g1.pack(anchor="w", pady=2)

        self.lbl_epic_g2 = tk.Label(card_epic.body, text="🎯 Goal 2: -", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.fg, justify="left")
        self.lbl_epic_g2.pack(anchor="w", pady=2)

        # --- 3. Pet Eggs Dashboard ---
        card_egg = CardFrame(dash_container, self.theme, title="🥚 Pet Eggs Pacing", header_color=self.theme.yellow, padding=12)
        card_egg.grid(row=0, column=2, sticky="nsew", padx=(5, 0))

        # Egg Inputs
        eg_in = tk.Frame(card_egg.body, bg=self.theme.surface)
        eg_in.pack(fill="x", pady=(0, 8))

        tk.Label(eg_in, text="Opened:", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.yellow).grid(row=0, column=0, sticky="w", pady=2)
        e_go = ModernEntry(eg_in, self.theme, textvariable=self.pacing_eggs_var, width=10)
        e_go.grid(row=0, column=1, sticky="w", padx=(4, 0), pady=2)
        e_go.bind("<KeyRelease>", lambda _e: self.on_pacing_change())

        tk.Label(eg_in, text="Goal 1 Target:", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.text_dim).grid(row=1, column=0, sticky="w", pady=2)
        e_gg1 = ModernEntry(eg_in, self.theme, textvariable=self.pacing_egg_target1_var, width=10)
        e_gg1.grid(row=1, column=1, sticky="w", padx=(4, 0), pady=2)
        e_gg1.bind("<KeyRelease>", lambda _e: self.on_pacing_change())

        tk.Label(eg_in, text="Goal 2 Target:", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.text_dim).grid(row=2, column=0, sticky="w", pady=2)
        e_gg2 = ModernEntry(eg_in, self.theme, textvariable=self.pacing_egg_target2_var, width=10)
        e_gg2.grid(row=2, column=1, sticky="w", padx=(4, 0), pady=2)
        e_gg2.bind("<KeyRelease>", lambda _e: self.on_pacing_change())

        self.lbl_egg_rates = tk.Label(card_egg.body, text="● Velocity: -", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.fg)
        self.lbl_egg_rates.pack(anchor="w", pady=(4, 6))

        self.lbl_egg_g1 = tk.Label(card_egg.body, text="🎯 Goal 1: -", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.fg, justify="left")
        self.lbl_egg_g1.pack(anchor="w", pady=2)

        self.lbl_egg_g2 = tk.Label(card_egg.body, text="🎯 Goal 2: -", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.fg, justify="left")
        self.lbl_egg_g2.pack(anchor="w", pady=2)

    def reset_pacing_scrolls_days_to_today(self) -> None:
        """Resets the scrolls days elapsed input to exact number of days since 07.Jan.2024."""
        start_date = datetime(2024, 1, 7)
        calc_days = max(1, (datetime.now() - start_date).days)
        self.pacing_scrolls_days_var.set(str(calc_days))
        self.on_pacing_change()

    def reset_pacing_eggs_days_to_today(self) -> None:
        """Resets the pet eggs days elapsed input to exact number of days since 07.Nov.2022."""
        start_date = datetime(2022, 11, 7)
        calc_days = max(1, (datetime.now() - start_date).days)
        self.pacing_eggs_days_var.set(str(calc_days))
        self.on_pacing_change()

    def on_pacing_change(self) -> None:
        """Saves settings and recalculates pacing metrics."""
        self.db.set_setting("pacing_scrolls_days_elapsed", self.pacing_scrolls_days_var.get().strip())
        self.db.set_setting("pacing_eggs_days_elapsed", self.pacing_eggs_days_var.get().strip())
        self.db.set_setting("pacing_rare_scrolls_opened", self.pacing_rare_scrolls_var.get().strip())
        self.db.set_setting("pacing_rare_target1", self.pacing_rare_target1_var.get().strip())
        self.db.set_setting("pacing_rare_target2", self.pacing_rare_target2_var.get().strip())

        self.db.set_setting("pacing_epic_scrolls_opened", self.pacing_epic_scrolls_var.get().strip())
        self.db.set_setting("pacing_epic_target1", self.pacing_epic_target1_var.get().strip())
        self.db.set_setting("pacing_epic_target2", self.pacing_epic_target2_var.get().strip())

        self.db.set_setting("pacing_eggs_opened", self.pacing_eggs_var.get().strip())
        self.db.set_setting("pacing_egg_target1", self.pacing_egg_target1_var.get().strip())
        self.db.set_setting("pacing_egg_target2", self.pacing_egg_target2_var.get().strip())

        self.update_pacing_stats()

    def update_pacing_stats(self) -> None:
        """Recalculates velocity and milestone completion dates for Rare Scrolls, Epic Scrolls, and Eggs."""
        if not hasattr(self, 'lbl_rare_rates'):
            return

        from datetime import timedelta

        try:
            days_scrolls = float(self.pacing_scrolls_days_var.get().replace(',', '').strip() or 1)
        except ValueError:
            days_scrolls = 1.0

        try:
            days_eggs = float(self.pacing_eggs_days_var.get().replace(',', '').strip() or 1)
        except ValueError:
            days_eggs = 1.0

        def _calc_category(opened_str: str, days_elapsed: float, g1_str: str, g2_str: str, lbl_rate: tk.Label, lbl_g1: tk.Label, lbl_g2: tk.Label, unit: str):
            try:
                opened = int(float(opened_str.replace(',', '').strip() or 0))
            except ValueError:
                opened = 0

            try:
                g1 = int(float(g1_str.replace(',', '').strip() or 1500))
            except ValueError:
                g1 = 1500

            try:
                g2 = int(float(g2_str.replace(',', '').strip() or 3000))
            except ValueError:
                g2 = 3000

            p1 = calculate_pulls_pacing(opened, days_elapsed, g1)
            p2 = calculate_pulls_pacing(opened, days_elapsed, g2)

            lbl_rate.config(
                text=f"● Velocity: {p1['per_day']:.2f} /day | {p1['per_week']:.2f} /wk | {p1['per_year']:.1f} /yr"
            )

            # Goal 1
            if p1["pulls_left"] <= 0:
                lbl_g1.config(text=f"🎯 Goal 1 ({g1:,} {unit}): ✅ Achieved!", fg=self.theme.green)
            else:
                date_g1 = (datetime.now() + timedelta(days=p1["days_to_goal"])).strftime("%Y-%m-%d") if p1["per_day"] > 0 else "N/A"
                lbl_g1.config(
                    text=f"🎯 Goal 1 ({g1:,} {unit}): {int(p1['pulls_left']):,} left\n"
                         f"   ⏱️ {p1['days_to_goal']:,.1f}d ({p1['weeks_to_goal']:,.1f}w) — Date: {date_g1}",
                    fg=self.theme.fg
                )

            # Goal 2
            if p2["pulls_left"] <= 0:
                lbl_g2.config(text=f"🎯 Goal 2 ({g2:,} {unit}): ✅ Achieved!", fg=self.theme.green)
            else:
                date_g2 = (datetime.now() + timedelta(days=p2["days_to_goal"])).strftime("%Y-%m-%d") if p2["per_day"] > 0 else "N/A"
                lbl_g2.config(
                    text=f"🎯 Goal 2 ({g2:,} {unit}): {int(p2['pulls_left']):,} left\n"
                         f"   ⏱️ {p2['days_to_goal']:,.1f}d ({p2['weeks_to_goal']:,.1f}w) — Date: {date_g2}",
                    fg=self.theme.fg
                )

        _calc_category(
            self.pacing_rare_scrolls_var.get(), days_scrolls, self.pacing_rare_target1_var.get(), self.pacing_rare_target2_var.get(),
            self.lbl_rare_rates, self.lbl_rare_g1, self.lbl_rare_g2, "Scrolls"
        )
        _calc_category(
            self.pacing_epic_scrolls_var.get(), days_scrolls, self.pacing_epic_target1_var.get(), self.pacing_epic_target2_var.get(),
            self.lbl_epic_rates, self.lbl_epic_g1, self.lbl_epic_g2, "Scrolls"
        )
        _calc_category(
            self.pacing_eggs_var.get(), days_eggs, self.pacing_egg_target1_var.get(), self.pacing_egg_target2_var.get(),
            self.lbl_egg_rates, self.lbl_egg_g1, self.lbl_egg_g2, "Eggs"
        )

    def update_luck_stats(self) -> None:
        """Calculates pull averages, weighted luck index, and refreshes the probability curves."""
        self.update_pacing_stats()
        # Scrolls stats
        res_scrolls = self.db.fetch_one("SELECT AVG(stars), COUNT(*) FROM pulls_scrolls")
        avg_scrolls = res_scrolls[0] if res_scrolls and res_scrolls[0] is not None else 0.0
        count_scrolls = res_scrolls[1] if res_scrolls else 0

        scroll_dist_rows = self.db.fetch_all("SELECT stars, COUNT(*) FROM pulls_scrolls GROUP BY stars")
        self.scroll_dist_map = {r[0]: r[1] for r in scroll_dist_rows}

        # Eggs stats
        res_eggs = self.db.fetch_one("SELECT AVG(stars), COUNT(*) FROM pulls_eggs")
        avg_eggs = res_eggs[0] if res_eggs and res_eggs[0] is not None else 0.0
        count_eggs = res_eggs[1] if res_eggs else 0

        egg_dist_rows = self.db.fetch_all("SELECT stars, COUNT(*) FROM pulls_eggs GROUP BY stars")
        self.egg_dist_map = {r[0]: r[1] for r in egg_dist_rows}

        self.lbl_avg_scroll_stars.config(text=f"Average Stars: {avg_scrolls:.2f}★")
        self.lbl_total_scrolls.config(text=f"Total Pulled: {count_scrolls} (Click for breakdown)")

        # Weighted Luck Scrolls
        w_score_s, w_count_s = 0.0, 0
        for s, c_val in self.scroll_dist_map.items():
            if 1 <= s <= 12:
                chance = SCROLL_STAR_CHANCES[s - 1]
                if chance > 0:
                    w_score_s += c_val * (100.0 / chance)
                    w_count_s += c_val

        if w_count_s > 0:
            exp_score = w_count_s * 12.0
            luck_pct = (w_score_s / exp_score) * 100.0
            color = self.theme.green if luck_pct >= 100 else self.theme.yellow
            self.lbl_weighted_scroll_luck.config(text=f"Weighted Luck: {luck_pct:.2f}%", fg=color)
        else:
            self.lbl_weighted_scroll_luck.config(text="Weighted Luck: -", fg=self.theme.fg)

        # Weighted Luck Eggs
        self.lbl_avg_egg_stars.config(text=f"Average Stars: {avg_eggs:.2f}★")
        self.lbl_total_eggs.config(text=f"Total Pulled: {count_eggs} (Click for breakdown)")

        w_score_e, w_count_e = 0.0, 0
        for s, c_val in self.egg_dist_map.items():
            if 1 <= s <= 12:
                chance = EGG_STAR_CHANCES[s - 1]
                if chance > 0:
                    w_score_e += c_val * (100.0 / chance)
                    w_count_e += c_val

        if w_count_e > 0:
            exp_score = w_count_e * 12.0
            luck_pct = (w_score_e / exp_score) * 100.0
            color = self.theme.green if luck_pct >= 100 else self.theme.yellow
            self.lbl_weighted_egg_luck.config(text=f"Weighted Luck: {luck_pct:.2f}%", fg=color)
        else:
            self.lbl_weighted_egg_luck.config(text="Weighted Luck: -", fg=self.theme.fg)

        # Update Matplotlib Charts
        if MATPLOTLIB_AVAILABLE:
            stars_x = list(range(1, 13))

            # --- Scroll Graph ---
            self.ax_scroll.clear()
            self.ax_scroll.plot(stars_x, SCROLL_STAR_CHANCES, marker='o', linestyle='--', label='Game Chance', color='#7982a9', alpha=0.8)

            self.user_scroll_probs = [0.0] * 12
            if count_scrolls > 0:
                for s, count in scroll_dist_rows:
                    if 1 <= s <= 12:
                        self.user_scroll_probs[s - 1] = (count / count_scrolls) * 100.0

            self.ax_scroll.plot(stars_x, self.user_scroll_probs, marker='o', linestyle='-', label='Your Pulls', color=self.theme.blue, linewidth=2)
            self.sc_scroll = self.ax_scroll.scatter(stars_x, self.user_scroll_probs, s=60, alpha=0)

            self.annot_scroll = self.ax_scroll.annotate(
                "", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.5", fc=self.theme.surface, ec=self.theme.border, lw=1),
                color=self.theme.fg,
                arrowprops=dict(arrowstyle="->", color=self.theme.blue, lw=1.2),
                zorder=10,
                fontsize=8
            )
            self.annot_scroll.set_visible(False)

            self._style_luck_chart(self.ax_scroll, "Scrolls Distribution")
            self.canvas_scroll.draw()

            # --- Egg Graph ---
            self.ax_egg.clear()
            self.ax_egg.plot(stars_x, EGG_STAR_CHANCES, marker='o', linestyle='--', label='Game Chance', color='#888888', alpha=0.8)

            self.user_egg_probs = [0.0] * 12
            if count_eggs > 0:
                for s, count in egg_dist_rows:
                    if 1 <= s <= 12:
                        self.user_egg_probs[s - 1] = (count / count_eggs) * 100.0

            self.ax_egg.plot(stars_x, self.user_egg_probs, marker='o', linestyle='-', label='Your Pulls', color=self.theme.yellow, linewidth=2)
            self.sc_egg = self.ax_egg.scatter(stars_x, self.user_egg_probs, s=60, alpha=0)

            self.annot_egg = self.ax_egg.annotate(
                "", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.5", fc=self.theme.surface, ec=self.theme.border, lw=1),
                color=self.theme.fg,
                arrowprops=dict(arrowstyle="->", color=self.theme.yellow, lw=1.2),
                zorder=10,
                fontsize=8
            )
            self.annot_egg.set_visible(False)

            self._style_luck_chart(self.ax_egg, "Eggs Distribution")
            self.canvas_egg.draw()

    def _style_luck_chart(self, ax: Any, title: str) -> None:
        ax.set_facecolor(self.theme.bg)
        ax.tick_params(axis='x', colors=self.theme.fg, labelsize=8)
        ax.tick_params(axis='y', colors=self.theme.fg, labelsize=8)
        for spine in ax.spines.values():
            spine.set_color(self.theme.border)
        ax.set_title(title, color=self.theme.fg, fontsize=10, fontweight="bold")
        ax.set_xlabel("Star Rating", color=self.theme.text_dim, fontsize=8)
        ax.set_ylabel("% Probability", color=self.theme.text_dim, fontsize=8)
        ax.legend(facecolor=self.theme.surface, edgecolor=self.theme.border, labelcolor=self.theme.fg, fontsize=8)
        ax.grid(True, color="#2d2d2d", linestyle='--', linewidth=0.5)

    def _on_scroll_hover(self, event: Any) -> None:
        self._on_luck_hover(event, self.canvas_scroll, self.ax_scroll, self.sc_scroll, self.annot_scroll, SCROLL_STAR_CHANCES, self.user_scroll_probs)

    def _on_egg_hover(self, event: Any) -> None:
        self._on_luck_hover(event, self.canvas_egg, self.ax_egg, self.sc_egg, self.annot_egg, EGG_STAR_CHANCES, self.user_egg_probs)

    def _on_luck_hover(self, event: Any, canvas: Any, ax: Any, sc: Any, annot: Any, game_probs: List[float], user_probs: List[float]) -> None:
        if not sc or not annot:
            return
        found = False
        if event.inaxes == ax:
            cont, ind = sc.contains(event)
            if cont:
                idx = ind["ind"][0]
                pos = sc.get_offsets()[idx]
                annot.xy = pos
                star_val = idx + 1
                g_prob = game_probs[idx]
                u_prob = user_probs[idx]
                diff = u_prob - g_prob

                text = f"{star_val}★ Rating\nGame: {g_prob:.2f}%\nYou: {u_prob:.2f}%\nDiff: {diff:+.2f}%"
                annot.set_text(text)
                annot.set_visible(True)
                canvas.draw_idle()
                found = True

        if not found and annot.get_visible():
            annot.set_visible(False)
            canvas.draw_idle()

    def show_scroll_breakdown(self, event: tk.Event) -> None:
        if not self.scroll_dist_map:
            return
        menu = tk.Menu(self, tearoff=0, bg=self.theme.surface, fg=self.theme.fg, activebackground=self.theme.btn_bg, activeforeground="#ffffff")
        menu.add_command(label="📜 Scrolls Pull Breakdown", state="disabled")
        menu.add_separator()
        for stars in range(1, 13):
            count = self.scroll_dist_map.get(stars, 0)
            if count > 0:
                menu.add_command(label=f"{stars}★ Stars: {count:,} pulls")
        menu.post(event.x_root, event.y_root)

    def show_egg_breakdown(self, event: tk.Event) -> None:
        if not self.egg_dist_map:
            return
        menu = tk.Menu(self, tearoff=0, bg=self.theme.surface, fg=self.theme.fg, activebackground=self.theme.btn_bg, activeforeground="#ffffff")
        menu.add_command(label="🥚 Eggs Pull Breakdown", state="disabled")
        menu.add_separator()
        for stars in range(1, 13):
            count = self.egg_dist_map.get(stars, 0)
            if count > 0:
                menu.add_command(label=f"{stars}★ Stars: {count:,} pulls")
        menu.post(event.x_root, event.y_root)

    # ==========================================
    # --- SCROLLS HISTORY SUB-TAB ---
    # ==========================================

    def _build_history_scrolls_ui(self) -> None:
        # Edit Card
        card_edit = CardFrame(self.tab_dp_scrolls, self.theme, padding=8)
        card_edit.pack(fill="x", padx=10, pady=(8, 4))

        row = tk.Frame(card_edit.body, bg=self.theme.surface)
        row.pack(fill="x")

        tk.Label(row, text="Date:", font=self.theme.fonts["body"], bg=self.theme.surface, fg=self.theme.fg).pack(side="left", padx=4)
        self.entry_scroll_hist_date = ModernEntry(row, self.theme, width=18)
        self.entry_scroll_hist_date.pack(side="left", padx=4)

        tk.Label(row, text="Hero:", font=self.theme.fonts["body"], bg=self.theme.surface, fg=self.theme.fg).pack(side="left", padx=4)
        self.entry_scroll_hist_name = ModernEntry(row, self.theme, width=15)
        self.entry_scroll_hist_name.pack(side="left", padx=4)

        tk.Label(row, text="Stars:", font=self.theme.fonts["body"], bg=self.theme.surface, fg=self.theme.fg).pack(side="left", padx=4)
        self.entry_scroll_hist_stars = ModernEntry(row, self.theme, width=6)
        self.entry_scroll_hist_stars.pack(side="left", padx=4)

        ModernButton(row, self.theme, text="Update", variant="warning", command=self.update_scroll_record).pack(side="left", padx=4)
        ModernButton(row, self.theme, text="Delete", variant="danger", command=self.delete_scroll_record).pack(side="left", padx=4)
        ModernButton(row, self.theme, text="Import CSV", variant="neutral", command=self.import_scrolls_csv).pack(side="left", padx=4)

        # Table Card
        tree_card = CardFrame(self.tab_dp_scrolls, self.theme, padding=2)
        tree_card.pack(fill="both", expand=True, padx=10, pady=(4, 8))

        sb = ModernScrollbar(tree_card.body, self.theme)
        sb.pack(side="right", fill="y")

        cols = ("Date", "Name", "Stars")
        self.tree_scrolls = ttk.Treeview(tree_card.body, columns=cols, show="headings", yscrollcommand=sb.set)
        sb.config(command=self.tree_scrolls.yview)

        for c in cols:
            self.tree_scrolls.heading(c, text=c, command=lambda col=c: self.sort_scroll_column(col, False))
            self.tree_scrolls.column(c, width=150, anchor="center")

        self.tree_scrolls.pack(fill="both", expand=True)
        setup_treeview_striping(self.tree_scrolls, self.theme)
        self.tree_scrolls.bind("<ButtonRelease-1>", self.select_scroll_item)

    # ==========================================
    # --- EGGS HISTORY SUB-TAB ---
    # ==========================================

    def _build_history_eggs_ui(self) -> None:
        card_edit = CardFrame(self.tab_dp_eggs, self.theme, padding=8)
        card_edit.pack(fill="x", padx=10, pady=(8, 4))

        row = tk.Frame(card_edit.body, bg=self.theme.surface)
        row.pack(fill="x")

        tk.Label(row, text="Date:", font=self.theme.fonts["body"], bg=self.theme.surface, fg=self.theme.fg).pack(side="left", padx=4)
        self.entry_egg_hist_date = ModernEntry(row, self.theme, width=18)
        self.entry_egg_hist_date.pack(side="left", padx=4)

        tk.Label(row, text="Pet:", font=self.theme.fonts["body"], bg=self.theme.surface, fg=self.theme.fg).pack(side="left", padx=4)
        self.entry_egg_hist_name = ModernEntry(row, self.theme, width=15)
        self.entry_egg_hist_name.pack(side="left", padx=4)

        tk.Label(row, text="Stars:", font=self.theme.fonts["body"], bg=self.theme.surface, fg=self.theme.fg).pack(side="left", padx=4)
        self.entry_egg_hist_stars = ModernEntry(row, self.theme, width=6)
        self.entry_egg_hist_stars.pack(side="left", padx=4)

        ModernButton(row, self.theme, text="Update", variant="warning", command=self.update_egg_record).pack(side="left", padx=4)
        ModernButton(row, self.theme, text="Delete", variant="danger", command=self.delete_egg_record).pack(side="left", padx=4)
        ModernButton(row, self.theme, text="Import CSV", variant="neutral", command=self.import_eggs_csv).pack(side="left", padx=4)

        tree_card = CardFrame(self.tab_dp_eggs, self.theme, padding=2)
        tree_card.pack(fill="both", expand=True, padx=10, pady=(4, 8))

        sb = ModernScrollbar(tree_card.body, self.theme)
        sb.pack(side="right", fill="y")

        cols = ("Date", "Name", "Stars")
        self.tree_eggs = ttk.Treeview(tree_card.body, columns=cols, show="headings", yscrollcommand=sb.set)
        sb.config(command=self.tree_eggs.yview)

        for c in cols:
            self.tree_eggs.heading(c, text=c, command=lambda col=c: self.sort_egg_column(col, False))
            self.tree_eggs.column(c, width=150, anchor="center")

        self.tree_eggs.pack(fill="both", expand=True)
        setup_treeview_striping(self.tree_eggs, self.theme)
        self.tree_eggs.bind("<ButtonRelease-1>", self.select_egg_item)

    # --- History Operations ---

    def load_pulls_history(self) -> None:
        """Loads pull log records into the history tables."""
        for r in self.tree_scrolls.get_children():
            self.tree_scrolls.delete(r)
        for r in self.tree_eggs.get_children():
            self.tree_eggs.delete(r)

        scroll_rows = self.db.fetch_all("SELECT id, date, name, stars FROM pulls_scrolls ORDER BY id DESC")
        for idx, row in enumerate(scroll_rows):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree_scrolls.insert("", "end", iid=row[0], values=(row[1], row[2], row[3]), tags=(tag,))

        egg_rows = self.db.fetch_all("SELECT id, date, name, stars FROM pulls_eggs ORDER BY id DESC")
        for idx, row in enumerate(egg_rows):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree_eggs.insert("", "end", iid=row[0], values=(row[1], row[2], row[3]), tags=(tag,))

        self.update_luck_stats()

    def select_scroll_item(self, event: tk.Event) -> None:
        item = self.tree_scrolls.identify_row(event.y)
        if item:
            self.selected_scroll_id = item
            vals = self.tree_scrolls.item(item, "values")
            if vals:
                self.entry_scroll_hist_date.delete(0, tk.END)
                self.entry_scroll_hist_date.insert(0, vals[0])
                self.entry_scroll_hist_name.delete(0, tk.END)
                self.entry_scroll_hist_name.insert(0, vals[1])
                self.entry_scroll_hist_stars.delete(0, tk.END)
                self.entry_scroll_hist_stars.insert(0, vals[2])
        else:
            self.clear_scroll_history_entries()

    def clear_scroll_history_entries(self) -> None:
        self.tree_scrolls.selection_remove(self.tree_scrolls.selection())
        self.selected_scroll_id = None
        self.entry_scroll_hist_date.delete(0, tk.END)
        self.entry_scroll_hist_name.delete(0, tk.END)
        self.entry_scroll_hist_stars.delete(0, tk.END)

    def update_scroll_record(self) -> None:
        if not self.selected_scroll_id:
            return
        d = self.entry_scroll_hist_date.get()
        n = self.entry_scroll_hist_name.get()
        s = self.entry_scroll_hist_stars.get()
        self.db.run_query("UPDATE pulls_scrolls SET date=?, name=?, stars=? WHERE id=?", (d, n, s, self.selected_scroll_id))
        self.load_pulls_history()
        self.clear_scroll_history_entries()

    def delete_scroll_record(self) -> None:
        if not self.selected_scroll_id:
            return
        if messagebox.askyesno("Confirm", "Delete this scroll pull record?"):
            self.db.run_query("DELETE FROM pulls_scrolls WHERE id=?", (self.selected_scroll_id,))
            self.load_pulls_history()
            self.clear_scroll_history_entries()

    def select_egg_item(self, event: tk.Event) -> None:
        item = self.tree_eggs.identify_row(event.y)
        if item:
            self.selected_egg_id = item
            vals = self.tree_eggs.item(item, "values")
            if vals:
                self.entry_egg_hist_date.delete(0, tk.END)
                self.entry_egg_hist_date.insert(0, vals[0])
                self.entry_egg_hist_name.delete(0, tk.END)
                self.entry_egg_hist_name.insert(0, vals[1])
                self.entry_egg_hist_stars.delete(0, tk.END)
                self.entry_egg_hist_stars.insert(0, vals[2])
        else:
            self.clear_egg_history_entries()

    def clear_egg_history_entries(self) -> None:
        self.tree_eggs.selection_remove(self.tree_eggs.selection())
        self.selected_egg_id = None
        self.entry_egg_hist_date.delete(0, tk.END)
        self.entry_egg_hist_name.delete(0, tk.END)
        self.entry_egg_hist_stars.delete(0, tk.END)

    def update_egg_record(self) -> None:
        if not self.selected_egg_id:
            return
        d = self.entry_egg_hist_date.get()
        n = self.entry_egg_hist_name.get()
        s = self.entry_egg_hist_stars.get()
        self.db.run_query("UPDATE pulls_eggs SET date=?, name=?, stars=? WHERE id=?", (d, n, s, self.selected_egg_id))
        self.load_pulls_history()
        self.clear_egg_history_entries()

    def delete_egg_record(self) -> None:
        if not self.selected_egg_id:
            return
        if messagebox.askyesno("Confirm", "Delete this egg pull record?"):
            self.db.run_query("DELETE FROM pulls_eggs WHERE id=?", (self.selected_egg_id,))
            self.load_pulls_history()
            self.clear_egg_history_entries()

    def import_pulls_csv_generic(self, table_name: str) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            count_added = 0
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if not row:
                        continue
                    star_val = None
                    for cell in row:
                        try:
                            val = int(cell.strip())
                            if 0 <= val <= 12:
                                star_val = val
                                break
                        except ValueError:
                            continue
                    if star_val is not None:
                        self.db.run_query(f"INSERT INTO {table_name} (name, stars, date) VALUES (?, ?, ?)", ("", star_val, timestamp))
                        count_added += 1

            self.load_pulls_history()
            self.show_pulls_status(f"Imported {count_added} records into {table_name.replace('pulls_', '')}.", self.theme.green)
        except Exception as e:
            self.show_pulls_status(f"Import failed: {e}", self.theme.red)

    def import_scrolls_csv(self) -> None:
        self.import_pulls_csv_generic("pulls_scrolls")

    def import_eggs_csv(self) -> None:
        self.import_pulls_csv_generic("pulls_eggs")

    def sort_scroll_column(self, col: str, reverse: bool) -> None:
        self.scroll_sort_col, self.scroll_sort_reverse = col, reverse
        items = [(self.tree_scrolls.set(k, col), k) for k in self.tree_scrolls.get_children('')]

        def sort_key(val: str) -> Any:
            try:
                return int(val)
            except ValueError:
                return val.lower()

        items.sort(key=lambda t: sort_key(t[0]), reverse=reverse)
        for index, (_val, k) in enumerate(items):
            self.tree_scrolls.move(k, '', index)
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree_scrolls.item(k, tags=(tag,))

        for c in ("Date", "Name", "Stars"):
            self.tree_scrolls.heading(c, text=c)
        arrow = " ▼" if reverse else " ▲"
        self.tree_scrolls.heading(col, text=col + arrow, command=lambda: self.sort_scroll_column(col, not reverse))

    def sort_egg_column(self, col: str, reverse: bool) -> None:
        self.egg_sort_col, self.egg_sort_reverse = col, reverse
        items = [(self.tree_eggs.set(k, col), k) for k in self.tree_eggs.get_children('')]

        def sort_key(val: str) -> Any:
            try:
                return int(val)
            except ValueError:
                return val.lower()

        items.sort(key=lambda t: sort_key(t[0]), reverse=reverse)
        for index, (_val, k) in enumerate(items):
            self.tree_eggs.move(k, '', index)
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree_eggs.item(k, tags=(tag,))

        for c in ("Date", "Name", "Stars"):
            self.tree_eggs.heading(c, text=c)
        arrow = " ▼" if reverse else " ▲"
        self.tree_eggs.heading(col, text=col + arrow, command=lambda: self.sort_egg_column(col, not reverse))
