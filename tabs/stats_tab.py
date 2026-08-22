"""
Stats Tab module.
Displays detailed numerical statistics and resource totals across all game mechanics.
"""

import tkinter as tk
from datetime import datetime
import math
from typing import Any, Dict

from constants import (
    HERO_XP_COSTS, HERO_XP_CUMULATIVE, DUST_COSTS_CUMULATIVE,
    PET_FEATHER_CUMULATIVE, PET_BOND_TIME_COSTS, PET_BOND_TIME_CUMULATIVE, PET_ELEMENTS_MAP,
    CASTLE_COSTS, OTHER_BUILDING_COSTS, ORE_MINE_COSTS,
    BUILDING_MAX_LEVEL, EQUIPMENT_DATA, format_seconds, calculate_xp_time
)
from ui_components import CardFrame


class StatsTab(tk.Frame):
    """Encapsulates the Statistics dashboard with elegant category summary cards."""

    def __init__(self, parent: tk.Widget, app: Any):
        super().__init__(parent, bg=app.theme.bg)
        self.app = app
        self.db = app.db
        self.theme = app.theme
        self.stats_vars: Dict[str, tk.StringVar] = {}

        self._build_ui()

    def _build_ui(self) -> None:
        container = tk.Frame(self, bg=self.theme.bg)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        container.columnconfigure(0, weight=1, uniform="stat_col")
        container.columnconfigure(1, weight=1, uniform="stat_col")

        # 1. Heroes Stats Card
        card_hero = CardFrame(container, self.theme, title="Heroes Overview", header_color=self.theme.blue)
        card_hero.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        hero_labels = [
            "Obtained", "Total Stars", "Total XP Levels", "Total XP Amount", "XP Time Remaining",
            "Total Dust Used", "Total Dust Needed",
            "● Blue Dust (Water)", "● Green Dust (Wind)",
            "● Yellow Dust (Earth)", "● Red Dust (Fire)",
            "Total Saved Dust", "Total Net Needed"
        ]
        self._populate_stat_rows(card_hero.body, "hero", hero_labels)

        # 2. Pets Stats Card (Structured Identically to Heroes)
        card_pet = CardFrame(container, self.theme, title="Pets Overview", header_color=self.theme.purple)
        card_pet.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        pet_labels = [
            "Obtained", "Total Stars", "Total Bond Levels", "Training Time Spent", "Training Time Remaining",
            "Total Feathers Used", "Total Feathers Needed",
            "● Blue Feathers (Aquatic)", "● Green Feathers (Critter)",
            "● Yellow Feathers (Bird)", "● Red Feathers (Beast)",
            "Total Saved Feathers", "Total Net Needed"
        ]
        self._populate_stat_rows(card_pet.body, "pet", pet_labels)

        # 3. Buildings Stats Card
        card_build = CardFrame(container, self.theme, title="Conquest Buildings", header_color=self.theme.yellow)
        card_build.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=10)
        build_labels = ["Total Levels", "Lumber Spent", "Lumber Needed", "Ore Spent", "Ore Needed", "Time Spent"]
        self._populate_stat_rows(card_build.body, "build", build_labels)

        # 4. Right Side Stack (Elixir & Equipment)
        right_stack = tk.Frame(container, bg=self.theme.bg)
        right_stack.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=10)
        right_stack.columnconfigure(0, weight=1)

        # Elixir Stats Card
        card_elixir = CardFrame(right_stack, self.theme, title="Elixir Overview", header_color=self.theme.green)
        card_elixir.pack(fill="x", pady=(0, 10))
        elixir_labels = ["Current Total", "Datapoints", "Avg Weekly Gain"]
        self._populate_stat_rows(card_elixir.body, "elixir", elixir_labels)

        # Equipment Stats Card
        card_equip = CardFrame(right_stack, self.theme, title="Equipment Overview", header_color=self.theme.red)
        card_equip.pack(fill="x")
        equip_labels = ["Total Levels", "Amber Spent", "Amber Needed"]
        self._populate_stat_rows(card_equip.body, "equip", equip_labels)

    def _populate_stat_rows(self, parent: tk.Widget, prefix: str, labels: list[str]) -> None:
        """Populates label-value key pairs into a card body."""
        for i, l_text in enumerate(labels):
            row = tk.Frame(parent, bg=self.theme.surface)
            row.pack(fill="x", pady=2)

            tk.Label(
                row,
                text=f"{l_text}:",
                font=self.theme.fonts["body"],
                bg=self.theme.surface,
                fg=self.theme.text_dim
            ).pack(side="left")

            var = tk.StringVar(value="-")
            self.stats_vars[f"{prefix}_{i}"] = var

            tk.Label(
                row,
                textvariable=var,
                font=self.theme.fonts["body_bold"],
                bg=self.theme.surface,
                fg=self.theme.fg
            ).pack(side="right")

    def refresh(self) -> None:
        """Recalculates all numerical summaries from database records."""
        # --- Heroes Stats ---
        hero_rows = self.db.fetch_all("SELECT name, sterne, xp_level, rarity, faction FROM daten")
        count_obtained, total_stars, total_xp_levels, total_xp_amount = 0, 0, 0, 0
        total_xp_needed = 0
        total_dust_used, total_dust_needed = 0, 0
        dust_needed_by_color = {"Blue": 0, "Green": 0, "Yellow": 0, "Red": 0}
        faction_map = {"Water": "Blue", "Wind": "Green", "Earth": "Yellow", "Fire": "Red"}

        for r in hero_rows:
            name, s_str, x_str, rarity, faction = r
            if not rarity:
                rarity = self.db.get_rarity(name)

            s = 0
            if s_str != '-':
                s = int(s_str)
                if s > 0:
                    count_obtained += 1
                total_stars += s

            x = int(x_str) if x_str != '-' else 0
            total_xp_levels += x
            if x > 1:
                total_xp_amount += HERO_XP_CUMULATIVE[min(x - 1, len(HERO_XP_COSTS))]

            needed_xp = sum(HERO_XP_COSTS[max(0, x - 1):])
            total_xp_needed += needed_xp

            costs_cum = DUST_COSTS_CUMULATIVE.get(rarity, DUST_COSTS_CUMULATIVE["Legendary"])
            s_clamped = max(0, min(s, 12))
            dust_used_val = costs_cum[s_clamped]
            dust_needed_val = costs_cum[-1] - dust_used_val
            total_dust_used += dust_used_val
            total_dust_needed += dust_needed_val

            col = faction_map.get(faction, "Blue")
            dust_needed_by_color[col] += dust_needed_val

        saved_dust_by_color = {}
        total_saved_dust = 0
        total_net_dust_needed = 0

        for col in ["Blue", "Green", "Yellow", "Red"]:
            try:
                s_val = int(self.db.get_setting(f"saved_dust_{col.lower()}", "0").replace(',', '').strip())
            except ValueError:
                s_val = 0
            saved_dust_by_color[col] = s_val
            total_saved_dust += s_val
            total_net_dust_needed += max(0, dust_needed_by_color[col] - s_val)

        # XP Time Calculation
        try:
            tg_rate = float(self.db.get_setting("xp_calc_tg_rate", "34692").replace(',', '').strip() or 0)
            away_rate = float(self.db.get_setting("xp_calc_away_rate", "31996").replace(',', '').strip() or 0)
        except ValueError:
            tg_rate, away_rate = 34692.0, 31996.0
        time_res = calculate_xp_time(0.0, total_xp_needed, tg_rate, away_rate)
        days_rem = time_res["days_both"]
        years_rem = time_res["years_both"]

        self.stats_vars["hero_0"].set(f"{count_obtained} / {len(hero_rows)}")
        self.stats_vars["hero_1"].set(f"{total_stars}")
        self.stats_vars["hero_2"].set(f"{total_xp_levels}")
        self.stats_vars["hero_3"].set(f"{total_xp_amount:,}")
        self.stats_vars["hero_4"].set(f"{days_rem:,.1f} days ({years_rem:.2f} yrs)")
        self.stats_vars["hero_5"].set(f"{total_dust_used:,}")
        self.stats_vars["hero_6"].set(f"{total_dust_needed:,}")
        self.stats_vars["hero_7"].set(f"{saved_dust_by_color['Blue']:,}  (Net: {max(0, dust_needed_by_color['Blue'] - saved_dust_by_color['Blue']):,})")
        self.stats_vars["hero_8"].set(f"{saved_dust_by_color['Green']:,}  (Net: {max(0, dust_needed_by_color['Green'] - saved_dust_by_color['Green']):,})")
        self.stats_vars["hero_9"].set(f"{saved_dust_by_color['Yellow']:,}  (Net: {max(0, dust_needed_by_color['Yellow'] - saved_dust_by_color['Yellow']):,})")
        self.stats_vars["hero_10"].set(f"{saved_dust_by_color['Red']:,}  (Net: {max(0, dust_needed_by_color['Red'] - saved_dust_by_color['Red']):,})")
        self.stats_vars["hero_11"].set(f"{total_saved_dust:,}")
        self.stats_vars["hero_12"].set(f"{total_net_dust_needed:,}")

        # --- Pets Stats (Symmetric with Heroes Overview) ---
        pet_rows = self.db.fetch_all("SELECT name, sterne, bond_level FROM pets")
        p_obtained, p_stars, p_bond, p_feathers_used, p_feathers_needed, p_time = 0, 0, 0, 0, 0, 0
        p_time_left = 0
        feathers_needed_by_color = {"Blue": 0, "Green": 0, "Yellow": 0, "Red": 0}

        for r in pet_rows:
            p_name, s_str, b_str = r[0], r[1], r[2]
            s = int(s_str) if s_str != '-' else 0
            if s > 0:
                p_obtained += 1
            p_stars += s

            b = int(b_str) if b_str != '-' else 0
            p_bond += b
            if b > 0:
                p_time += PET_BOND_TIME_CUMULATIVE[max(0, b - 1)]
            p_time_left += sum(PET_BOND_TIME_COSTS[max(0, b - 1):])

            s_clamped = max(0, min(s, 12))
            f_used = PET_FEATHER_CUMULATIVE[s_clamped]
            f_needed = PET_FEATHER_CUMULATIVE[-1] - f_used
            p_feathers_used += f_used
            p_feathers_needed += f_needed

            pet_color = PET_ELEMENTS_MAP.get(p_name, "Blue")
            feathers_needed_by_color[pet_color] += f_needed

        saved_feathers_by_color = {}
        total_saved_feathers = 0
        total_net_feathers_needed = 0

        for col in ["Blue", "Green", "Yellow", "Red"]:
            try:
                s_val = int(self.db.get_setting(f"saved_feathers_{col.lower()}", "0").replace(',', '').strip())
            except ValueError:
                s_val = 0
            saved_feathers_by_color[col] = s_val
            total_saved_feathers += s_val
            total_net_feathers_needed += max(0, feathers_needed_by_color[col] - s_val)

        self.stats_vars["pet_0"].set(f"{p_obtained} / {len(pet_rows)}")
        self.stats_vars["pet_1"].set(f"{p_stars}")
        self.stats_vars["pet_2"].set(f"{p_bond}")
        self.stats_vars["pet_3"].set(format_seconds(p_time))
        self.stats_vars["pet_4"].set(format_seconds(p_time_left))
        self.stats_vars["pet_5"].set(f"{p_feathers_used:,}")
        self.stats_vars["pet_6"].set(f"{p_feathers_needed:,}")
        self.stats_vars["pet_7"].set(f"{saved_feathers_by_color['Blue']:,}  (Net: {max(0, feathers_needed_by_color['Blue'] - saved_feathers_by_color['Blue']):,})")
        self.stats_vars["pet_8"].set(f"{saved_feathers_by_color['Green']:,}  (Net: {max(0, feathers_needed_by_color['Green'] - saved_feathers_by_color['Green']):,})")
        self.stats_vars["pet_9"].set(f"{saved_feathers_by_color['Yellow']:,}  (Net: {max(0, feathers_needed_by_color['Yellow'] - saved_feathers_by_color['Yellow']):,})")
        self.stats_vars["pet_10"].set(f"{saved_feathers_by_color['Red']:,}  (Net: {max(0, feathers_needed_by_color['Red'] - saved_feathers_by_color['Red']):,})")
        self.stats_vars["pet_11"].set(f"{total_saved_feathers:,}")
        self.stats_vars["pet_12"].set(f"{total_net_feathers_needed:,}")

        # --- Buildings Stats ---
        build_rows = self.db.fetch_all("SELECT name, level FROM buildings")
        b_levels, b_lumber, b_lumber_needed, b_ore, b_ore_needed, b_time = 0, 0, 0, 0, 0, 0

        speed_str = self.db.get_setting("const_speed", "100")
        lumber_str = self.db.get_setting("const_lumber", "100")
        ore_str = self.db.get_setting("const_ore", "100")

        try:
            mul_speed = float(speed_str) / 100.0
            mul_lumber = float(lumber_str) / 100.0
            mul_ore = float(ore_str) / 100.0
        except ValueError:
            mul_speed, mul_lumber, mul_ore = 1.0, 1.0, 1.0

        for name, lvl_str in build_rows:
            lvl = int(lvl_str) if lvl_str != '-' else 0
            b_levels += lvl
            costs_list = CASTLE_COSTS if name == "Castle" else (ORE_MINE_COSTS if "Ore Mine" in name else OTHER_BUILDING_COSTS)

            for i in range(len(costs_list)):
                cost_val = costs_list[i]
                time_sec = cost_val[0] * mul_speed
                lumber = math.ceil(cost_val[1] * mul_lumber)
                ore = math.ceil(cost_val[2] * mul_ore)

                if i < lvl:
                    b_time += time_sec
                    b_lumber += lumber
                    b_ore += ore
                if i >= lvl and i < BUILDING_MAX_LEVEL:
                    b_lumber_needed += lumber
                    b_ore_needed += ore

        self.stats_vars["build_0"].set(f"{b_levels}")
        self.stats_vars["build_1"].set(f"{b_lumber:,}")
        self.stats_vars["build_2"].set(f"{b_lumber_needed:,}")
        self.stats_vars["build_3"].set(f"{b_ore:,}")
        self.stats_vars["build_4"].set(f"{b_ore_needed:,}")
        self.stats_vars["build_5"].set(format_seconds(b_time))

        # --- Elixir Stats ---
        elixir_rows = self.db.fetch_all("SELECT date, total_elixir FROM elixir_data ORDER BY date ASC")
        if elixir_rows:
            self.stats_vars["elixir_0"].set(f"{float(elixir_rows[-1][1]):.2e}")
            self.stats_vars["elixir_1"].set(f"{len(elixir_rows)}")
            gains = []
            for i in range(1, len(elixir_rows)):
                try:
                    d1 = datetime.strptime(elixir_rows[i-1][0], "%Y-%m-%d")
                    d2 = datetime.strptime(elixir_rows[i][0], "%Y-%m-%d")
                    days = (d2 - d1).days
                    if days > 0:
                        diff = float(elixir_rows[i][1]) - float(elixir_rows[i-1][1])
                        gains.append((diff / days) * 7)
                except ValueError:
                    pass
            self.stats_vars["elixir_2"].set(f"{(sum(gains) / len(gains)):.2e}" if gains else "-")
        else:
            self.stats_vars["elixir_0"].set("-")
            self.stats_vars["elixir_1"].set("0")
            self.stats_vars["elixir_2"].set("-")

        # --- Equipment Stats ---
        equip_rows = self.db.fetch_all("SELECT name, level FROM equipment")
        equip_map = {r[0]: r[1] for r in equip_rows}
        e_levels, e_amber_spent, e_amber_needed = 0, 0, 0

        for name, levels in EQUIPMENT_DATA.items():
            lvl = equip_map.get(name, 0)
            e_levels += lvl
            e_amber_spent += sum(l[0] for l in levels[:lvl])
            e_amber_needed += sum(l[0] for l in levels[lvl:])

        self.stats_vars["equip_0"].set(f"{e_levels}")
        self.stats_vars["equip_1"].set(f"{e_amber_spent:,}")
        self.stats_vars["equip_2"].set(f"{e_amber_needed:,}")
