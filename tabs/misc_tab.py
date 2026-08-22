"""
Misc Tab module.
Includes Drop & Probability References, Chest Reward Calculator,
Element of Water Calculator, Secret Achievements Interactive Checklist,
and In-Game Promo Codes with one-click clipboard copying.
"""

import tkinter as tk
from tkinter import ttk
import math
from typing import Any, Dict, List, Optional

from constants import (
    FIREFLY_CHANCES, DYE_DROP_RATE, ENEMY_COIN_DROPS, GEM_DROP_CHANCES,
    OFFLINE_BAG_OF_GOODS, SECRET_ACHIEVEMENTS, PROMO_CODES,
    CHEST_TIER_CHANCES, CHEST_TIER_REWARDS,
    DUST_COSTS, PET_FEATHER_COSTS,
    get_water_element_cost, get_water_element_range_cost,
    calculate_expected_chest_rewards, format_resource_value
)
from ui_components import CardFrame, ModernButton, ModernEntry, ModernScrollbar, setup_treeview_striping


def parse_numeric_input(val_str: str, default: float = 0.0) -> float:
    """Parses numeric string supporting metric suffixes (K, M, B, T, etc.) and scientific notation."""
    s = val_str.replace(',', '').strip()
    if not s or s == '-':
        return default
    try:
        return float(s)
    except ValueError:
        pass

    suffixes = {
        'k': 1e3, 'm': 1e6, 'b': 1e9, 't': 1e12,
        'qa': 1e15, 'qi': 1e18, 'sx': 1e21, 'sp': 1e24, 'oc': 1e27, 'no': 1e30, 'dc': 1e33
    }
    s_lower = s.lower()
    for suffix, multiplier in suffixes.items():
        if s_lower.endswith(suffix):
            num_part = s_lower[:-len(suffix)].strip()
            try:
                return float(num_part) * multiplier
            except ValueError:
                pass
    return default


