"""
Heroes Tab module.
Includes Hero Datapoints management (CRUD, filtering, sorting, striping),
the strategic Team Calculator, and the Fashion tab.
"""

import random
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional

from constants import (
    HERO_NAMES, HERO_BASE_SCORES, HERO_DETAILS_MAP,
    HERO_XP_COSTS, HERO_XP_CUMULATIVE, DUST_COSTS_CUMULATIVE,
    FASHION_ITEMS, FASHION_COLORS, calculate_xp_time, format_seconds
)
from ui_components import CardFrame, ModernButton, ModernEntry, ModernScrollbar, setup_treeview_striping


class HeroesTab(tk.Frame):
    """Encapsulates all Hero functionality: Datapoints table, Team Calculator, and Fashion."""

    def __init__(self, parent: tk.Widget, app: Any):
        super().__init__(parent, bg=app.theme.bg)
        self.app = app
        self.db = app.db
        self.theme = app.theme

        # State Variables
        self.current_id: Optional[int] = None
        self.hide_heroes_var = tk.BooleanVar(value=False)
        self.dust_filter_var = tk.StringVar(value="All")
        
        # 4 Types of Saved Dust: Blue (Water), Green (Wind), Yellow (Earth), Red (Fire)
        self.saved_dust_vars = {
            "Blue": tk.StringVar(value=self.db.get_setting("saved_dust_blue", "0")),
            "Green": tk.StringVar(value=self.db.get_setting("saved_dust_green", "0")),
            "Yellow": tk.StringVar(value=self.db.get_setting("saved_dust_yellow", "0")),
            "Red": tk.StringVar(value=self.db.get_setting("saved_dust_red", "0"))
        }
        self.hero_sort_col = "Name"
        self.hero_sort_reverse = False

        # XP Time Calculator State
        self.last_total_xp_needed = 0
        self.xp_calc_tg_rate_var = tk.StringVar(value=self.db.get_setting("xp_calc_tg_rate", "34692"))
        self.xp_calc_away_rate_var = tk.StringVar(value=self.db.get_setting("xp_calc_away_rate", "31996"))

        # Load filter setting
        hide_val = self.db.get_setting("hide_unobtained_heroes", "0")
        if hide_val == '1':
            self.hide_heroes_var.set(True)

        self._build_ui()

    def _build_ui(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_datapoints = tk.Frame(self.notebook, bg=self.theme.bg)
        self.tab_team_calc = tk.Frame(self.notebook, bg=self.theme.bg)
        self.tab_fashion = tk.Frame(self.notebook, bg=self.theme.bg)
        self.tab_xp_calc = tk.Frame(self.notebook, bg=self.theme.bg)

        self.notebook.add(self.tab_datapoints, text="Datapoints")
        self.notebook.add(self.tab_team_calc, text="Team Calc")
        self.notebook.add(self.tab_fashion, text="Fashion")
        self.notebook.add(self.tab_xp_calc, text="XP Time Calculator")

        self._build_datapoints_ui()
        self._build_team_calc_ui()
        self._build_fashion_ui()
        self._build_xp_calc_ui()

    # ==========================================
    # --- DATAPOINTS SUB-TAB ---
    # ==========================================

    def _build_datapoints_ui(self) -> None:
        # Top Header Container (Split into Left: Controls & Right: Summary Statistics)
        header_container = tk.Frame(self.tab_datapoints, bg=self.theme.bg)
        header_container.pack(fill="x", padx=10, pady=(6, 4))

        left_frame = tk.Frame(header_container, bg=self.theme.bg)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 12))

        right_frame = tk.Frame(header_container, bg=self.theme.bg)
        right_frame.pack(side="right", fill="both", padx=(0, 0))

        # 1. Dust Inventory Frame
        lf_dust = tk.LabelFrame(
            left_frame,
            text="Dust Inventory",
            bg=self.theme.bg,
            fg=self.theme.fg,
            bd=1,
            relief="groove",
            font=self.theme.fonts["small_bold"]
        )
        lf_dust.pack(fill="x", pady=(0, 4), ipadx=4, ipady=3)

        d_row = tk.Frame(lf_dust, bg=self.theme.bg)
        d_row.pack(fill="x", padx=6, pady=2)

        self.entry_saved_dust = {}
        colors_cfg = [
            ("● Blue:", "Blue", "#60cdff"),
            ("● Green:", "Green", "#6ccb5f"),
            ("● Yellow:", "Yellow", "#ffd700"),
            ("● Red:", "Red", "#ff5252")
        ]

        for lbl_name, col_key, col_hex in colors_cfg:
            tk.Label(
                d_row,
                text=lbl_name,
                font=self.theme.fonts["body_bold"],
                bg=self.theme.bg,
                fg=col_hex
            ).pack(side="left", padx=(6, 4))

            e_dust = ModernEntry(d_row, self.theme, textvariable=self.saved_dust_vars[col_key], width=11)
            e_dust.pack(side="left", padx=(0, 16))
            e_dust.bind("<KeyRelease>", lambda _e, k=col_key: self.on_saved_dust_change(k))
            e_dust.bind("<FocusOut>", lambda _e, k=col_key: self.on_saved_dust_change(k))
            e_dust.bind("<Return>", lambda _e, k=col_key: self.on_saved_dust_change(k))
            self.entry_saved_dust[col_key] = e_dust

        # 2. Data Entry Frame
        lf_data = tk.LabelFrame(
            left_frame,
            text="Data Entry",
            bg=self.theme.bg,
            fg=self.theme.fg,
            bd=1,
            relief="groove",
            font=self.theme.fonts["small_bold"]
        )
        lf_data.pack(fill="x", pady=(0, 4), ipadx=4, ipady=3)

        input_row = tk.Frame(lf_data, bg=self.theme.bg)
        input_row.pack(fill="x", padx=6, pady=2)

        tk.Label(input_row, text="Name:", font=self.theme.fonts["body"], bg=self.theme.bg, fg=self.theme.fg).pack(side="left", padx=(2, 4))
        self.entry_name = ModernEntry(input_row, self.theme, width=18)
        self.entry_name.pack(side="left", padx=(0, 10))

        tk.Label(input_row, text="Stars:", font=self.theme.fonts["body"], bg=self.theme.bg, fg=self.theme.fg).pack(side="left", padx=(2, 4))
        self.entry_sterne = ModernEntry(input_row, self.theme, width=7)
        self.entry_sterne.pack(side="left", padx=(0, 10))

        tk.Label(input_row, text="XP Level:", font=self.theme.fonts["body"], bg=self.theme.bg, fg=self.theme.fg).pack(side="left", padx=(2, 4))
        self.entry_xp = ModernEntry(input_row, self.theme, width=9)
        self.entry_xp.pack(side="left", padx=(0, 12))

        self.entry_name.bind('<Return>', lambda e: self.add_record())
        self.entry_sterne.bind('<Return>', lambda e: self.add_record())
        self.entry_xp.bind('<Return>', lambda e: self.add_record())

        # Buttons inside Data Entry
        self.normal_btns = tk.Frame(input_row, bg=self.theme.bg)
        self.normal_btns.pack(side="left", padx=4)

        ModernButton(self.normal_btns, self.theme, text="Add", variant="success", command=self.add_record).pack(side="left", padx=3)
        ModernButton(self.normal_btns, self.theme, text="Update", variant="warning", command=self.update_record).pack(side="left", padx=3)
        ModernButton(self.normal_btns, self.theme, text="Delete", variant="danger", command=self.ask_delete).pack(side="left", padx=3)
        ModernButton(self.normal_btns, self.theme, text="Clear Fields", variant="neutral", command=self.clear_hero_fields_action).pack(side="left", padx=3)

        self.confirm_btns = tk.Frame(input_row, bg=self.theme.bg)
        tk.Label(self.confirm_btns, text="Really delete?", font=self.theme.fonts["body_bold"], fg=self.theme.red, bg=self.theme.bg).pack(side="left", padx=4)
        ModernButton(self.confirm_btns, self.theme, text="Yes", variant="danger", command=self.perform_delete).pack(side="left", padx=2)
        ModernButton(self.confirm_btns, self.theme, text="Cancel", variant="neutral", command=self.cancel_delete).pack(side="left", padx=2)

        self.status_label = tk.Label(lf_data, text="", font=self.theme.fonts["small"], bg=self.theme.bg, fg=self.theme.fg)
        self.status_label.pack(anchor="w", padx=6)

        # Search & Filter Row below Data Entry
        search_row = tk.Frame(left_frame, bg=self.theme.bg)
        search_row.pack(fill="x", pady=(2, 0), padx=4)

        tk.Label(search_row, text="Search:", font=self.theme.fonts["body"], bg=self.theme.bg, fg=self.theme.fg).pack(side="left", padx=(0, 4))
        self.entry_search = ModernEntry(search_row, self.theme, width=18)
        self.entry_search.pack(side="left", padx=(0, 14))
        self.entry_search.bind("<KeyRelease>", lambda e: self.load_data())

        self.chk_hide_heroes = tk.Checkbutton(
            search_row,
            text="Hide unobtained",
            variable=self.hide_heroes_var,
            command=self.toggle_hide_heroes,
            bg=self.theme.bg,
            fg=self.theme.fg,
            selectcolor=self.theme.surface,
            activebackground=self.theme.bg,
            activeforeground=self.theme.fg,
            font=self.theme.fonts["body"]
        )
        self.chk_hide_heroes.pack(side="left", padx=(0, 14))

        tk.Label(search_row, text="Rarity:", font=self.theme.fonts["body"], bg=self.theme.bg, fg=self.theme.fg).pack(side="left", padx=(0, 4))
        self.cmb_dust_filter = ttk.Combobox(
            search_row,
            textvariable=self.dust_filter_var,
            values=["All", "Legendary", "Epic", "Rare"],
            state="readonly",
            width=10
        )
        self.cmb_dust_filter.pack(side="left")
        self.cmb_dust_filter.bind("<<ComboboxSelected>>", lambda e: self.load_data())

        # 3. Summary Statistics Frame (Right Column)
        lf_stats = tk.LabelFrame(
            right_frame,
            text="Summary Statistics",
            bg=self.theme.bg,
            fg=self.theme.fg,
            bd=1,
            relief="groove",
            font=self.theme.fonts["small_bold"]
        )
        lf_stats.pack(fill="both", expand=True, ipadx=10, ipady=4)

        stats_grid = tk.Frame(lf_stats, bg=self.theme.bg)
        stats_grid.pack(fill="both", expand=True, padx=8, pady=4)

        # Left Sub-Column
        self.lbl_hero_total_stars = tk.Label(stats_grid, text="Total Stars: 0", font=self.theme.fonts["body_bold"], bg=self.theme.bg, fg="#ffd700")
        self.lbl_hero_total_stars.grid(row=0, column=0, sticky="w", padx=(0, 20), pady=2)

        self.lbl_hero_total_xp = tk.Label(stats_grid, text="Total XP Levels: 0", font=self.theme.fonts["body_bold"], bg=self.theme.bg, fg="#6ccb5f")
        self.lbl_hero_total_xp.grid(row=1, column=0, sticky="w", padx=(0, 20), pady=2)

        self.lbl_hero_grand_total_xp = tk.Label(stats_grid, text="Total XP: 0", font=self.theme.fonts["body_bold"], bg=self.theme.bg, fg="#e0e0e0")
        self.lbl_hero_grand_total_xp.grid(row=2, column=0, sticky="w", padx=(0, 20), pady=2)

        self.lbl_hero_total_xp_needed = tk.Label(stats_grid, text="XP Needed: 0", font=self.theme.fonts["body_bold"], bg=self.theme.bg, fg="#ff99a4")
        self.lbl_hero_total_xp_needed.grid(row=3, column=0, sticky="w", padx=(0, 20), pady=2)

        # Right Sub-Column
        self.lbl_dust_total_used = tk.Label(stats_grid, text="Dust Used: 0", font=self.theme.fonts["body_bold"], bg=self.theme.bg, fg="#ffa726")
        self.lbl_dust_total_used.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=2)

        self.lbl_dust_total_needed = tk.Label(stats_grid, text="Dust Needed: 0", font=self.theme.fonts["body_bold"], bg=self.theme.bg, fg="#6ccb5f")
        self.lbl_dust_total_needed.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=2)

        self.lbl_dust_total_saved = tk.Label(stats_grid, text="Dust Saved: 0", font=self.theme.fonts["body_bold"], bg=self.theme.bg, fg="#60cdff")
        self.lbl_dust_total_saved.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=2)

        # 4. Heroes Table (Treeview)
        tree_card = CardFrame(self.tab_datapoints, self.theme, padding=2)
        tree_card.pack(fill="both", expand=True, padx=10, pady=(4, 8))

        scrollbar = ModernScrollbar(tree_card.body, self.theme)
        scrollbar.pack(side="right", fill="y")

        cols = ("ID", "Name", "Faction", "Class", "Sterne", "Xp level", "Dust Used", "Dust Needed", "Total XP", "Next XP Cost")
        self.tree = ttk.Treeview(
            tree_card.body,
            columns=cols,
            show="headings",
            yscrollcommand=scrollbar.set,
            displaycolumns=("Name", "Faction", "Class", "Sterne", "Xp level", "Dust Used", "Dust Needed", "Total XP", "Next XP Cost")
        )
        scrollbar.config(command=self.tree.yview)

        # Headings & Widths
        col_configs = [
            ("Name", "Name", 180, "w"),
            ("Faction", "Faction", 100, "center"),
            ("Class", "Class", 100, "center"),
            ("Sterne", "Stars", 80, "center"),
            ("Xp level", "XP Level", 100, "center"),
            ("Dust Used", "Dust Used", 110, "e"),
            ("Dust Needed", "Dust Needed", 110, "e"),
            ("Total XP", "Total XP", 130, "e"),
            ("Next XP Cost", "Next XP Cost", 120, "e")
        ]
        for col_id, col_title, col_width, anchor in col_configs:
            self.tree.heading(col_id, text=col_title, command=lambda c=col_id: self.sort_column(c, False))
            self.tree.column(col_id, width=col_width, anchor=anchor)

        self.tree.pack(fill="both", expand=True)
        setup_treeview_striping(self.tree, self.theme)

        self.tree.bind("<ButtonRelease-1>", self.select_item)
        self.tree.bind("<BackSpace>", self.ask_delete)

    def show_status(self, message: str, color: Optional[str] = None) -> None:
        """Displays user feedback in the Hero status bar."""
        self.status_label.config(text=message, fg=color or self.theme.fg)

    def on_saved_dust_change(self, color_key: str, _event: Optional[tk.Event] = None) -> None:
        """Saves current inventory of dust for a specific color to settings."""
        val = self.saved_dust_vars[color_key].get().strip()
        self.db.set_setting(f"saved_dust_{color_key.lower()}", val)
        self.load_data()
        self.app.update_global_data()

    def toggle_hide_heroes(self) -> None:
        val = '1' if self.hide_heroes_var.get() else '0'
        self.db.set_setting("hide_unobtained_heroes", val)
        self.load_data()

    def load_data(self, _event: Optional[tk.Event] = None) -> None:
        """Loads and filters hero records from the database and updates totals and per-element net needed."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        search_text = self.entry_search.get().strip()
        query = "SELECT id, name, sterne, xp_level, rarity, faction, class FROM daten "
        params = []
        if search_text:
            query += "WHERE name LIKE ? "
            params.append(f"%{search_text}%")
        query += "ORDER BY name COLLATE NOCASE ASC"

        rows = self.db.fetch_all(query, tuple(params))

        total_stars, total_xp, grand_total_xp_cost, total_xp_needed = 0, 0, 0, 0
        total_dust_used, total_dust_needed = 0, 0
        filter_rarity = self.dust_filter_var.get()

        faction_map = {"Water": "Blue", "Wind": "Green", "Earth": "Yellow", "Fire": "Red"}
        dust_used_by_color = {"Blue": 0, "Green": 0, "Yellow": 0, "Red": 0}
        dust_needed_by_color = {"Blue": 0, "Green": 0, "Yellow": 0, "Red": 0}

        for idx, row in enumerate(rows):
            r_id, name, s_str, xp_str, rarity, faction, class_ = row
            if not rarity:
                rarity = self.db.get_rarity(name)

            if filter_rarity != "All" and filter_rarity != rarity:
                continue
            if self.hide_heroes_var.get() and s_str == '-':
                continue

            s = int(s_str) if s_str != '-' else 0
            xp = int(xp_str) if xp_str != '-' else 0

            total_stars += s
            total_xp += xp

            current_xp_cost = HERO_XP_CUMULATIVE[min(xp - 1, len(HERO_XP_COSTS))] if xp > 1 else 0
            next_xp_cost = f"{HERO_XP_COSTS[xp - 1]:,}" if 1 <= xp < 140 else "-"

            needed_xp = sum(HERO_XP_COSTS[max(0, xp - 1):])
            total_xp_needed += needed_xp
            grand_total_xp_cost += current_xp_cost

            costs_cum = DUST_COSTS_CUMULATIVE.get(rarity, DUST_COSTS_CUMULATIVE["Legendary"])
            s_clamped = max(0, min(s, 12))
            dust_used_val = costs_cum[s_clamped]
            dust_needed_val = costs_cum[-1] - dust_used_val
            total_dust_used += dust_used_val
            total_dust_needed += dust_needed_val

            col = faction_map.get(faction, "Blue")
            dust_used_by_color[col] += dust_used_val
            dust_needed_by_color[col] += dust_needed_val

            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert(
                "",
                "end",
                values=(
                    r_id, name, faction, class_, s_str, xp_str,
                    f"{dust_used_val:,}", f"{dust_needed_val:,}",
                    f"{current_xp_cost:,}", next_xp_cost
                ),
                tags=(tag,)
            )

        total_saved_dust = 0
        for col in ["Blue", "Green", "Yellow", "Red"]:
            try:
                s_val = int(self.saved_dust_vars[col].get().replace(',', '').strip())
            except ValueError:
                s_val = 0
            total_saved_dust += s_val

        self.lbl_hero_total_stars.config(text=f"Total Stars: {total_stars}")
        self.lbl_hero_total_xp.config(text=f"Total XP Levels: {total_xp}")
        self.lbl_hero_grand_total_xp.config(text=f"Total XP: {grand_total_xp_cost:,}")
        self.lbl_hero_total_xp_needed.config(text=f"XP Needed: {total_xp_needed:,}")
        self.lbl_dust_total_used.config(text=f"Dust Used: {total_dust_used:,}")
        self.lbl_dust_total_needed.config(text=f"Dust Needed: {total_dust_needed:,}")
        self.lbl_dust_total_saved.config(text=f"Dust Saved: {total_saved_dust:,}")

        self.last_total_xp_needed = total_xp_needed
        self.update_xp_calc()

        if self.hero_sort_col:
            self.sort_column(self.hero_sort_col, self.hero_sort_reverse)

        if self.hero_sort_col:
            self.sort_column(self.hero_sort_col, self.hero_sort_reverse)

    def add_record(self, _event: Optional[tk.Event] = None) -> None:
        """Adds or updates a hero record in the database."""
        name = self.entry_name.get().strip().title()
        sterne = self.entry_sterne.get().strip()
        xp = self.entry_xp.get().strip()

        if not name:
            self.show_status("Please enter a Hero Name.", self.theme.yellow)
            return
        if name not in HERO_NAMES:
            self.show_status(f"Hero '{name}' is not in the allowed hero list.", self.theme.yellow)
            return

        try:
            sterne_val = int(sterne) if sterne not in ["", "-"] else "-"
            if isinstance(sterne_val, int) and not (0 <= sterne_val <= 12):
                self.show_status("Stars must be between 0 and 12.", self.theme.yellow)
                return

            xp_val = int(xp) if xp not in ["", "-"] else "-"
            if isinstance(xp_val, int) and not (1 <= xp_val <= 140):
                self.show_status("XP Level must be between 1 and 140.", self.theme.yellow)
                return

            existing = self.db.fetch_one("SELECT id, sterne, xp_level FROM daten WHERE name = ?", (name,))

            if existing:
                new_sterne = sterne_val if sterne != "" else existing[1]
                new_xp = xp_val if xp != "" else existing[2]
                self.db.run_query("UPDATE daten SET sterne = ?, xp_level = ? WHERE id = ?", (new_sterne, new_xp, existing[0]))
                msg = f"Hero '{name}' updated successfully!"
            else:
                rarity = self.db.get_rarity(name)
                faction, cls = HERO_DETAILS_MAP.get(name, ("-", "-"))
                self.db.run_query(
                    "INSERT INTO daten (name, sterne, xp_level, rarity, faction, class) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, sterne_val, xp_val, rarity, faction, cls)
                )
                msg = f"Hero '{name}' added successfully!"

            self.load_data()
            self.clear_entries()
            self.app.update_global_data()
            self.show_status(msg, self.theme.green)
        except ValueError:
            self.show_status("Stars and XP Level must be valid integers.", self.theme.red)

    def select_item(self, event: tk.Event) -> None:
        """Populates the input fields when a row is clicked."""
        if self.tree.identify("region", event.x, event.y) == "heading":
            return
        item = self.tree.identify_row(event.y)
        if not item:
            self.tree.selection_remove(self.tree.selection())
            self.clear_entries()
            return

        data = self.tree.item(item, 'values')
        self.clear_entries()
        self.current_id = int(data[0])
        self.entry_name.insert(0, data[1])
        self.entry_sterne.insert(0, data[4])
        self.entry_xp.insert(0, data[5])

    def update_record(self) -> None:
        """Updates the selected hero record."""
        if self.current_id is None:
            self.show_status("Please select a hero from the list first.", self.theme.yellow)
            return

        name = self.entry_name.get().strip().title()
        sterne = self.entry_sterne.get().strip()
        xp = self.entry_xp.get().strip()

        if name not in HERO_NAMES:
            self.show_status(f"Hero '{name}' is not in the allowed hero list.", self.theme.yellow)
            return

        try:
            sterne_val = int(sterne) if sterne not in ["", "-"] else "-"
            if isinstance(sterne_val, int) and not (0 <= sterne_val <= 12):
                self.show_status("Stars must be between 0 and 12.", self.theme.yellow)
                return
            xp_val = int(xp) if xp not in ["", "-"] else "-"
            if isinstance(xp_val, int) and not (1 <= xp_val <= 140):
                self.show_status("XP Level must be between 1 and 140.", self.theme.yellow)
                return

            faction, cls = HERO_DETAILS_MAP.get(name, ("-", "-"))
            self.db.run_query(
                "UPDATE daten SET name = ?, sterne = ?, xp_level = ?, faction = ?, class = ? WHERE id = ?",
                (name, sterne_val, xp_val, faction, cls, self.current_id)
            )
            self.load_data()
            self.clear_entries()
            self.app.update_global_data()
            self.show_status(f"Hero '{name}' updated!", self.theme.green)
        except ValueError:
            self.show_status("Stars and XP Level must be integers.", self.theme.red)

    def ask_delete(self, _event: Optional[tk.Event] = None) -> None:
        """Shows deletion confirmation buttons."""
        if self.current_id is None:
            self.show_status("Please select a hero to delete.", self.theme.yellow)
            return
        self.normal_btns.pack_forget()
        self.confirm_btns.pack(side="left")
        self.show_status("Confirm deletion?", self.theme.yellow)

    def perform_delete(self, _event: Optional[tk.Event] = None) -> None:
        """Deletes the selected hero record."""
        if self.current_id is not None:
            self.db.run_query("DELETE FROM daten WHERE id = ?", (self.current_id,))
            self.load_data()
            self.clear_entries()
            self.app.update_global_data()
            self.show_status("Hero record deleted.", self.theme.green)

    def cancel_delete(self) -> None:
        """Cancels deletion and restores normal buttons."""
        self.reset_btns()
        self.show_status("Deletion cancelled.", self.theme.fg)

    def reset_btns(self) -> None:
        self.confirm_btns.pack_forget()
        self.normal_btns.pack(side="left")

    def clear_entries(self) -> None:
        self.entry_name.delete(0, tk.END)
        self.entry_sterne.delete(0, tk.END)
        self.entry_xp.delete(0, tk.END)
        self.current_id = None
        self.reset_btns()

    def clear_hero_fields_action(self) -> None:
        self.entry_search.delete(0, tk.END)
        self.load_data()
        self.clear_entries()

    def sort_column(self, col: str, reverse: bool) -> None:
        """Sorts table rows with numerical awareness and updates glyph headers."""
        self.hero_sort_col, self.hero_sort_reverse = col, reverse
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]

        def sort_key(val: str) -> Any:
            if val == "-":
                return -1
            try:
                return int(val.replace(',', ''))
            except ValueError:
                return val.lower()

        items.sort(key=lambda t: sort_key(t[0]), reverse=reverse)

        for index, (_val, k) in enumerate(items):
            self.tree.move(k, '', index)
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree.item(k, tags=(tag,))

        headers = {
            "Name": "Name", "Faction": "Faction", "Class": "Class",
            "Sterne": "Stars", "Xp level": "XP Level", "Dust Used": "Dust Used",
            "Dust Needed": "Dust Needed", "Total XP": "Total XP", "Next XP Cost": "Next XP Cost"
        }
        for c in headers:
            self.tree.heading(c, text=headers[c])

        arrow = " ▼" if reverse else " ▲"
        self.tree.heading(col, text=headers[col] + arrow, command=lambda: self.sort_column(col, not reverse))

    # ==========================================
    # --- TEAM CALCULATOR SUB-TAB ---
    # ==========================================

    def _build_team_calc_ui(self) -> None:
        main_frame = tk.Frame(self.tab_team_calc, bg=self.theme.bg)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Left Controls Card
        controls_card = CardFrame(main_frame, self.theme, title="Team Strategy Settings", header_color=self.theme.blue)
        controls_card.pack(side="left", fill="y", padx=(0, 15))

        # Opponent Factions
        tk.Label(
            controls_card.body, text="Opponent Factions (Max 2):",
            font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.fg
        ).pack(anchor="w", pady=(0, 4))

        self.team_calc_faction_vars = {
            "Fire": tk.BooleanVar(), "Water": tk.BooleanVar(),
            "Wind": tk.BooleanVar(), "Earth": tk.BooleanVar()
        }
        self.faction_checkboxes = []

        def on_faction_select():
            selected = sum(v.get() for v in self.team_calc_faction_vars.values())
            for var, chk in zip(self.team_calc_faction_vars.values(), self.faction_checkboxes):
                if selected >= 2 and not var.get():
                    chk.configure(state="disabled")
                else:
                    chk.configure(state="normal")

        fac_frame = tk.Frame(controls_card.body, bg=self.theme.surface)
        fac_frame.pack(fill="x", pady=(0, 12))

        for fac, var in self.team_calc_faction_vars.items():
            chk = tk.Checkbutton(
                fac_frame, text=fac, variable=var,
                bg=self.theme.surface, fg=self.theme.fg, selectcolor=self.theme.bg,
                activebackground=self.theme.surface, activeforeground=self.theme.fg,
                font=self.theme.fonts["body"], command=on_faction_select
            )
            chk.pack(anchor="w")
            self.faction_checkboxes.append(chk)

        # Class Composition
        tk.Label(
            controls_card.body, text="Class Composition (Sum = 5):",
            font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=self.theme.fg
        ).pack(anchor="w", pady=(0, 4))

        self.team_calc_class_vars = {
            "Warrior": tk.IntVar(value=0), "Assassin": tk.IntVar(value=0),
            "Mage": tk.IntVar(value=0), "Support": tk.IntVar(value=0)
        }

        # Load saved class preferences
        for cls in self.team_calc_class_vars:
            saved = self.db.get_setting(f"team_calc_{cls}")
            if saved:
                try:
                    self.team_calc_class_vars[cls].set(int(saved))
                except ValueError:
                    pass

        def validate_spinboxes(var_name: str):
            total = sum(v.get() for v in self.team_calc_class_vars.values())
            if total > 5:
                offending_var = self.team_calc_class_vars[var_name]
                offending_var.set(offending_var.get() - (total - 5))

        cls_frame = tk.Frame(controls_card.body, bg=self.theme.surface)
        cls_frame.pack(fill="x", pady=(0, 12))

        for i, (cls_name, var) in enumerate(self.team_calc_class_vars.items()):
            tk.Label(
                cls_frame, text=f"{cls_name}:", font=self.theme.fonts["body"],
                bg=self.theme.surface, fg=self.theme.fg
            ).grid(row=i, column=0, sticky="w", pady=2)

            sp = tk.Spinbox(
                cls_frame, from_=0, to=5, textvariable=var, width=4,
                bg=self.theme.bg, fg=self.theme.fg, buttonbackground=self.theme.btn_bg,
                relief="flat", font=self.theme.fonts["body"], highlightthickness=1,
                highlightbackground=self.theme.border
            )
            sp.grid(row=i, column=1, padx=8, pady=2)
            var.trace_add("write", lambda _n, _i, _m, cn=cls_name: validate_spinboxes(cn))

        # Toggles
        self.team_calc_faction_bonus_var = tk.BooleanVar(value=True)
        self.team_calc_support_no_faction_var = tk.BooleanVar(value=False)

        tk.Checkbutton(
            controls_card.body, text="Enable Faction Bonus Logic",
            variable=self.team_calc_faction_bonus_var, bg=self.theme.surface, fg=self.theme.fg,
            selectcolor=self.theme.bg, activebackground=self.theme.surface, activeforeground=self.theme.fg,
            font=self.theme.fonts["body"]
        ).pack(anchor="w", pady=2)

        tk.Checkbutton(
            controls_card.body, text="Disable Faction for Support",
            variable=self.team_calc_support_no_faction_var, bg=self.theme.surface, fg=self.theme.fg,
            selectcolor=self.theme.bg, activebackground=self.theme.surface, activeforeground=self.theme.fg,
            font=self.theme.fonts["body"]
        ).pack(anchor="w", pady=2)

        # Action Button
        ModernButton(
            controls_card.body, self.theme, text="Calculate Optimal Team",
            variant="success", command=self.calculate_and_display_team
        ).pack(fill="x", pady=(15, 5))

        self.team_calc_error_label = tk.Label(
            controls_card.body, text="", font=self.theme.fonts["small_bold"],
            bg=self.theme.surface, fg=self.theme.red
        )
        self.team_calc_error_label.pack(fill="x")

        # Right Results Area
        results_frame = tk.Frame(main_frame, bg=self.theme.bg)
        results_frame.pack(side="left", fill="both", expand=True)

        self.team_calc_frontline_card = CardFrame(results_frame, self.theme, title="Frontline Composition (2 Slots)", header_color=self.theme.yellow)
        self.team_calc_frontline_card.pack(fill="both", expand=True, pady=(0, 8))

        self.team_calc_backline_card = CardFrame(results_frame, self.theme, title="Backline Composition (3 Slots)", header_color=self.theme.green)
        self.team_calc_backline_card.pack(fill="both", expand=True, pady=(8, 0))

    def calculate_and_display_team(self) -> None:
        """Calculates optimal frontline/backline team lineups based on user preferences."""
        self.team_calc_error_label.config(text="")

        for widget in self.team_calc_frontline_card.body.winfo_children():
            widget.destroy()
        for widget in self.team_calc_backline_card.body.winfo_children():
            widget.destroy()

        selected_factions = [f for f, v in self.team_calc_faction_vars.items() if v.get()]
        class_composition = {c: v.get() for c, v in self.team_calc_class_vars.items()}
        faction_bonus_enabled = self.team_calc_faction_bonus_var.get()
        support_no_faction_enabled = self.team_calc_support_no_faction_var.get()

        # Save class preferences
        for cls, val in class_composition.items():
            self.db.set_setting(f"team_calc_{cls}", str(val))

        if sum(class_composition.values()) == 0:
            class_composition = {"Warrior": 2, "Assassin": 1, "Mage": 0, "Support": 2}
        elif sum(class_composition.values()) != 5:
            self.team_calc_error_label.config(text="Class sum must be exactly 5 (or 0 for default 2/1/0/2).")
            return

        fetched_heroes = self.db.fetch_all("SELECT Name, Faction, Class, Sterne FROM daten WHERE sterne != '-'")
        faction_map = {"Fire": "Wind", "Wind": "Earth", "Earth": "Water", "Water": "Fire"}

        all_heroes = []
        for name, faction, hero_class, stars_str in fetched_heroes:
            try:
                stars = int(stars_str)
            except (ValueError, TypeError):
                continue

            base_score = HERO_BASE_SCORES.get(name, 0.0)
            norm_score = (base_score / 10.0) * 100.0
            norm_stars = (stars / 12.0) * 100.0

            faction_score = 50.0
            apply_faction = faction_bonus_enabled
            if apply_faction and support_no_faction_enabled and hero_class == "Support":
                apply_faction = False

            faction_multiplier = 1.00
            if apply_faction and selected_factions:
                scores = []
                mults = []
                for opp in selected_factions:
                    if faction_map.get(faction) == opp:
                        scores.append(100.0)
                        mults.append(1.50)  # +50% Faction Advantage Bonus
                    elif faction_map.get(opp) == faction:
                        scores.append(0.0)
                        mults.append(0.50)  # -50% Faction Disadvantage
                    else:
                        scores.append(50.0)
                        mults.append(1.00)  # Neutral
                faction_score = sum(scores) / len(scores) if scores else 50.0
                faction_multiplier = sum(mults) / len(mults) if mults else 1.00

            norm_faction = faction_score
            raw_power = (norm_score * 0.60) + (norm_stars * 0.40)
            total_score = raw_power * faction_multiplier

            all_heroes.append({
                "name": name,
                "class": hero_class,
                "stars": stars,
                "score": total_score,
                "faction_score": faction_score
            })

        all_heroes.sort(key=lambda h: h['score'], reverse=True)

        selected_team = []
        heroes_by_class: Dict[str, List[dict]] = {"Warrior": [], "Assassin": [], "Mage": [], "Support": []}
        for h in all_heroes:
            if h['class'] in heroes_by_class:
                heroes_by_class[h['class']].append(h)

        for class_name, count in class_composition.items():
            for h in heroes_by_class[class_name][:count]:
                if h not in selected_team:
                    selected_team.append(h)

        if len(selected_team) < 5:
            remaining = [h for h in all_heroes if h not in selected_team]
            needed = 5 - len(selected_team)
            selected_team.extend(remaining[:needed])

        selected_team.sort(key=lambda h: h['score'], reverse=True)

        frontline, backline = [], []
        temp_team = list(selected_team)

        warriors = [h for h in temp_team if h['class'] == 'Warrior']
        for w in warriors:
            if len(frontline) < 2:
                frontline.append(w)
                temp_team.remove(w)

        while len(frontline) < 2 and temp_team:
            frontline.append(temp_team.pop(0))

        backline.extend(temp_team)
        frontline.sort(key=lambda h: h['score'], reverse=True)
        backline.sort(key=lambda h: h['score'], reverse=True)

        used_alts = set()

        def get_alt_text(hero_class: str) -> str:
            candidates = [h for h in all_heroes if h['class'] == hero_class and h not in selected_team and h['name'] not in used_alts]
            if candidates:
                best = candidates[0]
                used_alts.add(best['name'])
                return f"  |  Alt: {best['name']} ({best['stars']}★) - Score: {best['score']:.2f}"
            return ""

        def get_score_color(score: float) -> str:
            if score > 50:
                return self.theme.green
            if score < 50:
                return self.theme.red
            return self.theme.fg

        for i, hero in enumerate(frontline):
            alt_info = get_alt_text(hero['class'])
            t = f"#{i+1}  {hero['name']}  ({hero['stars']}★)  [{hero['class']}]  Score: {hero['score']:.2f}{alt_info}"
            row = tk.Frame(self.team_calc_frontline_card.body, bg=self.theme.surface)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=t, font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=get_score_color(hero['faction_score'])).pack(anchor="w")

        for i, hero in enumerate(backline):
            alt_info = get_alt_text(hero['class'])
            t = f"#{i+1}  {hero['name']}  ({hero['stars']}★)  [{hero['class']}]  Score: {hero['score']:.2f}{alt_info}"
            row = tk.Frame(self.team_calc_backline_card.body, bg=self.theme.surface)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=t, font=self.theme.fonts["body_bold"], bg=self.theme.surface, fg=get_score_color(hero['faction_score'])).pack(anchor="w")

    # ==========================================
    # --- FASHION SUB-TAB ---
    # ==========================================

    def _build_fashion_ui(self) -> None:
        main_frame = tk.Frame(self.tab_fashion, bg=self.theme.bg)
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # 1. Equipped Loadout Card
        card_loadout = CardFrame(main_frame, self.theme, title="Equipped Fashion Loadout", header_color=self.theme.purple)
        card_loadout.pack(fill="x", pady=(0, 10))

        slots_container = tk.Frame(card_loadout.body, bg=self.theme.surface)
        slots_container.pack(fill="x", pady=8)

        self.fashion_slots = []
        self.fashion_slot_colors = []

        for i in range(4):
            slot_card = tk.Frame(
                slots_container,
                bg=self.theme.bg,
                bd=1,
                relief="groove",
                padx=12,
                pady=10
            )
            slot_card.pack(side="left", expand=True, fill="x", padx=6)

            tk.Label(
                slot_card,
                text=f"Slot {chr(65 + i)}",
                font=self.theme.fonts["body_bold"],
                bg=self.theme.bg,
                fg=self.theme.fg
            ).pack()

            color_sq = tk.Frame(
                slot_card,
                width=36,
                height=36,
                bg=self.theme.surface,
                relief="solid",
                borderwidth=1
            )
            color_sq.pack(pady=(6, 4))
            color_sq.pack_propagate(False)
            self.fashion_slot_colors.append(color_sq)

            lbl_val = tk.Label(
                slot_card,
                text="Default",
                font=self.theme.fonts["card_title"],
                bg=self.theme.bg,
                fg=self.theme.yellow,
                width=14
            )
            lbl_val.pack(pady=2)
            self.fashion_slots.append(lbl_val)

        # Controls Row
        btn_row = tk.Frame(card_loadout.body, bg=self.theme.surface)
        btn_row.pack(fill="x", pady=(4, 6))

        ModernButton(
            btn_row, self.theme, text="🎲 Randomize Fashion", variant="success", command=self.randomize_fashion
        ).pack(side="left", padx=6)

        ModernButton(
            btn_row, self.theme, text="Select All", variant="neutral", command=self.select_all_fashion
        ).pack(side="left", padx=4)

        ModernButton(
            btn_row, self.theme, text="Deselect All", variant="neutral", command=self.deselect_all_fashion
        ).pack(side="left", padx=4)

        self.lbl_fashion_status = tk.Label(
            btn_row, text="", font=self.theme.fonts["small"], bg=self.theme.surface, fg=self.theme.green
        )
        self.lbl_fashion_status.pack(side="left", padx=12)

        # 2. Wardrobe Collection Grid Card
        card_collection = CardFrame(main_frame, self.theme, title="Hero Fashion & Outfits Collection", header_color=self.theme.blue, padding=6)
        card_collection.pack(fill="both", expand=True)

        # Canvas with scrollbar for responsive grid viewing
        canvas = tk.Canvas(card_collection.body, bg=self.theme.surface, highlightthickness=0)
        scrollbar = ModernScrollbar(card_collection.body, self.theme, orient="vertical", command=canvas.yview)
        self.fashion_list_frame = tk.Frame(canvas, bg=self.theme.surface)

        self.fashion_list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas_window = canvas.create_window((0, 0), window=self.fashion_list_frame, anchor="nw")

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, minsize=(event.width, event.height))

        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.fashion_vars: Dict[str, tk.IntVar] = {}
        self.load_fashion_data()

    def load_fashion_data(self) -> None:
        """Loads unlocked skin states from SQLite and builds the visual cards grid."""
        for widget in self.fashion_list_frame.winfo_children():
            widget.destroy()

        rows = self.db.fetch_all("SELECT name, is_unlocked FROM fashion")
        rows.sort(key=lambda x: FASHION_ITEMS.index(x[0]) if x[0] in FASHION_ITEMS else 999)

        self.fashion_vars = {}
        columns = 6

        for i, (name, unlocked) in enumerate(rows):
            r, c = divmod(i, columns)

            tile = tk.Frame(
                self.fashion_list_frame,
                bg=self.theme.bg,
                bd=1,
                relief="groove",
                padx=8,
                pady=6
            )
            tile.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

            header_f = tk.Frame(tile, bg=self.theme.bg)
            header_f.pack(fill="x", pady=(0, 4))

            # Color swatch preview
            col_hex = FASHION_COLORS.get(name, "#444444")
            swatch = tk.Frame(
                header_f,
                width=18,
                height=18,
                bg=col_hex,
                relief="solid",
                borderwidth=1
            )
            swatch.pack(side="left", padx=(0, 6))
            swatch.pack_propagate(False)

            tk.Label(
                header_f,
                text=name,
                font=self.theme.fonts["small_bold"],
                bg=self.theme.bg,
                fg=self.theme.fg,
                width=12,
                anchor="w"
            ).pack(side="left")

            var = tk.IntVar(value=unlocked)
            self.fashion_vars[name] = var
            cb = tk.Checkbutton(
                tile,
                text="Unlocked",
                variable=var,
                command=lambda n=name, v=var: self.on_fashion_check(n, v),
                bg=self.theme.bg,
                fg=self.theme.fg,
                selectcolor=self.theme.surface,
                activebackground=self.theme.bg,
                activeforeground=self.theme.fg,
                font=self.theme.fonts["small"]
            )
            cb.pack(anchor="w")

        for col_idx in range(columns):
            self.fashion_list_frame.columnconfigure(col_idx, weight=1)

    def on_fashion_check(self, name: str, var: tk.IntVar) -> None:
        """Saves individual skin unlock state to SQLite."""
        new_status = var.get()
        self.db.run_query("UPDATE fashion SET is_unlocked = ? WHERE name = ?", (new_status, name))
        self.lbl_fashion_status.config(text=f"Updated '{name}' status.", fg=self.theme.green)

    def select_all_fashion(self) -> None:
        """Unlocks all skins in database and refreshes checkboxes."""
        self.db.run_query("UPDATE fashion SET is_unlocked = 1")
        self.load_fashion_data()
        self.lbl_fashion_status.config(text="All skins unlocked!", fg=self.theme.green)

    def deselect_all_fashion(self) -> None:
        """Locks all skins in database (except Default) and refreshes checkboxes."""
        self.db.run_query("UPDATE fashion SET is_unlocked = CASE WHEN name = 'Default' THEN 1 ELSE 0 END")
        self.load_fashion_data()
        self.lbl_fashion_status.config(text="All skins locked (Default remains unlocked).", fg=self.theme.yellow)

    def randomize_fashion(self) -> None:
        """Rolls random unlocked skins into the 4 loadout slots with matching color swatches."""
        rows = self.db.fetch_all("SELECT name FROM fashion WHERE is_unlocked = 1")
        unlocked_items = [r[0] for r in rows]

        if not unlocked_items:
            unlocked_items = ["Default"]

        for slot_lbl, color_slot in zip(self.fashion_slots, self.fashion_slot_colors):
            choice = random.choice(unlocked_items)
            slot_lbl.config(text=choice)
            if choice in FASHION_COLORS:
                color_slot.config(bg=FASHION_COLORS[choice])
            else:
                color_slot.config(bg=self.theme.surface)

        self.lbl_fashion_status.config(text="✨ Randomized fashion loadout!", fg=self.theme.purple)

    # ==========================================
    # --- XP TIME CALCULATOR SUB-TAB ---
    # ==========================================

    def _build_xp_calc_ui(self) -> None:
        """Builds the modern XP Time Calculator interface with live rate calculations and projections."""
        calc_container = tk.Frame(self.tab_xp_calc, bg=self.theme.bg)
        calc_container.pack(fill="both", expand=True, padx=20, pady=16)

        # 1. Rate Inputs Card
        card_rates = CardFrame(
            calc_container,
            self.theme,
            title="Hourly XP Rate Configuration",
            header_color=self.theme.blue,
            padding=12
        )
        card_rates.pack(fill="x", pady=(0, 12))

        rates_grid = tk.Frame(card_rates.body, bg=self.theme.surface)
        rates_grid.pack(fill="x", pady=4)

        # Training Grounds Input
        tk.Label(
            rates_grid,
            text="Training Grounds Rate (XP/h):",
            font=self.theme.fonts["body_bold"],
            bg=self.theme.surface,
            fg=self.theme.fg
        ).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=6)

        entry_tg = ModernEntry(rates_grid, self.theme, textvariable=self.xp_calc_tg_rate_var, width=16)
        entry_tg.grid(row=0, column=1, sticky="w", padx=(0, 24), pady=6)
        entry_tg.bind("<KeyRelease>", lambda _e: self.on_xp_rate_change())
        entry_tg.bind("<FocusOut>", lambda _e: self.on_xp_rate_change())

        # Away Rate Input
        tk.Label(
            rates_grid,
            text="Away Rate (XP/h):",
            font=self.theme.fonts["body_bold"],
            bg=self.theme.surface,
            fg=self.theme.fg
        ).grid(row=0, column=2, sticky="w", padx=(0, 8), pady=6)

        entry_away = ModernEntry(rates_grid, self.theme, textvariable=self.xp_calc_away_rate_var, width=16)
        entry_away.grid(row=0, column=3, sticky="w", padx=(0, 16), pady=6)
        entry_away.bind("<KeyRelease>", lambda _e: self.on_xp_rate_change())
        entry_away.bind("<FocusOut>", lambda _e: self.on_xp_rate_change())

        # Total Combined Rate Display
        self.lbl_xp_calc_combined_rate = tk.Label(
            card_rates.body,
            text="● Combined Hourly XP Rate: 66,688 XP/h (Training Grounds + Away)",
            font=self.theme.fonts["body_bold"],
            bg=self.theme.surface,
            fg=self.theme.green
        )
        self.lbl_xp_calc_combined_rate.pack(anchor="w", pady=(6, 2))

        # 2. XP Overview Card
        card_xp_status = CardFrame(
            calc_container,
            self.theme,
            title="Total Heroes XP Status",
            header_color=self.theme.yellow,
            padding=12
        )
        card_xp_status.pack(fill="x", pady=(0, 12))

        status_row = tk.Frame(card_xp_status.body, bg=self.theme.surface)
        status_row.pack(fill="x", pady=4)

        self.lbl_xp_calc_total_needed = tk.Label(
            status_row,
            text="Total XP Needed (All Heroes to Lvl 140): 0",
            font=self.theme.fonts["body_bold"],
            bg=self.theme.surface,
            fg=self.theme.yellow
        )
        self.lbl_xp_calc_total_needed.pack(side="left", padx=(0, 30))

        # 3. Time Projection Cards (Grid)
        proj_container = tk.Frame(calc_container, bg=self.theme.bg)
        proj_container.pack(fill="both", expand=True)
        proj_container.columnconfigure(0, weight=2)
        proj_container.columnconfigure(1, weight=1)
        proj_container.columnconfigure(2, weight=1)

        # Combined Projection (Main Card)
        card_proj_main = CardFrame(
            proj_container,
            self.theme,
            title="⏳ Combined Projection (Active + Away)",
            header_color=self.theme.green,
            padding=14
        )
        card_proj_main.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=4)

        self.lbl_xp_time_hours = tk.Label(
            card_proj_main.body,
            text="Hours Remaining: 0.0 hrs",
            font=self.theme.fonts["section"],
            bg=self.theme.surface,
            fg=self.theme.fg
        )
        self.lbl_xp_time_hours.pack(anchor="w", pady=(4, 6))

        self.lbl_xp_time_days = tk.Label(
            card_proj_main.body,
            text="Days Remaining: 0.00 days",
            font=self.theme.fonts["body_bold"],
            bg=self.theme.surface,
            fg=self.theme.blue
        )
        self.lbl_xp_time_days.pack(anchor="w", pady=2)

        self.lbl_xp_time_years = tk.Label(
            card_proj_main.body,
            text="Years Remaining: 0.000 years",
            font=self.theme.fonts["body_bold"],
            bg=self.theme.surface,
            fg=self.theme.purple
        )
        self.lbl_xp_time_years.pack(anchor="w", pady=2)

        # Training Grounds Only
        card_tg = CardFrame(
            proj_container,
            self.theme,
            title="🏛️ Training Grounds Only",
            header_color=self.theme.blue,
            padding=12
        )
        card_tg.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)

        self.lbl_xp_time_tg_days = tk.Label(
            card_tg.body,
            text="0.0 days",
            font=self.theme.fonts["section"],
            bg=self.theme.surface,
            fg=self.theme.blue
        )
        self.lbl_xp_time_tg_days.pack(anchor="w", pady=(8, 4))

        tk.Label(
            card_tg.body,
            text="Excludes Away XP",
            font=self.theme.fonts["small"],
            bg=self.theme.surface,
            fg=self.theme.text_dim
        ).pack(anchor="w")

        # Away XP Only
        card_away = CardFrame(
            proj_container,
            self.theme,
            title="🌙 Away Production Only",
            header_color=self.theme.purple,
            padding=12
        )
        card_away.grid(row=0, column=2, sticky="nsew", padx=(8, 0), pady=4)

        self.lbl_xp_time_away_days = tk.Label(
            card_away.body,
            text="0.0 days",
            font=self.theme.fonts["section"],
            bg=self.theme.surface,
            fg=self.theme.purple
        )
        self.lbl_xp_time_away_days.pack(anchor="w", pady=(8, 4))

        tk.Label(
            card_away.body,
            text="Excludes TG XP",
            font=self.theme.fonts["small"],
            bg=self.theme.surface,
            fg=self.theme.text_dim
        ).pack(anchor="w")

        self.update_xp_calc()

    def on_xp_rate_change(self) -> None:
        """Saves updated XP rates to SQLite settings and recalculates time projection."""
        tg_str = self.xp_calc_tg_rate_var.get().replace(',', '').strip()
        away_str = self.xp_calc_away_rate_var.get().replace(',', '').strip()
        self.db.set_setting("xp_calc_tg_rate", tg_str)
        self.db.set_setting("xp_calc_away_rate", away_str)
        self.update_xp_calc()

    def update_xp_calc(self) -> None:
        """Recalculates XP Time projections using live total XP needed and current rates."""
        if not hasattr(self, 'lbl_xp_time_hours'):
            return

        try:
            tg_rate = float(self.xp_calc_tg_rate_var.get().replace(',', '').strip() or 0)
        except ValueError:
            tg_rate = 0.0

        try:
            away_rate = float(self.xp_calc_away_rate_var.get().replace(',', '').strip() or 0)
        except ValueError:
            away_rate = 0.0

        combined_rate = tg_rate + away_rate
        total_xp_needed = float(self.last_total_xp_needed)

        res = calculate_xp_time(0.0, total_xp_needed, tg_rate, away_rate)

        self.lbl_xp_calc_combined_rate.config(
            text=f"● Total Combined XP Rate: {int(combined_rate):,} XP/h (Training Grounds: {int(tg_rate):,} + Away: {int(away_rate):,})"
        )
        self.lbl_xp_calc_total_needed.config(
            text=f"Total XP Needed (All Heroes to Lvl 140): {int(total_xp_needed):,}"
        )

        hours_val = res["hours_both"]
        days_val = res["days_both"]
        years_val = res["years_both"]

        self.lbl_xp_time_hours.config(text=f"Hours Remaining: {hours_val:,.1f} hrs")
        self.lbl_xp_time_days.config(text=f"Days Remaining: {days_val:,.2f} days")
        self.lbl_xp_time_years.config(text=f"Years Remaining: {years_val:,.3f} years")

        self.lbl_xp_time_tg_days.config(text=f"{res['days_tg_only']:,.1f} days")
        self.lbl_xp_time_away_days.config(text=f"{res['days_away_only']:,.1f} days")
