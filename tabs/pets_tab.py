"""
Pets Tab module.
Provides Pet Datapoints management (CRUD, time calculations, feathers, sorting, and striping).
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Optional

from constants import (
    PET_NAMES, PET_FEATHER_COSTS, PET_FEATHER_CUMULATIVE,
    PET_BOND_TIME_COSTS, PET_BOND_TIME_CUMULATIVE, format_seconds
)
from ui_components import CardFrame, ModernButton, ModernEntry, ModernScrollbar, setup_treeview_striping


class PetsTab(tk.Frame):
    """Encapsulates the Pets management tab with CRUD operations, filters, and time metrics."""

    def __init__(self, parent: tk.Widget, app: Any):
        super().__init__(parent, bg=app.theme.bg)
        self.app = app
        self.db = app.db
        self.theme = app.theme

        # State Variables
        self.pet_current_id: Optional[int] = None
        self.hide_pets_var = tk.BooleanVar(value=False)

        # 4 Types of Saved Feathers: Blue, Green, Yellow, Red
        self.saved_feathers_vars = {
            "Blue": tk.StringVar(value=self.db.get_setting("saved_feathers_blue", "0")),
            "Green": tk.StringVar(value=self.db.get_setting("saved_feathers_green", "0")),
            "Yellow": tk.StringVar(value=self.db.get_setting("saved_feathers_yellow", "0")),
            "Red": tk.StringVar(value=self.db.get_setting("saved_feathers_red", "0"))
        }
        self.pet_sort_col = "Name"
        self.pet_sort_reverse = False

        hide_val = self.db.get_setting("hide_unobtained_pets", "0")
        if hide_val == '1':
            self.hide_pets_var.set(True)

        self._build_ui()

    def _build_ui(self) -> None:
        # Top Header Container (Split into Left: Controls & Right: Summary Statistics)
        header_container = tk.Frame(self, bg=self.theme.bg)
        header_container.pack(fill="x", padx=10, pady=(6, 4))

        left_frame = tk.Frame(header_container, bg=self.theme.bg)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 12))

        right_frame = tk.Frame(header_container, bg=self.theme.bg)
        right_frame.pack(side="right", fill="both", padx=(0, 0))

        # 1. Feathers Inventory Frame
        lf_feathers = tk.LabelFrame(
            left_frame,
            text="Feathers Inventory",
            bg=self.theme.bg,
            fg=self.theme.fg,
            bd=1,
            relief="groove",
            font=self.theme.fonts["small_bold"]
        )
        lf_feathers.pack(fill="x", pady=(0, 4), ipadx=4, ipady=3)

        d_row = tk.Frame(lf_feathers, bg=self.theme.bg)
        d_row.pack(fill="x", padx=6, pady=2)

        self.entry_saved_feathers = {}
        colors_cfg = [
            ("● Blue (Aquatic):", "Blue", "#60cdff"),
            ("● Green (Critter):", "Green", "#6ccb5f"),
            ("● Yellow (Bird):", "Yellow", "#ffd700"),
            ("● Red (Beast):", "Red", "#ff5252")
        ]

        for lbl_name, col_key, col_hex in colors_cfg:
            tk.Label(
                d_row,
                text=lbl_name,
                font=self.theme.fonts["body_bold"],
                bg=self.theme.bg,
                fg=col_hex
            ).pack(side="left", padx=(6, 4))

            e_f = ModernEntry(d_row, self.theme, textvariable=self.saved_feathers_vars[col_key], width=11)
            e_f.pack(side="left", padx=(0, 16))
            e_f.bind("<KeyRelease>", lambda _e, k=col_key: self.on_saved_feathers_change(k))
            e_f.bind("<FocusOut>", lambda _e, k=col_key: self.on_saved_feathers_change(k))
            e_f.bind("<Return>", lambda _e, k=col_key: self.on_saved_feathers_change(k))
            self.entry_saved_feathers[col_key] = e_f

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
        self.entry_pet_name = ModernEntry(input_row, self.theme, width=18)
        self.entry_pet_name.pack(side="left", padx=(0, 10))

        tk.Label(input_row, text="Stars:", font=self.theme.fonts["body"], bg=self.theme.bg, fg=self.theme.fg).pack(side="left", padx=(2, 4))
        self.entry_pet_sterne = ModernEntry(input_row, self.theme, width=7)
        self.entry_pet_sterne.pack(side="left", padx=(0, 10))

        tk.Label(input_row, text="Bond Level:", font=self.theme.fonts["body"], bg=self.theme.bg, fg=self.theme.fg).pack(side="left", padx=(2, 4))
        self.entry_pet_bond = ModernEntry(input_row, self.theme, width=9)
        self.entry_pet_bond.pack(side="left", padx=(0, 12))

        self.entry_pet_name.bind('<Return>', lambda e: self.add_pet_record())
        self.entry_pet_sterne.bind('<Return>', lambda e: self.add_pet_record())
        self.entry_pet_bond.bind('<Return>', lambda e: self.add_pet_record())

        # Buttons inside Data Entry
        self.pet_normal_btns = tk.Frame(input_row, bg=self.theme.bg)
        self.pet_normal_btns.pack(side="left", padx=4)

        ModernButton(self.pet_normal_btns, self.theme, text="Add", variant="success", command=self.add_pet_record).pack(side="left", padx=3)
        ModernButton(self.pet_normal_btns, self.theme, text="Update", variant="warning", command=self.update_pet_record).pack(side="left", padx=3)
        ModernButton(self.pet_normal_btns, self.theme, text="Delete", variant="danger", command=self.ask_delete_pet).pack(side="left", padx=3)
        ModernButton(self.pet_normal_btns, self.theme, text="Clear Fields", variant="neutral", command=self.clear_pet_fields_action).pack(side="left", padx=3)

        self.pet_confirm_btns = tk.Frame(input_row, bg=self.theme.bg)
        tk.Label(self.pet_confirm_btns, text="Really delete?", font=self.theme.fonts["body_bold"], fg=self.theme.red, bg=self.theme.bg).pack(side="left", padx=4)
        ModernButton(self.pet_confirm_btns, self.theme, text="Yes", variant="danger", command=self.perform_delete_pet).pack(side="left", padx=2)
        ModernButton(self.pet_confirm_btns, self.theme, text="Cancel", variant="neutral", command=self.cancel_delete_pet).pack(side="left", padx=2)

        self.pet_status_label = tk.Label(lf_data, text="", font=self.theme.fonts["small"], bg=self.theme.bg, fg=self.theme.fg)
        self.pet_status_label.pack(anchor="w", padx=6)

        # Search & Filter Row below Data Entry
        search_row = tk.Frame(left_frame, bg=self.theme.bg)
        search_row.pack(fill="x", pady=(2, 0), padx=4)

        tk.Label(search_row, text="Search:", font=self.theme.fonts["body"], bg=self.theme.bg, fg=self.theme.fg).pack(side="left", padx=(0, 4))
        self.entry_pet_search = ModernEntry(search_row, self.theme, width=18)
        self.entry_pet_search.pack(side="left", padx=(0, 14))
        self.entry_pet_search.bind("<KeyRelease>", lambda e: self.load_pets_data())

        self.chk_hide_pets = tk.Checkbutton(
            search_row,
            text="Hide unobtained",
            variable=self.hide_pets_var,
            command=self.toggle_hide_pets,
            bg=self.theme.bg,
            fg=self.theme.fg,
            selectcolor=self.theme.surface,
            activebackground=self.theme.bg,
            activeforeground=self.theme.fg,
            font=self.theme.fonts["body"]
        )
        self.chk_hide_pets.pack(side="left")

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
        self.lbl_pet_total_stars = tk.Label(stats_grid, text="Total Stars: 0", font=self.theme.fonts["body_bold"], bg=self.theme.bg, fg="#ffd700")
        self.lbl_pet_total_stars.grid(row=0, column=0, sticky="w", padx=(0, 20), pady=2)

        self.lbl_pet_total_bond = tk.Label(stats_grid, text="Total Bond Levels: 0", font=self.theme.fonts["body_bold"], bg=self.theme.bg, fg="#6ccb5f")
        self.lbl_pet_total_bond.grid(row=1, column=0, sticky="w", padx=(0, 20), pady=2)

        self.lbl_pet_total_feathers_used = tk.Label(stats_grid, text="Feathers Used: 0", font=self.theme.fonts["body_bold"], bg=self.theme.bg, fg="#e0e0e0")
        self.lbl_pet_total_feathers_used.grid(row=2, column=0, sticky="w", padx=(0, 20), pady=2)

        self.lbl_pet_total_feathers_needed = tk.Label(stats_grid, text="Feathers Needed: 0", font=self.theme.fonts["body_bold"], bg=self.theme.bg, fg="#ffa726")
        self.lbl_pet_total_feathers_needed.grid(row=3, column=0, sticky="w", padx=(0, 20), pady=2)

        self.lbl_pet_total_saved = tk.Label(stats_grid, text="Feathers Saved: 0", font=self.theme.fonts["body_bold"], bg=self.theme.bg, fg="#60cdff")
        self.lbl_pet_total_saved.grid(row=4, column=0, sticky="w", padx=(0, 20), pady=2)

        # Right Sub-Column
        self.lbl_pet_total_time_spent = tk.Label(stats_grid, text="Time Spent: 0s", font=self.theme.fonts["body_bold"], bg=self.theme.bg, fg="#e0e0e0")
        self.lbl_pet_total_time_spent.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=2)

        self.lbl_pet_total_time_left = tk.Label(stats_grid, text="Time Left: 0s", font=self.theme.fonts["body_bold"], bg=self.theme.bg, fg="#ff99a4")
        self.lbl_pet_total_time_left.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=2)

        # 4. Pets Table
        tree_card = CardFrame(self, self.theme, padding=2)
        tree_card.pack(fill="both", expand=True, padx=10, pady=(4, 8))

        scrollbar = ModernScrollbar(tree_card.body, self.theme)
        scrollbar.pack(side="right", fill="y")

        pet_cols = ("ID", "Name", "Sterne", "Bond", "Feathers Used", "Feathers Needed", "Time Spent", "Time Left")
        self.tree_pets = ttk.Treeview(
            tree_card.body,
            columns=pet_cols,
            show="headings",
            yscrollcommand=scrollbar.set,
            displaycolumns=("Name", "Sterne", "Bond", "Feathers Used", "Feathers Needed", "Time Spent", "Time Left")
        )
        scrollbar.config(command=self.tree_pets.yview)

        col_configs = [
            ("Name", "Name", 200, "w"),
            ("Sterne", "Stars", 80, "center"),
            ("Bond", "Bond Level", 100, "center"),
            ("Feathers Used", "Feathers Used", 120, "e"),
            ("Feathers Needed", "Feathers Needed", 120, "e"),
            ("Time Spent", "Time Spent", 140, "center"),
            ("Time Left", "Time Left", 140, "center")
        ]
        for col_id, col_title, col_width, anchor in col_configs:
            self.tree_pets.heading(col_id, text=col_title, command=lambda c=col_id: self.sort_pet_column(c, False))
            self.tree_pets.column(col_id, width=col_width, anchor=anchor)

        self.tree_pets.pack(fill="both", expand=True)
        setup_treeview_striping(self.tree_pets, self.theme)

        self.tree_pets.bind("<ButtonRelease-1>", self.select_pet_item)
        self.tree_pets.bind("<BackSpace>", self.ask_delete_pet)

    def show_pet_status(self, message: str, color: Optional[str] = None) -> None:
        """Displays user feedback in the Pet status bar."""
        self.pet_status_label.config(text=message, fg=color or self.theme.fg)

    def on_saved_feathers_change(self, color_key: str, _event: Optional[tk.Event] = None) -> None:
        """Saves current inventory of feathers for a specific color to settings."""
        val = self.saved_feathers_vars[color_key].get().strip()
        self.db.set_setting(f"saved_feathers_{color_key.lower()}", val)
        self.load_pets_data()
        self.app.update_global_data()

    def toggle_hide_pets(self) -> None:
        val = '1' if self.hide_pets_var.get() else '0'
        self.db.set_setting("hide_unobtained_pets", val)
        self.load_pets_data()

    def load_pets_data(self, _event: Optional[tk.Event] = None) -> None:
        """Loads and calculates pet totals and displays rows with alternating styles."""
        for row in self.tree_pets.get_children():
            self.tree_pets.delete(row)

        search_text = self.entry_pet_search.get().strip()
        query = "SELECT id, name, sterne, bond_level, feathers_used, feathers_needed FROM pets "
        params = []
        if search_text:
            query += "WHERE name LIKE ? "
            params.append(f"%{search_text}%")
        query += "ORDER BY name COLLATE NOCASE ASC"

        rows = self.db.fetch_all(query, tuple(params))

        total_stars, total_bond = 0, 0
        total_feathers_used, total_feathers_needed = 0, 0
        total_time_spent, total_time_needed = 0, 0

        for idx, row in enumerate(rows):
            r_id, name, s_str, b_str, _fu, _fn = row
            if self.hide_pets_var.get() and s_str == '-':
                continue

            current_stars = 0
            if s_str != "-":
                try:
                    current_stars = int(s_str)
                    total_stars += current_stars
                except ValueError:
                    pass

            current_bond = 0
            if b_str != "-":
                try:
                    current_bond = int(b_str)
                    total_bond += current_bond
                except ValueError:
                    pass

            s_clamped = max(0, min(current_stars, 12))
            feathers_used_val = PET_FEATHER_CUMULATIVE[s_clamped]
            feathers_needed_val = PET_FEATHER_CUMULATIVE[-1] - PET_FEATHER_CUMULATIVE[s_clamped]
            total_feathers_used += feathers_used_val
            total_feathers_needed += feathers_needed_val

            b_idx = max(0, current_bond - 1)
            time_spent_val = PET_BOND_TIME_CUMULATIVE[b_idx] if current_bond > 0 else 0
            time_needed_val = PET_BOND_TIME_CUMULATIVE[-1] - time_spent_val
            total_time_spent += time_spent_val
            total_time_needed += time_needed_val

            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree_pets.insert(
                "",
                "end",
                values=(
                    r_id, name, s_str, b_str,
                    f"{feathers_used_val:,}", f"{feathers_needed_val:,}",
                    format_seconds(time_spent_val), format_seconds(time_needed_val)
                ),
                tags=(tag,)
            )

        total_saved_feathers = 0
        for col in ["Blue", "Green", "Yellow", "Red"]:
            try:
                s_val = int(self.saved_feathers_vars[col].get().replace(',', '').strip())
            except ValueError:
                s_val = 0
            total_saved_feathers += s_val

        self.lbl_pet_total_stars.config(text=f"Total Stars: {total_stars}")
        self.lbl_pet_total_bond.config(text=f"Total Bond Levels: {total_bond}")
        self.lbl_pet_total_feathers_used.config(text=f"Feathers Used: {total_feathers_used:,}")
        self.lbl_pet_total_feathers_needed.config(text=f"Feathers Needed: {total_feathers_needed:,}")
        self.lbl_pet_total_saved.config(text=f"Feathers Saved: {total_saved_feathers:,}")
        self.lbl_pet_total_time_spent.config(text=f"Time Spent: {format_seconds(total_time_spent)}")
        self.lbl_pet_total_time_left.config(text=f"Time Left: {format_seconds(total_time_needed)}")

        if self.pet_sort_col:
            self.sort_pet_column(self.pet_sort_col, self.pet_sort_reverse)

    def add_pet_record(self, _event: Optional[tk.Event] = None) -> None:
        """Adds or updates a pet record in the database."""
        name = self.entry_pet_name.get().strip().title()
        sterne = self.entry_pet_sterne.get().strip()
        bond = self.entry_pet_bond.get().strip()

        if not name:
            self.show_pet_status("Please enter a Pet Name.", self.theme.yellow)
            return

        try:
            sterne_val = int(sterne) if sterne not in ["", "-"] else "-"
            if isinstance(sterne_val, int) and not (0 <= sterne_val <= 12):
                self.show_pet_status("Stars must be between 0 and 12.", self.theme.yellow)
                return

            bond_val = int(bond) if bond not in ["", "-"] else "-"
            if isinstance(bond_val, int) and not (1 <= bond_val <= 15):
                self.show_pet_status("Bond Level must be between 1 and 15.", self.theme.yellow)
                return

            existing = self.db.fetch_one("SELECT id, sterne, bond_level FROM pets WHERE name = ?", (name,))
            if existing:
                new_sterne = existing[1] if sterne == "" else sterne_val
                new_bond = existing[2] if bond == "" else bond_val
                self.db.run_query("UPDATE pets SET sterne = ?, bond_level = ? WHERE id = ?", (new_sterne, new_bond, existing[0]))
                msg = f"Pet '{name}' updated successfully!"
            else:
                self.db.run_query(
                    "INSERT INTO pets (name, sterne, bond_level, feathers_used, feathers_needed) VALUES (?, ?, ?, '-', '-')",
                    (name, sterne_val, bond_val)
                )
                msg = f"Pet '{name}' added successfully!"

            self.load_pets_data()
            self.clear_pet_entries()
            self.app.update_global_data()
            self.show_pet_status(msg, self.theme.green)
        except ValueError:
            self.show_pet_status("Stars and Bond Level must be integers.", self.theme.red)

    def select_pet_item(self, event: tk.Event) -> None:
        if self.tree_pets.identify("region", event.x, event.y) == "heading":
            return
        item = self.tree_pets.identify_row(event.y)
        if item:
            data = self.tree_pets.item(item, 'values')
            if data:
                self.clear_pet_entries()
                self.pet_current_id = int(data[0])
                self.entry_pet_name.insert(0, data[1])
                self.entry_pet_sterne.insert(0, data[2])
                self.entry_pet_bond.insert(0, data[3])
        else:
            self.tree_pets.selection_remove(self.tree_pets.selection())
            self.clear_pet_entries()

    def update_pet_record(self) -> None:
        if self.pet_current_id is None:
            self.show_pet_status("Please select a pet from the list first.", self.theme.yellow)
            return

        name = self.entry_pet_name.get().strip().title()
        sterne = self.entry_pet_sterne.get().strip()
        bond = self.entry_pet_bond.get().strip()

        try:
            sterne_val = int(sterne) if sterne not in ["", "-"] else "-"
            if isinstance(sterne_val, int) and not (0 <= sterne_val <= 12):
                self.show_pet_status("Stars must be between 0 and 12.", self.theme.yellow)
                return

            bond_val = int(bond) if bond not in ["", "-"] else "-"
            if isinstance(bond_val, int) and not (1 <= bond_val <= 15):
                self.show_pet_status("Bond Level must be between 1 and 15.", self.theme.yellow)
                return

            self.db.run_query("UPDATE pets SET name = ?, sterne = ?, bond_level = ? WHERE id = ?", (name, sterne_val, bond_val, self.pet_current_id))
            self.load_pets_data()
            self.clear_pet_entries()
            self.app.update_global_data()
            self.show_pet_status(f"Pet '{name}' updated!", self.theme.green)
        except ValueError:
            self.show_pet_status("Stars and Bond Level must be integers.", self.theme.red)

    def ask_delete_pet(self, _event: Optional[tk.Event] = None) -> None:
        if self.pet_current_id is None:
            self.show_pet_status("Please select a pet to delete.", self.theme.yellow)
            return
        self.pet_normal_btns.pack_forget()
        self.pet_confirm_btns.pack(side="left")
        self.show_pet_status("Confirm pet deletion?", self.theme.yellow)

    def perform_delete_pet(self, _event: Optional[tk.Event] = None) -> None:
        if self.pet_current_id is not None:
            self.db.run_query("DELETE FROM pets WHERE id = ?", (self.pet_current_id,))
            self.load_pets_data()
            self.clear_pet_entries()
            self.app.update_global_data()
            self.show_pet_status("Pet deleted.", self.theme.green)

    def cancel_delete_pet(self) -> None:
        self.pet_confirm_btns.pack_forget()
        self.pet_normal_btns.pack(side="left")
        self.show_pet_status("Deletion cancelled.", self.theme.fg)

    def clear_pet_entries(self) -> None:
        self.entry_pet_name.delete(0, tk.END)
        self.entry_pet_sterne.delete(0, tk.END)
        self.entry_pet_bond.delete(0, tk.END)
        self.pet_current_id = None
        self.pet_confirm_btns.pack_forget()
        self.pet_normal_btns.pack(side="left")

    def clear_pet_fields_action(self) -> None:
        self.entry_pet_search.delete(0, tk.END)
        self.load_pets_data()
        self.clear_pet_entries()

    def sort_pet_column(self, col: str, reverse: bool) -> None:
        """Sorts table rows considering time intervals and numerical strings."""
        self.pet_sort_col, self.pet_sort_reverse = col, reverse
        items = [(self.tree_pets.set(k, col), k) for k in self.tree_pets.get_children('')]

        def sort_key(val: str) -> Any:
            if val == "-":
                return -1
            if col in ["Time Spent", "Time Left"]:
                try:
                    parts = val.split()
                    h = int(parts[0][:-1])
                    m = int(parts[1][:-1])
                    s = int(parts[2][:-1])
                    return h * 3600 + m * 60 + s
                except Exception:
                    return 0
            try:
                return int(val.replace(',', ''))
            except ValueError:
                return val.lower()

        items.sort(key=lambda t: sort_key(t[0]), reverse=reverse)

        for index, (_val, k) in enumerate(items):
            self.tree_pets.move(k, '', index)
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree_pets.item(k, tags=(tag,))

        headers = {
            "Name": "Name", "Sterne": "Stars", "Bond": "Bond Level",
            "Feathers Used": "Feathers Used", "Feathers Needed": "Feathers Needed",
            "Time Spent": "Time Spent", "Time Left": "Time Left"
        }
        for c in headers:
            self.tree_pets.heading(c, text=headers[c])

        arrow = " ▼" if reverse else " ▲"
        self.tree_pets.heading(col, text=headers[col] + arrow, command=lambda: self.sort_pet_column(col, not reverse))