class MiscTab(tk.Frame):
    """Encapsulates all Miscellaneous game features: calculators, reference tables, achievements, and codes."""

    def __init__(self, parent: tk.Widget, app: Any):
        super().__init__(parent, bg=app.theme.bg)
        self.app = app
        self.db = app.db
        self.theme = app.theme

        # Chest Calculator State
        self.chest_daily_var = tk.StringVar(value=self.db.get_setting("chests_per_day", "8"))
        self.chest_days_var = tk.StringVar(value=self.db.get_setting("chest_eval_days", "365"))
        self.chest_chance_rare_var = tk.StringVar(value=self.db.get_setting("chest_chance_rare", "29.6"))
        self.chest_chance_epic_var = tk.StringVar(value=self.db.get_setting("chest_chance_epic", "62.9"))
        self.chest_chance_leg_var = tk.StringVar(value=self.db.get_setting("chest_chance_leg", "6.9"))
        self.chest_chance_mythic_var = tk.StringVar(value=self.db.get_setting("chest_chance_mythic", "0.6"))

        # Per-Tier Custom Gold & Elixir Inputs
        self.chest_gold_rare_var = tk.StringVar(value=self.db.get_setting("chest_gold_rare", "0"))
        self.chest_elixir_rare_var = tk.StringVar(value=self.db.get_setting("chest_elixir_rare", "59.7B"))

        self.chest_gold_epic_var = tk.StringVar(value=self.db.get_setting("chest_gold_epic", "0"))
        self.chest_elixir_epic_var = tk.StringVar(value=self.db.get_setting("chest_elixir_epic", "79.6B"))

        self.chest_gold_leg_var = tk.StringVar(value=self.db.get_setting("chest_gold_leg", "0"))
        self.chest_elixir_leg_var = tk.StringVar(value=self.db.get_setting("chest_elixir_leg", "111.0B"))

        self.chest_gold_mythic_var = tk.StringVar(value=self.db.get_setting("chest_gold_mythic", "0"))
        self.chest_elixir_mythic_var = tk.StringVar(value=self.db.get_setting("chest_elixir_mythic", "298.0B"))

        # Water Element State
        self.water_curr_var = tk.StringVar(value=self.db.get_setting("water_curr_lvl", "1"))
        self.water_target_var = tk.StringVar(value=self.db.get_setting("water_target_lvl", "50"))

        # Secret Achievements Checkbox Vars
        self.ach_vars: Dict[int, tk.IntVar] = {}

        self._build_ui()

    def _build_ui(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_drops = tk.Frame(self.notebook, bg=self.theme.bg)
        self.tab_chest = tk.Frame(self.notebook, bg=self.theme.bg)
        self.tab_water = tk.Frame(self.notebook, bg=self.theme.bg)
        self.tab_achievements = tk.Frame(self.notebook, bg=self.theme.bg)
        self.tab_promo = tk.Frame(self.notebook, bg=self.theme.bg)

        self.notebook.add(self.tab_drops, text="Drop References")
        self.notebook.add(self.tab_chest, text="Chest Calculator")
        self.notebook.add(self.tab_water, text="Water Element")
        self.notebook.add(self.tab_achievements, text="Secret Achievements")
        self.notebook.add(self.tab_promo, text="Promo Codes")

        self._build_drops_ui()
        self._build_chest_ui()
        self._build_water_ui()
        self._build_achievements_ui()
        self._build_promo_ui()

    # ==========================================
    # --- SUB-TAB 1: DROP REFERENCES ---
    # ==========================================

    def _build_drops_ui(self) -> None:
        container = tk.Frame(self.tab_drops, bg=self.theme.bg)
        container.pack(fill="both", expand=True, padx=16, pady=12)
        container.columnconfigure(0, weight=1, uniform="drop_col")
        container.columnconfigure(1, weight=1, uniform="drop_col")

        # --- LEFT COLUMN (4 Drop Cards) ---
        left_col = tk.Frame(container, bg=self.theme.bg)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # 1. Firefly Event Chances
        card_firefly = CardFrame(left_col, self.theme, title="🪰 Firefly Event Probabilities", header_color=self.theme.yellow, padding=8)
        card_firefly.pack(fill="x", pady=(0, 6))

        for event_name, prob in FIREFLY_CHANCES.items():
            row_f = tk.Frame(card_firefly.body, bg=self.theme.surface)
            row_f.pack(fill="x", pady=1)
            tk.Label(row_f, text=f"● {event_name}", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.fg).pack(side="left")
            tk.Label(row_f, text=f"{prob * 100:.2f}%", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.yellow).pack(side="right")

        # 2. Enemy Coin Drops & Special Rates
        card_enemy = CardFrame(left_col, self.theme, title="⚔️ Enemy Coin Drops & Special Rates", header_color=self.theme.red, padding=8)
        card_enemy.pack(fill="x", pady=(0, 6))

        for enemy, coins in ENEMY_COIN_DROPS.items():
            row_e = tk.Frame(card_enemy.body, bg=self.theme.surface)
            row_e.pack(fill="x", pady=1)
            tk.Label(row_e, text=f"● {enemy}", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.fg).pack(side="left")
            tk.Label(row_e, text=f"{coins} Coins", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.green).pack(side="right")

        dye_row = tk.Frame(card_enemy.body, bg=self.theme.surface)
        dye_row.pack(fill="x", pady=(6, 1))
        tk.Label(dye_row, text="● Dye Drop Rate:", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.purple).pack(side="left")
        tk.Label(dye_row, text="1 in 45,000 (0.0022%)", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.purple).pack(side="right")

        # 3. Gem Mine Drops
        card_gems = CardFrame(left_col, self.theme, title="💎 Gem Mine Drop Rates", header_color=self.theme.blue, padding=8)
        card_gems.pack(fill="x", pady=(0, 6))

        for gem, prob in GEM_DROP_CHANCES.items():
            row_g = tk.Frame(card_gems.body, bg=self.theme.surface)
            row_g.pack(fill="x", pady=1)
            tk.Label(row_g, text=f"● {gem}", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.fg).pack(side="left")
            tk.Label(row_g, text=f"{prob * 100:.2f}%", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.blue).pack(side="right")

        # 4. Offline Bag of Goods
        card_bag = CardFrame(left_col, self.theme, title="🎒 Offline Bag of Goods Efficiency", header_color=self.theme.green, padding=8)
        card_bag.pack(fill="x")

        for tier, data in OFFLINE_BAG_OF_GOODS.items():
            row_b = tk.Frame(card_bag.body, bg=self.theme.surface)
            row_b.pack(fill="x", pady=1)
            tk.Label(row_b, text=f"● Bag ({tier}): {int(data['amber_price'])} Amber / {data['offline_hours']}h", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.fg).pack(side="left")
            tk.Label(row_b, text=f"{data['price_per_hour']:.2f} Amber/h", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.green).pack(side="right")

        # --- RIGHT COLUMN (STAR DUST & PET FEATHER COSTS TABLE) ---
        card_costs = CardFrame(container, self.theme, title="⭐ Star Dust & Pet Feather Costs Reference", header_color=self.theme.blue, padding=8)
        card_costs.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tree_frame = tk.Frame(card_costs.body, bg=self.theme.surface)
        tree_frame.pack(fill="both", expand=True)

        cols = ("star", "rare_dust", "epic_dust", "leg_dust", "feathers")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        tree.heading("star", text="Star Tier")
        tree.heading("rare_dust", text="Rare Dust")
        tree.heading("epic_dust", text="Epic Dust")
        tree.heading("leg_dust", text="Legendary Dust")
        tree.heading("feathers", text="Pet Feathers")

        tree.column("star", anchor="center", width=80)
        tree.column("rare_dust", anchor="center", width=110)
        tree.column("epic_dust", anchor="center", width=110)
        tree.column("leg_dust", anchor="center", width=120)
        tree.column("feathers", anchor="center", width=110)

        for s in range(1, 13):
            r_cost = DUST_COSTS["Rare"][s - 1]
            e_cost = DUST_COSTS["Epic"][s - 1]
            l_cost = DUST_COSTS["Legendary"][s - 1]
            f_cost = PET_FEATHER_COSTS[s - 1]
            tag = "evenrow" if s % 2 == 0 else "oddrow"
            tree.insert("", "end", values=(f"{s} ★", f"{r_cost:,}", f"{e_cost:,}", f"{l_cost:,}", f"{f_cost:,}"), tags=(tag,))

        setup_treeview_striping(tree, self.theme)
        tree.pack(fill="both", expand=True)

    # ==========================================
    # --- SUB-TAB 2: CHEST CALCULATOR ---
    # ==========================================

    def _build_chest_ui(self) -> None:
        container = tk.Frame(self.tab_chest, bg=self.theme.bg)
        container.pack(fill="both", expand=True, padx=16, pady=12)

        # 1. Inputs Card
        card_inputs = CardFrame(container, self.theme, title="Chest Simulator Parameters & Rewards Per Rarity", header_color=self.theme.yellow, padding=10)
        card_inputs.pack(fill="x", pady=(0, 10))

        # Row 1: Global Simulation Parameters
        grid_p = tk.Frame(card_inputs.body, bg=self.theme.surface)
        grid_p.pack(fill="x", pady=(0, 6))

        tk.Label(grid_p, text="Chests / Day:", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.fg).pack(side="left", padx=(0, 4))
        e_cpd = ModernEntry(grid_p, self.theme, textvariable=self.chest_daily_var, width=6)
        e_cpd.pack(side="left", padx=(0, 12))
        e_cpd.bind("<KeyRelease>", lambda _e: self.update_chest_calc())

        tk.Label(grid_p, text="Period (Days):", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.fg).pack(side="left", padx=(0, 4))
        e_cd = ModernEntry(grid_p, self.theme, textvariable=self.chest_days_var, width=6)
        e_cd.pack(side="left", padx=(0, 16))
        e_cd.bind("<KeyRelease>", lambda _e: self.update_chest_calc())

        tk.Label(grid_p, text="Rare %:", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.blue).pack(side="left", padx=(0, 2))
        e_cr = ModernEntry(grid_p, self.theme, textvariable=self.chest_chance_rare_var, width=5)
        e_cr.pack(side="left", padx=(0, 8))
        e_cr.bind("<KeyRelease>", lambda _e: self.update_chest_calc())

        tk.Label(grid_p, text="Epic %:", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.purple).pack(side="left", padx=(0, 2))
        e_ce = ModernEntry(grid_p, self.theme, textvariable=self.chest_chance_epic_var, width=5)
        e_ce.pack(side="left", padx=(0, 8))
        e_ce.bind("<KeyRelease>", lambda _e: self.update_chest_calc())

        tk.Label(grid_p, text="Legendary %:", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.yellow).pack(side="left", padx=(0, 2))
        e_cl = ModernEntry(grid_p, self.theme, textvariable=self.chest_chance_leg_var, width=5)
        e_cl.pack(side="left", padx=(0, 8))
        e_cl.bind("<KeyRelease>", lambda _e: self.update_chest_calc())

        tk.Label(grid_p, text="Mythic %:", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.red).pack(side="left", padx=(0, 2))
        e_cm = ModernEntry(grid_p, self.theme, textvariable=self.chest_chance_mythic_var, width=5)
        e_cm.pack(side="left")
        e_cm.bind("<KeyRelease>", lambda _e: self.update_chest_calc())

        # Row 2: Per-Tier Gold & Elixir Inputs
        grid_tiers = tk.Frame(card_inputs.body, bg=self.theme.surface)
        grid_tiers.pack(fill="x", pady=4)
        for c in range(4):
            grid_tiers.columnconfigure(c, weight=1, uniform="chest_tier_col")

        # Rare Box
        b_rare = tk.LabelFrame(grid_tiers, text=" Rare Chest Reward ", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.blue, padx=6, pady=4)
        b_rare.grid(row=0, column=0, sticky="nsew", padx=3)
        tk.Label(b_rare, text="Gold/Chest:", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.yellow).grid(row=0, column=0, sticky="w")
        e_rg = ModernEntry(b_rare, self.theme, textvariable=self.chest_gold_rare_var, width=9)
        e_rg.grid(row=0, column=1, sticky="w", padx=2, pady=1)
        e_rg.bind("<KeyRelease>", lambda _e: self.update_chest_calc())
        tk.Label(b_rare, text="Elixir/Chest:", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.purple).grid(row=1, column=0, sticky="w")
        e_re = ModernEntry(b_rare, self.theme, textvariable=self.chest_elixir_rare_var, width=9)
        e_re.grid(row=1, column=1, sticky="w", padx=2, pady=1)
        e_re.bind("<KeyRelease>", lambda _e: self.update_chest_calc())

        # Epic Box
        b_epic = tk.LabelFrame(grid_tiers, text=" Epic Chest Reward ", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.purple, padx=6, pady=4)
        b_epic.grid(row=0, column=1, sticky="nsew", padx=3)
        tk.Label(b_epic, text="Gold/Chest:", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.yellow).grid(row=0, column=0, sticky="w")
        e_eg = ModernEntry(b_epic, self.theme, textvariable=self.chest_gold_epic_var, width=9)
        e_eg.grid(row=0, column=1, sticky="w", padx=2, pady=1)
        e_eg.bind("<KeyRelease>", lambda _e: self.update_chest_calc())
        tk.Label(b_epic, text="Elixir/Chest:", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.purple).grid(row=1, column=0, sticky="w")
        e_ee = ModernEntry(b_epic, self.theme, textvariable=self.chest_elixir_epic_var, width=9)
        e_ee.grid(row=1, column=1, sticky="w", padx=2, pady=1)
        e_ee.bind("<KeyRelease>", lambda _e: self.update_chest_calc())

        # Legendary Box
        b_leg = tk.LabelFrame(grid_tiers, text=" Legendary Chest Reward ", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.yellow, padx=6, pady=4)
        b_leg.grid(row=0, column=2, sticky="nsew", padx=3)
        tk.Label(b_leg, text="Gold/Chest:", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.yellow).grid(row=0, column=0, sticky="w")
        e_lg = ModernEntry(b_leg, self.theme, textvariable=self.chest_gold_leg_var, width=9)
        e_lg.grid(row=0, column=1, sticky="w", padx=2, pady=1)
        e_lg.bind("<KeyRelease>", lambda _e: self.update_chest_calc())
        tk.Label(b_leg, text="Elixir/Chest:", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.purple).grid(row=1, column=0, sticky="w")
        e_le = ModernEntry(b_leg, self.theme, textvariable=self.chest_elixir_leg_var, width=9)
        e_le.grid(row=1, column=1, sticky="w", padx=2, pady=1)
        e_le.bind("<KeyRelease>", lambda _e: self.update_chest_calc())

        # Mythic Box
        b_my = tk.LabelFrame(grid_tiers, text=" Mythic Chest Reward ", font=self.theme.fonts["small_bold"], bg=self.theme.surface, fg=self.theme.red, padx=6, pady=4)
        b_my.grid(row=0, column=3, sticky="nsew", padx=3)
        tk.Label(b_my, text="Gold/Chest:", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.yellow).grid(row=0, column=0, sticky="w")
        e_mg = ModernEntry(b_my, self.theme, textvariable=self.chest_gold_mythic_var, width=9)
        e_mg.grid(row=0, column=1, sticky="w", padx=2, pady=1)
        e_mg.bind("<KeyRelease>", lambda _e: self.update_chest_calc())
        tk.Label(b_my, text="Elixir/Chest:", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.purple).grid(row=1, column=0, sticky="w")
        e_me = ModernEntry(b_my, self.theme, textvariable=self.chest_elixir_mythic_var, width=9)
        e_me.grid(row=1, column=1, sticky="w", padx=2, pady=1)
        e_me.bind("<KeyRelease>", lambda _e: self.update_chest_calc())

        # Total Counts Label
        self.lbl_chest_counts = tk.Label(
            card_inputs.body,
            text="Total Chests: 2,920 (Rare: 864 | Epic: 1,837 | Legendary: 201 | Mythic: 18)",
            font=self.theme.fonts["body_bold"],
            bg=self.theme.surface,
            fg=self.theme.green
        )
        self.lbl_chest_counts.pack(anchor="w", pady=(6, 2))

        # 2. Expected Yields Matrix Table (Per-Tier Breakdown & Total)
        card_matrix = CardFrame(container, self.theme, title="🎁 Expected Yields Per Chest Rarity & Combined Total", header_color=self.theme.green, padding=8)
        card_matrix.pack(fill="both", expand=True)

        tree_m_frame = tk.Frame(card_matrix.body, bg=self.theme.surface)
        tree_m_frame.pack(fill="both", expand=True)

        cols_m = ("res", "rare", "epic", "leg", "mythic", "total", "daily")
        self.tree_chest_matrix = ttk.Treeview(tree_m_frame, columns=cols_m, show="headings")
        self.tree_chest_matrix.heading("res", text="Resource")
        self.tree_chest_matrix.heading("rare", text="🔵 Rare Yield")
        self.tree_chest_matrix.heading("epic", text="🟣 Epic Yield")
        self.tree_chest_matrix.heading("leg", text="🟡 Legendary Yield")
        self.tree_chest_matrix.heading("mythic", text="🔴 Mythic Yield")
        self.tree_chest_matrix.heading("total", text="⭐ Total Cumulative")
        self.tree_chest_matrix.heading("daily", text="⏱️ Daily Average")

        self.tree_chest_matrix.column("res", anchor="w", width=150)
        for c in cols_m[1:]:
            self.tree_chest_matrix.column(c, anchor="e", width=130)

        setup_treeview_striping(self.tree_chest_matrix, self.theme)
        self.tree_chest_matrix.pack(fill="both", expand=True)

        self.update_chest_calc()

    def update_chest_calc(self) -> None:
        """Calculates expected chest drop counts and cumulative yields per rarity tier."""
        if not hasattr(self, 'lbl_chest_counts') or not hasattr(self, 'tree_chest_matrix'):
            return

        cpd = parse_numeric_input(self.chest_daily_var.get(), 8.0)
        days = parse_numeric_input(self.chest_days_var.get(), 365.0)

        self.db.set_setting("chests_per_day", str(cpd))
        self.db.set_setting("chest_eval_days", str(days))

        r_c = parse_numeric_input(self.chest_chance_rare_var.get(), 29.6) / 100.0
        e_c = parse_numeric_input(self.chest_chance_epic_var.get(), 62.9) / 100.0
        l_c = parse_numeric_input(self.chest_chance_leg_var.get(), 6.9) / 100.0
        m_c = parse_numeric_input(self.chest_chance_mythic_var.get(), 0.6) / 100.0

        self.db.set_setting("chest_chance_rare", self.chest_chance_rare_var.get())
        self.db.set_setting("chest_chance_epic", self.chest_chance_epic_var.get())
        self.db.set_setting("chest_chance_leg", self.chest_chance_leg_var.get())
        self.db.set_setting("chest_chance_mythic", self.chest_chance_mythic_var.get())

        # Read Custom Gold & Elixir
        rg = parse_numeric_input(self.chest_gold_rare_var.get(), 0.0)
        re = parse_numeric_input(self.chest_elixir_rare_var.get(), 59_700_000_000.0)
        eg = parse_numeric_input(self.chest_gold_epic_var.get(), 0.0)
        ee = parse_numeric_input(self.chest_elixir_epic_var.get(), 79_600_000_000.0)
        lg = parse_numeric_input(self.chest_gold_leg_var.get(), 0.0)
        le = parse_numeric_input(self.chest_elixir_leg_var.get(), 111_000_000_000.0)
        mg = parse_numeric_input(self.chest_gold_mythic_var.get(), 0.0)
        me = parse_numeric_input(self.chest_elixir_mythic_var.get(), 298_000_000_000.0)

        self.db.set_setting("chest_gold_rare", self.chest_gold_rare_var.get())
        self.db.set_setting("chest_elixir_rare", self.chest_elixir_rare_var.get())
        self.db.set_setting("chest_gold_epic", self.chest_gold_epic_var.get())
        self.db.set_setting("chest_elixir_epic", self.chest_elixir_epic_var.get())
        self.db.set_setting("chest_gold_leg", self.chest_gold_leg_var.get())
        self.db.set_setting("chest_elixir_leg", self.chest_elixir_leg_var.get())
        self.db.set_setting("chest_gold_mythic", self.chest_gold_mythic_var.get())
        self.db.set_setting("chest_elixir_mythic", self.chest_elixir_mythic_var.get())

        custom_rewards = {
            "Rare": {"gold": rg, "elixir": re, "medals": 6, "amber": 15, "eggs": 2, "keys": 2, "rare_scrolls": 2, "epic_scrolls": 2},
            "Epic": {"gold": eg, "elixir": ee, "medals": 8, "amber": 25, "eggs": 3, "keys": 2, "rare_scrolls": 3, "epic_scrolls": 2},
            "Legendary": {"gold": lg, "elixir": le, "medals": 12, "amber": 75, "eggs": 4, "keys": 3, "rare_scrolls": 4, "epic_scrolls": 3},
            "Mythic": {"gold": mg, "elixir": me, "medals": 50, "amber": 250, "eggs": 10, "keys": 15, "rare_scrolls": 10, "epic_scrolls": 10}
        }

        chances_dict = {"Rare": r_c, "Epic": e_c, "Legendary": l_c, "Mythic": m_c}
        res = calculate_expected_chest_rewards(cpd, days, chances_dict, custom_rewards)

        self.lbl_chest_counts.config(
            text=f"Total Chests: {res['total_chests']:,.0f} (Rare: {res['rare_chests']:,.1f} | Epic: {res['epic_chests']:,.1f} | Legendary: {res['legendary_chests']:,.1f} | Mythic: {res['mythic_chests']:,.1f})"
        )

        for row in self.tree_chest_matrix.get_children():
            self.tree_chest_matrix.delete(row)

        res_specs = [
            ("Gold (Coins)", "gold", True),
            ("Elixir", "elixir", True),
            ("Medals", "medals", False),
            ("Amber", "amber", False),
            ("Pet Eggs", "eggs", False),
            ("Keys", "keys", False),
            ("Rare Scrolls", "rare_scrolls", False),
            ("Epic Scrolls", "epic_scrolls", False),
        ]

        pt = res.get("per_tier", {})
        for idx, (display_name, key, is_scaled) in enumerate(res_specs):
            r_val = pt.get("Rare", {}).get(key, 0.0)
            e_val = pt.get("Epic", {}).get(key, 0.0)
            l_val = pt.get("Legendary", {}).get(key, 0.0)
            m_val = pt.get("Mythic", {}).get(key, 0.0)
            tot_val = res.get(key, 0.0)
            d_val = tot_val / days if days > 0 else 0.0

            if is_scaled:
                r_str = format_resource_value(r_val)
                e_str = format_resource_value(e_val)
                l_str = format_resource_value(l_val)
                m_str = format_resource_value(m_val)
                tot_str = format_resource_value(tot_val)
                d_str = format_resource_value(d_val) + "/d"
            else:
                r_str = f"{r_val:,.1f}"
                e_str = f"{e_val:,.1f}"
                l_str = f"{l_val:,.1f}"
                m_str = f"{m_val:,.1f}"
                tot_str = f"{tot_val:,.1f}"
                d_str = f"{d_val:,.2f}/d"

            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree_chest_matrix.insert(
                "", "end",
                values=(display_name, r_str, e_str, l_str, m_str, tot_str, d_str),
                tags=(tag,)
            )

    # ==========================================
    # --- SUB-TAB 3: WATER ELEMENT ---
    # ==========================================

    def _build_water_ui(self) -> None:
        container = tk.Frame(self.tab_water, bg=self.theme.bg)
        container.pack(fill="both", expand=True, padx=16, pady=12)

        # 1. Inputs Card
        card_input = CardFrame(container, self.theme, title="Element of Water Unbounded Cost Calculator", header_color=self.theme.blue, padding=10)
        card_input.pack(fill="x", pady=(0, 8))

        r_in = tk.Frame(card_input.body, bg=self.theme.surface)
        r_in.pack(fill="x", pady=2)

        tk.Label(r_in, text="Current Level:", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.fg).pack(side="left", padx=(0, 6))
        e_curr = ModernEntry(r_in, self.theme, textvariable=self.water_curr_var, width=10)
        e_curr.pack(side="left", padx=(0, 20))
        e_curr.bind("<KeyRelease>", lambda _e: self.update_water_calc())

        tk.Label(r_in, text="Target Level:", font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.fg).pack(side="left", padx=(0, 6))
        e_tgt = ModernEntry(r_in, self.theme, textvariable=self.water_target_var, width=10)
        e_tgt.pack(side="left", padx=(0, 20))
        e_tgt.bind("<KeyRelease>", lambda _e: self.update_water_calc())

        # Formula description alert
        tk.Label(
            card_input.body,
            text="● Formula: Level 1 = 100,000. Multiplies by 10x every 4 levels (offsets: 1.0x, 2.5x, 5.0x, 7.5x). Unbounded with no max cap.",
            font=self.theme.fonts["small"],
            bg=self.theme.surface,
            fg=self.theme.blue
        ).pack(anchor="w", pady=(4, 0))

        # 2. Output Summary Cards
        out_grid = tk.Frame(container, bg=self.theme.bg)
        out_grid.pack(fill="x", pady=(0, 8))
        out_grid.columnconfigure(0, weight=1, uniform="water_col")
        out_grid.columnconfigure(1, weight=1, uniform="water_col")

        card_next = CardFrame(out_grid, self.theme, title="Next Level Cost", header_color=self.theme.yellow, padding=10)
        card_next.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

        self.lbl_water_next = tk.Label(card_next.body, text="0", font=self.theme.fonts["section"], bg=self.theme.surface, fg=self.theme.yellow)
        self.lbl_water_next.pack(anchor="w", pady=2)

        card_cum = CardFrame(out_grid, self.theme, title="Total Cumulative Cost to Target", header_color=self.theme.green, padding=10)
        card_cum.grid(row=0, column=1, sticky="nsew", padx=(4, 0))

        self.lbl_water_cum = tk.Label(card_cum.body, text="0", font=self.theme.fonts["section"], bg=self.theme.surface, fg=self.theme.green)
        self.lbl_water_cum.pack(anchor="w", pady=2)

        # 3. Preview Treeview Table
        card_preview = CardFrame(container, self.theme, title="Level-by-Level Step Cost Preview", header_color=self.theme.blue, padding=6)
        card_preview.pack(fill="both", expand=True)

        tree_f = tk.Frame(card_preview.body, bg=self.theme.surface)
        tree_f.pack(fill="both", expand=True)

        scrollbar = ModernScrollbar(tree_f, self.theme, orient="vertical")
        self.tree_water = ttk.Treeview(
            tree_f,
            columns=("level", "step_cost", "cum_cost"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree_water.yview)
        scrollbar.pack(side="right", fill="y")

        self.tree_water.heading("level", text="Level")
        self.tree_water.heading("step_cost", text="Level Upgrade Cost")
        self.tree_water.heading("cum_cost", text="Cumulative Cost From Level 1")
        self.tree_water.column("level", anchor="center", width=120)
        self.tree_water.column("step_cost", anchor="e", width=340)
        self.tree_water.column("cum_cost", anchor="e", width=340)
        self.tree_water.pack(side="left", fill="both", expand=True)
        setup_treeview_striping(self.tree_water, self.theme)

        self.update_water_calc()

    def update_water_calc(self) -> None:
        """Calculates Element of Water step and cumulative costs and populates preview."""
        if not hasattr(self, 'lbl_water_next'):
            return

        try:
            curr_lvl = int(self.water_curr_var.get().strip() or 1)
        except ValueError:
            curr_lvl = 1

        try:
            target_lvl = int(self.water_target_var.get().strip() or 50)
        except ValueError:
            target_lvl = 50

        self.db.set_setting("water_curr_lvl", str(curr_lvl))
        self.db.set_setting("water_target_lvl", str(target_lvl))

        next_cost = get_water_element_cost(curr_lvl + 1)
        cum_cost = get_water_element_range_cost(curr_lvl, target_lvl)

        self.lbl_water_next.config(text=f"Level {curr_lvl} ➔ {curr_lvl + 1}: {format_resource_value(next_cost)} ({next_cost:,})")
        self.lbl_water_cum.config(text=f"Level {curr_lvl} ➔ {target_lvl}: {format_resource_value(cum_cost)} ({cum_cost:,})")

        for row in self.tree_water.get_children():
            self.tree_water.delete(row)

        start = max(1, curr_lvl)
        end = min(start + 25, max(target_lvl + 1, start + 15))
        cum_running = 0
        for lvl in range(1, end + 1):
            cost = get_water_element_cost(lvl)
            cum_running += cost
            if lvl >= start:
                tag = "evenrow" if lvl % 2 == 0 else "oddrow"
                self.tree_water.insert(
                    "", "end",
                    values=(f"Level {lvl}", f"{format_resource_value(cost)} ({cost:,})", f"{format_resource_value(cum_running)} ({cum_running:,})"),
                    tags=(tag,)
                )

    # ==========================================
    # --- SUB-TAB 4: SECRET ACHIEVEMENTS ---
    # ==========================================

    def _build_achievements_ui(self) -> None:
        container = tk.Frame(self.tab_achievements, bg=self.theme.bg)
        container.pack(fill="both", expand=True, padx=16, pady=12)

        # Header Status Bar
        card_header = CardFrame(container, self.theme, title="Secret Achievements Checklist & Solution Guide", header_color=self.theme.purple, padding=10)
        card_header.pack(fill="x", pady=(0, 10))

        h_row = tk.Frame(card_header.body, bg=self.theme.surface)
        h_row.pack(fill="x", pady=2)

        self.lbl_ach_progress = tk.Label(
            h_row, text="Unlocked: 0 / 8 (0%)",
            font=self.theme.fonts["section"], bg=self.theme.surface, fg=self.theme.purple
        )
        self.lbl_ach_progress.pack(side="left", padx=(0, 20))

        ModernButton(h_row, self.theme, text="Select All", variant="primary", command=self.select_all_achievements).pack(side="left", padx=4)
        ModernButton(h_row, self.theme, text="Deselect All", variant="neutral", command=self.deselect_all_achievements).pack(side="left", padx=4)

        # List Container (2-Column Grid filling the whole window)
        card_list = CardFrame(container, self.theme, padding=8)
        card_list.pack(fill="both", expand=True)

        ach_grid = tk.Frame(card_list.body, bg=self.theme.surface)
        ach_grid.pack(fill="both", expand=True)
        ach_grid.columnconfigure(0, weight=1, uniform="ach_col")
        ach_grid.columnconfigure(1, weight=1, uniform="ach_col")

        ach_status = self.db.get_secret_achievements()

        for i, ach in enumerate(SECRET_ACHIEVEMENTS):
            a_id = ach["id"]
            is_done = ach_status.get(a_id, False)

            row_idx = i // 2
            col_idx = i % 2

            tile = tk.Frame(ach_grid, bg=self.theme.bg, bd=1, relief="groove", padx=10, pady=8)
            tile.grid(row=row_idx, column=col_idx, sticky="nsew", padx=6, pady=4)

            var = tk.IntVar(value=1 if is_done else 0)
            self.ach_vars[a_id] = var

            cb = tk.Checkbutton(
                tile,
                text=f"  #{a_id} — {ach['name']}",
                variable=var,
                command=lambda id_=a_id, v=var: self.on_achievement_toggle(id_, v),
                bg=self.theme.bg,
                fg=self.theme.fg,
                selectcolor=self.theme.surface,
                activebackground=self.theme.bg,
                activeforeground=self.theme.fg,
                font=self.theme.fonts["body_bold"]
            )
            cb.pack(anchor="w", pady=(0, 2))

            info_row = tk.Frame(tile, bg=self.theme.bg)
            info_row.pack(fill="x", padx=20)

            tk.Label(info_row, text=f"Hint: \"{ach['hint']}\"", font=self.theme.fonts["small"], bg=self.theme.bg, fg=self.theme.text_dim).pack(anchor="w")
            tk.Label(info_row, text=f"💡 Solution: {ach['solution']}", font=self.theme.fonts["small_bold"], bg=self.theme.bg, fg=self.theme.yellow).pack(anchor="w", pady=(1, 0))

        self.update_achievement_progress()

    def on_achievement_toggle(self, ach_id: int, var: tk.IntVar) -> None:
        """Saves secret achievement completion state in SQLite."""
        status = bool(var.get())
        self.db.set_secret_achievement_status(ach_id, status)
        self.update_achievement_progress()

    def select_all_achievements(self) -> None:
        for ach_id, var in self.ach_vars.items():
            var.set(1)
            self.db.set_secret_achievement_status(ach_id, True)
        self.update_achievement_progress()

    def deselect_all_achievements(self) -> None:
        for ach_id, var in self.ach_vars.items():
            var.set(0)
            self.db.set_secret_achievement_status(ach_id, False)
        self.update_achievement_progress()

    def update_achievement_progress(self) -> None:
        done = sum(1 for v in self.ach_vars.values() if v.get() == 1)
        total = len(SECRET_ACHIEVEMENTS)
        pct = (done / total * 100) if total > 0 else 0
        self.lbl_ach_progress.config(text=f"Unlocked: {done} / {total} ({pct:.0f}%)")

    # ==========================================
    # --- SUB-TAB 5: PROMO CODES ---
    # ==========================================

    def _build_promo_ui(self) -> None:
        container = tk.Frame(self.tab_promo, bg=self.theme.bg)
        container.pack(fill="both", expand=True, padx=16, pady=12)

        # Header Status Bar
        card_header = CardFrame(container, self.theme, title="In-Game Promo Codes Directory (One-Click Copy)", header_color=self.theme.green, padding=10)
        card_header.pack(fill="x", pady=(0, 10))

        self.lbl_promo_status = tk.Label(
            card_header.body,
            text="Click any 'Copy Code' button to copy the code directly to your clipboard.",
            font=self.theme.fonts["body_bold"],
            bg=self.theme.surface,
            fg=self.theme.green
        )
        self.lbl_promo_status.pack(anchor="w")

        # Codes List (2-Column Grid filling the whole window)
        card_list = CardFrame(container, self.theme, padding=8)
        card_list.pack(fill="both", expand=True)

        codes_grid = tk.Frame(card_list.body, bg=self.theme.surface)
        codes_grid.pack(fill="both", expand=True)
        codes_grid.columnconfigure(0, weight=1, uniform="code_col")
        codes_grid.columnconfigure(1, weight=1, uniform="code_col")

        for idx, item in enumerate(PROMO_CODES):
            code = item["code"]
            source = item["source"]

            r_idx = idx // 2
            c_idx = idx % 2

            row = tk.Frame(codes_grid, bg=self.theme.bg if idx % 2 == 0 else self.theme.surface, padx=10, pady=6, bd=1, relief="groove")
            row.grid(row=r_idx, column=c_idx, sticky="nsew", padx=6, pady=3)

            tk.Label(
                row, text=f"🔑 {code}", font=self.theme.fonts["body_bold"],
                bg=row["bg"], fg=self.theme.yellow, width=18, anchor="w"
            ).pack(side="left", padx=(4, 8))

            tk.Label(
                row, text=f"{source}", font=self.theme.fonts["small"],
                bg=row["bg"], fg=self.theme.text_dim, anchor="w"
            ).pack(side="left", expand=True)

            ModernButton(
                row, self.theme, text="📋 Copy", variant="primary",
                command=lambda c=code: self.copy_code_to_clipboard(c)
            ).pack(side="right", padx=4)

    def copy_code_to_clipboard(self, code: str) -> None:
        """Copies promo code string to the system clipboard and updates UI."""
        self.clipboard_clear()
        self.clipboard_append(code)
        self.lbl_promo_status.config(text=f"✅ Copied '{code}' to clipboard!", fg=self.theme.yellow)
