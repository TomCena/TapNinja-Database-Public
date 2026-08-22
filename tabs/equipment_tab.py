"""
Equipment Tab module.
Displays equipment upgrade levels, boost percentages, Amber resource costs,
and batch upgrade controls.
"""

import tkinter as tk
from typing import Any, Dict

from constants import EQUIPMENT_DATA
from ui_components import CardFrame, ModernButton


class EquipmentTab(tk.Frame):
    """Encapsulates equipment upgrade management, stat boost calculations, and Amber tracking."""

    def __init__(self, parent: tk.Widget, app: Any):
        super().__init__(parent, bg=app.theme.bg)
        self.app = app
        self.db = app.db
        self.theme = app.theme

        self.equipment_levels: Dict[str, int] = {name: 0 for name in EQUIPMENT_DATA}
        self.load_saved_levels()

        self._build_ui()

    def load_saved_levels(self) -> None:
        """Loads saved equipment levels from the SQLite database."""
        rows = self.db.fetch_all("SELECT name, level FROM equipment")
        for name, level in rows:
            if name in self.equipment_levels:
                self.equipment_levels[name] = level

    def _build_ui(self) -> None:
        # Table Card
        card_table = CardFrame(self, self.theme, title="Equipment Levels & Amber Investment", header_color=self.theme.green, padding=12)
        card_table.pack(fill="both", expand=True, padx=20, pady=(15, 8))

        self.table_frame = tk.Frame(card_table.body, bg=self.theme.surface)
        self.table_frame.pack(fill="both", expand=True)

        for i in range(6):
            self.table_frame.columnconfigure(i, weight=1)

        self.row_labels: Dict[str, Dict[str, tk.Label]] = {}
        self.load_equipment_data()

        # Action Bar
        btn_bar = tk.Frame(self, bg=self.theme.bg)
        btn_bar.pack(pady=10)

        ModernButton(
            btn_bar, self.theme, text="Max All Equipment to Cap", variant="warning",
            command=self.max_all_equipment, padx=20, pady=8
        ).pack()

    def load_equipment_data(self) -> None:
        """Constructs and populates the equipment table grid."""
        for w in self.table_frame.winfo_children():
            w.destroy()

        headers = ["Equipment", "Bonus %", "Level", "Amber Next", "Amber Needed", "Amber Used"]
        for col, text in enumerate(headers):
            lbl = tk.Label(
                self.table_frame, text=text, font=self.theme.fonts["body_bold"],
                bg=self.theme.btn_bg, fg=self.theme.fg, pady=6
            )
            lbl.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")

        row_idx = 1
        for name in EQUIPMENT_DATA:
            curr_level = self.equipment_levels[name]
            self.row_labels[name] = {}

            # 1. Name
            tk.Label(
                self.table_frame, text=name, font=self.theme.fonts["body_bold"],
                bg=self.theme.bg, fg=self.theme.fg, pady=6
            ).grid(row=row_idx, column=0, padx=2, pady=2, sticky="nsew")

            # 2. Boost
            lbl_boost = tk.Label(
                self.table_frame, text="", font=self.theme.fonts["body"],
                bg=self.theme.bg, fg=self.theme.green, pady=6
            )
            lbl_boost.grid(row=row_idx, column=1, padx=2, pady=2, sticky="nsew")
            self.row_labels[name]["boost"] = lbl_boost

            # 3. Level Controls
            lvl_frame = tk.Frame(self.table_frame, bg=self.theme.bg)
            lvl_frame.grid(row=row_idx, column=2, padx=2, pady=2, sticky="nsew")

            lbl_level = tk.Label(
                lvl_frame, text=str(curr_level), font=self.theme.fonts["body_bold"],
                bg=self.theme.bg, fg=self.theme.fg, width=4
            )

            btn_minus = ModernButton(
                lvl_frame, self.theme, text="-", variant="neutral",
                command=lambda n=name: self.change_equipment_level(n, -1),
                padx=6, pady=1
            )
            btn_plus = ModernButton(
                lvl_frame, self.theme, text="+", variant="neutral",
                command=lambda n=name: self.change_equipment_level(n, 1),
                padx=6, pady=1
            )

            btn_minus.pack(side="left", padx=4)
            lbl_level.pack(side="left", expand=True)
            btn_plus.pack(side="right", padx=4)
            self.row_labels[name]["level"] = lbl_level

            # 4. Amber Next
            lbl_next = tk.Label(
                self.table_frame, text="", font=self.theme.fonts["body"],
                bg=self.theme.bg, fg=self.theme.yellow, pady=6
            )
            lbl_next.grid(row=row_idx, column=3, padx=2, pady=2, sticky="nsew")
            self.row_labels[name]["next"] = lbl_next

            # 5. Amber Needed
            lbl_needed = tk.Label(
                self.table_frame, text="", font=self.theme.fonts["body"],
                bg=self.theme.bg, fg=self.theme.blue, pady=6
            )
            lbl_needed.grid(row=row_idx, column=4, padx=2, pady=2, sticky="nsew")
            self.row_labels[name]["needed"] = lbl_needed

            # 6. Amber Used
            lbl_used = tk.Label(
                self.table_frame, text="", font=self.theme.fonts["body"],
                bg=self.theme.bg, fg=self.theme.fg, pady=6
            )
            lbl_used.grid(row=row_idx, column=5, padx=2, pady=2, sticky="nsew")
            self.row_labels[name]["used"] = lbl_used

            self.update_row_display(name, curr_level)
            row_idx += 1

        # Totals Row
        tk.Label(
            self.table_frame, text="Total Investment", font=self.theme.fonts["body_bold"],
            bg=self.theme.surface, fg=self.theme.yellow, pady=8
        ).grid(row=row_idx, column=0, columnspan=4, padx=2, pady=(8, 2), sticky="nsew")

        self.lbl_total_amber_needed = tk.Label(
            self.table_frame, text="0", font=self.theme.fonts["body_bold"],
            bg=self.theme.surface, fg=self.theme.blue, pady=8
        )
        self.lbl_total_amber_needed.grid(row=row_idx, column=4, padx=2, pady=(8, 2), sticky="nsew")

        self.lbl_total_amber_used = tk.Label(
            self.table_frame, text="0", font=self.theme.fonts["body_bold"],
            bg=self.theme.surface, fg=self.theme.green, pady=8
        )
        self.lbl_total_amber_used.grid(row=row_idx, column=5, padx=2, pady=(8, 2), sticky="nsew")

        self.update_equipment_totals()

    def update_row_display(self, name: str, level: int) -> None:
        """Updates text labels for a single equipment row."""
        levels = EQUIPMENT_DATA[name]
        boost = levels[level][1]
        amber_next = levels[level][0]
        amber_needed = sum(l[0] for l in levels[level:])
        amber_used = sum(l[0] for l in levels[:level])

        labels = self.row_labels[name]
        labels["boost"].config(text=f"+{boost}%")
        labels["level"].config(text=str(level))
        labels["next"].config(text=f"{amber_next:,}" if amber_next > 0 else "MAX")
        labels["needed"].config(text=f"{amber_needed:,}")
        labels["used"].config(text=f"{amber_used:,}")

    def change_equipment_level(self, name: str, delta: int) -> None:
        """Increments or decrements an equipment piece level."""
        curr = self.equipment_levels[name]
        max_lvl = len(EQUIPMENT_DATA[name]) - 1
        new_lvl = curr + delta

        if 0 <= new_lvl <= max_lvl:
            self.equipment_levels[name] = new_lvl
            self.update_row_display(name, new_lvl)
            self.db.run_query("UPDATE equipment SET level = ? WHERE name = ?", (new_lvl, name))
            self.update_equipment_totals()
            self.app.update_global_data()

    def max_all_equipment(self) -> None:
        """Upgrades all equipment to maximum level."""
        for name in EQUIPMENT_DATA:
            max_lvl = len(EQUIPMENT_DATA[name]) - 1
            self.equipment_levels[name] = max_lvl
            self.db.run_query("UPDATE equipment SET level = ? WHERE name = ?", (max_lvl, name))
            self.update_row_display(name, max_lvl)

        self.update_equipment_totals()
        self.app.update_global_data()

    def update_equipment_totals(self) -> None:
        """Calculates and renders grand total Amber requirements."""
        total_needed, total_used = 0, 0
        for name, levels in EQUIPMENT_DATA.items():
            lvl = self.equipment_levels.get(name, 0)
            total_needed += sum(l[0] for l in levels[lvl:])
            total_used += sum(l[0] for l in levels[:lvl])

        if hasattr(self, 'lbl_total_amber_needed') and self.lbl_total_amber_needed.winfo_exists():
            self.lbl_total_amber_needed.config(text=f"{total_needed:,}")
        if hasattr(self, 'lbl_total_amber_used') and self.lbl_total_amber_used.winfo_exists():
            self.lbl_total_amber_used.config(text=f"{total_used:,}")
