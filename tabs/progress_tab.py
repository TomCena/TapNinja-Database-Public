"""
Progress Tab module.
Visualizes category and total game completion with dynamic color-scaled progress bars.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any

from constants import (
    HERO_XP_COSTS, HERO_XP_CUMULATIVE, DUST_COSTS_CUMULATIVE,
    PET_FEATHER_COSTS, PET_FEATHER_CUMULATIVE, PET_BOND_TIME_COSTS,
    PET_BOND_TIME_CUMULATIVE, BUILDING_MAX_LEVEL, EQUIPMENT_DATA,
    format_seconds
)
from ui_components import CardFrame


class ProgressTab(tk.Frame):
    """Encapsulates the Progress tab UI and live calculation updates."""

    def __init__(self, parent: tk.Widget, app: Any):
        super().__init__(parent, bg=app.theme.bg)
        self.app = app
        self.db = app.db
        self.theme = app.theme

        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)

        # 1. Total Progress Card
        card_total = CardFrame(self, self.theme, title="Total Completion", header_color=self.theme.yellow)
        card_total.pack(fill="x", padx=15, pady=(15, 8))

        top_row = tk.Frame(card_total.body, bg=self.theme.surface)
        top_row.pack(fill="x", pady=(0, 4))

        tk.Label(
            top_row,
            text="Overall Game Progress (Weighted Average)",
            font=self.theme.fonts["body"],
            bg=self.theme.surface,
            fg=self.theme.text_dim
        ).pack(side="left")

        self.prog_total_val = tk.StringVar(value="0.0%")
        tk.Label(
            top_row,
            textvariable=self.prog_total_val,
            font=self.theme.fonts["metric_large"],
            bg=self.theme.surface,
            fg=self.theme.yellow
        ).pack(side="right")

        self.pb_total = ttk.Progressbar(
            card_total.body,
            orient="horizontal",
            mode="determinate",
            style="Total.Horizontal.TProgressbar"
        )
        self.pb_total.pack(fill="x", pady=(0, 4))

        # 2. Category Cards Container (2-Column Grid)
        grid_container = tk.Frame(self, bg=self.theme.bg)
        grid_container.pack(fill="both", expand=True, padx=15, pady=8)
        grid_container.columnconfigure(0, weight=1, uniform="group")
        grid_container.columnconfigure(1, weight=1, uniform="group")

        # --- Heroes Progress Card ---
        card_heroes = CardFrame(grid_container, self.theme, title="Heroes Progress", header_color=self.theme.blue)
        card_heroes.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=6)

        self.prog_hero_stars_val = tk.StringVar()
        self.pb_hero_stars = self._add_progress_row(
            card_heroes.body, "Hero Stars (Max 12):", self.prog_hero_stars_val, "HeroStars.Horizontal.TProgressbar"
        )

        self.prog_hero_xp_val = tk.StringVar()
        self.pb_hero_xp = self._add_progress_row(
            card_heroes.body, "Hero XP Levels (Max 140):", self.prog_hero_xp_val, "HeroXP.Horizontal.TProgressbar"
        )

        self.prog_hero_total_xp_val = tk.StringVar()
        self.pb_hero_total_xp = self._add_progress_row(
            card_heroes.body, "Total Hero XP Amount:", self.prog_hero_total_xp_val, "HeroTotalXP.Horizontal.TProgressbar"
        )

        self.prog_hero_dust_val = tk.StringVar()
        self.pb_hero_dust = self._add_progress_row(
            card_heroes.body, "Total Dust Spent:", self.prog_hero_dust_val, "HeroDust.Horizontal.TProgressbar"
        )

        # --- Pets Progress Card ---
        card_pets = CardFrame(grid_container, self.theme, title="Pets Progress", header_color=self.theme.purple)
        card_pets.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=6)

        self.prog_pet_stars_val = tk.StringVar()
        self.pb_pet_stars = self._add_progress_row(
            card_pets.body, "Pet Stars (Max 12):", self.prog_pet_stars_val, "PetStars.Horizontal.TProgressbar"
        )

        self.prog_pet_bond_val = tk.StringVar()
        self.pb_pet_bond = self._add_progress_row(
            card_pets.body, "Pet Bond Levels (Max 15):", self.prog_pet_bond_val, "PetBond.Horizontal.TProgressbar"
        )

        self.prog_pet_feathers_val = tk.StringVar()
        self.pb_pet_feathers = self._add_progress_row(
            card_pets.body, "Total Feathers Spent:", self.prog_pet_feathers_val, "PetFeathers.Horizontal.TProgressbar"
        )

        self.prog_pet_time_val = tk.StringVar()
        self.pb_pet_time = self._add_progress_row(
            card_pets.body, "Total Bond Time Spent:", self.prog_pet_time_val, "PetTime.Horizontal.TProgressbar"
        )

        # --- Buildings Progress Card ---
        card_build = CardFrame(grid_container, self.theme, title="Buildings Progress", header_color=self.theme.yellow)
        card_build.grid(row=1, column=0, sticky="nsew", padx=(0, 6), pady=6)

        self.prog_build_val = tk.StringVar()
        self.pb_build = self._add_progress_row(
            card_build.body, f"Total Building Levels (Max {BUILDING_MAX_LEVEL}):", self.prog_build_val, "Build.Horizontal.TProgressbar"
        )

        # --- Equipment Progress Card ---
        card_equip = CardFrame(grid_container, self.theme, title="Equipment Progress", header_color=self.theme.green)
        card_equip.grid(row=1, column=1, sticky="nsew", padx=(6, 0), pady=6)

        self.prog_equip_val = tk.StringVar()
        self.pb_equip = self._add_progress_row(
            card_equip.body, "Total Equipment Levels:", self.prog_equip_val, "Equip.Horizontal.TProgressbar"
        )

    def _add_progress_row(
        self,
        parent: tk.Widget,
        label_text: str,
        str_var: tk.StringVar,
        style_name: str
    ) -> ttk.Progressbar:
        """Helper to create a label, percentage value, and progress bar unit."""
        row = tk.Frame(parent, bg=self.theme.surface)
        row.pack(fill="x", pady=(2, 1))

        tk.Label(
            row,
            text=label_text,
            font=self.theme.fonts["body"],
            bg=self.theme.surface,
            fg=self.theme.fg
        ).pack(side="left")

        tk.Label(
            row,
            textvariable=str_var,
            font=self.theme.fonts["small_bold"],
            bg=self.theme.surface,
            fg=self.theme.text_dim
        ).pack(side="right")

        pb = ttk.Progressbar(
            parent,
            orient="horizontal",
            mode="determinate",
            style=style_name
        )
        pb.pack(fill="x", pady=(0, 6))
        return pb

    def get_progress_color(self, current: float, maximum: float) -> str:
        """Dynamic gradient: Red -> Yellow -> Green -> Gold at 100%."""
        if maximum <= 0:
            return "#414868"
        ratio = min(1.0, current / maximum)
        if ratio >= 1.0:
            return "#ffd700"  # Gold
        if ratio < 0.5:
            r = 255
            g = int(255 * (ratio * 2))
        else:
            r = int(255 * (1 - (ratio - 0.5) * 2))
            g = 255
        return f"#{r:02x}{g:02x}00"

    def refresh(self) -> None:
        """Recalculates all category completions from database records."""
        # --- Heroes Calculation ---
        hero_rows = self.db.fetch_all("SELECT name, sterne, xp_level, rarity FROM daten")
        total_heroes = len(hero_rows)

        current_stars, current_xp, current_actual_xp, current_dust = 0, 0, 0, 0
        max_dust = 0

        max_xp_per_hero = sum(HERO_XP_COSTS)
        max_actual_xp = total_heroes * max_xp_per_hero
        max_stars = total_heroes * 12
        max_xp = total_heroes * 140

        for r in hero_rows:
            name, sterne_val, xp_val, rarity = r[0], r[1], r[2], r[3]
            s = int(sterne_val) if sterne_val != '-' else 0
            current_stars += s

            x = int(xp_val) if xp_val != '-' else 0
            current_xp += x

            if x > 1:
                current_actual_xp += HERO_XP_CUMULATIVE[min(x - 1, len(HERO_XP_COSTS))]

            if not rarity:
                rarity = self.db.get_rarity(name)
            costs_cum = DUST_COSTS_CUMULATIVE.get(rarity, DUST_COSTS_CUMULATIVE["Legendary"])
            max_dust += costs_cum[-1]
            current_dust += costs_cum[max(0, min(s, 12))]

        # --- Pets Calculation ---
        pet_rows = self.db.fetch_all("SELECT sterne, bond_level FROM pets")
        total_pets = len(pet_rows)

        current_pet_stars, current_pet_bond, current_pet_feathers, current_pet_time = 0, 0, 0, 0
        max_feathers_per_pet = sum(PET_FEATHER_COSTS)
        max_pet_feathers_total = total_pets * max_feathers_per_pet
        max_time_per_pet = sum(PET_BOND_TIME_COSTS)
        max_pet_time_total = total_pets * max_time_per_pet

        for r in pet_rows:
            s = int(r[0]) if r[0] != '-' else 0
            current_pet_stars += s

            if r[1] != '-':
                b = int(r[1])
                current_pet_bond += b
                current_pet_time += PET_BOND_TIME_CUMULATIVE[max(0, b - 1)]

            current_pet_feathers += PET_FEATHER_CUMULATIVE[max(0, min(s, 12))]

        max_pet_stars = total_pets * 12
        max_pet_bond = total_pets * 15

        # --- Buildings Calculation ---
        build_rows = self.db.fetch_all("SELECT level FROM buildings")
        total_buildings = len(build_rows)
        current_build_levels = sum(int(r[0]) for r in build_rows if r[0] != '-')
        max_build_total = total_buildings * BUILDING_MAX_LEVEL

        # --- Equipment Calculation ---
        equip_rows = self.db.fetch_all("SELECT name, level FROM equipment")
        equip_map = {r[0]: r[1] for r in equip_rows}
        current_equip_levels = sum(equip_map.get(name, 0) for name in EQUIPMENT_DATA)
        max_equip_levels = sum(len(levels) - 1 for levels in EQUIPMENT_DATA.values())

        total_saved_dust = 0
        dust_by_color = []
        for col in ["Blue", "Green", "Yellow", "Red"]:
            try:
                s_val = int(self.db.get_setting(f"saved_dust_{col.lower()}", "0").replace(',', '').strip())
            except ValueError:
                s_val = 0
            total_saved_dust += s_val
            if s_val > 0:
                dust_by_color.append(f"{col[0]}:{s_val:,}")

        total_saved_feathers = 0
        feathers_by_color = []
        for col in ["Blue", "Green", "Yellow", "Red"]:
            try:
                s_val = int(self.db.get_setting(f"saved_feathers_{col.lower()}", "0").replace(',', '').strip())
            except ValueError:
                s_val = 0
            total_saved_feathers += s_val
            if s_val > 0:
                feathers_by_color.append(f"{col[0]}:{s_val:,}")

        # --- Update Progress Bars ---
        def update_bar(pb, lbl, current, maximum, style_name, is_time=False, is_exp=False, extra_saved=0, breakdown_list=None):
            if maximum > 0:
                ratio = current / maximum
                pb['value'] = min(100.0, ratio * 100)
                curr_str = format_seconds(current) if is_time else (f"{current:.2e}" if is_exp else f"{current:,}")
                max_str = format_seconds(maximum) if is_time else (f"{maximum:.2e}" if is_exp else f"{maximum:,}")
                if extra_saved > 0:
                    detail = f" [{', '.join(breakdown_list)}]" if breakdown_list else ""
                    saved_str = f" (+{extra_saved:,} saved{detail})"
                else:
                    saved_str = ""
                lbl.set(f"{curr_str}{saved_str} / {max_str} ({ratio:.1%})")
                self.theme.style.configure(style_name, background=self.get_progress_color(current, maximum))

        update_bar(self.pb_hero_stars, self.prog_hero_stars_val, current_stars, max_stars, "HeroStars.Horizontal.TProgressbar")
        update_bar(self.pb_hero_xp, self.prog_hero_xp_val, current_xp, max_xp, "HeroXP.Horizontal.TProgressbar")
        update_bar(self.pb_hero_total_xp, self.prog_hero_total_xp_val, current_actual_xp, max_actual_xp, "HeroTotalXP.Horizontal.TProgressbar")
        update_bar(self.pb_hero_dust, self.prog_hero_dust_val, current_dust, max_dust, "HeroDust.Horizontal.TProgressbar", extra_saved=total_saved_dust, breakdown_list=dust_by_color)

        update_bar(self.pb_pet_stars, self.prog_pet_stars_val, current_pet_stars, max_pet_stars, "PetStars.Horizontal.TProgressbar")
        update_bar(self.pb_pet_bond, self.prog_pet_bond_val, current_pet_bond, max_pet_bond, "PetBond.Horizontal.TProgressbar")
        update_bar(self.pb_pet_feathers, self.prog_pet_feathers_val, current_pet_feathers, max_pet_feathers_total, "PetFeathers.Horizontal.TProgressbar", extra_saved=total_saved_feathers, breakdown_list=feathers_by_color)
        update_bar(self.pb_pet_time, self.prog_pet_time_val, current_pet_time, max_pet_time_total, "PetTime.Horizontal.TProgressbar", is_time=True)

        update_bar(self.pb_build, self.prog_build_val, current_build_levels, max_build_total, "Build.Horizontal.TProgressbar")
        update_bar(self.pb_equip, self.prog_equip_val, current_equip_levels, max_equip_levels, "Equip.Horizontal.TProgressbar")

        # Total Weighted Progress
        hero_ratio = (current_stars + current_xp) / (max_stars + max_xp) if (max_stars + max_xp) > 0 else 0
        pet_ratio = (current_pet_stars + current_pet_bond) / (max_pet_stars + max_pet_bond) if (max_pet_stars + max_pet_bond) > 0 else 0
        build_ratio = current_build_levels / max_build_total if max_build_total > 0 else 0

        total_ratio = (hero_ratio + pet_ratio + build_ratio) / 3
        self.pb_total['value'] = total_ratio * 100
        self.prog_total_val.set(f"{(total_ratio * 100):.1f}%")
        self.theme.style.configure("Total.Horizontal.TProgressbar", background=self.get_progress_color(total_ratio, 1.0))
