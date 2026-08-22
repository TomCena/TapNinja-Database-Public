"""
Conquest (Buildings) Tab module.
Manages building upgrade levels, future target planning, construction multipliers,
and total resource & time cost summaries.
"""

import tkinter as tk
from tkinter import ttk
import math
from typing import Any, Dict, Optional

from constants import (
    BUILDINGS_LIST, BUILDING_MAX_LEVEL,
    CASTLE_COSTS, OTHER_BUILDING_COSTS, ORE_MINE_COSTS,
    format_seconds, calculate_conquest_upgrade_time
)
from ui_components import CardFrame, ModernButton, ModernEntry


class ConquestTab(tk.Frame):
    """Encapsulates Conquest building upgrades, target costs, and research multipliers."""

    def __init__(self, parent: tk.Widget, app: Any):
        super().__init__(parent, bg=app.theme.bg)
        self.app = app
        self.db = app.db
        self.theme = app.theme

        # State Variables for Multipliers & Stored Resources
        self.const_speed_var = tk.StringVar(value=self.db.get_setting("const_speed", "100"))
        self.const_lumber_var = tk.StringVar(value=self.db.get_setting("const_lumber", "100"))
        self.const_ore_var = tk.StringVar(value=self.db.get_setting("const_ore", "100"))

        self.stored_lumber_var = tk.StringVar(value=self.db.get_setting("stored_lumber", "0"))
        self.stored_ore_var = tk.StringVar(value=self.db.get_setting("stored_ore", "0"))
        self.sawmill_1_rate_var = tk.StringVar(value=self.db.get_setting("sawmill_1_rate", "9091"))
        self.sawmill_2_rate_var = tk.StringVar(value=self.db.get_setting("sawmill_2_rate", "9091"))
        self.oremine_1_rate_var = tk.StringVar(value=self.db.get_setting("oremine_1_rate", "3382"))
        self.oremine_2_rate_var = tk.StringVar(value=self.db.get_setting("oremine_2_rate", "3382"))

        self.building_entries: Dict[str, ModernEntry] = {}
        self.building_target_entries: Dict[str, ModernEntry] = {}
        self.building_stats_labels: Dict[str, Dict[str, tk.Label]] = {}

        self._build_ui()

    def _build_ui(self) -> None:
        # 1. Construction Multipliers & Stored Resources Card
        card_multipliers = CardFrame(self, self.theme, title="Construction Multipliers & Stored Production Resources", header_color=self.theme.yellow, padding=8)
        card_multipliers.pack(fill="x", padx=15, pady=(10, 4))

        # Row 1: Multipliers
        m_row1 = tk.Frame(card_multipliers.body, bg=self.theme.surface)
        m_row1.pack(fill="x", pady=(0, 4))

        tk.Label(m_row1, text="Speed (%):", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.fg).pack(side="left", padx=(0, 4))
        self.entry_const_speed = ModernEntry(m_row1, self.theme, textvariable=self.const_speed_var, width=6, justify="center")
        self.entry_const_speed.pack(side="left", padx=(0, 15))

        tk.Label(m_row1, text="Lumber Cost (%):", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.yellow).pack(side="left", padx=(0, 4))
        self.entry_const_lumber = ModernEntry(m_row1, self.theme, textvariable=self.const_lumber_var, width=6, justify="center")
        self.entry_const_lumber.pack(side="left", padx=(0, 15))

        tk.Label(m_row1, text="Ore Cost (%):", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.green).pack(side="left", padx=(0, 4))
        self.entry_const_ore = ModernEntry(m_row1, self.theme, textvariable=self.const_ore_var, width=6, justify="center")
        self.entry_const_ore.pack(side="left", padx=(0, 15))

        for entry in (self.entry_const_speed, self.entry_const_lumber, self.entry_const_ore):
            entry.bind('<FocusOut>', lambda e: self.save_building_settings())
            entry.bind('<Return>', lambda e: self.save_building_settings())

        # Row 2: Stored Resources & Production Rates
        m_row2 = tk.Frame(card_multipliers.body, bg=self.theme.surface)
        m_row2.pack(fill="x", pady=(2, 0))

        tk.Label(m_row2, text="Stored Lumber:", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.yellow).pack(side="left", padx=(0, 4))
        self.entry_stored_lumber = ModernEntry(m_row2, self.theme, textvariable=self.stored_lumber_var, width=10)
        self.entry_stored_lumber.pack(side="left", padx=(0, 12))

        tk.Label(m_row2, text="Stored Ore:", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.green).pack(side="left", padx=(0, 4))
        self.entry_stored_ore = ModernEntry(m_row2, self.theme, textvariable=self.stored_ore_var, width=10)
        self.entry_stored_ore.pack(side="left", padx=(0, 15))

        tk.Label(m_row2, text="Sawmills Rate (L/h):", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.fg).pack(side="left", padx=(0, 4))
        self.entry_sawmill1 = ModernEntry(m_row2, self.theme, textvariable=self.sawmill_1_rate_var, width=7)
        self.entry_sawmill1.pack(side="left", padx=(0, 4))
        self.entry_sawmill2 = ModernEntry(m_row2, self.theme, textvariable=self.sawmill_2_rate_var, width=7)
        self.entry_sawmill2.pack(side="left", padx=(0, 15))

        tk.Label(m_row2, text="Ore Mines Rate (O/h):", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.fg).pack(side="left", padx=(0, 4))
        self.entry_oremine1 = ModernEntry(m_row2, self.theme, textvariable=self.oremine_1_rate_var, width=7)
        self.entry_oremine1.pack(side="left", padx=(0, 4))
        self.entry_oremine2 = ModernEntry(m_row2, self.theme, textvariable=self.oremine_2_rate_var, width=7)
        self.entry_oremine2.pack(side="left", padx=(0, 4))

        for entry in (self.entry_stored_lumber, self.entry_stored_ore, self.entry_sawmill1, self.entry_sawmill2, self.entry_oremine1, self.entry_oremine2):
            entry.bind('<KeyRelease>', lambda e: self.save_building_settings())
            entry.bind('<FocusOut>', lambda e: self.save_building_settings())
            entry.bind('<Return>', lambda e: self.save_building_settings())

        # 2. Sub-Notebook for Levels vs Targets
        self.buildings_notebook = ttk.Notebook(self)
        self.buildings_notebook.pack(fill="both", expand=True, padx=15, pady=4)

        self.tab_levels = tk.Frame(self.buildings_notebook, bg=self.theme.bg)
        self.tab_targets = tk.Frame(self.buildings_notebook, bg=self.theme.bg)

        self.buildings_notebook.add(self.tab_levels, text="Current Levels")
        self.buildings_notebook.add(self.tab_targets, text="Target Planner")

        for c in range(2):
            self.tab_levels.columnconfigure(c, weight=1, uniform="bcol")
            self.tab_targets.columnconfigure(c, weight=1, uniform="bcol")

        # 3. Summary Cards
        # Total Spent Card (Levels Tab)
        self.spent_card = CardFrame(self.tab_levels, self.theme, title="Total Resources Spent", header_color=self.theme.blue, padding=8)
        self.spent_card.grid(row=6, column=0, columnspan=2, sticky="ew", padx=5, pady=8)

        s_bar = tk.Frame(self.spent_card.body, bg=self.theme.surface)
        s_bar.pack(fill="x")

        self.lbl_spent_time = tk.Label(s_bar, text="Time: 0s", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.fg)
        self.lbl_spent_time.pack(side="left", expand=True)

        self.lbl_spent_lumber = tk.Label(s_bar, text="Lumber: 0", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.yellow)
        self.lbl_spent_lumber.pack(side="left", expand=True)

        self.lbl_spent_ore = tk.Label(s_bar, text="Ore: 0", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.green)
        self.lbl_spent_ore.pack(side="left", expand=True)

        # Total Target Cost Card (Targets Tab)
        self.target_cost_card = CardFrame(self.tab_targets, self.theme, title="Total Target Cost Required", header_color=self.theme.yellow, padding=8)
        self.target_cost_card.grid(row=6, column=0, columnspan=2, sticky="ew", padx=5, pady=8)

        t_bar = tk.Frame(self.target_cost_card.body, bg=self.theme.surface)
        t_bar.pack(fill="x")

        self.lbl_target_time = tk.Label(t_bar, text="Time: 0s", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.fg)
        self.lbl_target_time.pack(side="left", expand=True)

        self.lbl_target_lumber = tk.Label(t_bar, text="Lumber: 0", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.yellow)
        self.lbl_target_lumber.pack(side="left", expand=True)

        self.lbl_target_ore = tk.Label(t_bar, text="Ore: 0", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.green)
        self.lbl_target_ore.pack(side="left", expand=True)

        # 4. Load Saved Levels
        b_data = {r[0]: r[1] for r in self.db.fetch_all("SELECT name, level FROM buildings")}

        # 5. Populate Building Cards
        for i, text in enumerate(BUILDINGS_LIST):
            # --- LEVELS TAB CARD ---
            box = CardFrame(self.tab_levels, self.theme, padding=8)
            if i == 0:
                box.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=4, pady=4)
            else:
                box.grid(row=(i + 1) // 2, column=(i + 1) % 2, sticky="nsew", padx=4, pady=4)

            content = tk.Frame(box.body, bg=self.theme.surface)
            content.pack(fill="both", expand=True)

            # Left Info
            l_info = tk.Frame(content, bg=self.theme.surface)
            l_info.pack(side="left", padx=(0, 15))

            tk.Label(l_info, text=text, font=self.theme.fonts["section"], bg=self.theme.surface, fg=self.theme.fg).pack(anchor="w", pady=(0, 4))
            lvl_row = tk.Frame(l_info, bg=self.theme.surface)
            lvl_row.pack(anchor="w")

            tk.Label(lvl_row, text="Level:", font=self.theme.fonts["body"], bg=self.theme.surface, fg=self.theme.text_dim).pack(side="left", padx=(0, 4))
            e_lvl = ModernEntry(lvl_row, self.theme, width=6, justify="center")
            e_lvl.pack(side="left")
            self.building_entries[text] = e_lvl

            c_val = b_data.get(text, "-")
            if c_val != "-":
                e_lvl.insert(0, str(c_val))

            e_lvl.bind('<Return>', lambda _e, n=text, e=e_lvl: self.save_building_level(n, e))
            e_lvl.bind('<FocusOut>', lambda _e, n=text, e=e_lvl: self.save_building_level(n, e))

            # Stats Grid (Next & Remaining)
            s_grid = tk.Frame(content, bg=self.theme.surface)
            s_grid.pack(side="left", fill="both", expand=True)

            self.building_stats_labels[text] = {}

            tk.Label(s_grid, text="Next Level Cost", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.yellow).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))
            tk.Label(s_grid, text="Total Remaining", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.green).grid(row=0, column=2, columnspan=2, sticky="w", pady=(0, 2))

            labels_k = [("Time", "time"), ("Lumber", "lumber"), ("Ore", "ore")]
            for r, (lbl, k) in enumerate(labels_k):
                if k == "ore" and text in ["Ore Mine 1", "Ore Mine 2"]:
                    continue
                tk.Label(s_grid, text=f"{lbl}:", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.text_dim).grid(row=r + 1, column=0, sticky="e", padx=(0, 2))
                l_next = tk.Label(s_grid, text="-", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.yellow)
                l_next.grid(row=r + 1, column=1, sticky="w", padx=(2, 12))
                self.building_stats_labels[text][f"{k}_next"] = l_next

                tk.Label(s_grid, text=f"{lbl}:", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.text_dim).grid(row=r + 1, column=2, sticky="e", padx=(0, 2))
                l_total = tk.Label(s_grid, text="-", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.green)
                l_total.grid(row=r + 1, column=3, sticky="w", padx=2)
                self.building_stats_labels[text][f"{k}_total"] = l_total

            # Afford Time Row
            tk.Label(s_grid, text="Afford Time:", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.blue).grid(row=4, column=0, sticky="e", padx=(0, 2), pady=(3, 0))
            l_afford = tk.Label(s_grid, text="-", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.blue)
            l_afford.grid(row=4, column=1, columnspan=3, sticky="w", padx=(2, 0), pady=(3, 0))
            self.building_stats_labels[text]["afford_time"] = l_afford

            # --- TARGETS TAB CARD ---
            box_t = CardFrame(self.tab_targets, self.theme, padding=8)
            if i == 0:
                box_t.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=4, pady=4)
            else:
                box_t.grid(row=(i + 1) // 2, column=(i + 1) % 2, sticky="nsew", padx=4, pady=4)

            content_t = tk.Frame(box_t.body, bg=self.theme.surface)
            content_t.pack(fill="both", expand=True)

            l_info_t = tk.Frame(content_t, bg=self.theme.surface)
            l_info_t.pack(side="left", padx=(0, 15))

            tk.Label(l_info_t, text=text, font=self.theme.fonts["section"], bg=self.theme.surface, fg=self.theme.fg).pack(anchor="w", pady=(0, 4))
            tgt_row = tk.Frame(l_info_t, bg=self.theme.surface)
            tgt_row.pack(anchor="w")

            tk.Label(tgt_row, text="Target:", font=self.theme.fonts["body"], bg=self.theme.surface, fg=self.theme.text_dim).pack(side="left", padx=(0, 4))
            e_tgt = ModernEntry(tgt_row, self.theme, width=6, justify="center")
            e_tgt.pack(side="left")
            self.building_target_entries[text] = e_tgt

            e_tgt.bind('<Return>', lambda _e, n=text: self.update_building_stats(n))
            e_tgt.bind('<FocusOut>', lambda _e, n=text: self.update_building_stats(n))

            s_grid_t = tk.Frame(content_t, bg=self.theme.surface)
            s_grid_t.pack(side="left", fill="both", expand=True)

            tk.Label(s_grid_t, text="Target Upgrade Cost", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.blue).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))

            for r, (lbl, k) in enumerate(labels_k):
                if k == "ore" and text in ["Ore Mine 1", "Ore Mine 2"]:
                    continue
                tk.Label(s_grid_t, text=f"{lbl}:", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.text_dim).grid(row=r + 1, column=0, sticky="e", padx=(0, 2))
                l_target = tk.Label(s_grid_t, text="-", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.blue)
                l_target.grid(row=r + 1, column=1, sticky="w", padx=2)
                self.building_stats_labels[text][f"{k}_target"] = l_target

            self.update_building_stats(text)

        # Button Row (Levels Tab)
        b_bar = tk.Frame(self.tab_levels, bg=self.theme.bg)
        b_bar.grid(row=5, column=0, columnspan=2, pady=6)
        ModernButton(b_bar, self.theme, text="Max All Buildings to Castle Level", variant="warning", command=self.max_all_buildings).pack()

        # Set All Targets (Targets Tab)
        t_set_bar = tk.Frame(self.tab_targets, bg=self.theme.bg)
        t_set_bar.grid(row=5, column=0, columnspan=2, pady=6)

        tk.Label(t_set_bar, text="Set all targets to:", font=self.theme.fonts["body_bold"], bg=self.theme.bg, fg=self.theme.fg).pack(side="left", padx=5)
        self.entry_target_all = ModernEntry(t_set_bar, self.theme, width=6, justify="center")
        self.entry_target_all.pack(side="left", padx=5)
        self.entry_target_all.bind('<Return>', lambda e: self.set_all_targets())

        ModernButton(t_set_bar, self.theme, text="Apply All Targets", variant="primary", command=self.set_all_targets).pack(side="left", padx=5)

        # Status Bar
        self.build_status_label = tk.Label(self, text="", font=self.theme.fonts["body_bold"], bg=self.theme.bg, fg=self.theme.fg)
        self.build_status_label.pack(side="bottom", pady=4)

        self.update_total_spent_summary()
        self.update_total_target_summary()

    def show_build_status(self, message: str, color: Optional[str] = None) -> None:
        self.build_status_label.config(text=message, fg=color or self.theme.fg)

    def save_building_settings(self, _event: Optional[tk.Event] = None) -> None:
        """Validates and saves multiplier settings (Speed, Lumber, Ore) and stored resources."""
        vars_map = {
            'const_speed': self.const_speed_var,
            'const_lumber': self.const_lumber_var,
            'const_ore': self.const_ore_var,
            'stored_lumber': self.stored_lumber_var,
            'stored_ore': self.stored_ore_var,
            'sawmill_1_rate': self.sawmill_1_rate_var,
            'sawmill_2_rate': self.sawmill_2_rate_var,
            'oremine_1_rate': self.oremine_1_rate_var,
            'oremine_2_rate': self.oremine_2_rate_var
        }

        for key, var in vars_map.items():
            val = var.get().strip()
            self.db.set_setting(key, val)

        for name in self.building_entries:
            self.update_building_stats(name)
        self.update_total_spent_summary()
        self.update_total_target_summary()
        self.app.update_global_data()

    def update_building_stats(self, name: str) -> None:
        """Recalculates next level, total remaining, target costs, and afford time for a single building."""
        if name not in self.building_entries:
            return

        entry = self.building_entries[name]
        level_str = entry.get().strip()
        current_level = 0
        if level_str and level_str != "-":
            try:
                current_level = int(level_str)
            except ValueError:
                current_level = 0

        target_entry = self.building_target_entries.get(name)
        target_level = 0
        if target_entry:
            t_val = target_entry.get().strip()
            if t_val and t_val != "-":
                try:
                    target_level = int(t_val)
                except ValueError:
                    target_level = 0

        try:
            mul_speed = float(self.const_speed_var.get()) / 100.0
            mul_lumber = float(self.const_lumber_var.get()) / 100.0
            mul_ore = float(self.const_ore_var.get()) / 100.0
        except ValueError:
            mul_speed, mul_lumber, mul_ore = 1.0, 1.0, 1.0

        costs = CASTLE_COSTS if name == "Castle" else (ORE_MINE_COSTS if "Ore Mine" in name else OTHER_BUILDING_COSTS)

        # 1. Next Level & Afford Time
        next_time, next_lumber, next_ore, afford_str, afford_color = "-", "-", "-", "-", self.theme.fg
        if current_level < BUILDING_MAX_LEVEL and current_level < len(costs):
            c = costs[current_level]
            next_time = format_seconds(c[0] * mul_speed)
            req_lumber = math.ceil(c[1] * mul_lumber)
            req_ore = math.ceil(c[2] * mul_ore)
            next_lumber = f"{req_lumber:,}"
            next_ore = f"{req_ore:,}"

            # Calculate Afford Time with Stored Resources
            try:
                st_lumber = int(float(self.stored_lumber_var.get().replace(',', '').strip() or 0))
                st_ore = int(float(self.stored_ore_var.get().replace(',', '').strip() or 0))
                sm_rate = float(self.sawmill_1_rate_var.get().replace(',', '').strip() or 0) + float(self.sawmill_2_rate_var.get().replace(',', '').strip() or 0)
                om_rate = float(self.oremine_1_rate_var.get().replace(',', '').strip() or 0) + float(self.oremine_2_rate_var.get().replace(',', '').strip() or 0)
            except ValueError:
                st_lumber, st_ore, sm_rate, om_rate = 0, 0, 18182.0, 6764.0

            time_res = calculate_conquest_upgrade_time(req_lumber, st_lumber, sm_rate, req_ore, st_ore, om_rate)
            if time_res["net_lumber"] <= 0 and time_res["net_ore"] <= 0:
                afford_str = "Ready Now! 🟢"
                afford_color = self.theme.green
            else:
                max_h = time_res["max_hours"]
                if max_h >= 24:
                    afford_str = f"{max_h/24:.1f}d ({max_h:.1f}h) [Net: {int(time_res['net_lumber']):,} L, {int(time_res['net_ore']):,} O]"
                else:
                    afford_str = f"{format_seconds(max_h * 3600)} [Net: {int(time_res['net_lumber']):,} L, {int(time_res['net_ore']):,} O]"
                afford_color = self.theme.blue
        else:
            afford_str = "Max Level 🏆"
            afford_color = self.theme.yellow

        # 2. Total Remaining
        total_time_sec, total_lumber, total_ore = 0, 0, 0
        for i in range(current_level, BUILDING_MAX_LEVEL):
            if i < len(costs):
                c = costs[i]
                total_time_sec += c[0] * mul_speed
                total_lumber += math.ceil(c[1] * mul_lumber)
                total_ore += math.ceil(c[2] * mul_ore)

        # 3. Target Cost
        target_time_sec, target_lumber, target_ore = 0, 0, 0
        if target_level > current_level:
            limit = min(target_level, BUILDING_MAX_LEVEL)
            for i in range(current_level, limit):
                if i < len(costs):
                    c = costs[i]
                    target_time_sec += c[0] * mul_speed
                    target_lumber += math.ceil(c[1] * mul_lumber)
                    target_ore += math.ceil(c[2] * mul_ore)
            t_time_str = format_seconds(target_time_sec)
            t_lumber_str = f"{target_lumber:,}"
            t_ore_str = f"{target_ore:,}"
        else:
            t_time_str, t_lumber_str, t_ore_str = "-", "-", "-"

        labels = self.building_stats_labels.get(name, {})
        if "time_next" in labels: labels["time_next"].config(text=next_time)
        if "lumber_next" in labels: labels["lumber_next"].config(text=next_lumber)
        if "ore_next" in labels: labels["ore_next"].config(text=next_ore)
        if "afford_time" in labels: labels["afford_time"].config(text=afford_str, fg=afford_color)

        if "time_total" in labels: labels["time_total"].config(text=format_seconds(total_time_sec))
        if "lumber_total" in labels: labels["lumber_total"].config(text=f"{total_lumber:,}")
        if "ore_total" in labels: labels["ore_total"].config(text=f"{total_ore:,}")

        if "time_target" in labels: labels["time_target"].config(text=t_time_str)
        if "lumber_target" in labels: labels["lumber_target"].config(text=t_lumber_str)
        if "ore_target" in labels: labels["ore_target"].config(text=t_ore_str)

        self.update_total_target_summary()

    def update_total_spent_summary(self) -> None:
        """Calculates cumulative resource investment for currently unlocked building levels."""
        total_time, total_lumber, total_ore = 0, 0, 0
        try:
            mul_speed = float(self.const_speed_var.get()) / 100.0
            mul_lumber = float(self.const_lumber_var.get()) / 100.0
            mul_ore = float(self.const_ore_var.get()) / 100.0
        except ValueError:
            mul_speed, mul_lumber, mul_ore = 1.0, 1.0, 1.0

        for name, entry in self.building_entries.items():
            val = entry.get().strip()
            if not val or val == "-":
                continue
            try:
                lvl = int(val)
            except ValueError:
                continue

            costs = CASTLE_COSTS if name == "Castle" else (ORE_MINE_COSTS if "Ore Mine" in name else OTHER_BUILDING_COSTS)
            for i in range(min(lvl, len(costs))):
                c = costs[i]
                total_time += c[0] * mul_speed
                total_lumber += math.ceil(c[1] * mul_lumber)
                total_ore += math.ceil(c[2] * mul_ore)

        self.lbl_spent_time.config(text=f"Time: {format_seconds(total_time)}")
        self.lbl_spent_lumber.config(text=f"Lumber: {total_lumber:,}")
        self.lbl_spent_ore.config(text=f"Ore: {total_ore:,}")

    def update_total_target_summary(self) -> None:
        """Calculates cumulative cost required to reach all defined target levels."""
        total_time, total_lumber, total_ore = 0, 0, 0
        try:
            mul_speed = float(self.const_speed_var.get()) / 100.0
            mul_lumber = float(self.const_lumber_var.get()) / 100.0
            mul_ore = float(self.const_ore_var.get()) / 100.0
        except ValueError:
            mul_speed, mul_lumber, mul_ore = 1.0, 1.0, 1.0

        for name, entry in self.building_entries.items():
            curr_str = entry.get().strip()
            curr_lvl = 0
            if curr_str and curr_str != "-":
                try:
                    curr_lvl = int(curr_str)
                except ValueError:
                    pass

            target_entry = self.building_target_entries.get(name)
            target_lvl = 0
            if target_entry:
                tgt_str = target_entry.get().strip()
                if tgt_str and tgt_str != "-":
                    try:
                        target_lvl = int(tgt_str)
                    except ValueError:
                        pass

            if target_lvl <= curr_lvl:
                continue

            costs = CASTLE_COSTS if name == "Castle" else (ORE_MINE_COSTS if "Ore Mine" in name else OTHER_BUILDING_COSTS)
            limit = min(target_lvl, BUILDING_MAX_LEVEL)
            for i in range(curr_lvl, limit):
                if i < len(costs):
                    c = costs[i]
                    total_time += c[0] * mul_speed
                    total_lumber += math.ceil(c[1] * mul_lumber)
                    total_ore += math.ceil(c[2] * mul_ore)

        self.lbl_target_time.config(text=f"Time: {format_seconds(total_time)}")
        self.lbl_target_lumber.config(text=f"Lumber: {total_lumber:,}")
        self.lbl_target_ore.config(text=f"Ore: {total_ore:,}")

    def set_all_targets(self, _event: Optional[tk.Event] = None) -> None:
        """Sets a uniform target level across all buildings."""
        val = self.entry_target_all.get().strip()
        if not val:
            return
        try:
            target_val = int(val)
            if not (0 <= target_val <= BUILDING_MAX_LEVEL):
                self.show_build_status(f"Target level must be between 0 and {BUILDING_MAX_LEVEL}.", self.theme.yellow)
                return

            for name, entry in self.building_target_entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, str(target_val))
                self.update_building_stats(name)

            self.update_total_target_summary()
            self.show_build_status(f"All targets set to Level {target_val}.", self.theme.green)
        except ValueError:
            self.show_build_status("Target level must be an integer.", self.theme.red)

    def max_all_buildings(self) -> None:
        """Caps all buildings to the Castle's current level."""
        castle_entry = self.building_entries.get("Castle")
        if not castle_entry:
            return

        level_str = castle_entry.get().strip()
        if not level_str or level_str == "-":
            self.show_build_status("Castle level must be set first.", self.theme.yellow)
            return

        try:
            level_val = int(level_str)
            self.db.run_query("UPDATE buildings SET level = ? WHERE name != 'Castle'", (level_val,))

            for name, entry in self.building_entries.items():
                if name != "Castle":
                    entry.delete(0, tk.END)
                    entry.insert(0, str(level_val))
                    self.update_building_stats(name)

            self.app.update_global_data()
            self.update_total_spent_summary()
            self.update_total_target_summary()
            self.show_build_status(f"All buildings matched to Castle Level {level_val}.", self.theme.green)
        except ValueError:
            self.show_build_status("Invalid Castle level.", self.theme.red)

    def save_building_level(self, name: str, entry_widget: ModernEntry) -> None:
        """Validates and persists a building level change, enforcing Castle level caps."""
        level = entry_widget.get().strip()
        self.show_build_status("", self.theme.fg)
        try:
            if not level or level == "-":
                level_val: Any = "-"
            else:
                level_val = int(level)
                if not (0 <= level_val <= BUILDING_MAX_LEVEL):
                    entry_widget.delete(0, tk.END)
                    self.show_build_status(f"Level must be between 0 and {BUILDING_MAX_LEVEL}.", self.theme.yellow)
                    return

            if name != "Castle" and level_val != "-":
                res = self.db.fetch_one("SELECT level FROM buildings WHERE name = 'Castle'")
                c_str = res[0] if res else "-"
                castle_level = 0 if c_str == "-" else int(c_str)

                if level_val > castle_level:
                    entry_widget.delete(0, tk.END)
                    self.show_build_status(f"Building level cannot exceed Castle level ({castle_level}).", self.theme.yellow)
                    return

            self.db.run_query("UPDATE buildings SET level = ? WHERE name = ?", (level_val, name))

            if name == "Castle":
                castle_limit = 0 if level_val == "-" else level_val
                rows = self.db.fetch_all("SELECT name, level FROM buildings WHERE name != 'Castle'")
                updates_made = False
                for r_name, r_level in rows:
                    curr_lvl = 0 if r_level == "-" else int(r_level)
                    if curr_lvl > castle_limit:
                        self.db.run_query("UPDATE buildings SET level = ? WHERE name = ?", (level_val, r_name))
                        if r_name in self.building_entries:
                            self.building_entries[r_name].delete(0, tk.END)
                            self.building_entries[r_name].insert(0, str(level_val))
                            self.update_building_stats(r_name)
                        updates_made = True
                if updates_made:
                    self.show_build_status(f"Other buildings reduced to Castle level limit ({castle_limit}).", self.theme.yellow)

            self.update_building_stats(name)
            self.app.update_global_data()
            self.update_total_spent_summary()
            self.update_total_target_summary()
        except ValueError:
            pass
