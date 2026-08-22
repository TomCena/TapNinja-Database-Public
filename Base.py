"""
TapNinja Database Application - Modernized Desktop Architecture.
Main entry point and application coordinator for tracking heroes, pets, conquest upgrades,
elixir growth, equipment, pulls luck analytics, and game progress.
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

from constants import (
    HERO_NAMES, HERO_BASE_SCORES, HERO_DETAILS_MAP,
    RARE_HEROES, EPIC_HEROES, DUST_COSTS, DUST_COSTS_CUMULATIVE,
    HERO_XP_COSTS, HERO_XP_CUMULATIVE,
    PET_NAMES, PET_FEATHER_COSTS, PET_FEATHER_CUMULATIVE,
    PET_BOND_TIME_COSTS, PET_BOND_TIME_CUMULATIVE,
    EGG_STAR_CHANCES, SCROLL_STAR_CHANCES,
    EQUIPMENT_DATA, BUILDINGS_LIST, BUILDING_MAX_LEVEL,
    CASTLE_COSTS, OTHER_BUILDING_COSTS, ORE_MINE_COSTS,
    DEFAULT_THEME, format_seconds, get_prefix_sums
)
from database import DatabaseManager
from theme import ThemeManager, apply_windows_dark_titlebar
from ui_components import ConflictDialog

from tabs.progress_tab import ProgressTab
from tabs.stats_tab import StatsTab
from tabs.heroes_tab import HeroesTab
from tabs.pets_tab import PetsTab
from tabs.pulls_tab import PullsTab
from tabs.conquest_tab import ConquestTab
from tabs.elixir_tab import ElixirTab
from tabs.equipment_tab import EquipmentTab
from tabs.seasonal_tab import SeasonalTab
from tabs.misc_tab import MiscTab
from tabs.notepad_tab import NotepadTab
from tabs.rules_tab import RulesTab
from tabs.settings_tab import SettingsTab


class DatenVerwaltungApp:
    """
    Main Application coordinator for the TapNinja Database.
    Initializes database, theme, tab controllers, and handles global events.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("TapNinja Database & Progress Tracker")
        self.root.geometry("1800x1000")
        self.root.minsize(1200, 800)

        # Apply native Windows 11 Dark Mode and Mica title bar
        apply_windows_dark_titlebar(self.root)

        # --- Core Managers ---
        self.db = DatabaseManager()
        self.style = ttk.Style()
        self.theme = ThemeManager(self.style)

        # Load Theme from Database
        self.theme.load_from_db(self.db)
        self.theme.apply_ttk_styles()

        # Backward compatibility properties
        self.db_name = self.db.db_name
        self.hero_names = HERO_NAMES
        self.rare_heroes = RARE_HEROES
        self.epic_heroes = EPIC_HEROES
        self.dust_costs = DUST_COSTS
        self.hero_details_map = HERO_DETAILS_MAP
        self.pet_names = PET_NAMES
        self.pet_feather_costs = PET_FEATHER_COSTS
        self.egg_star_chances = EGG_STAR_CHANCES
        self.scroll_star_chances = SCROLL_STAR_CHANCES
        self.pet_bond_time_costs = PET_BOND_TIME_COSTS
        self.hero_xp_costs = HERO_XP_COSTS
        self.equipment_data = EQUIPMENT_DATA
        self.building_max_level = BUILDING_MAX_LEVEL
        self.castle_costs = CASTLE_COSTS
        self.other_building_costs = OTHER_BUILDING_COSTS
        self.ore_mine_costs = ORE_MINE_COSTS
        self.hero_xp_cumulative = HERO_XP_CUMULATIVE
        self.pet_feather_cumulative = PET_FEATHER_CUMULATIVE
        self.pet_bond_time_cumulative = PET_BOND_TIME_CUMULATIVE
        self.dust_costs_cumulative = DUST_COSTS_CUMULATIVE

        self.root.configure(bg=self.theme.bg)

        # --- Top Navigation Bar / Tabs Notebook ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(8, 4))
        self.notebook.bind("<<NotebookTabChanged>>", self._on_main_tab_changed)

        # --- Initialize Modular Tabs ---
        self.tab_progress = ProgressTab(self.notebook, self)
        self.tab_stats = StatsTab(self.notebook, self)
        self.tab_hero = HeroesTab(self.notebook, self)
        self.tab_pets = PetsTab(self.notebook, self)
        self.tab_pulls = PullsTab(self.notebook, self)
        self.tab_buildings = ConquestTab(self.notebook, self)
        self.tab_elixir = ElixirTab(self.notebook, self)
        self.tab_equipment = EquipmentTab(self.notebook, self)
        self.tab_seasonal = SeasonalTab(self.notebook, self)
        self.tab_misc = MiscTab(self.notebook, self)
        self.tab_notepad = NotepadTab(self.notebook, self)
        self.tab_rules = RulesTab(self.notebook, self)
        self.tab_settings = SettingsTab(self.notebook, self)

        # Add tabs in logical sequence
        self.notebook.add(self.tab_progress, text="Progress")
        self.notebook.add(self.tab_stats, text="Stats")
        self.notebook.add(self.tab_hero, text="Heroes")
        self.notebook.add(self.tab_pets, text="Pets")
        self.notebook.add(self.tab_pulls, text="Pulls")
        self.notebook.add(self.tab_buildings, text="Conquest")
        self.notebook.add(self.tab_elixir, text="Elixir")
        self.notebook.add(self.tab_equipment, text="Equipment")
        self.notebook.add(self.tab_seasonal, text="Seasonal")
        self.notebook.add(self.tab_misc, text="Misc")
        self.notebook.add(self.tab_notepad, text="Notepad")
        self.notebook.add(self.tab_rules, text="Info")
        self.notebook.add(self.tab_settings, text="Settings")

        # Global Deselection Binding
        self.root.bind("<Button-1>", self.on_background_click)

        # Initial Data Load across tabs
        self.reload_all_tabs()

    # --- Coordination & Refresh Methods ---

    def update_global_data(self) -> None:
        """Refreshes the high-level summary tabs (Progress and Stats)."""
        self.tab_progress.refresh()
        self.tab_stats.refresh()

    def reload_all_tabs(self) -> None:
        """Reloads all data across all tabs after import or database wipe."""
        self.tab_hero.load_data()
        self.tab_hero.load_fashion_data()
        self.tab_pets.load_pets_data()
        self.tab_pulls.load_pulls_history()
        self.tab_elixir.load_elixir_data()
        self.tab_equipment.load_saved_levels()
        self.tab_equipment.load_equipment_data()
        self.tab_seasonal.load_seasonal_data()
        self.tab_seasonal.update_graphs()
        self.tab_progress.refresh()
        self.tab_stats.refresh()

    def _on_main_tab_changed(self, _event: tk.Event) -> None:
        """Tab switch handler: resets focus and triggers targeted refreshes."""
        self.root.focus_set()
        selected_widget = self.notebook.nametowidget(self.notebook.select())
        if selected_widget == self.tab_progress:
            self.tab_progress.refresh()
        elif selected_widget == self.tab_stats:
            self.tab_stats.refresh()
        elif selected_widget == self.tab_seasonal:
            self.tab_seasonal.update_graphs()

    def apply_theme_update(self) -> None:
        """Applies theme changes app-wide, updating TTK styles, charts, and widgets."""
        old_colors = dict(self.theme.colors)
        self.theme.apply_ttk_styles()
        self.root.configure(bg=self.theme.bg)

        # Update Matplotlib Figures if present
        for tab in (self.tab_pulls, self.tab_elixir, self.tab_seasonal):
            if hasattr(tab, 'fig_scroll') and tab.fig_scroll:
                tab.fig_scroll.patch.set_facecolor(self.theme.surface)
            if hasattr(tab, 'fig_egg') and tab.fig_egg:
                tab.fig_egg.patch.set_facecolor(self.theme.surface)
            if hasattr(tab, 'fig') and tab.fig:
                tab.fig.patch.set_facecolor(self.theme.surface)

        if hasattr(self.tab_pulls, 'update_luck_stats'):
            self.tab_pulls.update_luck_stats()
        if hasattr(self.tab_elixir, 'update_elixir_graph'):
            self.tab_elixir.update_elixir_graph()
        if hasattr(self.tab_seasonal, 'update_graphs'):
            self.tab_seasonal.update_graphs()

        self.theme.update_widget_tree(self.root, old_colors)
        self.update_global_data()

        self.theme.update_widget_tree(self.root, old_colors)
        self.update_global_data()

    def on_background_click(self, event: tk.Event) -> None:
        """Clears row selections and focuses root when clicking on empty background."""
        interactive_classes = ['Entry', 'TEntry', 'Button', 'TButton', 'Treeview', 'Scrollbar', 'TScrollbar', 'Text', 'Spinbox']
        if event.widget.winfo_class() in interactive_classes:
            return

        self.root.focus_set()

        # Deselect in tables
        for tree_attr in [
            (self.tab_hero, 'tree', 'clear_entries'),
            (self.tab_pets, 'tree_pets', 'clear_pet_entries'),
            (self.tab_pulls, 'tree_scrolls', 'clear_scroll_history_entries'),
            (self.tab_pulls, 'tree_eggs', 'clear_egg_history_entries')
        ]:
            tab_obj, tree_name, clear_method = tree_attr
            if hasattr(tab_obj, tree_name):
                tree = getattr(tab_obj, tree_name)
                if tree.selection():
                    tree.selection_remove(tree.selection())
                    if hasattr(tab_obj, clear_method):
                        getattr(tab_obj, clear_method)()

        if hasattr(self.tab_elixir, 'tree_elixir') and self.tab_elixir.tree_elixir.selection():
            self.tab_elixir.tree_elixir.selection_remove(self.tab_elixir.tree_elixir.selection())

    # --- Backward-Compatibility Delegation Helpers ---

    def run_query(self, query: str, parameters: tuple = ()):
        return self.db.run_query(query, parameters)

    def get_rarity(self, name: str) -> str:
        return self.db.get_rarity(name)

    def _get_prefix_sums(self, lst):
        return get_prefix_sums(lst)

    def format_seconds(self, seconds: float | int) -> str:
        return format_seconds(seconds)


if __name__ == "__main__":
    app_root = tk.Tk()
    app = DatenVerwaltungApp(app_root)
    app_root.deiconify()
    app_root.lift()
    app_root.attributes('-topmost', True)
    app_root.after_idle(app_root.attributes, '-topmost', False)
    app_root.focus_force()
    app_root.mainloop()