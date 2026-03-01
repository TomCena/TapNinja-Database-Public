import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import colorchooser
import sqlite3
import math
import csv
from datetime import datetime, timedelta
import re
import random

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.dates as mdates
    import matplotlib.ticker as mticker
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

HERO_BASE_SCORES = {
    "Akira": 4.75, "Alekas": 7.75, "Alivia": 7.50, "Belu": 6.00, "Blazer": 3.67,
    "Demid": 4.67, "Dia": 7.50, "Duncan": 6.00, "Ekho": 8.25, "Elyanna": 4.00,
    "Falkron": 9.50, "Fang": 2.00, "Fin": 9.25, "Hiro": 9.75, "Husk": 7.75,
    "Irbinok": 4.00, "Jari": 2.00, "Jie": 2.00, "Kaoru": 2.33, "Kenju": 3.00,
    "Kito": 10.00, "Locke": 5.67, "Maki": 9.75, "Momo": 5.75, "Ninja": 1.67,
    "Papyrus": 5.67, "Ray": 6.75, "Sayid": 9.25, "Scarlet": 3.00, "Scorn": 7.75,
    "Scythe": 5.00, "Sketchy": 1.00, "Snow": 4.33, "Tateju": 3.00, "Terra": 3.00,
    "Tier": 7.25, "Tomak": 5.67, "Ulrik": 9.00, "Waju": 4.33, "Wasp": 3.67, "Xyzl": 5.33
}

class ConflictDialog(tk.Toplevel):
    def __init__(self, parent, date_str, old_val, new_val):
        super().__init__(parent)
        self.title("Duplicate Date")
        self.result = None
        
        bg_color = "#1a1b26"
        fg_color = "#ffffff"
        btn_bg = "#414868"
        
        self.configure(bg=bg_color)
        
        try:
            x = parent.winfo_rootx() + 100
            y = parent.winfo_rooty() + 100
            self.geometry(f"+{x}+{y}")
        except:
            pass

        msg = f"Date {date_str} already exists.\n\nExisting: {old_val}\nNew: {new_val}\n\nChoose action:"
        tk.Label(self, text=msg, padx=20, pady=20, bg=bg_color, fg=fg_color).pack()
        
        btn_frame = tk.Frame(self, bg=bg_color)
        btn_frame.pack(pady=10)
        
        buttons = [
            ("Overwrite", "overwrite"),
            ("Skip", "skip"),
            ("Overwrite All", "overwrite_all"),
            ("Skip All", "skip_all")
        ]
        
        for text, val in buttons:
            tk.Button(btn_frame, text=text, command=lambda v=val: self.set_result(v), 
                      bg=btn_bg, fg=fg_color, relief="flat", padx=10).pack(side="left", padx=5)
        
        self.transient(parent)
        self.grab_set()
        self.wait_window()
        
    def set_result(self, value):
        self.result = value
        self.destroy()

class DatenVerwaltungApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Management System")
        self.root.geometry("1600x1000")
        
        # --- Graceful DB Shutdown ---
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- OPTIMIZATION: Persistent DB Connection ---
        self.db_name = "datenbank.db"
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        
        # --- OPTIMIZATION: Timers for Debouncing ---
        self._hero_search_timer = None
        self._pet_search_timer = None

        self.hero_names = [
            "Ninja", "Fang", "Jari", "Jie", "Waju", "Tateju", "Kenju", "Sketchy", "Ray", "Kaoru",
            "Belu", "Terra", "Demid", "Momo", "Locke", "Duncan", "Sayid", "Scorn", "Tomak", "Scarlet",
            "Blazer", "Maki", "Hiro", "Akira", "Scythe", "Irbinok", "Husk", "Alivia", "Wasp", "Elyanna",
            "Fin", "Kito", "Tier", "Falkron", "Snow", "Alekas", "Papyrus", "Xyzl", "Ulrik", "Dia", "Ekho"
        ]
        self.rare_heroes = ["Ninja", "Fang", "Jari", "Jie", "Waju", "Tateju", "Kenju", "Sketchy"]
        self.epic_heroes = ["Ray", "Kaoru", "Belu", "Terra", "Demid", "Momo", "Locke", "Duncan", "Sayid"]
        
        self.dust_costs = {
            "Legendary": [100, 500, 1000, 2500, 5000, 7500, 10000, 25000, 50000, 100000, 250000, 1000000],
            "Epic": [50, 250, 500, 1250, 2500, 3750, 5000, 12500, 25000, 50000, 125000, 500000],
            "Rare": [25, 125, 250, 625, 1250, 1875, 2500, 6250, 12500, 25000, 62500, 250000]
        }
        self.hero_details_map = { 
            "Fin": ("Water", "Warrior"), "Kito": ("Water", "Assassin"), "Tier": ("Water", "Mage"), "Tièr": ("Water", "Mage"),
            "Snow": ("Water", "Support"), "Falkron": ("Water", "Support"), "Dia": ("Water", "Assassin"),
            "Husk": ("Earth", "Warrior"), "Alivia": ("Earth", "Assassin"), "Wasp": ("Earth", "Mage"),
            "Elyanna": ("Earth", "Support"), "Ulrik": ("Earth", "Warrior"), "Ekho": ("Earth", "Support"),
            "Hiro": ("Wind", "Warrior"), "Akira": ("Wind", "Assassin"), "Scythe": ("Wind", "Mage"),
            "Irbinok": ("Wind", "Support"), "Alekas": ("Wind", "Warrior"), "Papyrus": ("Wind", "Support"),
            "Scorn": ("Fire", "Warrior"), "Tomak": ("Fire", "Warrior"), "Scarlet": ("Fire", "Assassin"),
            "Blazer": ("Fire", "Mage"), "Maki": ("Fire", "Support"), "Xyzl": ("Fire", "Mage"),
            "Demid": ("Water", "Mage"), "Momo": ("Water", "Support"), "Locke": ("Water", "Mage"),
            "Terra": ("Earth", "Mage"), "Duncan": ("Earth", "Warrior"), "Kaoru": ("Wind", "Mage"),
            "Belu": ("Wind", "Warrior"), "Sayid": ("Wind", "Assassin"), "Ray": ("Fire", "Mage"),
            "Waju": ("Water", "Assassin"), "Kenju": ("Water", "Warrior"), "Tateju": ("Earth", "Warrior"),
            "Jie": ("Earth", "Support"), "Sketchy": ("Earth", "Mage"), "Ninja": ("Wind", "Assassin"),
            "Jari": ("Wind", "Warrior"), "Fang": ("Fire", "Assassin")
        }
        self.pet_names = [
            "Frog", "Turtle", "Penguin", "Crab", "Otter", "Bunny", "Mouse/Capybara", "Hedgehog",
            "Snake", "Squirrel", "Chicken/Duck", "Crane", "Raven", "Dragonfly", "Dragonling/Luckdragon",
            "Parrot/Peafowl", "Cat", "Dog/Wolf", "Fox", "Panda", "Racoon"
        ]
        self.pet_feather_costs = [5, 10, 25, 50, 200, 500, 1000, 2500, 5000, 10000, 25000, 100000]
        self.egg_star_chances = [20.0, 24.0, 22.5, 15.0, 9.2, 4.6, 2.8, 1.2, 0.45, 0.18, 0.072, 0.045] 
        self.scroll_star_chances= [20.0, 16.0, 12.8, 25.6, 12.8, 6.4, 3.2, 1.9, 0.77, 0.31, 0.124, 0.083] 
        self.pet_bond_time_costs = [200, 11520, 46080, 103680, 172800, 270720, 368640, 460800, 604800, 806400, 1152000, 1152000, 1152000, 1152000] 
        self.hero_xp_costs = [
            100, 150, 200, 250, 300, 350, 400, 450, 500,
            600, 700, 800, 900, 1000,
            1200, 1400, 1600, 1800, 2000,
            2250, 2500, 2750, 3000,
            3500, 4000, 4500, 5000,
            6000, 7000, 8000, 9000, 10000,
            12000, 14000, 16000, 18000, 20000,
            22000, 24000, 26000, 28000, 30000,
            32500, 35000, 37500, 40000, 42500, 45000, 47500, 50000, 52500, 55000, 57500, 60000, 62500, 65000, 67500, 70000, 72500, 75000, 77500, 80000, 82500, 85000, 87500, 90000, 92500, 95000, 97500, 100000,
            105000, 110000, 115000, 120000, 125000, 130000, 135000, 140000, 145000, 150000,
            160000, 170000, 180000, 190000, 200000, 210000, 220000, 230000, 240000,
            260000, 280000, 300000, 320000, 340000, 360000, 380000, 400000,
            450000, 500000, 550000, 600000, 650000, 700000, 750000, 800000, 850000, 900000, 950000, 1000000,
            1050000, 1100000, 1150000, 1200000, 1250000, 1300000, 1350000, 1400000, 1450000, 1500000,
            1575000, 1650000, 1725000, 1800000, 1875000, 1950000, 2025000, 2100000, 2175000, 2250000, 2325000, 2400000, 2475000, 2550000, 2625000, 2700000, 2775000, 2850000, 2925000, 3000000
        ]
        
        self.equipment_data = {
            "Kimono": [[50, 0], [140, 25], [268, 50], [403, 75], [526, 100], [569, 125], [750, 150], [871, 175], [992, 200], [1113, 225], [1234, 250], [1355, 275], [1476, 300], [1598, 325], [1719, 350], [1840, 375], [1961, 400], [2082, 425], [2203, 450], [2324, 475], [2425, 500], [2505, 525], [2565, 550], [2605, 575], [2625, 600], [0, 625]],
            "Katana": [[75, 0], [142, 7.5], [241, 15], [408, 22.5], [536, 30], [664, 37.5], [792, 45], [920, 52.5], [1048, 60], [1176, 67.5], [1304, 75], [1431, 82.5], [1559, 90], [1687, 97.5], [1815, 105], [1943, 112.5], [2071, 120], [2199, 127.5], [2327, 135], [2455, 142.5], [2456, 150], [2457, 157.5], [2458, 165], [2459, 172.5], [2460, 180], [0, 187.5]],
            "Kabuto": [[100, 0], [221, 2.5], [349, 5], [484, 7.5], [607, 10], [727, 12.5], [842, 15], [952, 17.5], [1057, 20], [1158, 22.5], [1259, 25], [1360, 27.5], [1461, 30], [1562, 32.5], [1663, 35], [1764, 37.5], [1865, 40], [1966, 42.5], [2067, 45], [2168, 47.5], [2269, 50], [2370, 52.5], [2471, 55], [2572, 57.5], [2673, 60], [0, 62.5]],
            "Geta": [[50, 0], [100, 15], [175, 30], [250, 45], [330, 60], [410, 75], [490, 90], [570, 105], [650, 120], [735, 135], [820, 150], [905, 165], [990, 180], [1075, 195], [1165, 210], [1255, 225], [1345, 240], [1435, 255], [1525, 270], [1620, 285], [1715, 300], [1810, 315], [1905, 330], [2000, 345], [2095, 360], [0, 375]],
            "Kote": [[200, 0], [220, 0.4], [378, 0.8], [559, 1.2], [678, 1.6], [814, 2], [997, 2.4], [1154, 2.8], [1250, 3.2], [1437, 3.6], [1614, 4], [1767, 4.4], [1882, 4.8], [2072, 5.2], [2253, 5.6], [2418, 6], [2560, 6.4], [2782, 6.8], [2754, 7.2], [2779, 7.6], [3057, 8], [3026, 8.4], [3126, 8.8], [3267, 9.2], [3420, 9.6], [0, 10]],
            "Yubiwa": [[500, 0], [625, 4], [750, 8], [875, 12], [1000, 16], [1125, 20], [1250, 24], [1375, 28], [1500, 32], [1625, 36], [1750, 40], [1875, 44], [2000, 48], [2125, 52], [2250, 56], [2375, 60], [2500, 64], [2625, 68], [2750, 72], [2875, 76], [3000, 80], [3125, 84], [3250, 88], [3375, 92], [3500, 96], [0, 100]],
            "Menpo": [[250, 0], [300, 0.4], [400, 0.8], [500, 1.2], [600, 1.6], [800, 2], [1000, 2.4], [1100, 2.8], [1250, 3.2], [1500, 3.6], [1600, 4], [1750, 4.4], [1900, 4.8], [2000, 5.2], [2250, 5.6], [2400, 6], [2500, 6.4], [2600, 6.8], [2750, 7.2], [2800, 7.6], [2900, 8], [3000, 8.4], [3100, 8.8], [3250, 9.2], [3500, 9.6], [0, 10]]
        }

        self.equipment_levels = {name: 0 for name in self.equipment_data}

        self.hero_xp_cumulative = self._get_prefix_sums(self.hero_xp_costs)
        self.pet_feather_cumulative = self._get_prefix_sums(self.pet_feather_costs)
        self.pet_bond_time_cumulative = self._get_prefix_sums(self.pet_bond_time_costs)
        self.dust_costs_cumulative = {k: self._get_prefix_sums(v) for k, v in self.dust_costs.items()}
        
        self.fashion_items = [
            "Default", "Ruby Red", "Bamboo", "Lapis Lazuli", "Iris", "Amber", "Lime", 
            "Navy Blue", "Magenta", "Citrine", "Moss Green", "Opal", "Chestnut", 
            "Bellflower", "Jasmine", "Crimson", "Pear", "Granite", "Charcoal", 
            "Bronze", "Sage", "Peach", "Azure", "Lavender", "Amethyst", "Orchid", 
            "Sandy Brown", "Apple Green", "Sapphire", "Night Black"
        ]

        self.fashion_colors = {
            "Ruby Red": "#9B111E", "Bamboo": "#006442", "Lapis Lazuli": "#26619C", "Iris": "#5D3FD3",
            "Amber": "#FF7E00", "Lime": "#00FF00", "Navy Blue": "#000080", "Magenta": "#FF1DCE",
            "Citrine": "#E4D00A", "Moss Green": "#4A5D23", "Opal": "#A8C3BC", "Chestnut": "#954535",
            "Bellflower": "#5D3F6A", "Jasmine": "#F8DE7E", "Crimson": "#DC143C", "Pear": "#D1E231",
            "Granite": "#676767", "Charcoal": "#36454F", "Bronze": "#CD7F32", "Sage": "#BCB88A",
            "Peach": "#F47983", "Azure": "#007FFF", "Lavender": "#B57EDC", "Amethyst": "#9966CC",
            "Orchid": "#DA70D6", "Sandy Brown": "#F4A460", "Apple Green": "#8DB600", "Sapphire": "#082567",
            "Night Black": "#292C36"
        }

        self.init_db() 
        self.load_saved_equipment_levels()

        self.default_theme = { 
            "bg_color": "#1a1b26", "fg_color": "#ffffff", "entry_bg": "#24283b", "btn_bg": "#414868",
            "accent_green": "#66bb6a", "accent_yellow": "#ffb74d", "accent_red": "#ef5350"
        }
        self.load_theme() 
        self.building_max_level = 14 

        self.root.configure(bg=self.bg_color)

        style = ttk.Style()
        self.style = style
        style.theme_use("clam") 
        style.configure("Treeview", background=self.entry_bg, foreground=self.fg_color, fieldbackground=self.entry_bg, borderwidth=0)
        style.configure("Treeview.Heading", background="#333333", foreground=self.fg_color, relief="flat")
        style.map("Treeview", background=[('selected', '#b0bec5')], foreground=[('selected', 'black')])

        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.btn_bg, foreground=self.fg_color, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", self.accent_green)], foreground=[("selected", "white")])
        
        self.hide_heroes_var = tk.BooleanVar(value=False)
        self.hide_pets_var = tk.BooleanVar(value=False)
        self.dust_filter_var = tk.StringVar(value="All")
        
        self.hero_sort_col = "Name"
        self.hero_sort_reverse = False
        self.pet_sort_col = "Name"
        self.pet_sort_reverse = False
        self.pet_feathers_used_sort_reverse = False
        self.pet_feathers_needed_sort_reverse = False
        self.pet_time_spent_sort_reverse = False
        self.pet_time_needed_sort_reverse = False
        self.elixir_sort_col = "Date"
        self.elixir_sort_reverse = True
        self.scroll_sort_col = "Date"
        self.scroll_sort_reverse = True
        self.egg_sort_col = "Date"
        self.egg_sort_reverse = True
        
        self.show_weekly_gain_var = tk.BooleanVar(value=True)
        self.show_future_projection_var = tk.BooleanVar(value=False)
        self.notepad_save_timer = None 
        self.calculated_avg_growth = 0.0 
        self.selected_scroll_id = None 
        self.selected_egg_id = None 
        
        with self.conn:
            c = self.conn.cursor()
            c.execute("SELECT value FROM settings WHERE key='hide_unobtained_heroes'")
            result = c.fetchone()
            if result and result[0] == '1':
                self.hide_heroes_var.set(True)

            c.execute("SELECT value FROM settings WHERE key='hide_unobtained_pets'")
            result = c.fetchone()
            if result and result[0] == '1':
                self.hide_pets_var.set(True)

            self.const_speed_var = tk.StringVar(value="100")
            self.const_lumber_var = tk.StringVar(value="100")
            self.const_ore_var = tk.StringVar(value="100")
            
            c.execute("SELECT value FROM settings WHERE key='const_speed'")
            res = c.fetchone()
            if res: self.const_speed_var.set(res[0])
            
            c.execute("SELECT value FROM settings WHERE key='const_lumber'")
            res = c.fetchone()
            if res: self.const_lumber_var.set(res[0])
            
            c.execute("SELECT value FROM settings WHERE key='const_ore'")
            res = c.fetchone()
            if res: self.const_ore_var.set(res[0])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.tab_progress = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_stats = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_hero = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_pets = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_pulls = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_buildings = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_elixir = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_equipment = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_notepad = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_rules = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_settings = tk.Frame(self.notebook, bg=self.bg_color)

        self.notebook.add(self.tab_progress, text="Progress")
        self.notebook.add(self.tab_stats, text="Stats")
        self.notebook.add(self.tab_hero, text="Heroes")
        self.notebook.add(self.tab_pets, text="Pets")
        self.notebook.add(self.tab_pulls, text="Pulls")
        self.notebook.add(self.tab_buildings, text="Conquest")
        self.notebook.add(self.tab_elixir, text="Elixir")
        self.notebook.add(self.tab_equipment, text="Equipment")
        self.notebook.add(self.tab_notepad, text="Notepad")
        self.notebook.add(self.tab_rules, text="Rules")
        self.notebook.add(self.tab_settings, text="Settings")

        # --- Progress Tab UI ---
        self.tab_progress.columnconfigure(0, weight=1)

        self.prog_total_frame = tk.LabelFrame(self.tab_progress, text="Total Progress", bg=self.bg_color, fg=self.fg_color)
        self.prog_total_frame.pack(fill="x", padx=10, pady=10)

        self.prog_total_val = tk.StringVar()
        tk.Label(self.prog_total_frame, textvariable=self.prog_total_val, bg=self.bg_color, fg=self.fg_color).pack(anchor="e", padx=5)
        self.pb_total = ttk.Progressbar(self.prog_total_frame, orient="horizontal", length=100, mode="determinate", style="Total.Horizontal.TProgressbar")
        self.pb_total.pack(fill="x", padx=5, pady=(0, 10))

        self.prog_hero_frame = tk.LabelFrame(self.tab_progress, text="Heroes Progress", bg=self.bg_color, fg=self.fg_color)
        self.prog_hero_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(self.prog_hero_frame, text="Hero Stars (Max 12):", bg=self.bg_color, fg=self.fg_color).pack(anchor="w", padx=5)
        self.prog_hero_stars_val = tk.StringVar()
        tk.Label(self.prog_hero_frame, textvariable=self.prog_hero_stars_val, bg=self.bg_color, fg=self.fg_color).pack(anchor="e", padx=5)
        self.pb_hero_stars = ttk.Progressbar(self.prog_hero_frame, orient="horizontal", length=100, mode="determinate", style="HeroStars.Horizontal.TProgressbar")
        self.pb_hero_stars.pack(fill="x", padx=5, pady=(0, 10))

        tk.Label(self.prog_hero_frame, text="Hero XP Levels (Max 140):", bg=self.bg_color, fg=self.fg_color).pack(anchor="w", padx=5)
        self.prog_hero_xp_val = tk.StringVar()
        tk.Label(self.prog_hero_frame, textvariable=self.prog_hero_xp_val, bg=self.bg_color, fg=self.fg_color).pack(anchor="e", padx=5)
        self.pb_hero_xp = ttk.Progressbar(self.prog_hero_frame, orient="horizontal", length=100, mode="determinate", style="HeroXP.Horizontal.TProgressbar")
        self.pb_hero_xp.pack(fill="x", padx=5, pady=(0, 10))

        tk.Label(self.prog_hero_frame, text="Total Hero XP Amount:", bg=self.bg_color, fg=self.fg_color).pack(anchor="w", padx=5)
        self.prog_hero_total_xp_val = tk.StringVar()
        tk.Label(self.prog_hero_frame, textvariable=self.prog_hero_total_xp_val, bg=self.bg_color, fg=self.fg_color).pack(anchor="e", padx=5)
        self.pb_hero_total_xp = ttk.Progressbar(self.prog_hero_frame, orient="horizontal", length=100, mode="determinate", style="HeroTotalXP.Horizontal.TProgressbar")
        self.pb_hero_total_xp.pack(fill="x", padx=5, pady=(0, 10))

        tk.Label(self.prog_hero_frame, text="Total Dust Spent:", bg=self.bg_color, fg=self.fg_color).pack(anchor="w", padx=5)
        self.prog_hero_dust_val = tk.StringVar()
        tk.Label(self.prog_hero_frame, textvariable=self.prog_hero_dust_val, bg=self.bg_color, fg=self.fg_color).pack(anchor="e", padx=5)
        self.pb_hero_dust = ttk.Progressbar(self.prog_hero_frame, orient="horizontal", length=100, mode="determinate", style="HeroDust.Horizontal.TProgressbar")
        self.pb_hero_dust.pack(fill="x", padx=5, pady=(0, 10))

        self.prog_pet_frame = tk.LabelFrame(self.tab_progress, text="Pets Progress", bg=self.bg_color, fg=self.fg_color)
        self.prog_pet_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(self.prog_pet_frame, text="Pet Stars (Max 12):", bg=self.bg_color, fg=self.fg_color).pack(anchor="w", padx=5)
        self.prog_pet_stars_val = tk.StringVar()
        tk.Label(self.prog_pet_frame, textvariable=self.prog_pet_stars_val, bg=self.bg_color, fg=self.fg_color).pack(anchor="e", padx=5)
        self.pb_pet_stars = ttk.Progressbar(self.prog_pet_frame, orient="horizontal", length=100, mode="determinate", style="PetStars.Horizontal.TProgressbar")
        self.pb_pet_stars.pack(fill="x", padx=5, pady=(0, 10))

        tk.Label(self.prog_pet_frame, text="Pet Bond Levels (Max 15):", bg=self.bg_color, fg=self.fg_color).pack(anchor="w", padx=5)
        self.prog_pet_bond_val = tk.StringVar()
        tk.Label(self.prog_pet_frame, textvariable=self.prog_pet_bond_val, bg=self.bg_color, fg=self.fg_color).pack(anchor="e", padx=5)
        self.pb_pet_bond = ttk.Progressbar(self.prog_pet_frame, orient="horizontal", length=100, mode="determinate", style="PetBond.Horizontal.TProgressbar")
        self.pb_pet_bond.pack(fill="x", padx=5, pady=(0, 10))

        tk.Label(self.prog_pet_frame, text="Total Feathers Spent:", bg=self.bg_color, fg=self.fg_color).pack(anchor="w", padx=5)
        self.prog_pet_feathers_val = tk.StringVar()
        tk.Label(self.prog_pet_frame, textvariable=self.prog_pet_feathers_val, bg=self.bg_color, fg=self.fg_color).pack(anchor="e", padx=5)
        self.pb_pet_feathers = ttk.Progressbar(self.prog_pet_frame, orient="horizontal", length=100, mode="determinate", style="PetFeathers.Horizontal.TProgressbar")
        self.pb_pet_feathers.pack(fill="x", padx=5, pady=(0, 10))

        tk.Label(self.prog_pet_frame, text="Total Time Spent:", bg=self.bg_color, fg=self.fg_color).pack(anchor="w", padx=5)
        self.prog_pet_time_val = tk.StringVar()
        tk.Label(self.prog_pet_frame, textvariable=self.prog_pet_time_val, bg=self.bg_color, fg=self.fg_color).pack(anchor="e", padx=5)
        self.pb_pet_time = ttk.Progressbar(self.prog_pet_frame, orient="horizontal", length=100, mode="determinate", style="PetTime.Horizontal.TProgressbar")
        self.pb_pet_time.pack(fill="x", padx=5, pady=(0, 10))

        self.prog_build_frame = tk.LabelFrame(self.tab_progress, text="Buildings Progress", bg=self.bg_color, fg=self.fg_color)
        self.prog_build_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(self.prog_build_frame, text=f"Total Building Levels (Max {self.building_max_level}):", bg=self.bg_color, fg=self.fg_color).pack(anchor="w", padx=5)
        self.prog_build_val = tk.StringVar()
        tk.Label(self.prog_build_frame, textvariable=self.prog_build_val, bg=self.bg_color, fg=self.fg_color).pack(anchor="e", padx=5)
        self.pb_build = ttk.Progressbar(self.prog_build_frame, orient="horizontal", length=100, mode="determinate", style="Build.Horizontal.TProgressbar")
        self.pb_build.pack(fill="x", padx=5, pady=(0, 10))

        self.prog_equip_frame = tk.LabelFrame(self.tab_progress, text="Equipment Progress", bg=self.bg_color, fg=self.fg_color)
        self.prog_equip_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(self.prog_equip_frame, text="Total Equipment Levels:", bg=self.bg_color, fg=self.fg_color).pack(anchor="w", padx=5)
        self.prog_equip_val = tk.StringVar()
        tk.Label(self.prog_equip_frame, textvariable=self.prog_equip_val, bg=self.bg_color, fg=self.fg_color).pack(anchor="e", padx=5)
        self.pb_equip = ttk.Progressbar(self.prog_equip_frame, orient="horizontal", length=100, mode="determinate", style="Equip.Horizontal.TProgressbar")
        self.pb_equip.pack(fill="x", padx=5, pady=(0, 10))

        # --- Stats Tab UI ---
        self.stats_vars = {} 
        
        stats_frame = tk.Frame(self.tab_stats, bg=self.bg_color)
        stats_frame.pack(fill="both", expand=True, padx=20, pady=20)
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)

        f_hero = tk.LabelFrame(stats_frame, text="Heroes Stats", bg=self.bg_color, fg=self.fg_color)
        f_hero.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        hero_labels = ["Obtained", "Total Stars", "Total XP Levels", "Total XP Amount", "Dust Used", "Dust Needed"]
        for i, l in enumerate(hero_labels):
            tk.Label(f_hero, text=l+":", bg=self.bg_color, fg=self.fg_color).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            v = tk.StringVar(value="-")
            self.stats_vars[f"hero_{i}"] = v
            tk.Label(f_hero, textvariable=v, bg=self.bg_color, fg=self.fg_color).grid(row=i, column=1, sticky="e", padx=5, pady=2)

        f_pet = tk.LabelFrame(stats_frame, text="Pets Stats", bg=self.bg_color, fg=self.fg_color)
        f_pet.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        pet_labels = ["Obtained", "Total Stars", "Total Bond", "Feathers Used", "Feathers Needed", "Time Spent"]
        for i, l in enumerate(pet_labels):
            tk.Label(f_pet, text=l+":", bg=self.bg_color, fg=self.fg_color).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            v = tk.StringVar(value="-")
            self.stats_vars[f"pet_{i}"] = v
            tk.Label(f_pet, textvariable=v, bg=self.bg_color, fg=self.fg_color).grid(row=i, column=1, sticky="e", padx=5, pady=2)

        f_build = tk.LabelFrame(stats_frame, text="Buildings Stats", bg=self.bg_color, fg=self.fg_color)
        f_build.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        build_labels = ["Total Levels", "Lumber Spent", "Lumber Needed", "Ore Spent", "Ore Needed", "Time Spent"]
        for i, l in enumerate(build_labels):
            tk.Label(f_build, text=l+":", bg=self.bg_color, fg=self.fg_color).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            v = tk.StringVar(value="-")
            self.stats_vars[f"build_{i}"] = v
            tk.Label(f_build, textvariable=v, bg=self.bg_color, fg=self.fg_color).grid(row=i, column=1, sticky="e", padx=5, pady=2)

        f_elixir = tk.LabelFrame(stats_frame, text="Elixir Stats", bg=self.bg_color, fg=self.fg_color)
        f_elixir.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        elixir_labels = ["Current Total", "Datapoints", "Avg Weekly Gain"]
        for i, l in enumerate(elixir_labels):
            tk.Label(f_elixir, text=l+":", bg=self.bg_color, fg=self.fg_color).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            v = tk.StringVar(value="-")
            self.stats_vars[f"elixir_{i}"] = v
            tk.Label(f_elixir, textvariable=v, bg=self.bg_color, fg=self.fg_color).grid(row=i, column=1, sticky="e", padx=5, pady=2)

        f_equip = tk.LabelFrame(stats_frame, text="Equipment Stats", bg=self.bg_color, fg=self.fg_color)
        f_equip.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        equip_labels = ["Total Levels", "Amber Spent", "Amber Needed"]
        for i, l in enumerate(equip_labels):
            tk.Label(f_equip, text=l+":", bg=self.bg_color, fg=self.fg_color).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            v = tk.StringVar(value="-")
            self.stats_vars[f"equip_{i}"] = v
            tk.Label(f_equip, textvariable=v, bg=self.bg_color, fg=self.fg_color).grid(row=i, column=1, sticky="e", padx=5, pady=2)

        # --- Buildings Tab UI ---
        buildings_list = ["Castle", "Tavern", "School", "Storage", "Training Grounds", 
                          "Saw Mill 1", "Saw Mill 2", "Ore Mine 1", "Ore Mine 2"]
        
        self.build_settings_frame = tk.LabelFrame(self.tab_buildings, text="Construction Multipliers (%)", bg=self.bg_color, fg=self.fg_color)
        self.build_settings_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(self.build_settings_frame, text="Speed:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5)
        self.entry_const_speed = tk.Entry(self.build_settings_frame, textvariable=self.const_speed_var, width=5, bg=self.entry_bg, fg=self.fg_color, insertbackground="white")
        self.entry_const_speed.pack(side="left", padx=5)
        
        tk.Label(self.build_settings_frame, text="Lumber Cost:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5)
        self.entry_const_lumber = tk.Entry(self.build_settings_frame, textvariable=self.const_lumber_var, width=5, bg=self.entry_bg, fg=self.fg_color, insertbackground="white")
        self.entry_const_lumber.pack(side="left", padx=5)
        
        tk.Label(self.build_settings_frame, text="Ore Cost:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5)
        self.entry_const_ore = tk.Entry(self.build_settings_frame, textvariable=self.const_ore_var, width=5, bg=self.entry_bg, fg=self.fg_color, insertbackground="white")
        self.entry_const_ore.pack(side="left", padx=5)
        
        self.entry_const_speed.bind('<FocusOut>', self.save_building_settings)
        self.entry_const_speed.bind('<Return>', self.save_building_settings)
        self.entry_const_lumber.bind('<FocusOut>', self.save_building_settings)
        self.entry_const_lumber.bind('<Return>', self.save_building_settings)
        self.entry_const_ore.bind('<FocusOut>', self.save_building_settings)
        self.entry_const_ore.bind('<Return>', self.save_building_settings)

        self.buildings_notebook = ttk.Notebook(self.tab_buildings)
        self.buildings_notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tab_build_levels = tk.Frame(self.buildings_notebook, bg=self.bg_color)
        self.tab_build_targets = tk.Frame(self.buildings_notebook, bg=self.bg_color)
        
        self.buildings_notebook.add(self.tab_build_levels, text="Levels")
        self.buildings_notebook.add(self.tab_build_targets, text="Targets")

        for c in range(2):
            self.tab_build_levels.columnconfigure(c, weight=1, uniform="col")
            self.tab_build_targets.columnconfigure(c, weight=1, uniform="col")
        
        self.spent_frame = tk.LabelFrame(self.tab_build_levels, text="Total Resources Spent", bg=self.bg_color, fg=self.fg_color)
        self.spent_frame.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        self.lbl_spent_time = tk.Label(self.spent_frame, text="Time: 0s", bg=self.bg_color, fg=self.fg_color, font=("Arial", 10, "bold"))
        self.lbl_spent_time.pack(side="left", expand=True, pady=5)
        
        self.lbl_spent_lumber = tk.Label(self.spent_frame, text="Lumber: 0", bg=self.bg_color, fg=self.accent_yellow, font=("Arial", 10, "bold"))
        self.lbl_spent_lumber.pack(side="left", expand=True, pady=5)
        
        self.lbl_spent_ore = tk.Label(self.spent_frame, text="Ore: 0", bg=self.bg_color, fg=self.accent_green, font=("Arial", 10, "bold"))
        self.lbl_spent_ore.pack(side="left", expand=True, pady=5)

        self.target_cost_frame = tk.LabelFrame(self.tab_build_targets, text="Total Target Cost", bg=self.bg_color, fg=self.fg_color)
        self.target_cost_frame.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        self.lbl_target_time = tk.Label(self.target_cost_frame, text="Time: 0s", bg=self.bg_color, fg=self.fg_color, font=("Arial", 10, "bold"))
        self.lbl_target_time.pack(side="left", expand=True, pady=5)
        
        self.lbl_target_lumber = tk.Label(self.target_cost_frame, text="Lumber: 0", bg=self.bg_color, fg=self.accent_yellow, font=("Arial", 10, "bold"))
        self.lbl_target_lumber.pack(side="left", expand=True, pady=5)
        
        self.lbl_target_ore = tk.Label(self.target_cost_frame, text="Ore: 0", bg=self.bg_color, fg=self.accent_green, font=("Arial", 10, "bold"))
        self.lbl_target_ore.pack(side="left", expand=True, pady=5)

        self.castle_costs = [
            (4, 200, 500), (300, 4000, 2000), (7200, 10000, 5000), (86400, 24000, 12000),
            (172800, 57600, 28800), (260000, 105000, 52500), (300000, 160000, 80000),
            (370000, 225000, 112500), (440000, 300000, 150000), (520000, 437500, 218750),
            (656000, 630000, 315000), (820000, 880000, 440000), (1020000, 1200000, 600000),
            (1270000, 1600000, 800000), (1550000, 2200000, 1100000)
        ]
        
        self.other_building_costs = [
            (2, 100, 250), (150, 2000, 1000), (3600, 5000, 2500), (43200, 12000, 6000),
            (86400, 28800, 14400), (130000, 52500, 26250), (150000, 80000, 40000),
            (185000, 112500, 56250), (220000, 150000, 75000), (260000, 218750, 109375),
            (328000, 315000, 157500), (410000, 440000, 220000), (510000, 600000, 300000),
            (635000, 800000, 400000), (775000, 1100000, 550000)
        ]
        
        self.ore_mine_costs = [(t, l, 0) for t, l, o in self.other_building_costs]

        building_data = {}
        with self.conn:
            c = self.conn.cursor()
            c.execute("SELECT name, level FROM buildings")
            for row in c.fetchall():
                building_data[row[0]] = row[1]

        self.building_entries = {}
        self.building_target_entries = {}
        self.building_stats_labels = {}

        for i, text in enumerate(buildings_list):
            box = tk.Frame(self.tab_build_levels, bg=self.entry_bg, highlightbackground=self.fg_color, highlightthickness=1)
            
            if i == 0: 
                box.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
            else:
                box.grid(row=(i + 1) // 2, column=(i + 1) % 2, sticky="nsew", padx=5, pady=5)
            
            content = tk.Frame(box, bg=self.entry_bg)
            content.pack(expand=True)

            left_frame = tk.Frame(content, bg=self.entry_bg)
            left_frame.pack(side="left", padx=10)

            tk.Label(left_frame, text=text, font=("Arial", 14, "bold"), bg=self.entry_bg, fg=self.fg_color).pack(pady=(0, 5))
            
            lvl_frame = tk.Frame(left_frame, bg=self.entry_bg)
            lvl_frame.pack()
            tk.Label(lvl_frame, text="Level:", font=("Arial", 10), bg=self.entry_bg, fg=self.fg_color).pack(side="left", padx=5)
            
            entry_lvl = tk.Entry(lvl_frame, width=10, bg=self.bg_color, fg=self.fg_color, insertbackground="white", relief="flat", justify="center")
            entry_lvl.pack(side="left", padx=5)
            self.building_entries[text] = entry_lvl
            
            current_val = building_data.get(text, "-")
            if current_val != "-":
                entry_lvl.insert(0, current_val)
            
            entry_lvl.bind('<Return>', lambda event, n=text, e=entry_lvl: self.save_building_level(n, e))
            entry_lvl.bind('<FocusOut>', lambda event, n=text, e=entry_lvl: self.save_building_level(n, e))

            stats_frame = tk.Frame(content, bg=self.entry_bg)
            stats_frame.pack(side="left", padx=10, pady=5)
            
            self.building_stats_labels[text] = {}
            
            tk.Label(stats_frame, text="Next Level", font=("Arial", 8, "bold"), bg=self.entry_bg, fg=self.fg_color).grid(row=0, column=0, columnspan=2)
            tk.Label(stats_frame, text="Remaining", font=("Arial", 8, "bold"), bg=self.entry_bg, fg=self.fg_color).grid(row=0, column=2, columnspan=2)

            labels = ["Time", "Lumber", "Ore"]
            keys = ["time", "lumber", "ore"]

            for r, (lbl, k) in enumerate(zip(labels, keys)):
                if k == "ore" and text in ["Ore Mine 1", "Ore Mine 2"]:
                    continue

                tk.Label(stats_frame, text=lbl+":", font=("Arial", 8), bg=self.entry_bg, fg=self.fg_color).grid(row=r+1, column=0, sticky="e")
                l_next = tk.Label(stats_frame, text="-", font=("Arial", 8), bg=self.entry_bg, fg=self.accent_yellow)
                l_next.grid(row=r+1, column=1, sticky="w", padx=(2, 10))
                self.building_stats_labels[text][f"{k}_next"] = l_next
                
                tk.Label(stats_frame, text=lbl+":", font=("Arial", 8), bg=self.entry_bg, fg=self.fg_color).grid(row=r+1, column=2, sticky="e")
                l_total = tk.Label(stats_frame, text="-", font=("Arial", 8), bg=self.entry_bg, fg=self.accent_green)
                l_total.grid(row=r+1, column=3, sticky="w", padx=2)
                self.building_stats_labels[text][f"{k}_total"] = l_total
            
            box_tgt = tk.Frame(self.tab_build_targets, bg=self.entry_bg, highlightbackground=self.fg_color, highlightthickness=1)
            if i == 0:
                box_tgt.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
            else:
                box_tgt.grid(row=(i + 1) // 2, column=(i + 1) % 2, sticky="nsew", padx=5, pady=5)
            
            content_tgt = tk.Frame(box_tgt, bg=self.entry_bg)
            content_tgt.pack(expand=True)

            left_frame_tgt = tk.Frame(content_tgt, bg=self.entry_bg)
            left_frame_tgt.pack(side="left", padx=10)

            tk.Label(left_frame_tgt, text=text, font=("Arial", 14, "bold"), bg=self.entry_bg, fg=self.fg_color).pack(pady=(0, 5))
            
            target_frame = tk.Frame(left_frame_tgt, bg=self.entry_bg)
            target_frame.pack()
            tk.Label(target_frame, text="Target:", font=("Arial", 10), bg=self.entry_bg, fg=self.fg_color).pack(side="left", padx=5)
            
            entry_target = tk.Entry(target_frame, width=10, bg=self.bg_color, fg=self.fg_color, insertbackground="white", relief="flat", justify="center")
            entry_target.pack(side="left", padx=5)
            self.building_target_entries[text] = entry_target
            
            entry_target.bind('<Return>', lambda event, n=text: self.update_building_stats(n))
            entry_target.bind('<FocusOut>', lambda event, n=text: self.update_building_stats(n))

            stats_frame_tgt = tk.Frame(content_tgt, bg=self.entry_bg)
            stats_frame_tgt.pack(side="left", padx=10, pady=5)

            tk.Label(stats_frame_tgt, text="Target Cost", font=("Arial", 8, "bold"), bg=self.entry_bg, fg=self.fg_color).grid(row=0, column=0, columnspan=2)

            for r, (lbl, k) in enumerate(zip(labels, keys)):
                if k == "ore" and text in ["Ore Mine 1", "Ore Mine 2"]:
                    continue
                
                tk.Label(stats_frame_tgt, text=lbl+":", font=("Arial", 8), bg=self.entry_bg, fg=self.fg_color).grid(row=r+1, column=0, sticky="e")
                l_target = tk.Label(stats_frame_tgt, text="-", font=("Arial", 8), bg=self.entry_bg, fg="#b0bec5")
                l_target.grid(row=r+1, column=1, sticky="w", padx=2)
                self.building_stats_labels[text][f"{k}_target"] = l_target
            
            self.update_building_stats(text) 

        self.btn_max_all = tk.Button(self.tab_build_levels, text="Max All", command=self.max_all_buildings, bg=self.accent_yellow, fg="black", relief="flat", padx=10)
        self.btn_max_all.grid(row=5, column=0, columnspan=2, pady=10)

        self.target_set_all_frame = tk.Frame(self.tab_build_targets, bg=self.bg_color)
        self.target_set_all_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        tk.Label(self.target_set_all_frame, text="Set all targets to:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5)
        self.entry_target_all = tk.Entry(self.target_set_all_frame, width=5, bg=self.entry_bg, fg=self.fg_color, insertbackground="white", relief="flat", justify="center")
        self.entry_target_all.pack(side="left", padx=5)
        self.entry_target_all.bind('<Return>', self.set_all_targets)
        tk.Button(self.target_set_all_frame, text="Set", command=self.set_all_targets, bg=self.accent_yellow, fg="black", relief="flat", padx=10).pack(side="left", padx=5)

        self.build_status_label = tk.Label(self.tab_buildings, text="", font=("Arial", 10), bg=self.bg_color, fg=self.fg_color)
        self.build_status_label.pack(side="bottom", pady=5)

        self.update_total_spent_summary()
        self.update_total_target_summary()

        # --- Elixir Tab UI ---
        self.elixir_notebook = ttk.Notebook(self.tab_elixir)
        self.elixir_notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_elixir_datapoints = tk.Frame(self.elixir_notebook, bg=self.bg_color)
        self.tab_elixir_expected = tk.Frame(self.elixir_notebook, bg=self.bg_color)
        self.tab_elixir_graph = tk.Frame(self.elixir_notebook, bg=self.bg_color)
        
        self.elixir_notebook.add(self.tab_elixir_expected, text="Expected")
        self.elixir_notebook.add(self.tab_elixir_datapoints, text="Datapoints")
        self.elixir_notebook.add(self.tab_elixir_graph, text="Graph")

        if MATPLOTLIB_AVAILABLE:
            self.graph_controls = tk.Frame(self.tab_elixir_graph, bg=self.bg_color)
            self.graph_controls.pack(side="top", fill="x", padx=10, pady=5)
            
            tk.Checkbutton(self.graph_controls, text="Show Weekly Gain", variable=self.show_weekly_gain_var, 
                           command=self.update_elixir_graph, bg=self.bg_color, fg=self.fg_color, 
                           selectcolor=self.entry_bg, activebackground=self.bg_color, 
                           activeforeground=self.fg_color).pack(side="left", padx=5)

            tk.Checkbutton(self.graph_controls, text="Show Projection (6m)", variable=self.show_future_projection_var, 
                           command=self.update_elixir_graph, bg=self.bg_color, fg=self.fg_color, 
                           selectcolor=self.entry_bg, activebackground=self.bg_color, 
                           activeforeground=self.fg_color).pack(side="left", padx=5)

            tk.Label(self.graph_controls, text="Time Filter:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=(10, 5))
            self.graph_filter_var = tk.StringVar(value="All Time")
            self.cmb_graph_filter = ttk.Combobox(self.graph_controls, textvariable=self.graph_filter_var, 
                                                 values=["All Time", "2025", "2026", "Past 3 Months", "Past 6 Months"], 
                                                 state="readonly", width=15)
            self.cmb_graph_filter.pack(side="left", padx=5)
            self.cmb_graph_filter.bind("<<ComboboxSelected>>", lambda e: self.update_elixir_graph())
            
            tk.Button(self.graph_controls, text="Reset", command=self.reset_graph_filter, bg=self.btn_bg, fg="white", relief="flat").pack(side="left", padx=2)
            tk.Button(self.graph_controls, text="Save Image", command=self.save_graph_image, bg=self.accent_green, fg="white", relief="flat").pack(side="left", padx=5)

            self.lbl_avg_gain = tk.Label(self.graph_controls, text="Avg Weekly Gain: -", bg=self.bg_color, fg=self.accent_yellow, font=("Arial", 9, "bold"))
            self.lbl_avg_gain.pack(side="left", padx=10)

            self.lbl_dist_stats = tk.Label(self.graph_controls, text="", bg=self.bg_color, fg=self.fg_color, font=("Arial", 9, "bold"))
            self.lbl_dist_stats.pack(side="left", padx=10)

            self.charts_frame = tk.Frame(self.tab_elixir_graph, bg=self.bg_color)
            self.charts_frame.pack(fill="both", expand=True)

            self.fig, (self.ax, self.ax_dist) = plt.subplots(1, 2, figsize=(8, 4), dpi=100, gridspec_kw={'width_ratios': [3, 1]})
            self.ax2 = None 
            self.fig.patch.set_facecolor(self.bg_color)
            self.ax.set_facecolor(self.bg_color)
            self.ax.tick_params(axis='x', colors=self.fg_color)
            self.ax.tick_params(axis='y', colors=self.fg_color)
            self.ax.spines['bottom'].set_color(self.fg_color)
            self.ax.spines['top'].set_color(self.fg_color)
            self.ax.spines['left'].set_color(self.fg_color)
            self.ax.spines['right'].set_color(self.fg_color)
            self.ax.set_title("Total Elixir Over Time", color=self.fg_color)
            self.ax.set_xlabel("Date", color=self.fg_color)
            self.ax.set_ylabel("Total Elixir", color=self.fg_color)
            
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.charts_frame)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            
            self.canvas.mpl_connect("motion_notify_event", self.on_graph_hover)
            self.canvas.mpl_connect("motion_notify_event", self.on_dist_hover)
            self.sc = None 
            self.sc2 = None
            self.annot = None 
            self.annot2 = None

            self.ax_dist.set_facecolor(self.bg_color)
            self.annot_dist = None
            self.bp_dict = None 
        else:
            tk.Label(self.tab_elixir_graph, text="Matplotlib not found.\nPlease install it using: pip install matplotlib", bg=self.bg_color, fg=self.fg_color).pack(expand=True)

        self.calc_frame = tk.LabelFrame(self.tab_elixir_expected, text="Time Calculator", padx=10, pady=10, bg=self.bg_color, fg=self.fg_color)
        self.calc_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(self.calc_frame, text="Current Elixir:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_calc_current = tk.Entry(self.calc_frame, bg=self.entry_bg, fg=self.fg_color, insertbackground="white")
        self.entry_calc_current.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.calc_frame, text="Target Elixir:", bg=self.bg_color, fg=self.fg_color).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_calc_target = tk.Entry(self.calc_frame, bg=self.entry_bg, fg=self.fg_color, insertbackground="white")
        self.entry_calc_target.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.calc_frame, text="Weekly Growth (%):", bg=self.bg_color, fg=self.fg_color).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_calc_percent = tk.Entry(self.calc_frame, bg=self.entry_bg, fg=self.fg_color, insertbackground="white")
        self.entry_calc_percent.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(self.calc_frame, text="Calculate", command=self.calculate_expected_elixir, bg=self.accent_green, fg="white", relief="flat").grid(row=3, column=0, columnspan=2, pady=10)

        self.lbl_calc_result = tk.Label(self.calc_frame, text="", bg=self.bg_color, fg=self.fg_color, font=("Arial", 10, "bold"))
        self.lbl_calc_result.grid(row=4, column=0, columnspan=2, pady=5)

        self.elixir_input_frame = tk.LabelFrame(self.tab_elixir_datapoints, text="Data Entry", padx=10, pady=10, bg=self.bg_color, fg=self.fg_color)
        self.elixir_input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(self.elixir_input_frame, text="Date (DD.MM.YYYY):", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, padx=5)
        self.entry_elixir_date = tk.Entry(self.elixir_input_frame, bg=self.entry_bg, fg=self.fg_color, insertbackground="white")
        self.entry_elixir_date.grid(row=0, column=1, padx=5)
        self.entry_elixir_date.insert(0, datetime.now().strftime("%d.%m.%Y"))

        tk.Label(self.elixir_input_frame, text="Total Elixir:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=2, padx=5)
        self.entry_elixir_val = tk.Entry(self.elixir_input_frame, bg=self.entry_bg, fg=self.fg_color, insertbackground="white")
        self.entry_elixir_val.grid(row=0, column=3, padx=5)
        self.entry_elixir_val.bind('<Return>', self.add_elixir_record)

        tk.Button(self.elixir_input_frame, text="Add", command=self.add_elixir_record, bg=self.accent_green, fg="white", relief="flat", padx=10).grid(row=0, column=4, padx=10)
        tk.Button(self.elixir_input_frame, text="Delete Selected", command=self.ask_delete_elixir, bg=self.accent_red, fg="white", relief="flat", padx=10).grid(row=0, column=5, padx=10)
        tk.Button(self.elixir_input_frame, text="Import CSV", command=self.import_elixir_csv, bg=self.accent_yellow, fg="black", relief="flat", padx=10).grid(row=0, column=6, padx=10)

        self.elixir_status_label = tk.Label(self.tab_elixir_datapoints, text="", bg=self.bg_color, fg=self.fg_color)
        self.elixir_status_label.pack(pady=5)

        elixir_cols = ("Date", "Total Elixir", "Bonus", "Daily Bonus", "%")
        self.tree_elixir = ttk.Treeview(self.tab_elixir_datapoints, columns=elixir_cols, show="headings")
        for col in elixir_cols:
            self.tree_elixir.heading(col, text=col, command=lambda c=col: self.sort_elixir_column(c, False))
            self.tree_elixir.column(col, width=150, anchor="center")
        self.tree_elixir.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Pulls Tab UI ---
        self.pulls_status_label = tk.Label(self.tab_pulls, text="", font=("Arial", 10), bg=self.bg_color, fg=self.fg_color)
        self.pulls_notebook = ttk.Notebook(self.tab_pulls)
        self.pulls_notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_pulls_main = tk.Frame(self.pulls_notebook, bg=self.bg_color)
        self.tab_pulls_luck = tk.Frame(self.pulls_notebook, bg=self.bg_color)
        self.tab_pulls_dp_scrolls = tk.Frame(self.pulls_notebook, bg=self.bg_color)
        self.tab_pulls_dp_eggs = tk.Frame(self.pulls_notebook, bg=self.bg_color)

        self.pulls_notebook.add(self.tab_pulls_main, text="Main")
        self.pulls_notebook.add(self.tab_pulls_luck, text="Luck")
        self.pulls_notebook.add(self.tab_pulls_dp_scrolls, text="Datapoints Scrolls")
        self.pulls_notebook.add(self.tab_pulls_dp_eggs, text="Datapoints Eggs")
        self.pulls_notebook.bind("<<NotebookTabChanged>>", self.on_pulls_tab_change)

        self.luck_left = tk.Frame(self.tab_pulls_luck, bg=self.bg_color)
        self.luck_left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.luck_right = tk.Frame(self.tab_pulls_luck, bg=self.bg_color)
        self.luck_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(self.luck_left, text="Scrolls Luck", font=("Arial", 16, "bold"), bg=self.bg_color, fg=self.fg_color).pack(pady=5)
        self.lbl_avg_scroll_stars = tk.Label(self.luck_left, text="Average Stars: -", font=("Arial", 12), bg=self.bg_color, fg=self.fg_color)
        self.lbl_avg_scroll_stars.pack()
        self.lbl_total_scrolls = tk.Label(self.luck_left, text="Total Pulled: -", font=("Arial", 12), bg=self.bg_color, fg=self.fg_color, cursor="hand2")
        self.lbl_total_scrolls.pack()
        self.lbl_total_scrolls.bind("<Button-1>", self.show_scroll_breakdown) 
        self.lbl_weighted_scroll_luck = tk.Label(self.luck_left, text="Weighted Luck: -", font=("Arial", 12), bg=self.bg_color, fg=self.fg_color)
        self.lbl_weighted_scroll_luck.pack()
        
        tk.Label(self.luck_right, text="Eggs Luck", font=("Arial", 16, "bold"), bg=self.bg_color, fg=self.fg_color).pack(pady=5)
        self.lbl_avg_egg_stars = tk.Label(self.luck_right, text="Average Stars: -", font=("Arial", 12), bg=self.bg_color, fg=self.fg_color)
        self.lbl_avg_egg_stars.pack()
        self.lbl_total_eggs = tk.Label(self.luck_right, text="Total Pulled: -", font=("Arial", 12), bg=self.bg_color, fg=self.fg_color, cursor="hand2")
        self.lbl_total_eggs.pack()
        self.lbl_total_eggs.bind("<Button-1>", self.show_egg_breakdown) 
        self.lbl_weighted_egg_luck = tk.Label(self.luck_right, text="Weighted Luck: -", font=("Arial", 12), bg=self.bg_color, fg=self.fg_color)
        self.lbl_weighted_egg_luck.pack()
        
        self.scroll_dist_map = {}
        self.egg_dist_map = {}
        
        if MATPLOTLIB_AVAILABLE:
            self.fig_scroll, self.ax_scroll = plt.subplots(figsize=(4, 3), dpi=100)
            self.fig_scroll.patch.set_facecolor(self.bg_color)
            self.canvas_scroll = FigureCanvasTkAgg(self.fig_scroll, master=self.luck_left)
            self.canvas_scroll.get_tk_widget().pack(fill="both", expand=True, pady=10)
            self.canvas_scroll.mpl_connect("motion_notify_event", self.on_scroll_hover)

            self.fig_egg, self.ax_egg = plt.subplots(figsize=(4, 3), dpi=100)
            self.fig_egg.patch.set_facecolor(self.bg_color)
            self.canvas_egg = FigureCanvasTkAgg(self.fig_egg, master=self.luck_right)
            self.canvas_egg.get_tk_widget().pack(fill="both", expand=True, pady=10)
            self.canvas_egg.mpl_connect("motion_notify_event", self.on_egg_hover)

            self.sc_scroll = None
            self.annot_scroll = None
            self.sc_egg = None
            self.annot_egg = None
            self.user_scroll_probs = []
            self.user_egg_probs = []

        self.pulls_status_label = tk.Label(self.tab_pulls_main, text="", font=("Arial", 10), bg=self.bg_color, fg=self.fg_color)
        self.pulls_status_label.pack(side="bottom", pady=5)

        self.pulls_left = tk.Frame(self.tab_pulls_main, bg=self.bg_color)
        self.pulls_left.pack(side="left", fill="both", expand=True)

        self.pulls_right = tk.Frame(self.tab_pulls_main, bg=self.bg_color)
        self.pulls_right.pack(side="right", fill="both", expand=True)

        tk.Label(self.pulls_left, text="Scrolls", font=("Arial", 24, "bold"), bg=self.bg_color, fg=self.fg_color).pack(pady=20)
        tk.Label(self.pulls_right, text="Eggs", font=("Arial", 24, "bold"), bg=self.bg_color, fg=self.fg_color).pack(pady=20)

        self.scrolls_input_frame = tk.Frame(self.pulls_left, bg=self.bg_color)
        self.scrolls_input_frame.pack(pady=10)

        tk.Label(self.scrolls_input_frame, text="Name:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_scroll_name = tk.Entry(self.scrolls_input_frame, width=20, bg=self.entry_bg, fg=self.fg_color, insertbackground="white", relief="flat")
        self.entry_scroll_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.scrolls_input_frame, text="Stars:", bg=self.bg_color, fg=self.fg_color).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_scroll_stars = tk.Entry(self.scrolls_input_frame, width=20, bg=self.entry_bg, fg=self.fg_color, insertbackground="white", relief="flat")
        self.entry_scroll_stars.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.scrolls_input_frame, text="Pull", command=self.process_scroll_pull, bg=self.accent_green, fg="white", relief="flat", width=15).grid(row=2, column=0, columnspan=2, pady=10)

        self.entry_scroll_name.bind('<Return>', self.process_scroll_pull)
        self.entry_scroll_stars.bind('<Return>', self.process_scroll_pull)

        self.eggs_input_frame = tk.Frame(self.pulls_right, bg=self.bg_color)
        self.eggs_input_frame.pack(pady=10)

        tk.Label(self.eggs_input_frame, text="Name:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_egg_name = tk.Entry(self.eggs_input_frame, width=20, bg=self.entry_bg, fg=self.fg_color, insertbackground="white", relief="flat")
        self.entry_egg_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.eggs_input_frame, text="Stars:", bg=self.bg_color, fg=self.fg_color).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_egg_stars = tk.Entry(self.eggs_input_frame, width=20, bg=self.entry_bg, fg=self.fg_color, insertbackground="white", relief="flat")
        self.entry_egg_stars.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.eggs_input_frame, text="Pull", command=self.process_egg_pull, bg=self.accent_green, fg="white", relief="flat", width=15).grid(row=2, column=0, columnspan=2, pady=10)

        self.entry_egg_name.bind('<Return>', self.process_egg_pull)
        self.entry_egg_stars.bind('<Return>', self.process_egg_pull)

        self.scrolls_hist_frame = tk.Frame(self.tab_pulls_dp_scrolls, bg=self.bg_color)
        self.scrolls_hist_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(self.scrolls_hist_frame, text="Date:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5)
        self.entry_scroll_hist_date = tk.Entry(self.scrolls_hist_frame, width=20, bg=self.entry_bg, fg=self.fg_color, insertbackground="white")
        self.entry_scroll_hist_date.pack(side="left", padx=5)
        
        tk.Label(self.scrolls_hist_frame, text="Name:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5)
        self.entry_scroll_hist_name = tk.Entry(self.scrolls_hist_frame, width=15, bg=self.entry_bg, fg=self.fg_color, insertbackground="white")
        self.entry_scroll_hist_name.pack(side="left", padx=5)
        
        tk.Label(self.scrolls_hist_frame, text="Stars:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5)
        self.entry_scroll_hist_stars = tk.Entry(self.scrolls_hist_frame, width=5, bg=self.entry_bg, fg=self.fg_color, insertbackground="white")
        self.entry_scroll_hist_stars.pack(side="left", padx=5)
        
        tk.Button(self.scrolls_hist_frame, text="Update", command=self.update_scroll_record, bg=self.accent_yellow, fg="black", relief="flat").pack(side="left", padx=5)
        tk.Button(self.scrolls_hist_frame, text="Delete", command=self.delete_scroll_record, bg=self.accent_red, fg="white", relief="flat").pack(side="left", padx=5)
        tk.Button(self.scrolls_hist_frame, text="Import CSV", command=self.import_scrolls_csv, bg=self.accent_yellow, fg="black", relief="flat").pack(side="left", padx=5)

        self.scrolls_tree_frame = tk.Frame(self.tab_pulls_dp_scrolls, bg=self.bg_color)
        self.scrolls_tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.scrollbar_scrolls = tk.Scrollbar(self.scrolls_tree_frame)
        self.scrollbar_scrolls.pack(side="right", fill="y")

        cols_scrolls = ("Date", "Name", "Stars")
        self.tree_scrolls = ttk.Treeview(self.scrolls_tree_frame, columns=cols_scrolls, show="headings", yscrollcommand=self.scrollbar_scrolls.set)
        for col in cols_scrolls:
            self.tree_scrolls.heading(col, text=col, command=lambda c=col: self.sort_scroll_column(c, False))
            self.tree_scrolls.column(col, width=150, anchor="center")
        self.tree_scrolls.pack(fill="both", expand=True)
        self.scrollbar_scrolls.config(command=self.tree_scrolls.yview)
        self.tree_scrolls.bind("<ButtonRelease-1>", self.select_scroll_item)
        
        self.eggs_hist_frame = tk.Frame(self.tab_pulls_dp_eggs, bg=self.bg_color)
        self.eggs_hist_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(self.eggs_hist_frame, text="Date:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5)
        self.entry_egg_hist_date = tk.Entry(self.eggs_hist_frame, width=20, bg=self.entry_bg, fg=self.fg_color, insertbackground="white")
        self.entry_egg_hist_date.pack(side="left", padx=5)
        
        tk.Label(self.eggs_hist_frame, text="Name:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5)
        self.entry_egg_hist_name = tk.Entry(self.eggs_hist_frame, width=15, bg=self.entry_bg, fg=self.fg_color, insertbackground="white")
        self.entry_egg_hist_name.pack(side="left", padx=5)
        
        tk.Label(self.eggs_hist_frame, text="Stars:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5)
        self.entry_egg_hist_stars = tk.Entry(self.eggs_hist_frame, width=5, bg=self.entry_bg, fg=self.fg_color, insertbackground="white")
        self.entry_egg_hist_stars.pack(side="left", padx=5)
        
        tk.Button(self.eggs_hist_frame, text="Update", command=self.update_egg_record, bg=self.accent_yellow, fg="black", relief="flat").pack(side="left", padx=5)
        tk.Button(self.eggs_hist_frame, text="Delete", command=self.delete_egg_record, bg=self.accent_red, fg="white", relief="flat").pack(side="left", padx=5)
        tk.Button(self.eggs_hist_frame, text="Import CSV", command=self.import_eggs_csv, bg=self.accent_yellow, fg="black", relief="flat").pack(side="left", padx=5)

        self.eggs_tree_frame = tk.Frame(self.tab_pulls_dp_eggs, bg=self.bg_color)
        self.eggs_tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.scrollbar_eggs = tk.Scrollbar(self.eggs_tree_frame)
        self.scrollbar_eggs.pack(side="right", fill="y")

        cols_eggs = ("Date", "Name", "Stars")
        self.tree_eggs = ttk.Treeview(self.eggs_tree_frame, columns=cols_eggs, show="headings", yscrollcommand=self.scrollbar_eggs.set)
        for col in cols_eggs:
            self.tree_eggs.heading(col, text=col, command=lambda c=col: self.sort_egg_column(c, False))
            self.tree_eggs.column(col, width=150, anchor="center")
        self.tree_eggs.pack(fill="both", expand=True)
        self.scrollbar_eggs.config(command=self.tree_eggs.yview)
        self.tree_eggs.bind("<ButtonRelease-1>", self.select_egg_item)

        self.load_pulls_history() 

        # --- Equipment Tab UI ---
        self.equip_table_frame = tk.Frame(self.tab_equipment, bg=self.bg_color)
        self.equip_table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for i in range(6):
            self.equip_table_frame.columnconfigure(i, weight=1)

        self.load_equipment_data() 
        
        self.btn_equip_max = tk.Button(self.tab_equipment, text="Max All", command=self.max_all_equipment, bg=self.accent_yellow, fg="black", relief="flat", padx=10)
        self.btn_equip_max.pack(pady=10)

        # --- Heroes Tab UI ---
        self.hero_notebook = ttk.Notebook(self.tab_hero)
        self.hero_notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_hero_datapoints = tk.Frame(self.hero_notebook, bg=self.bg_color)
        self.tab_hero_team_calc = tk.Frame(self.hero_notebook, bg=self.bg_color)
        self.tab_hero_fashion = tk.Frame(self.hero_notebook, bg=self.bg_color)

        self.hero_notebook.add(self.tab_hero_datapoints, text="Datapoints")
        self.hero_notebook.add(self.tab_hero_team_calc, text="Team Calc")
        self.hero_notebook.add(self.tab_hero_fashion, text="Fashion")

        self.setup_team_calculator() 
        self.setup_fashion_ui()

        self.input_frame = tk.LabelFrame(self.tab_hero_datapoints, text="Data Entry", padx=10, pady=10, bg=self.bg_color, fg=self.fg_color)
        self.input_frame.pack(fill="x", padx=10, pady=5)

        self.current_id = None 

        tk.Label(self.input_frame, text="Name:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, sticky="w", padx=5)
        self.entry_name = tk.Entry(self.input_frame, width=25, bg=self.entry_bg, fg=self.fg_color, insertbackground="white", relief="flat")
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.input_frame, text="Stars:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=2, sticky="w", padx=5)
        self.entry_sterne = tk.Entry(self.input_frame, width=10, bg=self.entry_bg, fg=self.fg_color, insertbackground="white", relief="flat")
        self.entry_sterne.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(self.input_frame, text="XP Level:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=4, sticky="w", padx=5)
        self.entry_xp = tk.Entry(self.input_frame, width=15, bg=self.entry_bg, fg=self.fg_color, insertbackground="white", relief="flat")
        self.entry_xp.grid(row=0, column=5, padx=5, pady=5)

        self.entry_name.bind('<Return>', self.add_record)
        self.entry_sterne.bind('<Return>', self.add_record)
        self.entry_xp.bind('<Return>', self.add_record)

        self.btn_frame = tk.Frame(self.tab_hero_datapoints, bg=self.bg_color)
        self.btn_frame.pack(pady=10)

        self.normal_btns = tk.Frame(self.btn_frame, bg=self.bg_color)
        self.normal_btns.pack()

        self.btn_add = tk.Button(self.normal_btns, text="Add", command=self.add_record, bg=self.accent_green, fg="white", relief="flat", padx=10)
        self.btn_add.grid(row=0, column=0, padx=10)

        self.btn_update = tk.Button(self.normal_btns, text="Update", command=self.update_record, bg=self.accent_yellow, fg="black", relief="flat", padx=10)
        self.btn_update.grid(row=0, column=1, padx=10)

        self.btn_delete = tk.Button(self.normal_btns, text="Delete", command=self.ask_delete, bg=self.accent_red, fg="white", relief="flat", padx=10)
        self.btn_delete.grid(row=0, column=2, padx=10)

        self.btn_clear = tk.Button(self.normal_btns, text="Clear Fields", command=self.clear_hero_fields_action, bg=self.btn_bg, fg="white", relief="flat", padx=10)
        self.btn_clear.grid(row=0, column=3, padx=10)

        self.confirm_btns = tk.Frame(self.btn_frame, bg=self.bg_color)
        tk.Label(self.confirm_btns, text="Really delete?", fg="#ff6666", bg=self.bg_color).pack(side="left", padx=5)
        tk.Button(self.confirm_btns, text="Yes", command=self.perform_delete, bg=self.accent_red, fg="white", relief="flat").pack(side="left", padx=5)
        tk.Button(self.confirm_btns, text="No", command=self.cancel_delete, bg=self.btn_bg, fg="white", relief="flat").pack(side="left", padx=5)

        self.status_label = tk.Label(self.tab_hero_datapoints, text="", font=("Arial", 10), bg=self.bg_color, fg=self.fg_color)
        self.status_label.pack(pady=5)

        self.search_frame = tk.Frame(self.tab_hero_datapoints, bg=self.bg_color)
        self.search_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        tk.Label(self.search_frame, text="Search:", bg=self.bg_color, fg=self.fg_color).pack(side="left")
        self.entry_search = tk.Entry(self.search_frame, width=25, bg=self.entry_bg, fg=self.fg_color, insertbackground="white", relief="flat")
        self.entry_search.pack(side="left", padx=5)
        
        # --- OPTIMIZATION: Debounced searching ---
        self.entry_search.bind("<KeyRelease>", self.schedule_load_data)
        
        self.chk_hide_heroes = tk.Checkbutton(self.search_frame, text="Hide unobtained", variable=self.hide_heroes_var, command=self.toggle_hide_heroes, bg=self.bg_color, fg=self.fg_color, selectcolor=self.entry_bg, activebackground=self.bg_color, activeforeground=self.fg_color)
        self.chk_hide_heroes.pack(side="left", padx=10)

        tk.Label(self.search_frame, text="Rarity:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=(10, 5))
        self.cmb_dust_filter = ttk.Combobox(self.search_frame, textvariable=self.dust_filter_var, values=["All", "Legendary", "Epic", "Rare"], state="readonly", width=10)
        self.cmb_dust_filter.pack(side="left", padx=5)
        self.cmb_dust_filter.bind("<<ComboboxSelected>>", self.load_data)

        self.hero_stats_frame = tk.Frame(self.tab_hero_datapoints, bg=self.bg_color)
        self.hero_stats_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        self.hero_stats_frame.grid_columnconfigure(0, minsize=250)
        self.hero_stats_frame.grid_columnconfigure(1, minsize=100) 
        self.hero_stats_frame.grid_columnconfigure(2, minsize=100) 
        self.hero_stats_frame.grid_columnconfigure(3, minsize=100) 
        self.hero_stats_frame.grid_columnconfigure(4, minsize=250) 
        self.hero_stats_frame.grid_columnconfigure(5, minsize=100) 
        self.hero_stats_frame.grid_columnconfigure(6, minsize=100) 
        self.hero_stats_frame.grid_columnconfigure(7, minsize=150) 
        self.hero_stats_frame.grid_columnconfigure(8, minsize=150) 

        tk.Label(self.hero_stats_frame, text="", bg=self.bg_color).grid(row=0, column=0) 
        tk.Label(self.hero_stats_frame, text="", bg=self.bg_color).grid(row=0, column=1)
        tk.Label(self.hero_stats_frame, text="", bg=self.bg_color).grid(row=0, column=2)
        self.lbl_hero_total_stars = tk.Label(self.hero_stats_frame, text="Total: 0", bg=self.bg_color, fg=self.accent_yellow, font=("Arial", 10, "bold"))
        self.lbl_hero_total_stars.grid(row=0, column=3, sticky="w")
        self.lbl_hero_total_xp = tk.Label(self.hero_stats_frame, text="Total: 0", bg=self.bg_color, fg=self.accent_green, font=("Arial", 10, "bold"))
        self.lbl_hero_total_xp.grid(row=0, column=4, sticky="w")
        self.lbl_dust_total_used = tk.Label(self.hero_stats_frame, text="Dust Used: 0", bg=self.bg_color, fg=self.accent_yellow, font=("Arial", 10, "bold"))
        self.lbl_dust_total_used.grid(row=0, column=5, sticky="w")
        self.lbl_dust_total_needed = tk.Label(self.hero_stats_frame, text="Dust Needed: 0", bg=self.bg_color, fg=self.accent_green, font=("Arial", 10, "bold"))
        self.lbl_dust_total_needed.grid(row=0, column=6, sticky="w")
        self.lbl_hero_grand_total_xp = tk.Label(self.hero_stats_frame, text="Total XP: 0", bg=self.bg_color, fg="#b0bec5", font=("Arial", 10, "bold"))
        self.lbl_hero_grand_total_xp.grid(row=0, column=7, sticky="w")
        self.lbl_hero_total_xp_needed = tk.Label(self.hero_stats_frame, text="XP Needed: 0", bg=self.bg_color, fg="#ffab91", font=("Arial", 10, "bold"))
        self.lbl_hero_total_xp_needed.grid(row=0, column=8, sticky="w")

        self.tree_frame = tk.Frame(self.tab_hero_datapoints, bg=self.bg_color)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.scrollbar = tk.Scrollbar(self.tree_frame)
        self.scrollbar.pack(side="right", fill="y")

        cols = ("ID", "Name", "Faction", "Class", "Sterne", "Xp level", "Dust Used", "Dust Needed", "Total XP", "Next XP Cost")
        self.tree = ttk.Treeview(self.tree_frame, columns=cols, show="headings", yscrollcommand=self.scrollbar.set, displaycolumns=("Name", "Faction", "Class", "Sterne", "Xp level", "Dust Used", "Dust Needed", "Total XP", "Next XP Cost"))
        
        self.tree.heading("Name", text="Name", command=lambda: self.sort_column("Name", False))
        self.tree.heading("Faction", text="Faction", command=lambda: self.sort_column("Faction", False))
        self.tree.heading("Class", text="Class", command=lambda: self.sort_column("Class", False))
        self.tree.heading("Sterne", text="Stars", command=lambda: self.sort_column("Sterne", False))
        self.tree.heading("Xp level", text="XP Level", command=lambda: self.sort_column("Xp level", False))
        self.tree.heading("Dust Used", text="Dust Used", command=lambda: self.sort_column("Dust Used", False))
        self.tree.heading("Dust Needed", text="Dust Needed", command=lambda: self.sort_column("Dust Needed", False))
        self.tree.heading("Total XP", text="Total XP", command=lambda: self.sort_column("Total XP", False))
        self.tree.heading("Next XP Cost", text="Next XP Cost", command=lambda: self.sort_column("Next XP Cost", False))

        self.tree.column("Name", width=250)
        self.tree.column("Faction", width=100)
        self.tree.column("Class", width=100)
        self.tree.column("Sterne", width=100)
        self.tree.column("Xp level", width=250)
        self.tree.column("Dust Used", width=100)
        self.tree.column("Dust Needed", width=100)
        self.tree.column("Total XP", width=150)
        self.tree.column("Next XP Cost", width=150)

        self.tree.pack(fill="both", expand=True)
        self.scrollbar.config(command=self.tree.yview)

        self.tree.bind("<ButtonRelease-1>", self.select_item)
        self.tree.bind("<BackSpace>", self.ask_delete)
        self.root.bind("<Button-1>", self.on_background_click) 

        self.load_data() 

        # --- Pets Tab UI ---
        self.pet_current_id = None
        
        self.pet_input_frame = tk.LabelFrame(self.tab_pets, text="Data Entry", padx=10, pady=10, bg=self.bg_color, fg=self.fg_color)
        self.pet_input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(self.pet_input_frame, text="Name:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, sticky="w", padx=5)
        self.entry_pet_name = tk.Entry(self.pet_input_frame, width=25, bg=self.entry_bg, fg=self.fg_color, insertbackground="white", relief="flat")
        self.entry_pet_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.pet_input_frame, text="Stars:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=2, sticky="w", padx=5)
        self.entry_pet_sterne = tk.Entry(self.pet_input_frame, width=10, bg=self.entry_bg, fg=self.fg_color, insertbackground="white", relief="flat")
        self.entry_pet_sterne.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(self.pet_input_frame, text="Bond Level:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=4, sticky="w", padx=5)
        self.entry_pet_bond = tk.Entry(self.pet_input_frame, width=15, bg=self.entry_bg, fg=self.fg_color, insertbackground="white", relief="flat")
        self.entry_pet_bond.grid(row=0, column=5, padx=5, pady=5)

        self.entry_pet_name.bind('<Return>', self.add_pet_record)
        self.entry_pet_sterne.bind('<Return>', self.add_pet_record)
        self.entry_pet_bond.bind('<Return>', self.add_pet_record)

        self.pet_btn_frame = tk.Frame(self.tab_pets, bg=self.bg_color)
        self.pet_btn_frame.pack(pady=10)

        self.pet_normal_btns = tk.Frame(self.pet_btn_frame, bg=self.bg_color)
        self.pet_normal_btns.pack()

        tk.Button(self.pet_normal_btns, text="Add", command=self.add_pet_record, bg=self.accent_green, fg="white", relief="flat", padx=10).grid(row=0, column=0, padx=10)
        tk.Button(self.pet_normal_btns, text="Update", command=self.update_pet_record, bg=self.accent_yellow, fg="black", relief="flat", padx=10).grid(row=0, column=1, padx=10)
        tk.Button(self.pet_normal_btns, text="Delete", command=self.ask_delete_pet, bg=self.accent_red, fg="white", relief="flat", padx=10).grid(row=0, column=2, padx=10)
        tk.Button(self.pet_normal_btns, text="Clear Fields", command=self.clear_pet_fields_action, bg=self.btn_bg, fg="white", relief="flat", padx=10).grid(row=0, column=3, padx=10)

        self.pet_confirm_btns = tk.Frame(self.pet_btn_frame, bg=self.bg_color)
        tk.Label(self.pet_confirm_btns, text="Really delete?", fg="#ff6666", bg=self.bg_color).pack(side="left", padx=5)
        tk.Button(self.pet_confirm_btns, text="Yes", command=self.perform_delete_pet, bg=self.accent_red, fg="white", relief="flat").pack(side="left", padx=5)
        tk.Button(self.pet_confirm_btns, text="No", command=self.cancel_delete_pet, bg=self.btn_bg, fg="white", relief="flat").pack(side="left", padx=5)

        self.pet_status_label = tk.Label(self.tab_pets, text="", font=("Arial", 10), bg=self.bg_color, fg=self.fg_color)
        self.pet_status_label.pack(pady=5)

        self.pet_search_frame = tk.Frame(self.tab_pets, bg=self.bg_color)
        self.pet_search_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        tk.Label(self.pet_search_frame, text="Search:", bg=self.bg_color, fg=self.fg_color).pack(side="left")
        self.entry_pet_search = tk.Entry(self.pet_search_frame, width=25, bg=self.entry_bg, fg=self.fg_color, insertbackground="white", relief="flat")
        self.entry_pet_search.pack(side="left", padx=5)
        
        # --- OPTIMIZATION: Debounced searching ---
        self.entry_pet_search.bind("<KeyRelease>", self.schedule_load_pets_data)

        self.chk_hide_pets = tk.Checkbutton(self.pet_search_frame, text="Hide unobtained", variable=self.hide_pets_var, command=self.toggle_hide_pets, bg=self.bg_color, fg=self.fg_color, selectcolor=self.entry_bg, activebackground=self.bg_color, activeforeground=self.fg_color)
        self.chk_hide_pets.pack(side="left", padx=10)

        self.pet_stats_frame = tk.Frame(self.tab_pets, bg=self.bg_color)
        self.pet_stats_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        self.pet_stats_frame.grid_columnconfigure(0, minsize=250)
        self.pet_stats_frame.grid_columnconfigure(1, minsize=100)
        self.pet_stats_frame.grid_columnconfigure(2, minsize=250)
        self.pet_stats_frame.grid_columnconfigure(3, minsize=100)
        self.pet_stats_frame.grid_columnconfigure(4, minsize=100)
        self.pet_stats_frame.grid_columnconfigure(5, minsize=100)
        self.pet_stats_frame.grid_columnconfigure(6, minsize=100)

        tk.Label(self.pet_stats_frame, text="", bg=self.bg_color).grid(row=0, column=0)
        self.lbl_pet_total_stars = tk.Label(self.pet_stats_frame, text="Total: 0", bg=self.bg_color, fg=self.accent_yellow, font=("Arial", 10, "bold"))
        self.lbl_pet_total_stars.grid(row=0, column=1, sticky="w")
        self.lbl_pet_total_bond = tk.Label(self.pet_stats_frame, text="Total: 0", bg=self.bg_color, fg=self.accent_green, font=("Arial", 10, "bold"))
        self.lbl_pet_total_bond.grid(row=0, column=2, sticky="w")
        self.lbl_pet_total_feathers_used = tk.Label(self.pet_stats_frame, text="Used: 0", bg=self.bg_color, fg="#b0bec5", font=("Arial", 10, "bold"))
        self.lbl_pet_total_feathers_used.grid(row=0, column=3, sticky="w")
        self.lbl_pet_total_feathers_needed = tk.Label(self.pet_stats_frame, text="Needed: 0", bg=self.bg_color, fg="#ffab91", font=("Arial", 10, "bold"))
        self.lbl_pet_total_feathers_needed.grid(row=0, column=4, sticky="w")
        self.lbl_pet_total_time_spent = tk.Label(self.pet_stats_frame, text="Time Spent: 0s", bg=self.bg_color, fg="#ce93d8", font=("Arial", 10, "bold"))
        self.lbl_pet_total_time_spent.grid(row=0, column=5, sticky="w")
        self.lbl_pet_total_time_left = tk.Label(self.pet_stats_frame, text="Time Left: 0s", bg=self.bg_color, fg="#ef9a9a", font=("Arial", 10, "bold"))
        self.lbl_pet_total_time_left.grid(row=0, column=6, sticky="w")

        self.pet_tree_frame = tk.Frame(self.tab_pets, bg=self.bg_color)
        self.pet_tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.pet_scrollbar = tk.Scrollbar(self.pet_tree_frame)
        self.pet_scrollbar.pack(side="right", fill="y")

        pet_cols = ("ID", "Name", "Sterne", "Bond", "Feathers Used", "Feathers Needed", "Time Spent", "Time Left")
        self.tree_pets = ttk.Treeview(self.pet_tree_frame, columns=pet_cols, show="headings", yscrollcommand=self.pet_scrollbar.set, displaycolumns=("Name", "Sterne", "Bond", "Feathers Used", "Feathers Needed", "Time Spent", "Time Left"))
        
        self.tree_pets.heading("Name", text="Name", command=lambda: self.sort_pet_column("Name", False))
        self.tree_pets.heading("Sterne", text="Stars", command=lambda: self.sort_pet_column("Sterne", False))
        self.tree_pets.heading("Bond", text="Bond Level", command=lambda: self.sort_pet_column("Bond", False))
        self.tree_pets.heading("Feathers Used", text="Feathers Used", command=lambda: self.sort_pet_column("Feathers Used", False))
        self.tree_pets.heading("Feathers Needed", text="Feathers Needed", command=lambda: self.sort_pet_column("Feathers Needed", False))
        self.tree_pets.heading("Time Spent", text="Time Spent", command=lambda: self.sort_pet_column("Time Spent", False))
        self.tree_pets.heading("Time Left", text="Time Left", command=lambda: self.sort_pet_column("Time Left", False))

        self.tree_pets.column("Name", width=250)
        self.tree_pets.column("Sterne", width=100)
        self.tree_pets.column("Bond", width=250)
        self.tree_pets.column("Feathers Used", width=100)
        self.tree_pets.column("Feathers Needed", width=100)
        self.tree_pets.column("Time Spent", width=150)
        self.tree_pets.column("Time Left", width=150)

        self.tree_pets.pack(fill="both", expand=True)
        self.pet_scrollbar.config(command=self.tree_pets.yview)

        self.tree_pets.bind("<ButtonRelease-1>", self.select_pet_item)
        self.tree_pets.bind("<BackSpace>", self.ask_delete_pet)

        # --- Notepad Tab UI ---
        self.notepad_toolbar = tk.Frame(self.tab_notepad, bg=self.entry_bg, pady=5)
        self.notepad_toolbar.pack(side="top", fill="x")

        tk.Button(self.notepad_toolbar, text="☑ Checklist", command=self.insert_checklist, bg=self.btn_bg, fg=self.fg_color, relief="flat").pack(side="left", padx=5)
        
        self.lbl_notepad_status = tk.Label(self.notepad_toolbar, text="", bg=self.entry_bg, fg=self.fg_color)
        self.lbl_notepad_status.pack(side="right", padx=10)

        self.notepad_frame = tk.Frame(self.tab_notepad, bg=self.bg_color)
        self.notepad_frame.pack(fill="both", expand=True)

        self.scroll_notepad = tk.Scrollbar(self.notepad_frame)
        self.scroll_notepad.pack(side="right", fill="y")

        self.txt_notepad = tk.Text(self.notepad_frame, bg=self.entry_bg, fg=self.fg_color, font=("Consolas", 10), 
                                   insertbackground=self.fg_color, relief="flat", yscrollcommand=self.scroll_notepad.set,
                                   undo=True, state="normal")
        self.txt_notepad.pack(side="left", fill="both", expand=True)
        self.scroll_notepad.config(command=self.txt_notepad.yview)
        
        self.txt_notepad.bind("<KeyRelease>", self.schedule_save_notepad)
        self.txt_notepad.bind("<FocusOut>", self.save_notepad_content)
        self.txt_notepad.bind("<Button-1>", self.on_notepad_click)

        with self.conn:
            c = self.conn.cursor()
            c.execute("SELECT value FROM settings WHERE key='notepad_content'")
            res = c.fetchone()
            if res:
                self.txt_notepad.insert("1.0", res[0])

        # --- Rules Tab UI ---
        rules_text = """
# RULES & INFORMATION

## General Disclamer
*AI was used to help code this as I don't have enough coding knowledge, especially with databases.*
Base code was written by me but optimized with AI so it'll run on anything less than a NASA PC.
This Information tab tells you most if not all important information about what this program does.
This was made by **@i.eatchildren** on discord if you find any issues or want something added, please DM me.

---

## Core Functionality

* **Database**: All your data is saved locally in a file named `datenbank.db`.
* **Automatic Saving**: Your data, settings, and preferences are saved automatically as you make changes.
* **Sorting**: Click on column headers in any table to sort the data. Click again to reverse the order.
* **Deselection**: Click on any empty background area to deselect an item in a table and clear the input fields.
* **Theme**: Customize the application's appearance in the `Settings` tab.

---

## Tab-Specific Functions

### [Progress]
* **Purpose**: Provides a high-level visual overview of your game progress.
* **Features**:
    * **Total Progress**: A weighted average of your progress across Heroes, Pets, and Buildings.
    * **Progress Bars**: Visual indicators for different categories that change color from Red to Yellow, then Green, and finally Gold at 100%.
    * **Categories**: Tracks Hero Stars, Hero XP, Total XP amount, Dust spent, Pet Stars, Pet Bonds, Feathers spent, Time spent, Building levels, and Equipment levels.

### [Stats]
* **Purpose**: Shows a detailed numerical breakdown of all your game statistics.
* **Features**:
    * **Comprehensive Overview**: Displays totals for Heroes, Pets, Buildings, Elixir, and Equipment.
    * **Resource Tracking**: Check your total resource usage (Dust, Feathers, Lumber, Ore, Amber) and see what's still needed to max everything out.

### [Heroes]
* **Purpose**: Manage individual hero data.
* **Data Points**:
    * **Stars**: 0-12
    * **XP Level**: 1-140

#### Subtab: Datapoints
* **Summary Bar**: The bar at the top shows the sum of stats for the currently displayed heroes.
* **CRUD Operations**: Add, Update, or Delete hero records.
* **Filtering**:
    * `Hide unobtained`: Hides heroes that have 0 stars.
    * `Rarity Filter`: Show only Legendary, Epic, or Rare heroes.

#### Subtab: Team Calculator
* Calculates the theoretically best team based on your hero data.
* **Opponent Faction**: Select up to two opponent factions to get a strategic advantage.
* **Class Composition**: Specify how many of each class (Warrior, Assassin, etc.) you want in the team.
* **Faction Bonus Logic**: Toggle whether to consider the faction advantage/disadvantage system.
* **Support Logic**: Option to disable faction bonus calculations specifically for Support class heroes.
* **Scoring**: Ranks heroes based on a weighted score of their base stats, stars, and faction advantage.

#### Subtab: Fashion
* Track which fashion items you have unlocked.
* **Randomize**: Generates a random outfit combination from your unlocked items.

### [Pets]
* **Purpose**: Manage individual pet data.
* **Data Points**:
    * **Stars**: 0-12
    * **Bond Level**: 1-15
* **Features**:
    * **Summary Bar**: Shows total stats for displayed pets (Stars, Bond, Feathers, Time).
    * **CRUD Operations**: Add, Update, or Delete pet records.
    * **Filtering**: `Hide unobtained` hides pets with 0 stars.

### [Pulls]
* **Purpose**: Track your luck with Hero Scrolls and Pet Eggs.

#### Subtab: Main
* Input your pulls. The app automatically updates the corresponding Hero/Pet if the new pull has more stars. Every pull is logged.

#### Subtab: Luck
* Visualizes your pull luck against the game's official probabilities.
* **Weighted Luck**: A metric that shows how lucky your pulls are, with >100% being lucky.
* Click `Total Pulled` to see a detailed breakdown of how many of each star rating you've pulled.

#### Subtab: Datapoints (Scrolls/Eggs)
* View, edit, delete, or import your entire pull history from a CSV file.

### [Conquest (Buildings)]
* **Purpose**: Manage your building levels and plan upgrades.
* **Features**:
    * **Max Level**: 14 for all buildings.
    * **Construction Multipliers**: Adjust the Speed, Lumber, and Ore costs to match your in-game research and ascension bonuses (values from 0.1% to 100%).

#### Subtab: Levels
* View current upgrade costs and the total resources needed to max out each building.
* `Max All`: Sets all other buildings to your current Castle level.
* **Rule**: No building can be a higher level than your Castle.

#### Subtab: Targets
* Plan future upgrades by setting a target level for each building to see the total resource cost from your current level to the target.
* `Set All`: Sets a uniform target for all buildings.

### [Elixir]
* **Purpose**: Track and project your Total Elixir gains.

#### Subtab: Expected
* A calculator to estimate how long it will take to reach a target amount of Elixir.
* `Weekly Growth` is auto-filled based on your recent history but can be overridden.

#### Subtab: Datapoints
* Manually Add, Delete, or Import Elixir records from a CSV file.
* The table automatically shows the gain and percentage increase between datapoints.

#### Subtab: Graph
* A line chart visualizing your Total Elixir and Weekly Gain over time.
* `Show Projection (6m)`: Extrapolates your elixir growth for the next 6 months based on your average gain.
* A boxplot chart shows the distribution and variance of your percentage growth.
* Includes time filters and a `Save Image` button.

### [Equipment]
* **Purpose**: Manage your equipment levels.
* **Features**:
    * Shows the current Boost %, the Amber cost for the next level, and the total Amber needed to max out.
    * Use the `+` and `-` buttons to easily adjust levels.
    * `Max All`: Instantly sets all equipment to the maximum level.

### [Notepad]
* **Purpose**: A simple space for notes.
* **Features**:
    * A basic text editor for jotting down strategies, reminders, or to-do lists.
    * `Checklist` button: Inserts a `☐` checkbox. Click the box in the text to toggle it between `☐` and `☑`.

### [Settings]
* **Purpose**: Manage application data and appearance.
* **Features**:
    * **Data Management**:
        * `Export Data to CSV`: Saves all your data into a single CSV file.
        * `Import Data from CSV`: Loads data from a previously exported CSV file.
    * **Theme Customization**:
        * Change the colors of the application (Background, Foreground, Accents, etc.).
    * **Danger Zone**:
        * `Reset All Progress`: Wipes all your entered data from the database. **This cannot be undone.**
"""
        self.txt_rules = tk.Text(self.tab_rules, bg=self.bg_color, fg=self.fg_color, font=("Segoe UI", 10), padx=10, pady=10, relief="flat", wrap="word")
        self.txt_rules.pack(fill="both", expand=True)
        
        self.txt_rules.tag_configure("h1", font=("Segoe UI", 20, "bold"), foreground=self.accent_yellow, spacing1=10, spacing3=5)
        self.txt_rules.tag_configure("h2", font=("Segoe UI", 18, "bold"), foreground=self.accent_green, spacing1=10, spacing3=5)
        self.txt_rules.tag_configure("h3", font=("Segoe UI", 16, "bold", "underline"), spacing1=5, spacing3=2)
        self.txt_rules.tag_configure("h4", font=("Segoe UI", 12, "bold", "italic"), foreground=self.accent_yellow, spacing1=5, spacing3=2)
        self.txt_rules.tag_configure("bold", font=("Segoe UI", 10, "bold"))
        self.txt_rules.tag_configure("italic", font=("Segoe UI", 10, "italic"))
        self.txt_rules.tag_configure("underline", underline=True)
        self.txt_rules.tag_configure("strike", overstrike=True)
        self.txt_rules.tag_configure("code", font=("Consolas", 10), background="#333333", foreground="#e0e0e0")
        self.txt_rules.tag_configure("bullet_0", lmargin1=20, lmargin2=30)
        self.txt_rules.tag_configure("bullet_1", lmargin1=40, lmargin2=50)
        self.txt_rules.tag_configure("normal", font=("Segoe UI", 10))

        self.render_markdown(rules_text)
        self.txt_rules.config(state="disabled") 

        # --- Settings Tab UI ---
        self.settings_frame = tk.Frame(self.tab_settings, bg=self.bg_color)
        self.settings_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.data_mgmt_frame = tk.LabelFrame(self.settings_frame, text="Data Management", bg=self.bg_color, fg=self.fg_color, padx=10, pady=10)
        self.data_mgmt_frame.pack(fill="x", pady=10)

        tk.Button(self.data_mgmt_frame, text="Export Data to CSV", command=self.export_csv, bg=self.accent_green, fg="white", relief="flat", padx=10).pack(side="left", padx=10)
        tk.Button(self.data_mgmt_frame, text="Import Data from CSV", command=self.import_csv, bg=self.accent_yellow, fg="black", relief="flat", padx=10).pack(side="left", padx=10)

        self.theme_frame = tk.LabelFrame(self.settings_frame, text="Theme Customization", bg=self.bg_color, fg=self.fg_color, padx=10, pady=10)
        self.theme_frame.pack(fill="x", pady=10)
        
        self.theme_vars = {}
        theme_labels = {
            "bg_color": "Background", "fg_color": "Foreground", "entry_bg": "Entry/Input",
            "btn_bg": "Button/Tabs", "accent_green": "Accent Green", "accent_yellow": "Accent Yellow",
            "accent_red": "Accent Red"
        }
        
        r, c = 0, 0
        for key, label in theme_labels.items():
            tk.Label(self.theme_frame, text=label, bg=self.bg_color, fg=self.fg_color).grid(row=r, column=c, padx=5, pady=5, sticky="e")
            
            current_val = getattr(self, key)
            
            contrast = self.get_contrast_color(current_val)
            frame = tk.Frame(self.theme_frame, bg=contrast, padx=1, pady=1)
            frame.grid(row=r, column=c+1, padx=5, pady=5, sticky="w")
            
            btn = tk.Button(frame, bg=current_val, width=10, relief="flat")
            btn.configure(command=lambda k=key, b=btn, f=frame: self.pick_theme_color(k, b, f))
            btn.pack(fill="both", expand=True)
            
            self.theme_vars[key] = current_val
            
            c += 2
            if c >= 6:
                c = 0; r += 1
                
        tk.Button(self.theme_frame, text="Save & Apply Theme", command=self.save_theme, bg=self.accent_green, fg="white", relief="flat").grid(row=r+1, column=0, columnspan=2, pady=10, padx=5)
        tk.Button(self.theme_frame, text="Reset to Default", command=self.reset_theme, bg=self.accent_red, fg="white", relief="flat").grid(row=r+1, column=2, columnspan=2, pady=10, padx=5)

        self.danger_frame = tk.LabelFrame(self.settings_frame, text="Danger Zone", bg=self.bg_color, fg="#ef5350", padx=10, pady=10)
        self.danger_frame.pack(fill="x", pady=10)

        self.btn_reset = tk.Button(self.danger_frame, text="Reset All Progress", command=self.ask_reset_progress, bg=self.accent_red, fg="white", relief="flat", padx=10)
        self.btn_reset.pack(side="left", padx=10)

        self.reset_confirm_frame = tk.Frame(self.danger_frame, bg=self.bg_color)
        tk.Label(self.reset_confirm_frame, text="Are you sure? This cannot be undone.", fg="#ff6666", bg=self.bg_color).pack(side="left", padx=5)
        tk.Button(self.reset_confirm_frame, text="Yes, Reset Everything", command=self.perform_reset_progress, bg=self.accent_red, fg="white", relief="flat").pack(side="left", padx=5)
        tk.Button(self.reset_confirm_frame, text="Cancel", command=self.cancel_reset, bg=self.btn_bg, fg="white", relief="flat").pack(side="left", padx=5)

        self.settings_status_label = tk.Label(self.settings_frame, text="", font=("Arial", 10), bg=self.bg_color, fg=self.fg_color)
        self.settings_status_label.pack(pady=10)

        # --- Initial Data Load ---
        self.load_pets_data()
        self.update_progress_tab()
        self.load_elixir_data()
        self.update_stats_tab()

    def on_closing(self):
        # Gracefully shut down DB on exit
        if hasattr(self, 'conn'):
            self.conn.close()
        self.root.destroy()

    def render_markdown(self, text):
        lines = text.split('\n')
        for line in lines:
            tags = ["normal"]
            
            if line.startswith("# "):
                tags = ["h1"]
                line = line[2:]
            elif line.startswith("## "):
                tags = ["h2"]
                line = line[3:]
            elif line.startswith("#### "):
                tags = ["h4"]
                line = line[5:]
            elif line.startswith("### "):
                tags = ["h3"]
                line = line[4:]
            elif line.strip() == "---":
                self.txt_rules.insert("end", "-"*100 + "\n", "normal")
                continue
            
            stripped = line.lstrip()
            if stripped.startswith("* "):
                indent = len(line) - len(stripped)
                tags.append("bullet_1" if indent > 0 else "bullet_0")
                line = "• " + stripped[2:]
            
            parts = re.split(r'(\*\*.*?\*\*|`.*?`|\*.*?\*|__.*?__|~~.*?~~)', line)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    self.txt_rules.insert("end", part[2:-2], tuple(tags + ["bold"]))
                elif part.startswith("`") and part.endswith("`"):
                    self.txt_rules.insert("end", part[1:-1], tuple(tags + ["code"]))
                elif part.startswith("*") and part.endswith("*"):
                    self.txt_rules.insert("end", part[1:-1], tuple(tags + ["italic"]))
                elif part.startswith("__") and part.endswith("__"):
                    self.txt_rules.insert("end", part[2:-2], tuple(tags + ["underline"]))
                elif part.startswith("~~") and part.endswith("~~"):
                    self.txt_rules.insert("end", part[2:-2], tuple(tags + ["strike"]))
                else:
                    self.txt_rules.insert("end", part, tuple(tags))
            
            self.txt_rules.insert("end", "\n")


    def setup_team_calculator(self):
        main_frame = tk.Frame(self.tab_hero_team_calc, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        controls_frame = tk.Frame(main_frame, bg=self.bg_color)
        controls_frame.pack(side="left", fill="y", padx=(0, 20))

        faction_frame = tk.LabelFrame(controls_frame, text="Opponent Faction (Max 2)", bg=self.bg_color, fg=self.fg_color, padx=10, pady=10)
        faction_frame.pack(fill="x", pady=(0, 15))

        self.team_calc_faction_vars = {
            "Fire": tk.BooleanVar(), "Water": tk.BooleanVar(),
            "Wind": tk.BooleanVar(), "Earth": tk.BooleanVar()
        }
        
        self.faction_checkboxes = []

        def on_faction_select():
            selected_count = sum(v.get() for v in self.team_calc_faction_vars.values())
            if selected_count >= 2:
                for var, chk in zip(self.team_calc_faction_vars.values(), self.faction_checkboxes):
                    if not var.get():
                        chk.configure(state="disabled")
            else:
                for chk in self.faction_checkboxes:
                    chk.configure(state="normal")

        for faction, var in self.team_calc_faction_vars.items():
            chk = tk.Checkbutton(faction_frame, text=faction, variable=var, bg=self.bg_color, fg=self.fg_color,
                                selectcolor=self.entry_bg, activebackground=self.bg_color, activeforeground=self.fg_color,
                                command=on_faction_select)
            chk.pack(anchor="w")
            self.faction_checkboxes.append(chk)

        class_frame = tk.LabelFrame(controls_frame, text="Class Composition (Sum must be 5)", bg=self.bg_color, fg=self.fg_color, padx=10, pady=10)
        class_frame.pack(fill="x", pady=15)

        self.team_calc_class_vars = {
            "Warrior": tk.IntVar(value=2), "Assassin": tk.IntVar(value=1),
            "Mage": tk.IntVar(value=0), "Support": tk.IntVar(value=2)
        }
        
        with self.conn:
            c = self.conn.cursor()
            for cls in self.team_calc_class_vars:
                c.execute("SELECT value FROM settings WHERE key=?", (f"team_calc_{cls}",))
                res = c.fetchone()
                if res:
                    try: self.team_calc_class_vars[cls].set(int(res[0]))
                    except ValueError: pass
        
        self.spinboxes = {}
        self.last_spinbox_values = {k: v.get() for k, v in self.team_calc_class_vars.items()}

        def validate_spinboxes(var_name, *args):
            total = sum(v.get() for v in self.team_calc_class_vars.values())
            if total > 5:
                offending_var = self.team_calc_class_vars[var_name.split("_")[0]] 
                current_val = offending_var.get()
                offending_var.set(current_val - (total - 5)) 

        for i, (class_name, var) in enumerate(self.team_calc_class_vars.items()):
            tk.Label(class_frame, text=class_name, bg=self.bg_color, fg=self.fg_color).grid(row=i, column=0, sticky="w", pady=2)
            spinbox = tk.Spinbox(class_frame, from_=0, to=5, textvariable=var, width=5, bg=self.entry_bg, fg=self.fg_color,
                                 buttonbackground=self.btn_bg, relief="flat")
            spinbox.grid(row=i, column=1, padx=5)
            self.spinboxes[class_name] = spinbox
            var.trace_add("write", lambda name, index, mode, cn=class_name: validate_spinboxes(cn))

        self.team_calc_faction_bonus_var = tk.BooleanVar(value=True)
        toggle_frame = tk.Frame(controls_frame, bg=self.bg_color)
        toggle_frame.pack(fill="x", pady=15)
        chk_bonus = tk.Checkbutton(toggle_frame, text="Enable Faction Bonus Logic", variable=self.team_calc_faction_bonus_var,
                                   bg=self.bg_color, fg=self.fg_color, selectcolor=self.entry_bg,
                                   activebackground=self.bg_color, activeforeground=self.fg_color)
        chk_bonus.pack(anchor="w")
        
        self.team_calc_support_ignore_faction_var = tk.BooleanVar(value=False)
        chk_support_ignore = tk.Checkbutton(toggle_frame, text="Disable Faction Bonus for Support", variable=self.team_calc_support_ignore_faction_var,
                                   bg=self.bg_color, fg=self.fg_color, selectcolor=self.entry_bg,
                                   activebackground=self.bg_color, activeforeground=self.fg_color)
        chk_support_ignore.pack(anchor="w")

        btn_calculate = tk.Button(controls_frame, text="Calculate Team", bg=self.accent_green, fg="white",
                                  relief="flat", padx=10, pady=5, command=self.calculate_and_display_team)
        btn_calculate.pack(fill="x", pady=(20, 5))

        self.team_calc_error_label = tk.Label(controls_frame, text="", bg=self.bg_color, fg=self.accent_red)
        self.team_calc_error_label.pack(fill="x", pady=(0, 10))
        
        results_area = tk.Frame(main_frame, bg=self.bg_color)
        results_area.pack(side="left", fill="both", expand=True)

        self.team_calc_frontline_frame = tk.LabelFrame(results_area, text="Frontline (2 Slots)", bg=self.bg_color, fg=self.fg_color, padx=10, pady=10)
        self.team_calc_frontline_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.team_calc_backline_frame = tk.LabelFrame(results_area, text="Backline (3 Slots)", bg=self.bg_color, fg=self.fg_color, padx=10, pady=10)
        self.team_calc_backline_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.team_calc_substitutes_frame = tk.LabelFrame(results_area, text="Alternatives (Next Highest Scores)", bg=self.bg_color, fg=self.fg_color, padx=10, pady=10)
        self.team_calc_substitutes_frame.pack(fill="both", expand=True, pady=(10, 0))

    def calculate_and_display_team(self):
        self.team_calc_error_label.config(text="")
        for widget in self.team_calc_frontline_frame.winfo_children(): widget.destroy()
        for widget in self.team_calc_backline_frame.winfo_children(): widget.destroy()
        for widget in self.team_calc_substitutes_frame.winfo_children(): widget.destroy()

        selected_factions = [f for f, v in self.team_calc_faction_vars.items() if v.get()]
        class_composition = {c: v.get() for c, v in self.team_calc_class_vars.items()}
        faction_bonus_enabled = self.team_calc_faction_bonus_var.get()
        support_ignore_faction = self.team_calc_support_ignore_faction_var.get()

        with self.conn:
            c = self.conn.cursor()
            for cls, val in class_composition.items():
                c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (f"team_calc_{cls}", val))

        if sum(class_composition.values()) == 0:
            class_composition = {"Warrior": 2, "Assassin": 1, "Mage": 0, "Support": 2}
        elif sum(class_composition.values()) != 5:
            self.team_calc_error_label.config(text="The sum of class composition must be exactly 5 (or 0 for default).")
            return

        all_heroes = []
        c = self.conn.cursor()
        c.execute("SELECT Name, Faction, Class, Sterne FROM daten WHERE sterne != '-'")
        fetched_heroes = c.fetchall()

        faction_map = {"Fire": "Wind", "Wind": "Earth", "Earth": "Water", "Water": "Fire"}

        for name, faction, hero_class, stars_str in fetched_heroes:
            try:
                stars = int(stars_str)
            except (ValueError, TypeError):
                continue
            
            base_score = HERO_BASE_SCORES.get(name, 0)
            norm_score = (base_score / 10) * 100
            norm_stars = (stars / 12) * 100

            faction_score = 50 
            if faction_bonus_enabled and selected_factions:
                if hero_class == "Support" and support_ignore_faction:
                    faction_score = 50
                else:
                    scores = []
                    for opp_faction in selected_factions:
                        if faction_map.get(faction) == opp_faction:
                            scores.append(100) 
                        elif faction_map.get(opp_faction) == faction:
                            scores.append(0) 
                        else:
                            scores.append(50) 
                    faction_score = sum(scores) / len(scores) if scores else 50
            
            norm_faction = faction_score
            total_score = (norm_score * 0.50) + (norm_stars * 0.30) + (norm_faction * 0.20)
            
            all_heroes.append({
                "name": name,
                "class": hero_class,
                "stars": stars,
                "score": total_score,
                "faction_score": faction_score
            })

        all_heroes.sort(key=lambda h: h['score'], reverse=True)
        selected_team = []
        
        heroes_by_class = {"Warrior": [], "Assassin": [], "Mage": [], "Support": []}
        for hero in all_heroes:
            if hero['class'] in heroes_by_class:
                heroes_by_class[hero['class']].append(hero)

        for class_name, count in class_composition.items():
            for hero in heroes_by_class[class_name][:count]:
                if hero not in selected_team:
                    selected_team.append(hero)

        if len(selected_team) < 5:
            remaining_heroes = [h for h in all_heroes if h not in selected_team]
            needed = 5 - len(selected_team)
            selected_team.extend(remaining_heroes[:needed])

        selected_team.sort(key=lambda h: h['score'], reverse=True)

        frontline = []
        backline = []
        temp_team = list(selected_team)
        
        warriors_in_team = [h for h in temp_team if h['class'] == 'Warrior']
        for h in warriors_in_team:
            if len(frontline) < 2:
                frontline.append(h)
                temp_team.remove(h)

        while len(frontline) < 2 and temp_team:
            frontline.append(temp_team.pop(0))
        
        backline.extend(temp_team)
        
        frontline.sort(key=lambda h: h['score'], reverse=True)
        backline.sort(key=lambda h: h['score'], reverse=True)

        used_alts = set()

        def get_alt_text(hero_class):
            candidates = [h for h in all_heroes if h['class'] == hero_class and h not in selected_team and h['name'] not in used_alts]
            if candidates:
                best = candidates[0]
                used_alts.add(best['name'])
                return f"  |  Alt: {best['name']} ({best['stars']}*) - {best['score']:.2f}"
            return ""

        def get_color(score):
            if score > 50: return self.accent_green
            if score < 50: return self.accent_red
            return self.fg_color

        for i, hero in enumerate(frontline):
            alt_text = get_alt_text(hero['class'])
            text = f"{i+1}. {hero['name']} ({hero['stars']}*) - Score: {hero['score']:.2f}{alt_text}"
            tk.Label(self.team_calc_frontline_frame, text=text, bg=self.bg_color, fg=get_color(hero['faction_score']), font=("Arial", 10)).pack(anchor="w", padx=5)

        for i, hero in enumerate(backline):
            alt_text = get_alt_text(hero['class'])
            text = f"{i+1}. {hero['name']} ({hero['stars']}*) - Score: {hero['score']:.2f}{alt_text}"
            tk.Label(self.team_calc_backline_frame, text=text, bg=self.bg_color, fg=get_color(hero['faction_score']), font=("Arial", 10)).pack(anchor="w", padx=5)

        self.team_calc_substitutes_frame.pack_forget()

    def setup_fashion_ui(self):
        # Main container
        main_frame = tk.Frame(self.tab_hero_fashion, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Slots Frame
        slots_frame = tk.Frame(main_frame, bg=self.bg_color)
        slots_frame.pack(pady=20)

        self.fashion_slots = []
        self.fashion_slot_colors = []
        for i in range(4):
            frame = tk.Frame(slots_frame, bg=self.entry_bg, highlightbackground=self.fg_color, highlightthickness=1, padx=10, pady=10)
            frame.pack(side="left", padx=10)
            
            lbl_title = tk.Label(frame, text=f"Slot {chr(65+i)}", font=("Arial", 10, "bold"), bg=self.entry_bg, fg=self.fg_color)
            lbl_title.pack()
            
            color_sq = tk.Frame(frame, width=36, height=36, bg=self.entry_bg, relief="solid", borderwidth=1)
            color_sq.pack(pady=(5, 0))
            self.fashion_slot_colors.append(color_sq)
            
            lbl_val = tk.Label(frame, text="-", font=("Arial", 12), bg=self.entry_bg, fg=self.accent_yellow, width=15)
            lbl_val.pack(pady=5)
            self.fashion_slots.append(lbl_val)

        # Controls Frame
        controls_frame = tk.Frame(main_frame, bg=self.bg_color)
        controls_frame.pack(pady=20)

        # Randomize Button
        btn_random = tk.Button(controls_frame, text="Randomize Fashion", command=self.randomize_fashion, 
                               bg=self.accent_green, fg="white", font=("Arial", 12, "bold"), relief="flat", padx=20, pady=5)
        btn_random.pack(side="left", padx=20)

        tk.Button(controls_frame, text="Select All", command=self.select_all_fashion, bg=self.btn_bg, fg=self.fg_color, font=("Arial", 10), relief="flat", padx=10).pack(side="left", padx=10)
        tk.Button(controls_frame, text="Deselect All", command=self.deselect_all_fashion, bg=self.btn_bg, fg=self.fg_color, font=("Arial", 10), relief="flat", padx=10).pack(side="left", padx=10)

        # Grid Container
        grid_frame = tk.Frame(main_frame, bg=self.bg_color)
        grid_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Content Frame (Centered, no scrollbar)
        self.fashion_list_frame = tk.Frame(grid_frame, bg=self.bg_color)
        self.fashion_list_frame.pack(anchor="n")
        
        self.load_fashion_data()

    def load_fashion_data(self):
        for widget in self.fashion_list_frame.winfo_children():
            widget.destroy()
        
        c = self.conn.cursor()
        c.execute("SELECT name, is_unlocked FROM fashion")
        rows = c.fetchall()
        
        rows.sort(key=lambda x: self.fashion_items.index(x[0]) if x[0] in self.fashion_items else 999)
        
        self.fashion_vars = {}

        columns = 6
        for i, (name, unlocked) in enumerate(rows):
            r, c = divmod(i, columns)
            
            frame = tk.Frame(self.fashion_list_frame, bg=self.entry_bg, highlightbackground=self.fg_color, highlightthickness=1, padx=5, pady=5)
            frame.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
            
            header_frame = tk.Frame(frame, bg=self.entry_bg)
            header_frame.pack(pady=(0, 5))
            
            if name in self.fashion_colors:
                tk.Frame(header_frame, width=18, height=18, bg=self.fashion_colors[name], relief="solid", borderwidth=1).pack(side="left", padx=(0, 5))
            
            tk.Label(header_frame, text=name, font=("Arial", 10, "bold"), bg=self.entry_bg, fg=self.fg_color, width=15, wraplength=120).pack(side="left")
            
            var = tk.IntVar(value=unlocked)
            self.fashion_vars[name] = var
            cb = tk.Checkbutton(frame, text="Unlocked", variable=var, command=lambda n=name, v=var: self.on_fashion_check(n, v), 
                                bg=self.entry_bg, fg=self.fg_color, selectcolor=self.bg_color, activebackground=self.entry_bg, activeforeground=self.fg_color)
            cb.pack()

    def on_fashion_check(self, name, var):
        new_status = var.get()
        c = self.conn.cursor()
        c.execute("UPDATE fashion SET is_unlocked = ? WHERE name = ?", (new_status, name))
        self.conn.commit()

    def select_all_fashion(self):
        c = self.conn.cursor()
        c.execute("UPDATE fashion SET is_unlocked = 1")
        self.conn.commit()
        self.load_fashion_data()

    def deselect_all_fashion(self):
        c = self.conn.cursor()
        c.execute("UPDATE fashion SET is_unlocked = 0")
        self.conn.commit()
        self.load_fashion_data()

    def randomize_fashion(self):
        c = self.conn.cursor()
        c.execute("SELECT name FROM fashion WHERE is_unlocked = 1")
        unlocked_items = [row[0] for row in c.fetchall()]
        
        if not unlocked_items:
            unlocked_items = ["Default"]

        for slot, color_slot in zip(self.fashion_slots, self.fashion_slot_colors):
            choice = random.choice(unlocked_items)
            slot.config(text=choice)
            if choice in self.fashion_colors:
                color_slot.config(bg=self.fashion_colors[choice])
            else:
                color_slot.config(bg=self.entry_bg)

    def _get_prefix_sums(self, lst):
        sums = [0]
        curr = 0
        for x in lst:
            curr += x
            sums.append(curr)
        return sums

    def get_contrast_color(self, hex_color):
        if not hex_color or not isinstance(hex_color, str) or not hex_color.startswith("#"):
             return "#000000"
        try:
            r, g, b = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return "#000000" if luminance > 0.5 else "#ffffff"
        except Exception:
            return "#000000"

    def load_theme(self):
        c = self.conn.cursor()
        for key, default in self.default_theme.items():
            c.execute("SELECT value FROM settings WHERE key=?", ("theme_" + key,))
            res = c.fetchone()
            val = res[0] if res else default
            setattr(self, key, val)

    def pick_theme_color(self, key, btn, frame):
        curr = self.theme_vars.get(key, getattr(self, key))
        color = colorchooser.askcolor(color=curr, title=f"Choose {key}")[1]
        if color:
            self.theme_vars[key] = color
            btn.configure(bg=color)
            frame.configure(bg=self.get_contrast_color(color))

    def save_theme(self):
        with self.conn:
            c = self.conn.cursor()
            for key, val in self.theme_vars.items():
                c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ("theme_" + key, val))
        
        self.apply_theme()
        self.show_settings_status("Theme saved and applied!", "#66bb6a")

    def apply_theme(self):
        old_colors = {
            "bg_color": self.bg_color, "fg_color": self.fg_color, "entry_bg": self.entry_bg,
            "btn_bg": self.btn_bg, "accent_green": self.accent_green, "accent_yellow": self.accent_yellow,
            "accent_red": self.accent_red
        }

        for key, val in self.theme_vars.items():
            setattr(self, key, val)

        self.root.configure(bg=self.bg_color)

        self.style.configure("Treeview", background=self.entry_bg, foreground=self.fg_color, fieldbackground=self.entry_bg)
        self.style.configure("Treeview.Heading", foreground=self.fg_color)
        self.style.configure("TNotebook", background=self.bg_color)
        self.style.configure("TNotebook.Tab", background=self.btn_bg, foreground=self.fg_color)
        self.style.map("TNotebook.Tab", background=[("selected", self.accent_green)], foreground=[("selected", "white")])

        if MATPLOTLIB_AVAILABLE:
            for fig, ax in [(getattr(self, 'fig', None), getattr(self, 'ax', None)),
                           (getattr(self, 'fig_scroll', None), getattr(self, 'ax_scroll', None)),
                           (getattr(self, 'fig_egg', None), getattr(self, 'ax_egg', None))]:
                if fig and ax:
                    fig.patch.set_facecolor(self.bg_color)
                    ax.set_facecolor(self.bg_color)
                    ax.tick_params(axis='x', colors=self.fg_color)
                    ax.tick_params(axis='y', colors=self.fg_color)
                    ax.spines['bottom'].set_color(self.fg_color)
                    ax.spines['top'].set_color(self.fg_color)
                    ax.spines['left'].set_color(self.fg_color)
                    ax.spines['right'].set_color(self.fg_color)
                    ax.title.set_color(self.fg_color)
                    ax.xaxis.label.set_color(self.fg_color)
                    ax.yaxis.label.set_color(self.fg_color)
                    
                    legend = ax.get_legend()
                    if legend:
                        legend.get_frame().set_facecolor(self.bg_color)
                        legend.get_frame().set_edgecolor(self.fg_color)
                        for text in legend.get_texts():
                            text.set_color(self.fg_color)
            if hasattr(self, 'canvas'): self.canvas.draw()
            if hasattr(self, 'canvas_scroll'): self.canvas_scroll.draw()
            if hasattr(self, 'canvas_egg'): self.canvas_egg.draw()

        self.update_widget_tree(self.root, old_colors)
        self.update_progress_tab()
        for name in self.building_entries:
            self.update_building_stats(name)

    def update_widget_tree(self, widget, old_colors):
        try:
            if not widget.winfo_exists(): return
            w_class = widget.winfo_class()
            
            try:
                current_bg = widget.cget("bg")
                if current_bg == old_colors["bg_color"]: widget.configure(bg=self.bg_color)
                elif current_bg == old_colors["entry_bg"]: widget.configure(bg=self.entry_bg)
                elif current_bg == old_colors["btn_bg"]: widget.configure(bg=self.btn_bg)
            except: pass

            try:
                current_fg = widget.cget("fg")
                if current_fg == old_colors["fg_color"]: widget.configure(fg=self.fg_color)
            except: pass

            if w_class == "Entry":
                widget.configure(insertbackground=self.fg_color)
            elif w_class == "Checkbutton":
                widget.configure(selectcolor=self.entry_bg, activebackground=self.bg_color, activeforeground=self.fg_color)
                
        except Exception: pass

        for child in widget.winfo_children():
            self.update_widget_tree(child, old_colors)

    def reset_theme(self):
        with self.conn:
            c = self.conn.cursor()
            for key in self.default_theme:
                c.execute("DELETE FROM settings WHERE key=?", ("theme_" + key,))
        
        self.theme_vars.update(self.default_theme)
        self.apply_theme()
        self.show_settings_status("Theme reset and applied!", "#66bb6a")

    def on_tab_change(self, event):
        self.root.focus_set()

    def on_pulls_tab_change(self, event):
        if self.pulls_notebook.select() == str(self.tab_pulls_luck):
            self.update_luck_stats() 

    def update_global_data(self):
        self.update_progress_tab()
        self.update_stats_tab()

    def get_progress_color(self, current, maximum):
        if maximum == 0:
            return "#404040" 
        
        ratio = current / maximum
        if ratio >= 1.0: return "#ffd700" 
        
        if ratio < 0.5:
            r, g = 255, int(255 * (ratio * 2))
        else:
            r, g = int(255 * (1 - (ratio - 0.5) * 2)), 255
            
        return f"#{r:02x}{g:02x}00"

    def update_progress_tab(self):
        c = self.conn.cursor()
        
        c.execute("SELECT name, sterne, xp_level, rarity FROM daten")
        rows = c.fetchall()
        total_heroes = len(rows)
        
        current_stars, current_xp, current_actual_xp, current_dust = 0, 0, 0, 0
        max_dust = 0
        
        max_xp_per_hero = sum(self.hero_xp_costs)
        max_actual_xp = total_heroes * max_xp_per_hero
        max_stars = total_heroes * 12
        max_xp = total_heroes * 140

        for r in rows:
            name, sterne_val, xp_val, rarity = r[0], r[1], r[2], r[3]
            s = int(sterne_val) if sterne_val != '-' else 0
            current_stars += s
            x = int(xp_val) if xp_val != '-' else 0
            current_xp += x
            
            if x > 1:
                current_actual_xp += self.hero_xp_cumulative[min(x - 1, len(self.hero_xp_costs))]

            if not rarity: rarity = self.get_rarity(name)
            costs_cum = self.dust_costs_cumulative.get(rarity, self.dust_costs_cumulative["Legendary"])
            max_dust += costs_cum[-1]
            current_dust += costs_cum[max(0, min(s, 12))]
        
        c.execute("SELECT sterne, bond_level FROM pets")
        rows = c.fetchall()
        total_pets = len(rows)
        
        current_pet_stars, current_pet_bond, current_pet_feathers, current_pet_time = 0, 0, 0, 0
        
        max_feathers_per_pet = sum(self.pet_feather_costs)
        max_pet_feathers_total = total_pets * max_feathers_per_pet
        max_time_per_pet = sum(self.pet_bond_time_costs)
        max_pet_time_total = total_pets * max_time_per_pet

        for r in rows:
            s = int(r[0]) if r[0] != '-' else 0
            current_pet_stars += s
            if r[1] != '-':
                b = int(r[1])
                current_pet_bond += b
                current_pet_time += self.pet_bond_time_cumulative[max(0, b - 1)]
            current_pet_feathers += self.pet_feather_cumulative[max(0, min(s, 12))]
        
        max_pet_stars = total_pets * 12
        max_pet_bond = total_pets * 15

        c.execute("SELECT level FROM buildings")
        rows = c.fetchall()
        total_buildings = len(rows)
        current_build_levels = sum(int(r[0]) for r in rows if r[0] != '-')
        max_build_total = total_buildings * self.building_max_level
        
        c.execute("SELECT name, level FROM equipment")
        equip_map = {r[0]: r[1] for r in c.fetchall()}
        current_equip_levels = sum(equip_map.get(name, 0) for name in self.equipment_data)
        max_equip_levels = sum(len(levels) - 1 for levels in self.equipment_data.values())

        def update_pb(pb, lbl, current, maximum, style_name, is_time=False, is_exp=False):
            if maximum > 0:
                ratio = current / maximum
                pb['value'] = ratio * 100
                current_str = self.format_seconds(current) if is_time else f"{current:,}"
                max_str = self.format_seconds(maximum) if is_time else f"{maximum:,}"
                if is_exp:
                    current_str = f"{current:.2e}"
                    max_str = f"{maximum:.2e}"
                lbl.set(f"{current_str} / {max_str} ({ratio:.1%})")
                self.style.configure(style_name, background=self.get_progress_color(current, maximum))

        update_pb(self.pb_hero_stars, self.prog_hero_stars_val, current_stars, max_stars, "HeroStars.Horizontal.TProgressbar")
        update_pb(self.pb_hero_xp, self.prog_hero_xp_val, current_xp, max_xp, "HeroXP.Horizontal.TProgressbar")
        update_pb(self.pb_hero_total_xp, self.prog_hero_total_xp_val, current_actual_xp, max_actual_xp, "HeroTotalXP.Horizontal.TProgressbar")
        update_pb(self.pb_hero_dust, self.prog_hero_dust_val, current_dust, max_dust, "HeroDust.Horizontal.TProgressbar")
        
        update_pb(self.pb_pet_stars, self.prog_pet_stars_val, current_pet_stars, max_pet_stars, "PetStars.Horizontal.TProgressbar")
        update_pb(self.pb_pet_bond, self.prog_pet_bond_val, current_pet_bond, max_pet_bond, "PetBond.Horizontal.TProgressbar")
        update_pb(self.pb_pet_feathers, self.prog_pet_feathers_val, current_pet_feathers, max_pet_feathers_total, "PetFeathers.Horizontal.TProgressbar")
        update_pb(self.pb_pet_time, self.prog_pet_time_val, current_pet_time, max_pet_time_total, "PetTime.Horizontal.TProgressbar", is_time=True)

        update_pb(self.pb_build, self.prog_build_val, current_build_levels, max_build_total, "Build.Horizontal.TProgressbar")
        update_pb(self.pb_equip, self.prog_equip_val, current_equip_levels, max_equip_levels, "Equip.Horizontal.TProgressbar")

        hero_ratio = (current_stars + current_xp) / (max_stars + max_xp) if (max_stars + max_xp) > 0 else 0
        pet_ratio = (current_pet_stars + current_pet_bond) / (max_pet_stars + max_pet_bond) if (max_pet_stars + max_pet_bond) > 0 else 0
        build_ratio = current_build_levels / max_build_total if max_build_total > 0 else 0
        
        total_ratio = (hero_ratio + pet_ratio + build_ratio) / 3
        
        self.pb_total['value'] = total_ratio * 100
        self.prog_total_val.set(f"{(total_ratio * 100):.1f}%")
        self.style.configure("Total.Horizontal.TProgressbar", background=self.get_progress_color(total_ratio, 1.0))

    def update_stats_tab(self):
        c = self.conn.cursor()
        
        c.execute("SELECT name, sterne, xp_level, rarity FROM daten")
        rows = c.fetchall()
        
        count_obtained, total_stars, total_xp_levels, total_xp_amount, total_dust_used, total_dust_needed = 0, 0, 0, 0, 0, 0
        
        for r in rows:
            name, s_str, x_str, rarity = r
            if not rarity: rarity = self.get_rarity(name)
            
            s = 0
            if s_str != '-':
                s = int(s_str)
                if s > 0: count_obtained += 1
                total_stars += s
            
            x = int(x_str) if x_str != '-' else 0
            total_xp_levels += x
            if x > 1:
                total_xp_amount += self.hero_xp_cumulative[min(x - 1, len(self.hero_xp_costs))]
            
            costs_cum = self.dust_costs_cumulative.get(rarity, self.dust_costs_cumulative["Legendary"])
            s_clamped = max(0, min(s, 12))
            total_dust_used += costs_cum[s_clamped]
            total_dust_needed += (costs_cum[-1] - costs_cum[s_clamped])
        
        self.stats_vars["hero_0"].set(f"{count_obtained} / {len(rows)}")
        self.stats_vars["hero_1"].set(f"{total_stars}")
        self.stats_vars["hero_2"].set(f"{total_xp_levels}")
        self.stats_vars["hero_3"].set(f"{total_xp_amount:,}")
        self.stats_vars["hero_4"].set(f"{total_dust_used:,}")
        self.stats_vars["hero_5"].set(f"{total_dust_needed:,}")

        c.execute("SELECT sterne, bond_level FROM pets")
        rows = c.fetchall()
        
        p_obtained, p_stars, p_bond, p_feathers_used, p_feathers_needed, p_time = 0, 0, 0, 0, 0, 0
        
        for r in rows:
            s = int(r[0]) if r[0] != '-' else 0
            if s > 0: p_obtained += 1
            p_stars += s
            
            b = int(r[1]) if r[1] != '-' else 0
            p_bond += b
            if b > 0: p_time += self.pet_bond_time_cumulative[max(0, b - 1)]
            
            s_clamped = max(0, min(s, 12))
            p_feathers_used += self.pet_feather_cumulative[s_clamped]
            p_feathers_needed += (self.pet_feather_cumulative[-1] - self.pet_feather_cumulative[s_clamped])
        
        self.stats_vars["pet_0"].set(f"{p_obtained} / {len(rows)}")
        self.stats_vars["pet_1"].set(f"{p_stars}")
        self.stats_vars["pet_2"].set(f"{p_bond}")
        self.stats_vars["pet_3"].set(f"{p_feathers_used:,}")
        self.stats_vars["pet_4"].set(f"{p_feathers_needed:,}")
        self.stats_vars["pet_5"].set(self.format_seconds(p_time))

        c.execute("SELECT name, level FROM buildings")
        rows = c.fetchall()
        
        b_levels, b_lumber, b_lumber_needed, b_ore, b_ore_needed, b_time = 0, 0, 0, 0, 0, 0
        
        try:
            mul_speed, mul_lumber, mul_ore = float(self.const_speed_var.get())/100, float(self.const_lumber_var.get())/100, float(self.const_ore_var.get())/100
        except:
            mul_speed, mul_lumber, mul_ore = 1.0, 1.0, 1.0
        
        for name, lvl_str in rows:
            lvl = int(lvl_str) if lvl_str != '-' else 0
            b_levels += lvl
            
            costs_list = self.castle_costs if name == "Castle" else (self.ore_mine_costs if "Ore Mine" in name else self.other_building_costs)
            
            for i in range(len(costs_list)):
                cost_val = costs_list[i]
                time, lumber, ore = cost_val[0] * mul_speed, math.ceil(cost_val[1] * mul_lumber), math.ceil(cost_val[2] * mul_ore)
                if i < lvl:
                    b_time += time; b_lumber += lumber; b_ore += ore
                if i >= lvl and i < self.building_max_level:
                    b_lumber_needed += lumber; b_ore_needed += ore
        
        self.stats_vars["build_0"].set(f"{b_levels}"); self.stats_vars["build_1"].set(f"{b_lumber:,}"); self.stats_vars["build_2"].set(f"{b_lumber_needed:,}")
        self.stats_vars["build_3"].set(f"{b_ore:,}"); self.stats_vars["build_4"].set(f"{b_ore_needed:,}"); self.stats_vars["build_5"].set(self.format_seconds(b_time))

        c.execute("SELECT date, total_elixir FROM elixir_data ORDER BY date ASC")
        rows = c.fetchall()
        
        if rows:
            self.stats_vars["elixir_0"].set(f"{float(rows[-1][1]):.2e}")
            self.stats_vars["elixir_1"].set(f"{len(rows)}")
            gains = [(float(rows[i][1]) - float(rows[i-1][1])) / (datetime.strptime(rows[i][0], "%Y-%m-%d") - datetime.strptime(rows[i-1][0], "%Y-%m-%d")).days * 7 for i in range(1, len(rows)) if (datetime.strptime(rows[i][0], "%Y-%m-%d") - datetime.strptime(rows[i-1][0], "%Y-%m-%d")).days > 0]
            self.stats_vars["elixir_2"].set(f"{(sum(gains) / len(gains)):.2e}" if gains else "-")
        else:
            self.stats_vars["elixir_0"].set("-"); self.stats_vars["elixir_1"].set("0"); self.stats_vars["elixir_2"].set("-")

        c.execute("SELECT name, level FROM equipment")
        equip_map = {r[0]: r[1] for r in c.fetchall()}
        e_levels, e_amber_spent, e_amber_needed = 0, 0, 0
        
        for name, levels in self.equipment_data.items():
            lvl = equip_map.get(name, 0)
            e_levels += lvl
            e_amber_spent += sum(l[0] for l in levels[:lvl])
            e_amber_needed += sum(l[0] for l in levels[lvl:])
            
        self.stats_vars["equip_0"].set(f"{e_levels}"); self.stats_vars["equip_1"].set(f"{e_amber_spent:,}"); self.stats_vars["equip_2"].set(f"{e_amber_needed:,}")

    def init_db(self):
        with self.conn:
            c = self.conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS daten (id INTEGER PRIMARY KEY, name TEXT NOT NULL, sterne TEXT, xp_level TEXT, dust_used TEXT, dust_needed TEXT, rarity TEXT, faction TEXT, class TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS pets (id INTEGER PRIMARY KEY, name TEXT NOT NULL, sterne TEXT, bond_level TEXT, feathers_used TEXT, feathers_needed TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS buildings (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, level TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS elixir_data (id INTEGER PRIMARY KEY, date TEXT NOT NULL, total_elixir REAL)")
            c.execute("CREATE TABLE IF NOT EXISTS pulls_scrolls (id INTEGER PRIMARY KEY, name TEXT, stars INTEGER, date TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS pulls_eggs (id INTEGER PRIMARY KEY, name TEXT, stars INTEGER, date TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS equipment (name TEXT PRIMARY KEY, level INTEGER)")
            c.execute("CREATE TABLE IF NOT EXISTS fashion (name TEXT PRIMARY KEY, is_unlocked INTEGER)")

            def add_column(table, column, type, default="'-'"):
                c.execute(f"PRAGMA table_info({table})")
                if column not in [info[1] for info in c.fetchall()]:
                    c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {type} DEFAULT {default}")

            add_column("daten", "dust_used", "TEXT")
            add_column("daten", "dust_needed", "TEXT")
            add_column("daten", "rarity", "TEXT", "NULL")
            add_column("daten", "faction", "TEXT", "NULL")
            add_column("daten", "class", "TEXT", "NULL")
            add_column("pets", "feathers_used", "TEXT")
            add_column("pets", "feathers_needed", "TEXT")

            c.execute("SELECT id, name FROM daten WHERE rarity IS NULL OR faction IS NULL OR class IS NULL")
            for row_id, name in c.fetchall():
                rarity = self.get_rarity(name)
                faction, cls = self.hero_details_map.get(name, ("-", "-"))
                c.execute("UPDATE daten SET rarity = ?, faction = ?, class = ? WHERE id = ?", (rarity, faction, cls, row_id))

            for name in self.hero_names:
                c.execute("SELECT 1 FROM daten WHERE name = ?", (name,))
                if not c.fetchone():
                    rarity = self.get_rarity(name)
                    faction, cls = self.hero_details_map.get(name, ("-", "-"))
                    c.execute("INSERT INTO daten (name, sterne, xp_level, rarity, faction, class) VALUES (?, '-', '-', ?, ?, ?)", (name, rarity, faction, cls))
            for name in self.pet_names:
                c.execute("SELECT 1 FROM pets WHERE name = ?", (name,))
                if not c.fetchone():
                    c.execute("INSERT INTO pets (name, sterne, bond_level) VALUES (?, '-', '-')", (name,))
            c.executemany("INSERT OR IGNORE INTO buildings (name, level) VALUES (?, '-')", 
                          [(n,) for n in ["Castle", "Tavern", "School", "Storage", "Training Grounds", "Saw Mill 1", "Saw Mill 2", "Ore Mine 1", "Ore Mine 2"]])
            c.executemany("INSERT OR IGNORE INTO equipment (name, level) VALUES (?, 0)", [(n,) for n in self.equipment_data])
            
            for item in self.fashion_items:
                c.execute("INSERT OR IGNORE INTO fashion (name, is_unlocked) VALUES (?, ?)", (item, 1 if item == "Default" else 0))

    def load_saved_equipment_levels(self):
        c = self.conn.cursor()
        c.execute("SELECT name, level FROM equipment")
        for name, level in c.fetchall():
            if name in self.equipment_levels:
                self.equipment_levels[name] = level

    def run_query(self, query, parameters=()):
        c = self.conn.cursor()
        result = c.execute(query, parameters)
        self.conn.commit()
        return result

    def get_rarity(self, name):
        if name in self.rare_heroes: return "Rare"
        if name in self.epic_heroes: return "Epic"
        return "Legendary"

    def show_status(self, message, color="black"):
        self.status_label.config(text=message, fg=color)

    def show_pet_status(self, message, color="black"):
        self.pet_status_label.config(text=message, fg=color)

    def show_pulls_status(self, message, color="black"):
        self.pulls_status_label.config(text=message, fg=color)

    def show_build_status(self, message, color="black"):
        self.build_status_label.config(text=message, fg=color)

    def show_settings_status(self, message, color="black"):
        self.settings_status_label.config(text=message, fg=color)

    def show_elixir_status(self, message, color="black"):
        self.elixir_status_label.config(text=message, fg=color)

    def toggle_hide_heroes(self):
        val = '1' if self.hide_heroes_var.get() else '0'
        self.run_query("INSERT OR REPLACE INTO settings (key, value) VALUES ('hide_unobtained_heroes', ?)", (val,))
        self.load_data()

    def toggle_hide_pets(self):
        val = '1' if self.hide_pets_var.get() else '0'
        self.run_query("INSERT OR REPLACE INTO settings (key, value) VALUES ('hide_unobtained_pets', ?)", (val,))
        self.load_pets_data()

    def schedule_load_data(self, event=None):
        if self._hero_search_timer:
            self.root.after_cancel(self._hero_search_timer)
        self._hero_search_timer = self.root.after(250, self.load_data)

    def schedule_load_pets_data(self, event=None):
        if self._pet_search_timer:
            self.root.after_cancel(self._pet_search_timer)
        self._pet_search_timer = self.root.after(250, self.load_pets_data)

    def load_data(self, event=None):
        # Disable column display during bulk update for performance
        self.tree.configure(displaycolumns="")
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        search_text = self.entry_search.get()
        query = "SELECT id, name, sterne, xp_level, rarity, faction, class FROM daten "
        params = []
        if search_text:
            query += "WHERE name LIKE ? "
            params.append('%' + search_text + '%')
        query += "ORDER BY name COLLATE NOCASE ASC"

        c = self.conn.cursor()
        c.execute(query, params)
        rows = c.fetchall()
            
        total_stars, total_xp, grand_total_xp_cost, total_xp_needed, total_dust_used, total_dust_needed = 0, 0, 0, 0, 0, 0
        filter_rarity = self.dust_filter_var.get()

        for row in rows:
            id, name, s_str, xp_str, rarity, faction, class_ = row
            if not rarity: rarity = self.get_rarity(name)
            
            if filter_rarity != "All" and filter_rarity != rarity: continue
            if self.hide_heroes_var.get() and s_str == '-': continue

            s = int(s_str) if s_str != '-' else 0
            xp = int(xp_str) if xp_str != '-' else 0
            
            total_stars += s
            total_xp += xp
            
            current_xp_cost = self.hero_xp_cumulative[min(xp - 1, len(self.hero_xp_costs))] if xp > 1 else 0
            next_xp_cost = f"{self.hero_xp_costs[xp - 1]:,}" if 1 <= xp < 140 else "-"
            
            needed_xp = sum(self.hero_xp_costs[max(0, xp - 1):])
            total_xp_needed += needed_xp
            grand_total_xp_cost += current_xp_cost
            
            costs_cum = self.dust_costs_cumulative.get(rarity, self.dust_costs_cumulative["Legendary"])
            s_clamped = max(0, min(s, 12))
            dust_used_val = costs_cum[s_clamped]
            dust_needed_val = costs_cum[-1] - dust_used_val
            total_dust_used += dust_used_val
            total_dust_needed += dust_needed_val
            
            self.tree.insert("", "end", values=(id, name, faction, class_, s_str, xp_str, f"{dust_used_val:,}", f"{dust_needed_val:,}", f"{current_xp_cost:,}", next_xp_cost))
        
        self.lbl_hero_total_stars.config(text=f"Total Stars: {total_stars}")
        self.lbl_hero_total_xp.config(text=f"Total XP Levels: {total_xp}")
        self.lbl_hero_grand_total_xp.config(text=f"Total XP: {grand_total_xp_cost:,}")
        self.lbl_hero_total_xp_needed.config(text=f"XP Needed: {total_xp_needed:,}")
        self.lbl_dust_total_used.config(text=f"Dust Used: {total_dust_used:,}")
        self.lbl_dust_total_needed.config(text=f"Dust Needed: {total_dust_needed:,}")

        self.tree.configure(displaycolumns=("Name", "Faction", "Class", "Sterne", "Xp level", "Dust Used", "Dust Needed", "Total XP", "Next XP Cost"))

        if self.hero_sort_col:
            self.sort_column(self.hero_sort_col, self.hero_sort_reverse)

    def add_record(self, event=None):
        name = self.entry_name.get().strip().title()
        sterne = self.entry_sterne.get()
        xp = self.entry_xp.get()
        if not name:
            self.show_status("Please enter a Name.", "#ffb74d")
            return
        if name not in self.hero_names:
            self.show_status(f"Hero '{name}' is not in the allowed list.", "#ffb74d")
            return

        try:
            sterne_val = int(sterne) if sterne not in ["", "-"] else "-"
            if isinstance(sterne_val, int) and not (0 <= sterne_val <= 12):
                self.show_status("Stars must be between 0 and 12.", "#ffb74d"); return

            xp_val = int(xp) if xp not in ["", "-"] else "-"
            if isinstance(xp_val, int) and not (1 <= xp_val <= 140):
                self.show_status("XP Level must be between 1 and 140.", "#ffb74d"); return

            c = self.conn.cursor()
            c.execute("SELECT id, sterne, xp_level FROM daten WHERE name = ?", (name,))
            existing = c.fetchone()

            if existing:
                new_sterne = sterne_val if sterne != "" else existing[1]
                new_xp = xp_val if xp != "" else existing[2]
                self.run_query("UPDATE daten SET sterne = ?, xp_level = ? WHERE id = ?", (new_sterne, new_xp, existing[0]))
                msg = "Existing hero updated!"
            else:
                rarity, faction, cls = self.get_rarity(name), *self.hero_details_map.get(name, ("-", "-"))
                self.run_query("INSERT INTO daten (name, sterne, xp_level, rarity, faction, class) VALUES (?, ?, ?, ?, ?, ?)", (name, sterne_val, xp_val, rarity, faction, cls))
                msg = "Record added!"

            self.load_data()
            self.clear_entries()
            self.update_global_data()
            self.show_status(msg, "#66bb6a")
        except ValueError:
            self.show_status("Stars and XP must be numbers.", "#ef5350")

    def select_item(self, event):
        if self.tree.identify("region", event.x, event.y) == "heading": return
        item = self.tree.identify_row(event.y)
        if not item:
            self.tree.selection_remove(self.tree.selection()); self.clear_entries()
            return
            
        data = self.tree.item(item, 'values')
        self.clear_entries(); self.current_id = data[0]
        self.entry_name.insert(0, data[1]); self.entry_sterne.insert(0, data[4]); self.entry_xp.insert(0, data[5])

    def update_record(self):
        if self.current_id is None:
            self.show_status("Please select an entry from the list first.", "#ffb74d"); return

        name, sterne, xp = self.entry_name.get().strip().title(), self.entry_sterne.get(), self.entry_xp.get()
        if name not in self.hero_names:
            self.show_status(f"Hero '{name}' is not in the allowed list.", "#ffb74d"); return

        try:
            sterne_val = int(sterne) if sterne not in ["", "-"] else "-"
            if isinstance(sterne_val, int) and not (0 <= sterne_val <= 12):
                self.show_status("Stars must be between 0 and 12.", "#ffb74d"); return
            xp_val = int(xp) if xp not in ["", "-"] else "-"
            if isinstance(xp_val, int) and not (1 <= xp_val <= 140):
                self.show_status("XP Level must be between 1 and 140.", "#ffb74d"); return

            faction, cls = self.hero_details_map.get(name, ("-", "-"))
            self.run_query("UPDATE daten SET name = ?, sterne = ?, xp_level = ?, faction = ?, class = ? WHERE id = ?", (name, sterne_val, xp_val, faction, cls, self.current_id))
            self.load_data(); self.clear_entries(); self.update_global_data()
            self.show_status("Record updated!", "#66bb6a")
        except ValueError:
             self.show_status("Stars and XP must be numbers.", "#ef5350")

    def ask_delete(self, event=None):
        if self.current_id is None:
            self.show_status("Please select an entry from the list first.", "#ffb74d"); return
        self.normal_btns.pack_forget(); self.confirm_btns.pack()
        self.show_status("Please confirm.", "#ffb74d")
        self.root.bind('<Return>', self.perform_delete)

    def perform_delete(self, event=None):
        self.run_query("DELETE FROM daten WHERE id = ?", (self.current_id,))
        self.load_data(); self.clear_entries(); self.update_global_data()
        self.show_status("Record deleted!", "#66bb6a")

    def cancel_delete(self):
        self.reset_btns(); self.show_status("Deletion cancelled.", self.fg_color)

    def reset_btns(self):
        self.confirm_btns.pack_forget(); self.normal_btns.pack()
        self.root.unbind('<Return>')

    def clear_entries(self):
        self.entry_name.delete(0, tk.END); self.entry_sterne.delete(0, tk.END); self.entry_xp.delete(0, tk.END)
        self.current_id = None; self.reset_btns()

    def clear_hero_fields_action(self):
        self.entry_search.delete(0, tk.END); self.load_data(); self.clear_entries()

    def sort_column(self, col, reverse):
        self.hero_sort_col, self.hero_sort_reverse = col, reverse
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        
        def sort_key(val): 
            if val == "-": return -1
            try: return int(val.replace(',', ''))
            except ValueError: return val.lower()

        l.sort(key=lambda t: sort_key(t[0]), reverse=reverse)

        for index, (val, k) in enumerate(l): self.tree.move(k, '', index)

        headers = {"Name": "Name", "Faction": "Faction", "Class": "Class", "Sterne": "Stars", "Xp level": "XP Level", "Dust Used": "Dust Used", "Dust Needed": "Dust Needed", "Total XP": "Total XP", "Next XP Cost": "Next XP Cost"}
        for c in headers: self.tree.heading(c, text=headers[c]) 
            
        arrow = " ▼" if reverse else " ▲"
        self.tree.heading(col, text=headers[col] + arrow, command=lambda: self.sort_column(col, not reverse))

    def on_background_click(self, event):
        widget = event.widget
        interactive_classes = ['Entry', 'TEntry', 'Button', 'TButton', 'Treeview', 'Scrollbar', 'TScrollbar', 'Text', 'Spinbox']
        
        if widget.winfo_class() in interactive_classes:
            return

        self.root.focus_set()

        if self.tree.selection() or self.current_id is not None:
            self.tree.selection_remove(self.tree.selection())
            self.clear_entries()
        
        if self.tree_pets.selection() or self.pet_current_id is not None:
            self.tree_pets.selection_remove(self.tree_pets.selection())
            self.clear_pet_entries()
            
        if self.tree_scrolls.selection() or self.selected_scroll_id is not None:
            self.tree_scrolls.selection_remove(self.tree_scrolls.selection())
            self.clear_scroll_history_entries()
            
        if self.tree_eggs.selection() or self.selected_egg_id is not None:
            self.tree_eggs.selection_remove(self.tree_eggs.selection())
            self.clear_egg_history_entries()

        if self.tree_elixir.selection():
            self.tree_elixir.selection_remove(self.tree_elixir.selection())

    def load_pets_data(self, event=None):
        self.tree_pets.configure(displaycolumns="")
        for row in self.tree_pets.get_children():
            self.tree_pets.delete(row)
        
        search_text = self.entry_pet_search.get()

        c = self.conn.cursor()
        if search_text:
            c.execute("SELECT id, name, sterne, bond_level, feathers_used, feathers_needed FROM pets WHERE name LIKE ? ORDER BY name COLLATE NOCASE ASC", ('%' + search_text + '%',))
        else:
            c.execute("SELECT id, name, sterne, bond_level, feathers_used, feathers_needed FROM pets ORDER BY name COLLATE NOCASE ASC")
        rows = c.fetchall()
            
        total_stars = 0
        total_bond = 0
        total_feathers_used = 0
        total_feathers_needed = 0
        total_time_spent = 0
        total_time_needed = 0

        for row in rows:
            if row[2] != "-":
                total_stars += int(row[2])
            if row[3] != "-":
                total_bond += int(row[3])
            
            current_stars = 0
            if row[2] != "-":
                try: current_stars = int(row[2])
                except ValueError: current_stars = 0
            
            current_stars = max(0, min(current_stars, 12))
            
            feathers_used_val = self.pet_feather_cumulative[current_stars]
            feathers_needed_val = self.pet_feather_cumulative[-1] - self.pet_feather_cumulative[current_stars]
            
            total_feathers_used += feathers_used_val
            total_feathers_needed += feathers_needed_val
            
            f_used = f"{feathers_used_val:,}"
            f_needed = f"{feathers_needed_val:,}"
            
            current_bond = 0
            if row[3] != "-":
                try: current_bond = int(row[3])
                except ValueError: current_bond = 0
            
            limit_idx = max(0, current_bond - 1)
            time_spent_val = self.pet_bond_time_cumulative[limit_idx]
            time_needed_val = self.pet_bond_time_cumulative[-1] - self.pet_bond_time_cumulative[limit_idx]
            
            total_time_spent += time_spent_val
            total_time_needed += time_needed_val
            
            t_spent = self.format_seconds(time_spent_val)
            t_needed = self.format_seconds(time_needed_val)

            if self.hide_pets_var.get() and row[2] == '-':
                continue
            self.tree_pets.insert("", "end", values=(row[0], row[1], row[2], row[3], f_used, f_needed, t_spent, t_needed))
        
        self.lbl_pet_total_stars.config(text=f"Total Stars: {total_stars}")
        self.lbl_pet_total_bond.config(text=f"Total Bond Level: {total_bond}")
        self.lbl_pet_total_feathers_used.config(text=f"Used: {total_feathers_used:,}")
        self.lbl_pet_total_feathers_needed.config(text=f"Needed: {total_feathers_needed:,}")
        self.lbl_pet_total_time_spent.config(text=f"Time Spent: {self.format_seconds(total_time_spent)}")
        self.lbl_pet_total_time_left.config(text=f"Time Left: {self.format_seconds(total_time_needed)}")

        self.tree_pets.configure(displaycolumns=("Name", "Sterne", "Bond", "Feathers Used", "Feathers Needed", "Time Spent", "Time Left"))

        if self.pet_sort_col:
            self.sort_pet_column(self.pet_sort_col, self.pet_sort_reverse)

    def load_equipment_data(self):
        for widget in self.equip_table_frame.winfo_children():
            widget.destroy()
            
        headers = ["Name", "Boost%", "Level", "Amber Next", "Amber Needed", "Amber Used"]
        for col, text in enumerate(headers):
            lbl = tk.Label(self.equip_table_frame, text=text, font=("Arial", 10, "bold"), bg=self.bg_color, fg=self.fg_color)
            lbl.grid(row=0, column=col, padx=1, pady=5, sticky="nsew")

        row_idx = 1
        for name in self.equipment_data:
            current_level = self.equipment_levels[name]
            
            tk.Label(self.equip_table_frame, text=name, bg=self.entry_bg, fg=self.fg_color, relief="solid", borderwidth=1).grid(row=row_idx, column=0, sticky="nsew")
            lbl_boost = tk.Label(self.equip_table_frame, text="", bg=self.entry_bg, fg=self.fg_color, relief="solid", borderwidth=1)
            lbl_boost.grid(row=row_idx, column=1, sticky="nsew")
            
            frame_level = tk.Frame(self.equip_table_frame, bg=self.entry_bg, relief="solid", borderwidth=1)
            frame_level.grid(row=row_idx, column=2, sticky="nsew")
            
            lbl_level = tk.Label(frame_level, text="", bg=self.entry_bg, fg=self.fg_color, width=5)
            
            btn_minus = tk.Button(frame_level, text="-", font=("Arial", 8, "bold"), width=2, bg=self.btn_bg, fg=self.fg_color, relief="flat")
            btn_plus = tk.Button(frame_level, text="+", font=("Arial", 8, "bold"), width=2, bg=self.btn_bg, fg=self.fg_color, relief="flat")
            
            btn_minus.pack(side="left", fill="y")
            lbl_level.pack(side="left", expand=True, fill="both")
            btn_plus.pack(side="left", fill="y")
            
            lbl_next = tk.Label(self.equip_table_frame, text="", bg=self.entry_bg, fg=self.fg_color, relief="solid", borderwidth=1)
            lbl_next.grid(row=row_idx, column=3, sticky="nsew")
            
            lbl_needed = tk.Label(self.equip_table_frame, text="", bg=self.entry_bg, fg=self.fg_color, relief="solid", borderwidth=1)
            lbl_needed.grid(row=row_idx, column=4, sticky="nsew")
            
            lbl_used = tk.Label(self.equip_table_frame, text="", bg=self.entry_bg, fg=self.fg_color, relief="solid", borderwidth=1)
            lbl_used.grid(row=row_idx, column=5, sticky="nsew")
            
            btn_minus.config(command=lambda n=name, l=lbl_level, b=lbl_boost, nx=lbl_next, nd=lbl_needed, u=lbl_used: self.change_equipment_level(n, -1, l, b, nx, nd, u))
            btn_plus.config(command=lambda n=name, l=lbl_level, b=lbl_boost, nx=lbl_next, nd=lbl_needed, u=lbl_used: self.change_equipment_level(n, 1, l, b, nx, nd, u))
            
            self.update_equipment_row_display(name, current_level, lbl_level, lbl_boost, lbl_next, lbl_needed, lbl_used)
            
            row_idx += 1
            
        tk.Label(self.equip_table_frame, text="Total", font=("Arial", 10, "bold"), bg=self.bg_color, fg=self.fg_color).grid(row=row_idx, column=0, sticky="nsew", pady=(10, 0))
        
        self.lbl_total_amber_needed = tk.Label(self.equip_table_frame, text="0", font=("Arial", 10, "bold"), bg=self.bg_color, fg=self.fg_color)
        self.lbl_total_amber_needed.grid(row=row_idx, column=4, sticky="nsew", pady=(10, 0))
        
        self.lbl_total_amber_used = tk.Label(self.equip_table_frame, text="0", font=("Arial", 10, "bold"), bg=self.bg_color, fg=self.fg_color)
        self.lbl_total_amber_used.grid(row=row_idx, column=5, sticky="nsew", pady=(10, 0))
        
        self.update_equipment_totals()

    def change_equipment_level(self, name, delta, lbl_level, lbl_boost, lbl_next, lbl_needed, lbl_used):
        current_level = self.equipment_levels[name]
        new_level = current_level + delta
        max_level = len(self.equipment_data[name]) - 1
        
        if 0 <= new_level <= max_level:
            self.equipment_levels[name] = new_level
            self.update_equipment_row_display(name, new_level, lbl_level, lbl_boost, lbl_next, lbl_needed, lbl_used)
            self.run_query("UPDATE equipment SET level = ? WHERE name = ?", (new_level, name))
            self.update_equipment_totals()

    def max_all_equipment(self):
        with self.conn:
            c = self.conn.cursor()
            for name in self.equipment_data:
                max_lvl = len(self.equipment_data[name]) - 1
                self.equipment_levels[name] = max_lvl
                c.execute("UPDATE equipment SET level = ? WHERE name = ?", (max_lvl, name))
        self.load_equipment_data()

    def update_equipment_totals(self):
        total_needed = 0
        total_used = 0
        
        for name in self.equipment_data:
            level = self.equipment_levels.get(name, 0)
            levels = self.equipment_data[name]
            
            total_needed += sum(l[0] for l in levels[level:])
            total_used += sum(l[0] for l in levels[:level])
            
        if hasattr(self, 'lbl_total_amber_needed') and self.lbl_total_amber_needed.winfo_exists():
            self.lbl_total_amber_needed.config(text=f"{total_needed:,}")
        if hasattr(self, 'lbl_total_amber_used') and self.lbl_total_amber_used.winfo_exists():
            self.lbl_total_amber_used.config(text=f"{total_used:,}")

    def update_equipment_row_display(self, name, level, lbl_level, lbl_boost, lbl_next, lbl_needed, lbl_used):
        levels = self.equipment_data[name]
        
        boost = levels[level][1]
        lbl_boost.config(text=f"{boost}%")
        
        lbl_level.config(text=str(level))
        
        amber_next = levels[level][0]
        lbl_next.config(text=f"{amber_next:,}")
        
        amber_needed = sum(l[0] for l in levels[level:])
        lbl_needed.config(text=f"{amber_needed:,}")
        
        amber_used = sum(l[0] for l in levels[:level])
        lbl_used.config(text=f"{amber_used:,}")

    def add_pet_record(self, event=None):
        name = self.entry_pet_name.get().strip().title()
        sterne = self.entry_pet_sterne.get()
        bond = self.entry_pet_bond.get()

        if name == "":
            self.show_pet_status("Please enter a Name.", "#ffb74d")
            return

        try:
            if sterne == "" or sterne == "-":
                sterne_val = "-"
            else:
                sterne_val = int(sterne)
                if not (0 <= sterne_val <= 12):
                    self.show_pet_status("Stars must be between 0 and 12.", "#ffb74d")
                    return

            if bond == "" or bond == "-":
                bond_val = "-"
            else:
                bond_val = int(bond)
                if not (1 <= bond_val <= 15):
                    self.show_pet_status("Bond Level must be between 1 and 15.", "#ffb74d")
                    return

            c = self.conn.cursor()
            c.execute("SELECT id, sterne, bond_level FROM pets WHERE name = ?", (name,))
            existing_data = c.fetchone()

            if existing_data:
                existing_id, existing_sterne, existing_bond = existing_data
                new_sterne = existing_sterne if sterne == "" else sterne_val
                new_bond = existing_bond if bond == "" else bond_val

                query = "UPDATE pets SET sterne = ?, bond_level = ? WHERE id = ?"
                self.run_query(query, (new_sterne, new_bond, existing_id))
                msg = "Existing pet updated!"
            else:
                query = "INSERT INTO pets (name, sterne, bond_level, feathers_used, feathers_needed) VALUES (?, ?, ?, '-', '-')"
                self.run_query(query, (name, sterne_val, bond_val))
                msg = "Pet added!"

            self.load_pets_data()
            self.clear_pet_entries()
            self.update_global_data()
            self.show_pet_status(msg, "#66bb6a")
        except ValueError:
            self.show_pet_status("Stars and Bond must be numbers.", "#ef5350")

    def select_pet_item(self, event):
        region = self.tree_pets.identify("region", event.x, event.y)
        if region == "heading":
            return

        item = self.tree_pets.identify_row(event.y)
        if item:
            data = self.tree_pets.item(item, 'values')
            if data:
                self.clear_pet_entries()
                self.pet_current_id = data[0]
                
                self.entry_pet_name.insert(0, data[1])
                self.entry_pet_sterne.insert(0, data[2])
                self.entry_pet_bond.insert(0, data[3])
        else:
            self.tree_pets.selection_remove(self.tree_pets.selection())
            self.clear_pet_entries()

    def update_pet_record(self):
        if self.pet_current_id is None:
            self.show_pet_status("Please select a pet from the list first.", "#ffb74d")
            return

        name = self.entry_pet_name.get().strip().title()
        sterne = self.entry_pet_sterne.get()
        bond = self.entry_pet_bond.get()

        try:
            if sterne == "" or sterne == "-":
                sterne_val = "-"
            else:
                sterne_val = int(sterne)
                if not (0 <= sterne_val <= 12):
                    self.show_pet_status("Stars must be between 0 and 12.", "#ffb74d")
                    return

            if bond == "" or bond == "-":
                bond_val = "-"
            else:
                bond_val = int(bond)
                if not (1 <= bond_val <= 15):
                    self.show_pet_status("Bond Level must be between 1 and 15.", "#ffb74d")
                    return

            query = "UPDATE pets SET name = ?, sterne = ?, bond_level = ? WHERE id = ?"
            self.run_query(query, (name, sterne_val, bond_val, self.pet_current_id))
            self.load_pets_data()
            self.clear_pet_entries()
            self.update_global_data()
            self.show_pet_status("Pet updated!", "#66bb6a")
        except ValueError:
             self.show_pet_status("Stars and Bond must be numbers.", "#ef5350")

    def ask_delete_pet(self, event=None):
        if self.pet_current_id is None:
            self.show_pet_status("Please select a pet from the list first.", "#ffb74d")
            return

        self.pet_normal_btns.pack_forget()
        self.pet_confirm_btns.pack()
        self.show_pet_status("Please confirm.", "#ffb74d")
        self.root.bind('<Return>', self.perform_delete_pet)

    def perform_delete_pet(self, event=None):
        query = "DELETE FROM pets WHERE id = ?"
        self.run_query(query, (self.pet_current_id,))
        self.load_pets_data()
        self.clear_pet_entries()
        self.update_global_data()
        self.show_pet_status("Pet deleted!", "#66bb6a")

    def cancel_delete_pet(self):
        self.pet_confirm_btns.pack_forget()
        self.pet_normal_btns.pack()
        self.root.unbind('<Return>')
        self.show_pet_status("Deletion cancelled.", self.fg_color)

    def clear_pet_entries(self):
        self.entry_pet_name.delete(0, tk.END)
        self.entry_pet_sterne.delete(0, tk.END)
        self.entry_pet_bond.delete(0, tk.END)
        self.pet_current_id = None
        self.pet_confirm_btns.pack_forget()
        self.pet_normal_btns.pack()
        self.root.unbind('<Return>')

    def load_elixir_data(self):
        for row in self.tree_elixir.get_children():
            self.tree_elixir.delete(row)
        
        c = self.conn.cursor()
        c.execute("SELECT id, date, total_elixir FROM elixir_data ORDER BY date ASC")
        rows = c.fetchall()

        if rows:
            last_val = rows[-1][2]
            self.entry_calc_current.delete(0, tk.END)
            self.entry_calc_current.insert(0, "{:.2e}".format(last_val))

        prev_elixir = 0
        prev_date_obj = None
        percentages = []

        for row in rows:
            r_id, r_date, r_elixir = row
            bonus = 0
            daily_bonus = 0
            pct_increase = 0.0
            
            try:
                curr_date_obj = datetime.strptime(r_date, "%Y-%m-%d")
            except ValueError:
                curr_date_obj = None

            if prev_elixir > 0 and prev_date_obj and curr_date_obj:
                bonus = r_elixir - prev_elixir
                days = (curr_date_obj - prev_date_obj).days
                if days <= 0: days = 1 
                daily_bonus = bonus / days
                pct_increase = (bonus / prev_elixir) * 100
            elif prev_elixir > 0:
                 bonus = r_elixir - prev_elixir
                 pct_increase = (bonus / prev_elixir) * 100
            
            if prev_elixir > 0:
                percentages.append(pct_increase)

            fmt_elixir = "{:.2e}".format(r_elixir)
            fmt_bonus = "{:.2e}".format(bonus) if bonus != 0 else "-"
            fmt_daily = "{:.2e}".format(daily_bonus) if daily_bonus != 0 else "-"
            fmt_pct = f"{pct_increase:.2f}%" if pct_increase != 0 else "-"

            display_date = r_date
            if curr_date_obj:
                display_date = curr_date_obj.strftime("%d.%m.%Y")
            self.tree_elixir.insert("", "end", iid=r_id, values=(display_date, fmt_elixir, fmt_bonus, fmt_daily, fmt_pct))
            
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

    def sort_elixir_column(self, col, reverse):
        self.elixir_sort_col = col
        self.elixir_sort_reverse = reverse

        l = [(self.tree_elixir.set(k, col), k) for k in self.tree_elixir.get_children('')]

        def sort_key(val):
            if val == "-": return -float('inf')
            try: return datetime.strptime(val, "%d.%m.%Y").timestamp()
            except ValueError: pass
            
            if val.endswith('%'):
                try: return float(val[:-1])
                except ValueError: pass
            
            try: return float(val)
            except ValueError: pass
            
            return val.lower()

        l.sort(key=lambda t: sort_key(t[0]), reverse=reverse)

        for index, (val, k) in enumerate(l):
            self.tree_elixir.move(k, '', index)
        
        for c in ("Date", "Total Elixir", "Bonus", "Daily Bonus", "%"):
            self.tree_elixir.heading(c, text=c, command=lambda c=c: self.sort_elixir_column(c, False))
        
        arrow = " ▼" if reverse else " ▲"
        self.tree_elixir.heading(col, text=col + arrow, command=lambda: self.sort_elixir_column(col, not reverse))

    def calculate_expected_elixir(self):
        try:
            current_str = self.entry_calc_current.get().strip()
            if not current_str:
                c = self.conn.cursor()
                c.execute("SELECT total_elixir FROM elixir_data ORDER BY date DESC LIMIT 1")
                res = c.fetchone()
                if res:
                    current = float(res[0])
                    self.entry_calc_current.insert(0, "{:.2e}".format(current))
                else:
                    self.lbl_calc_result.config(text="No data available", fg="#ef5350")
                    return
            else:
                current = float(current_str)

            target = float(self.entry_calc_target.get())
            percent_str = self.entry_calc_percent.get().strip()
            if not percent_str:
                percent = self.calculated_avg_growth
                self.entry_calc_percent.insert(0, f"{percent:.2f}")
            else:
                percent = float(percent_str)

            if current <= 0 or target <= 0 or percent <= 0:
                self.lbl_calc_result.config(text="Values must be > 0", fg="#ef5350")
                return
            
            if current >= target:
                self.lbl_calc_result.config(text="Target already reached!", fg="#66bb6a")
                return

            rate = percent / 100.0
            weeks = math.log(target / current) / math.log(1 + rate)
            
            self.lbl_calc_result.config(text=f"Time to reach target: {weeks:.2f} weeks", fg="#66bb6a")
            
        except ValueError:
            self.lbl_calc_result.config(text="Invalid input", fg="#ef5350")

    def add_elixir_record(self, event=None):
        date_str = self.entry_elixir_date.get().strip()
        elixir_str = self.entry_elixir_val.get().strip()

        if not date_str or not elixir_str:
            self.show_elixir_status("Please enter Date and Total Elixir.", "#ffb74d")
            return

        try:
            dt = datetime.strptime(date_str, "%d.%m.%Y")
            iso_date = dt.strftime("%Y-%m-%d")
            elixir_val = float(elixir_str)
            
            c = self.conn.cursor()
            c.execute("SELECT id, total_elixir FROM elixir_data WHERE date = ?", (iso_date,))
            existing = c.fetchone()
            
            if existing:
                existing_id, existing_val = existing
                if messagebox.askyesno("Duplicate Date", f"Date {date_str} already exists (Value: {existing_val}).\nOverwrite with {elixir_val}?"):
                    self.run_query("UPDATE elixir_data SET total_elixir = ? WHERE id = ?", (elixir_val, existing_id))
                    self.show_elixir_status("Datapoint updated.", "#66bb6a")
                    self.entry_elixir_val.delete(0, tk.END)
                    self.load_elixir_data()
                    self.update_stats_tab()
            else:
                self.run_query("INSERT INTO elixir_data (date, total_elixir) VALUES (?, ?)", (iso_date, elixir_val))
                self.entry_elixir_val.delete(0, tk.END)
                self.load_elixir_data()
                self.show_elixir_status("Datapoint added.", "#66bb6a")
                self.update_stats_tab()
        except ValueError:
            self.show_elixir_status("Invalid Date (DD.MM.YYYY) or Number.", "#ef5350")

    def ask_delete_elixir(self, event=None):
        selected = self.tree_elixir.selection()
        if not selected:
            self.show_elixir_status("Select a row to delete.", "#ffb74d")
            return
        
        for item in selected:
            self.run_query("DELETE FROM elixir_data WHERE id = ?", (item,))
        
        self.load_elixir_data()
        self.show_elixir_status("Deleted.", "#66bb6a")
        self.update_stats_tab()

    def import_elixir_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
            
        try:
            count_added = 0
            count_updated = 0
            count_skipped = 0
            action_all = None

            with self.conn:
                c = self.conn.cursor()
                with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    
                    for row in reader:
                        if not row or len(row) < 2:
                            continue
                        
                        date_str = row[0].strip()
                        elixir_str = row[1].strip()
                        
                        if date_str.lower() == "date":
                            continue
                            
                        try:
                            dt = datetime.strptime(date_str, "%d.%m.%Y")
                            iso_date = dt.strftime("%Y-%m-%d")
                            elixir_val = float(elixir_str)
                            
                            c.execute("SELECT id, total_elixir FROM elixir_data WHERE date = ?", (iso_date,))
                            existing = c.fetchone()

                            if existing:
                                existing_id, existing_val = existing
                                action = action_all
                                if action is None:
                                    dlg = ConflictDialog(self.root, date_str, existing_val, elixir_val)
                                    action = dlg.result
                                    if action in ['overwrite_all', 'skip_all']:
                                        action_all = action
                                
                                if action in ['overwrite', 'overwrite_all']:
                                    c.execute("UPDATE elixir_data SET total_elixir = ? WHERE id = ?", (elixir_val, existing_id))
                                    count_updated += 1
                                else:
                                    count_skipped += 1
                            else:
                                c.execute("INSERT INTO elixir_data (date, total_elixir) VALUES (?, ?)", (iso_date, elixir_val))
                                count_added += 1
                        except ValueError:
                            continue
            
            self.load_elixir_data()
            self.update_stats_tab()
            self.show_elixir_status(f"Imported: {count_added} added, {count_updated} updated, {count_skipped} skipped.", "#66bb6a")
        except Exception as e:
            self.show_elixir_status(f"Import failed: {e}", "#ef5350")

    def reset_graph_filter(self):
        self.graph_filter_var.set("All Time")
        self.update_elixir_graph()

    def save_graph_image(self):
        if not MATPLOTLIB_AVAILABLE:
            return
            
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if not file_path:
            return
            
        try:
            self.fig.savefig(file_path, facecolor=self.bg_color)
            self.show_elixir_status(f"Graph saved to {file_path}", "#66bb6a")
        except Exception as e:
            self.show_elixir_status(f"Failed to save graph: {e}", "#ef5350")

    def update_elixir_graph(self):
        if not MATPLOTLIB_AVAILABLE:
            return
            
        c = self.conn.cursor()
        c.execute("SELECT date, total_elixir FROM elixir_data ORDER BY date ASC")
        rows = c.fetchall()
        
        all_dates = []
        all_values = []
        all_gains = []
        
        prev_date = None
        prev_val = None
        
        for r_date, r_val in rows:
            try:
                dt = datetime.strptime(r_date, "%Y-%m-%d")
                all_dates.append(dt)
                all_values.append(r_val)
                
                if prev_date is not None and prev_val is not None:
                    days = (dt - prev_date).days
                    gain = r_val - prev_val
                    if days > 0:
                        daily = gain / days
                        weekly = daily * 7
                        all_gains.append(weekly)
                    else:
                        all_gains.append(0)
                else:
                    all_gains.append(0)
                
                prev_date = dt
                prev_val = r_val
            except ValueError:
                continue
        
        self.graph_dates = []
        self.graph_values = []
        self.graph_weekly_gains = []
        
        start_dt = None
        end_dt = None
        
        filter_option = self.graph_filter_var.get()
        now = datetime.now()
        
        if filter_option == "2025":
            start_dt = datetime(2025, 1, 1)
            end_dt = datetime(2025, 12, 31, 23, 59, 59)
        elif filter_option == "2026":
            start_dt = datetime(2026, 1, 1)
            end_dt = datetime(2026, 12, 31, 23, 59, 59)
        elif filter_option == "Past 3 Months":
            start_dt = now - timedelta(days=90)
        elif filter_option == "Past 6 Months":
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
        
        avg_gain = 0
        total_gain = 0
        if self.graph_values:
            total_gain = self.graph_values[-1] - self.graph_values[0]

        if valid_gains_for_avg:
            avg_gain = sum(valid_gains_for_avg) / len(valid_gains_for_avg)
            self.lbl_avg_gain.config(text=f"Avg Weekly Gain: {avg_gain:.2e} | Total Gained: {total_gain:.2e}")
        else:
            self.lbl_avg_gain.config(text=f"Avg Weekly Gain: - | Total Gained: {total_gain:.2e}")

        self.ax.clear()
        if self.ax2 is not None:
            try: self.ax2.remove()
            except: pass
            self.ax2 = None

        self.sc = None
        self.sc2 = None
        self.annot = None
        self.annot2 = None
        
        if self.graph_dates:
            p1, = self.ax.plot(self.graph_dates, self.graph_values, marker='o', linestyle='-', color=self.accent_green, markersize=4, label="Total Elixir")
            self.sc = self.ax.scatter(self.graph_dates, self.graph_values, s=50, alpha=0)
            lines = [p1]
            
            if self.show_weekly_gain_var.get():
                self.ax2 = self.ax.twinx()
                color_gain = "#b0bec5"
                p2, = self.ax2.plot(self.graph_dates, self.graph_weekly_gains, marker='x', linestyle='--', color=color_gain, markersize=4, label="Weekly Gain")
                self.sc2 = self.ax2.scatter(self.graph_dates, self.graph_weekly_gains, s=50, alpha=0)
                
                self.annot2 = self.ax2.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="#404040", ec=color_gain, alpha=1),
                                color=self.fg_color,
                                arrowprops=dict(arrowstyle="->", color=color_gain),
                                zorder=10)
                self.annot2.set_visible(False)
                
                self.ax2.tick_params(axis='y', colors=color_gain)
                self.ax2.spines['bottom'].set_visible(False)
                self.ax2.spines['top'].set_visible(False)
                self.ax2.spines['left'].set_visible(False)
                self.ax2.spines['right'].set_color(color_gain)
                self.ax2.set_ylabel("Weekly Gain", color=color_gain)
                self.ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"{x:.0e}".replace('+', '')))
                
                lines.append(p2)
            
            if self.show_future_projection_var.get() and avg_gain > 0:
                last_date = self.graph_dates[-1]
                last_val = self.graph_values[-1]
                
                future_dates = [last_date]
                future_values = [last_val]
                
                for i in range(1, 27):
                    future_dates.append(last_date + timedelta(weeks=i))
                    future_values.append(last_val + (avg_gain * i))
                
                p_proj, = self.ax.plot(future_dates, future_values, linestyle=':', color='#ce93d8', label="Projected (6m)")
                lines.append(p_proj)

            self.annot = self.ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="#404040", ec=self.fg_color, alpha=1),
                            color=self.fg_color,
                            arrowprops=dict(arrowstyle="->", color=self.fg_color),
                            zorder=10)
            self.annot.set_visible(False)

            self.ax.grid(True, color='#404040', linestyle='--', linewidth=0.5)
            
            self.ax.set_facecolor(self.bg_color)
            self.ax.tick_params(axis='x', colors=self.fg_color, rotation=45)
            self.ax.tick_params(axis='y', colors=self.fg_color)
            self.ax.spines['bottom'].set_color(self.fg_color)
            self.ax.spines['top'].set_color(self.fg_color)
            self.ax.spines['left'].set_color(self.fg_color)
            
            if self.show_weekly_gain_var.get():
                self.ax.spines['right'].set_visible(False)
            else:
                self.ax.spines['right'].set_visible(True)
                self.ax.spines['right'].set_color(self.fg_color)
            
            self.ax.set_title("Total Elixir & Weekly Gain", color=self.fg_color)
            self.ax.set_xlabel("Date", color=self.fg_color)
            self.ax.set_ylabel("Total Elixir", color=self.fg_color)
            
            labels = [l.get_label() for l in lines]
            self.ax.legend(lines, labels, loc='upper left', facecolor=self.bg_color, edgecolor=self.fg_color, labelcolor=self.fg_color)
            
            self.ax.xaxis.set_major_locator(mdates.MonthLocator())
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            
            self.ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"{x:.0e}".replace('+', '')))
            
            self.fig.autofmt_xdate()
            
        self.canvas.draw()
        self.update_elixir_distribution()

    def on_graph_hover(self, event):
        if not self.sc or not self.annot:
            return
            
        found = False
        
        if event.inaxes in [self.ax, self.ax2]:
            if self.sc2 and self.annot2:
                cont, ind = self.sc2.contains(event)
                if cont:
                    idx = ind["ind"][0]
                    text = f"{self.graph_dates[idx].strftime('%d.%m.%Y')}\nWeekly: {self.graph_weekly_gains[idx]:.2e}"
                    if not self.annot2.get_visible() or self.annot2.get_text() != text:
                        pos = self.sc2.get_offsets()[idx]
                        self.annot2.xy = pos
                        self.annot2.set_text(text)
                        self.annot2.set_visible(True)
                        self.annot.set_visible(False)
                        self.canvas.draw_idle()
                    found = True
            
            if not found and self.sc:
                cont, ind = self.sc.contains(event)
                if cont:
                    idx = ind["ind"][0]
                    text = f"{self.graph_dates[idx].strftime('%d.%m.%Y')}\nTotal: {self.graph_values[idx]:.2e}"
                    if not self.annot.get_visible() or self.annot.get_text() != text:
                        pos = self.sc.get_offsets()[idx]
                        self.annot.xy = pos
                        self.annot.set_text(text)
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

    def update_elixir_distribution(self):
        if not MATPLOTLIB_AVAILABLE:
            return

        c = self.conn.cursor()
        c.execute("SELECT date, total_elixir FROM elixir_data ORDER BY date ASC")
        rows = c.fetchall()

        percentages = []
        prev_val = None
        
        for r_date, r_val in rows:
            try:
                dt = datetime.strptime(r_date, "%Y-%m-%d")
                val = float(r_val)
                
                if prev_val is not None and prev_val > 0:
                    pct = (val - prev_val) / prev_val * 100
                    percentages.append((dt, pct))
                
                prev_val = val
            except ValueError:
                continue
        
        filter_option = self.graph_filter_var.get()
        now = datetime.now()
        start_dt = None
        end_dt = None
        
        if filter_option == "2025":
            start_dt = datetime(2025, 1, 1)
            end_dt = datetime(2025, 12, 31, 23, 59, 59)
        elif filter_option == "2026":
            start_dt = datetime(2026, 1, 1)
            end_dt = datetime(2026, 12, 31, 23, 59, 59)
        elif filter_option == "Past 3 Months":
            start_dt = now - timedelta(days=90)
        elif filter_option == "Past 6 Months":
            start_dt = now - timedelta(days=180)
            
        filtered_pcts = []
        for d, p in percentages:
            if start_dt and d < start_dt: continue
            if end_dt and d > end_dt: continue
            filtered_pcts.append(p)
            
        self.ax_dist.clear()
        self.bp_dict = None
        
        if filtered_pcts:
            avg_val = sum(filtered_pcts) / len(filtered_pcts)
            min_val = min(filtered_pcts)
            max_val = max(filtered_pcts)
            self.lbl_dist_stats.config(text=f"Avg: {avg_val:.2f}%  |  Min: {min_val:.2f}%  |  Max: {max_val:.2f}%")

            self.bp_dict = self.ax_dist.boxplot(filtered_pcts, vert=True, patch_artist=True,
                                 boxprops=dict(facecolor=self.accent_green, color=self.fg_color),
                                 capprops=dict(color=self.fg_color),
                                 whiskerprops=dict(color=self.fg_color),
                                 flierprops=dict(markeredgecolor=self.fg_color),
                                 medianprops=dict(color=self.accent_yellow))
        else:
            self.lbl_dist_stats.config(text="No data")

        self.ax_dist.set_facecolor(self.bg_color)
        self.ax_dist.tick_params(axis='x', colors=self.fg_color)
        self.ax_dist.tick_params(axis='y', colors=self.fg_color)
        self.ax_dist.spines['bottom'].set_color(self.fg_color)
        self.ax_dist.spines['top'].set_color(self.fg_color)
        self.ax_dist.spines['left'].set_color(self.fg_color)
        self.ax_dist.spines['right'].set_color(self.fg_color)
        
        self.ax_dist.set_title("Dist %", color=self.fg_color)
        self.ax_dist.set_ylabel("% Change", color=self.fg_color)
        self.ax_dist.set_xticks([])
        self.ax_dist.yaxis.set_major_formatter(mticker.PercentFormatter())
        self.ax_dist.grid(True, color='#404040', linestyle='--', linewidth=0.5, alpha=0.5)
        
        self.annot_dist = self.ax_dist.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="#404040", ec=self.fg_color, alpha=1),
                        color=self.fg_color,
                        arrowprops=dict(arrowstyle="->", color=self.fg_color),
                        zorder=10)
        self.annot_dist.set_visible(False)

        self.fig.tight_layout()
        self.canvas.draw()

    def on_dist_hover(self, event):
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
                text = f"Outlier: {val:.2f}%"
                if not self.annot_dist.get_visible() or self.annot_dist.get_text() != text:
                    self.annot_dist.xy = (flier.get_xdata()[idx], val)
                    self.annot_dist.set_text(text)
                    self.annot_dist.set_visible(True)
                    self.canvas.draw_idle()
                found = True
                break
        
        if not found:
            for box in self.bp_dict.get('boxes', []):
                cont, _ = box.contains(event)
                if cont:
                    path = box.get_path()
                    extent = path.get_extents()
                    q1 = extent.ymin
                    q3 = extent.ymax
                    medians = self.bp_dict.get('medians', [])
                    median = medians[0].get_ydata()[0] if medians else (q1+q3)/2
                    
                    text = f"Q1: {q1:.2f}%\nMedian: {median:.2f}%\nQ3: {q3:.2f}%"
                    if not self.annot_dist.get_visible() or self.annot_dist.get_text() != text:
                        self.annot_dist.xy = (event.xdata, event.ydata)
                        self.annot_dist.set_text(text)
                        self.annot_dist.set_visible(True)
                        self.canvas.draw_idle()
                    found = True
                    break

        if not found:
            if self.annot_dist.get_visible():
                self.annot_dist.set_visible(False)
                self.canvas.draw_idle()

    def update_annot(self, ind, sc, annot):
        pass 

    def clear_pet_fields_action(self):
        self.entry_pet_search.delete(0, tk.END)
        self.load_pets_data()
        self.clear_pet_entries()

    def sort_pet_column(self, col, reverse):
        self.pet_sort_col = col
        self.pet_sort_reverse = reverse

        l = [(self.tree_pets.set(k, col), k) for k in self.tree_pets.get_children('')]
        
        def sort_key(val):
            if val == "-": return -1
            if col in ["Time Spent", "Time Left"]:
                try:
                    parts = val.split()
                    h = int(parts[0][:-1])
                    m = int(parts[1][:-1])
                    s = int(parts[2][:-1])
                    return h * 3600 + m * 60 + s
                except:
                    return 0
            try: return int(val.replace(',', ''))
            except ValueError: return val.lower()

        l.sort(key=lambda t: sort_key(t[0]), reverse=reverse)

        for index, (val, k) in enumerate(l):
            self.tree_pets.move(k, '', index)

        headers = {"Name": "Name", "Sterne": "Stars", "Bond": "Bond Level", "Feathers Used": "Feathers Used", "Feathers Needed": "Feathers Needed", "Time Spent": "Time Spent", "Time Left": "Time Left"}
        for c in headers:
            self.tree_pets.heading(c, text=headers[c])
            
        arrow = " ▼" if reverse else " ▲"
        self.tree_pets.heading(col, text=headers[col] + arrow, command=lambda: self.sort_pet_column(col, not reverse))

    def update_luck_stats(self):
        c = self.conn.cursor()
        
        c.execute("SELECT AVG(stars), COUNT(*) FROM pulls_scrolls")
        res_scrolls = c.fetchone()
        avg_scrolls = res_scrolls[0] if res_scrolls and res_scrolls[0] is not None else 0.0
        count_scrolls = res_scrolls[1] if res_scrolls else 0

        c.execute("SELECT stars, COUNT(*) FROM pulls_scrolls GROUP BY stars")
        scroll_dist_rows = c.fetchall()
        self.scroll_dist_map = {r[0]: r[1] for r in scroll_dist_rows}
        
        c.execute("SELECT AVG(stars), COUNT(*) FROM pulls_eggs")
        res_eggs = c.fetchone()
        avg_eggs = res_eggs[0] if res_eggs and res_eggs[0] is not None else 0.0
        count_eggs = res_eggs[1] if res_eggs else 0

        c.execute("SELECT stars, COUNT(*) FROM pulls_eggs GROUP BY stars")
        egg_dist_rows = c.fetchall()
        self.egg_dist_map = {r[0]: r[1] for r in egg_dist_rows}
            
        self.lbl_avg_scroll_stars.config(text=f"Average Stars: {avg_scrolls:.2f}")
        self.lbl_total_scrolls.config(text=f"Total Pulled: {count_scrolls}")

        w_score_s = 0
        w_count_s = 0
        for s, c_val in self.scroll_dist_map.items():
            if 1 <= s <= 12:
                chance = self.scroll_star_chances[s-1]
                if chance > 0:
                    w_score_s += c_val * (100.0 / chance)
                    w_count_s += c_val
        
        if w_count_s > 0:
            exp_score = w_count_s * 12
            luck_pct = (w_score_s / exp_score) * 100
            self.lbl_weighted_scroll_luck.config(text=f"Weighted Luck: {luck_pct:.2f}%")
        else:
            self.lbl_weighted_scroll_luck.config(text="Weighted Luck: -")
        
        self.lbl_avg_egg_stars.config(text=f"Average Stars: {avg_eggs:.2f}")
        self.lbl_total_eggs.config(text=f"Total Pulled: {count_eggs}")

        w_score_e = 0
        w_count_e = 0
        for s, c_val in self.egg_dist_map.items():
            if 1 <= s <= 12:
                chance = self.egg_star_chances[s-1]
                if chance > 0:
                    w_score_e += c_val * (100.0 / chance)
                    w_count_e += c_val
        
        if w_count_e > 0:
            exp_score = w_count_e * 12
            luck_pct = (w_score_e / exp_score) * 100
            self.lbl_weighted_egg_luck.config(text=f"Weighted Luck: {luck_pct:.2f}%")
        else:
            self.lbl_weighted_egg_luck.config(text="Weighted Luck: -")

        if MATPLOTLIB_AVAILABLE:
            stars_x = list(range(1, 13))
            
            self.ax_scroll.clear()
            self.ax_scroll.plot(stars_x, self.scroll_star_chances, marker='o', linestyle='--', label='Game Chance', color='gray')
            
            self.user_scroll_probs = [0.0] * 12
            if count_scrolls > 0:
                for s, count in scroll_dist_rows:
                    if 1 <= s <= 12:
                        self.user_scroll_probs[s-1] = (count / count_scrolls) * 100
            
            self.ax_scroll.plot(stars_x, self.user_scroll_probs, marker='o', linestyle='-', label='Your Pulls', color=self.accent_green)
            
            self.sc_scroll = self.ax_scroll.scatter(stars_x, self.user_scroll_probs, s=50, alpha=0)
            self.annot_scroll = self.ax_scroll.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="#404040", ec=self.fg_color, alpha=1),
                            color=self.fg_color,
                            arrowprops=dict(arrowstyle="->", color=self.fg_color),
                            zorder=10)
            self.annot_scroll.set_visible(False)

            self.style_luck_graph(self.ax_scroll, "Scrolls Distribution")
            self.canvas_scroll.draw()

            self.ax_egg.clear()
            self.ax_egg.plot(stars_x, self.egg_star_chances, marker='o', linestyle='--', label='Game Chance', color='gray')
            
            self.user_egg_probs = [0.0] * 12
            if count_eggs > 0:
                for s, count in egg_dist_rows:
                    if 1 <= s <= 12:
                        self.user_egg_probs[s-1] = (count / count_eggs) * 100
            
            self.ax_egg.plot(stars_x, self.user_egg_probs, marker='o', linestyle='-', label='Your Pulls', color=self.accent_yellow)
            
            self.sc_egg = self.ax_egg.scatter(stars_x, self.user_egg_probs, s=50, alpha=0)
            self.annot_egg = self.ax_egg.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="#404040", ec=self.fg_color, alpha=1),
                            color=self.fg_color,
                            arrowprops=dict(arrowstyle="->", color=self.fg_color),
                            zorder=10)
            self.annot_egg.set_visible(False)

            self.style_luck_graph(self.ax_egg, "Eggs Distribution")
            self.canvas_egg.draw()

    def show_scroll_breakdown(self, event):
        if not self.scroll_dist_map:
            return
        
        menu = tk.Menu(self.root, tearoff=0, bg=self.bg_color, fg=self.fg_color, activebackground=self.btn_bg, activeforeground=self.fg_color)
        menu.add_command(label="Scroll Pulls Breakdown", state="disabled")
        menu.add_separator()
        
        for stars in range(1, 13):
            count = self.scroll_dist_map.get(stars, 0)
            if count > 0:
                menu.add_command(label=f"{stars} Stars: {count}")
        
        menu.post(event.x_root, event.y_root)

    def show_egg_breakdown(self, event):
        if not self.egg_dist_map:
            return
        
        menu = tk.Menu(self.root, tearoff=0, bg=self.bg_color, fg=self.fg_color, activebackground=self.btn_bg, activeforeground=self.fg_color)
        menu.add_command(label="Egg Pulls Breakdown", state="disabled")
        menu.add_separator()
        
        for stars in range(1, 13):
            count = self.egg_dist_map.get(stars, 0)
            if count > 0:
                menu.add_command(label=f"{stars} Stars: {count}")
        
        menu.post(event.x_root, event.y_root)

    def style_luck_graph(self, ax, title):
        ax.set_facecolor(self.bg_color)
        ax.tick_params(axis='x', colors=self.fg_color)
        ax.tick_params(axis='y', colors=self.fg_color)
        ax.spines['bottom'].set_color(self.fg_color)
        ax.spines['top'].set_color(self.fg_color)
        ax.spines['left'].set_color(self.fg_color)
        ax.spines['right'].set_color(self.fg_color)
        ax.set_title(title, color=self.fg_color)
        ax.set_xlabel("Stars", color=self.fg_color)
        ax.set_ylabel("% Chance", color=self.fg_color)
        ax.legend(facecolor=self.bg_color, edgecolor=self.fg_color, labelcolor=self.fg_color)
        ax.grid(True, color='#404040', linestyle='--', linewidth=0.5)

    def on_scroll_hover(self, event):
        self.on_luck_hover(event, self.canvas_scroll, self.ax_scroll, self.sc_scroll, self.annot_scroll, self.scroll_star_chances, self.user_scroll_probs)

    def on_egg_hover(self, event):
        self.on_luck_hover(event, self.canvas_egg, self.ax_egg, self.sc_egg, self.annot_egg, self.egg_star_chances, self.user_egg_probs)

    def on_luck_hover(self, event, canvas, ax, sc, annot, game_probs, user_probs):
        if not sc or not annot: return
        found = False
        if event.inaxes == ax:
            cont, ind = sc.contains(event)
            if cont:
                idx = ind["ind"][0]
                pos = sc.get_offsets()[idx]
                
                star_val = idx + 1
                g_prob = game_probs[idx]
                u_prob = user_probs[idx]
                diff = u_prob - g_prob
                
                text = f"Stars: {star_val}\nGame: {g_prob:.2f}%\nYou: {u_prob:.2f}%\nDiff: {diff:+.2f}%"
                
                current_text = annot.get_text()
                is_visible = annot.get_visible()
                
                if not is_visible or current_text != text:
                    annot.xy = pos
                    annot.set_text(text)
                    annot.set_visible(True)
                    canvas.draw_idle()
                found = True
        
        if not found and annot.get_visible():
            annot.set_visible(False)
            canvas.draw_idle()

    def load_pulls_history(self):
        for row in self.tree_scrolls.get_children():
            self.tree_scrolls.delete(row)
        for row in self.tree_eggs.get_children():
            self.tree_eggs.delete(row)
            
        c = self.conn.cursor()
        c.execute("SELECT id, date, name, stars FROM pulls_scrolls ORDER BY id DESC")
        for row in c.fetchall():
            self.tree_scrolls.insert("", "end", iid=row[0], values=(row[1], row[2], row[3]))
        
        c.execute("SELECT id, date, name, stars FROM pulls_eggs ORDER BY id DESC")
        for row in c.fetchall():
            self.tree_eggs.insert("", "end", iid=row[0], values=(row[1], row[2], row[3]))
        
        self.update_luck_stats()
        
        if self.scroll_sort_col:
            self.sort_scroll_column(self.scroll_sort_col, self.scroll_sort_reverse)
        if self.egg_sort_col:
            self.sort_egg_column(self.egg_sort_col, self.egg_sort_reverse)

    def sort_scroll_column(self, col, reverse):
        self.scroll_sort_col = col
        self.scroll_sort_reverse = reverse

        l = [(self.tree_scrolls.set(k, col), k) for k in self.tree_scrolls.get_children('')]
        
        def sort_key(val):
            try: return int(val)
            except ValueError: return val.lower()

        l.sort(key=lambda t: sort_key(t[0]), reverse=reverse)

        for index, (val, k) in enumerate(l):
            self.tree_scrolls.move(k, '', index)

        headers = ["Date", "Name", "Stars"]
        for c in headers:
            self.tree_scrolls.heading(c, text=c, command=lambda c=c: self.sort_scroll_column(c, False))
            
        arrow = " ▼" if reverse else " ▲"
        self.tree_scrolls.heading(col, text=col + arrow, command=lambda: self.sort_scroll_column(col, not reverse))

    def sort_egg_column(self, col, reverse):
        self.egg_sort_col = col
        self.egg_sort_reverse = reverse

        l = [(self.tree_eggs.set(k, col), k) for k in self.tree_eggs.get_children('')]
        
        def sort_key(val):
            try: return int(val)
            except ValueError: return val.lower()

        l.sort(key=lambda t: sort_key(t[0]), reverse=reverse)

        for index, (val, k) in enumerate(l):
            self.tree_eggs.move(k, '', index)

        headers = ["Date", "Name", "Stars"]
        for c in headers:
            self.tree_eggs.heading(c, text=c, command=lambda c=c: self.sort_egg_column(c, False))
            
        arrow = " ▼" if reverse else " ▲"
        self.tree_eggs.heading(col, text=col + arrow, command=lambda: self.sort_egg_column(col, not reverse))

    def select_scroll_item(self, event):
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

    def clear_scroll_history_entries(self):
        self.tree_scrolls.selection_remove(self.tree_scrolls.selection())
        self.selected_scroll_id = None
        self.entry_scroll_hist_date.delete(0, tk.END)
        self.entry_scroll_hist_name.delete(0, tk.END)
        self.entry_scroll_hist_stars.delete(0, tk.END)

    def update_scroll_record(self):
        if not self.selected_scroll_id: return
        d = self.entry_scroll_hist_date.get()
        n = self.entry_scroll_hist_name.get()
        s = self.entry_scroll_hist_stars.get()
        self.run_query("UPDATE pulls_scrolls SET date=?, name=?, stars=? WHERE id=?", (d, n, s, self.selected_scroll_id))
        self.load_pulls_history()
        self.clear_scroll_history_entries()

    def delete_scroll_record(self):
        if not self.selected_scroll_id: return
        if messagebox.askyesno("Confirm", "Delete this record?"):
            self.run_query("DELETE FROM pulls_scrolls WHERE id=?", (self.selected_scroll_id,))
            self.load_pulls_history()
            self.clear_scroll_history_entries()

    def select_egg_item(self, event):
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

    def clear_egg_history_entries(self):
        self.tree_eggs.selection_remove(self.tree_eggs.selection())
        self.selected_egg_id = None
        self.entry_egg_hist_date.delete(0, tk.END)
        self.entry_egg_hist_name.delete(0, tk.END)
        self.entry_egg_hist_stars.delete(0, tk.END)

    def update_egg_record(self):
        if not self.selected_egg_id: return
        d = self.entry_egg_hist_date.get()
        n = self.entry_egg_hist_name.get()
        s = self.entry_egg_hist_stars.get()
        self.run_query("UPDATE pulls_eggs SET date=?, name=?, stars=? WHERE id=?", (d, n, s, self.selected_egg_id))
        self.load_pulls_history()
        self.clear_egg_history_entries()

    def delete_egg_record(self):
        if not self.selected_egg_id: return
        if messagebox.askyesno("Confirm", "Delete this record?"):
            self.run_query("DELETE FROM pulls_eggs WHERE id=?", (self.selected_egg_id,))
            self.load_pulls_history()
            self.clear_egg_history_entries()

    def import_pulls_csv_generic(self, table_name):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path: return
            
        try:
            count_added = 0
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            c = self.conn.cursor()
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if not row: continue
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
                        c.execute(f"INSERT INTO {table_name} (name, stars, date) VALUES (?, ?, ?)", ("", star_val, timestamp))
                        count_added += 1
            self.conn.commit()
            
            self.load_pulls_history()
            self.show_pulls_status(f"Imported {count_added} records into {table_name.replace('pulls_', '')}.", "#66bb6a")
        except Exception as e:
            self.show_pulls_status(f"Import failed: {e}", "#ef5350")

    def import_scrolls_csv(self):
        self.import_pulls_csv_generic("pulls_scrolls")

    def import_eggs_csv(self):
        self.import_pulls_csv_generic("pulls_eggs")

    def process_scroll_pull(self, event=None):
        name = self.entry_scroll_name.get().strip().title()
        sterne = self.entry_scroll_stars.get()

        if sterne == "":
            self.show_pulls_status("Please enter Stars.", "#ffb74d")
            return

        if name and name not in self.hero_names:
            self.show_pulls_status(f"Hero '{name}' is not in the allowed list.", "#ffb74d")
            return

        try:
            if sterne == "-":
                sterne_val = "-"
            else:
                sterne_val = int(sterne)
                if not (0 <= sterne_val <= 12):
                    self.show_pulls_status("Stars must be between 0 and 12.", "#ffb74d")
                    return
            
            msg = "Logged Scroll Pull (Stars only)"
            if name:
                c = self.conn.cursor()
                c.execute("SELECT id, sterne FROM daten WHERE name = ?", (name,))
                existing_data = c.fetchone()

                if existing_data:
                    existing_id, existing_sterne = existing_data
                    current_stars = -1 if existing_sterne == "-" else int(existing_sterne)
                    new_stars = -1 if sterne_val == "-" else int(sterne_val)

                    if new_stars > current_stars:
                        self.run_query("UPDATE daten SET sterne = ? WHERE id = ?", (sterne_val, existing_id))
                        msg = f"Updated Hero: {name}"
                    else:
                        msg = f"Hero {name} not updated (Current: {existing_sterne})"
                else:
                    rarity = self.get_rarity(name)
                    faction, cls = self.hero_details_map.get(name, ("-", "-"))
                    self.run_query("INSERT INTO daten (name, sterne, xp_level, dust_used, dust_needed, rarity, faction, class) VALUES (?, ?, '-', '-', '-', ?, ?, ?)", (name, sterne_val, rarity, faction, cls))
                    msg = f"Added Hero: {name}"

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.run_query("INSERT INTO pulls_scrolls (name, stars, date) VALUES (?, ?, ?)", (name, sterne_val, timestamp))

            self.load_data() 
            self.entry_scroll_name.delete(0, tk.END)
            self.entry_scroll_stars.delete(0, tk.END)
            self.load_pulls_history()
            self.update_global_data()
            self.show_pulls_status(msg, "#66bb6a")

        except ValueError:
            self.show_pulls_status("Stars must be a number.", "#ef5350")

    def process_egg_pull(self, event=None):
        name = self.entry_egg_name.get().strip().title()
        sterne = self.entry_egg_stars.get()

        if sterne == "":
            self.show_pulls_status("Please enter Stars.", "#ffb74d")
            return

        if name and name not in self.pet_names:
            self.show_pulls_status(f"Pet '{name}' is not in the allowed list.", "#ffb74d")
            return

        try:
            if sterne == "-":
                sterne_val = "-"
            else:
                sterne_val = int(sterne)
                if not (0 <= sterne_val <= 12):
                    self.show_pulls_status("Stars must be between 0 and 12.", "#ffb74d")
                    return
            
            msg = "Logged Egg Pull (Stars only)"
            if name:
                c = self.conn.cursor()
                c.execute("SELECT id, sterne FROM pets WHERE name = ?", (name,))
                existing_data = c.fetchone()

                if existing_data:
                    existing_id, existing_sterne = existing_data
                    current_stars = -1 if existing_sterne == "-" else int(existing_sterne)
                    new_stars = -1 if sterne_val == "-" else int(sterne_val)

                    if new_stars > current_stars:
                        self.run_query("UPDATE pets SET sterne = ? WHERE id = ?", (sterne_val, existing_id))
                        msg = f"Updated Pet: {name}"
                    else:
                        msg = f"Pet {name} not updated (Current: {existing_sterne})"
                else:
                    self.run_query("INSERT INTO pets (name, sterne, bond_level, feathers_used, feathers_needed) VALUES (?, ?, '-', '-', '-')", (name, sterne_val))
                    msg = f"Added Pet: {name}"

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.run_query("INSERT INTO pulls_eggs (name, stars, date) VALUES (?, ?, ?)", (name, sterne_val, timestamp))
            self.load_pets_data()
            self.entry_egg_name.delete(0, tk.END)
            self.entry_egg_stars.delete(0, tk.END)
            self.load_pulls_history()
            self.update_global_data()
            self.show_pulls_status(msg, "#66bb6a")

        except ValueError:
            self.show_pulls_status("Stars must be a number.", "#ef5350")

    def format_seconds(self, seconds):
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return f"{h}h {m}m {s}s"

    def save_building_settings(self, event=None):
        vars_map = {
            'const_speed': self.const_speed_var,
            'const_lumber': self.const_lumber_var,
            'const_ore': self.const_ore_var
        }

        for key, var in vars_map.items():
            val = var.get().strip()
            if val == "":
                final_val = "100"
            else:
                try:
                    f_val = float(val)
                    if f_val < 0.1: f_val = 0.1
                    elif f_val > 100: f_val = 100
                    final_val = str(int(f_val)) if f_val.is_integer() else str(f_val)
                except ValueError:
                    final_val = "100"
            
            if val != final_val:
                var.set(final_val)
            
            self.run_query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, final_val))
        
        for name in self.building_entries:
            self.update_building_stats(name)
        self.update_total_spent_summary()
        self.update_total_target_summary()
        self.update_global_data()

    def insert_checklist(self):
        self.txt_notepad.insert("insert", "☐ ")
        self.txt_notepad.focus_set()

    def on_notepad_click(self, event):
        index = self.txt_notepad.index(f"@{event.x},{event.y}")
        char = self.txt_notepad.get(index)
        
        if char == "☐":
            self.txt_notepad.delete(index)
            self.txt_notepad.insert(index, "☑")
            self.schedule_save_notepad()
            return "break"
        elif char == "☑":
            self.txt_notepad.delete(index)
            self.txt_notepad.insert(index, "☐")
            self.schedule_save_notepad()
            return "break"

    def schedule_save_notepad(self, event=None):
        if self.notepad_save_timer:
            self.root.after_cancel(self.notepad_save_timer)
        self.notepad_save_timer = self.root.after(1000, self.save_notepad_content)

    def save_notepad_content(self, event=None):
        content = self.txt_notepad.get("1.0", tk.END)
        self.run_query("INSERT OR REPLACE INTO settings (key, value) VALUES ('notepad_content', ?)", (content,))
        self.lbl_notepad_status.config(text="Saved", fg="#66bb6a")
        if self.notepad_save_timer:
            self.root.after_cancel(self.notepad_save_timer)
            self.notepad_save_timer = None

    def update_building_stats(self, name):
        if name not in self.building_entries:
            return
            
        entry = self.building_entries[name]
        level_str = entry.get().strip()
        
        current_level = 0
        if level_str != "" and level_str != "-":
            try: current_level = int(level_str)
            except ValueError: current_level = 0
        
        target_entry = self.building_target_entries.get(name)
        target_level = 0
        if target_entry:
            t_val = target_entry.get().strip()
            if t_val and t_val != "-":
                try: target_level = int(t_val)
                except ValueError: target_level = 0
        
        try:
            mul_speed = float(self.const_speed_var.get()) / 100.0
            mul_lumber = float(self.const_lumber_var.get()) / 100.0
            mul_ore = float(self.const_ore_var.get()) / 100.0
        except ValueError:
            mul_speed, mul_lumber, mul_ore = 1.0, 1.0, 1.0
            
        costs = []
        if name == "Castle": costs = self.castle_costs
        elif name in ["Ore Mine 1", "Ore Mine 2"]: costs = self.ore_mine_costs
        else: costs = self.other_building_costs
            
        next_time, next_lumber, next_ore = "-", "-", "-"
        if current_level < self.building_max_level and current_level < len(costs):
            c = costs[current_level]
            next_time = self.format_seconds(c[0] * mul_speed)
            next_lumber = f"{math.ceil(c[1] * mul_lumber):,}"
            next_ore = f"{math.ceil(c[2] * mul_ore):,}"
            
        total_time_sec = 0
        total_lumber = 0
        total_ore = 0
        
        for i in range(current_level, self.building_max_level):
            if i < len(costs):
                c = costs[i]
                total_time_sec += c[0] * mul_speed
                total_lumber += math.ceil(c[1] * mul_lumber)
                total_ore += math.ceil(c[2] * mul_ore)
            
        total_time = self.format_seconds(total_time_sec)
        total_lumber_str = f"{total_lumber:,}"
        total_ore_str = f"{total_ore:,}"
        
        target_time_sec = 0
        target_lumber = 0
        target_ore = 0
        
        if target_level > current_level:
            limit = min(target_level, self.building_max_level)
            for i in range(current_level, limit):
                if i < len(costs):
                    c = costs[i]
                    target_time_sec += c[0] * mul_speed
                    target_lumber += math.ceil(c[1] * mul_lumber)
                    target_ore += math.ceil(c[2] * mul_ore)
            
            t_time_str = self.format_seconds(target_time_sec)
            t_lumber_str = f"{target_lumber:,}"
            t_ore_str = f"{target_ore:,}"
        else:
            t_time_str = "-"
            t_lumber_str = "-"
            t_ore_str = "-"
        
        labels = self.building_stats_labels.get(name, {})
        if "time_next" in labels: labels["time_next"].config(text=next_time)
        if "lumber_next" in labels: labels["lumber_next"].config(text=next_lumber)
        if "ore_next" in labels: labels["ore_next"].config(text=next_ore)
        
        if "time_total" in labels: labels["time_total"].config(text=total_time)
        if "lumber_total" in labels: labels["lumber_total"].config(text=total_lumber_str)
        if "ore_total" in labels: labels["ore_total"].config(text=total_ore_str)
        
        if "time_target" in labels: labels["time_target"].config(text=t_time_str)
        if "lumber_target" in labels: labels["lumber_target"].config(text=t_lumber_str)
        if "ore_target" in labels: labels["ore_target"].config(text=t_ore_str)
        self.update_total_target_summary()

    def update_total_spent_summary(self):
        total_time = 0
        total_lumber = 0
        total_ore = 0

        try:
            mul_speed = float(self.const_speed_var.get()) / 100.0
            mul_lumber = float(self.const_lumber_var.get()) / 100.0
            mul_ore = float(self.const_ore_var.get()) / 100.0
        except ValueError:
            mul_speed, mul_lumber, mul_ore = 1.0, 1.0, 1.0

        for name, entry in self.building_entries.items():
            val = entry.get().strip()
            if val == "" or val == "-": continue
            try: level = int(val)
            except ValueError: continue
            
            costs = []
            if name == "Castle": costs = self.castle_costs
            elif name in ["Ore Mine 1", "Ore Mine 2"]: costs = self.ore_mine_costs
            else: costs = self.other_building_costs
            
            for i in range(min(level, len(costs))):
                c = costs[i]
                total_time += c[0] * mul_speed
                total_lumber += math.ceil(c[1] * mul_lumber)
                total_ore += math.ceil(c[2] * mul_ore)

        self.lbl_spent_time.config(text=f"Time: {self.format_seconds(total_time)}")
        self.lbl_spent_lumber.config(text=f"Lumber: {total_lumber:,}")
        self.lbl_spent_ore.config(text=f"Ore: {total_ore:,}")

    def update_total_target_summary(self):
        total_time = 0
        total_lumber = 0
        total_ore = 0

        try:
            mul_speed = float(self.const_speed_var.get()) / 100.0
            mul_lumber = float(self.const_lumber_var.get()) / 100.0
            mul_ore = float(self.const_ore_var.get()) / 100.0
        except ValueError:
            mul_speed, mul_lumber, mul_ore = 1.0, 1.0, 1.0

        for name, entry in self.building_entries.items():
            val = entry.get().strip()
            current_level = 0
            if val != "" and val != "-":
                try: current_level = int(val)
                except ValueError: pass
            
            target_entry = self.building_target_entries.get(name)
            target_level = 0
            if target_entry:
                t_val = target_entry.get().strip()
                if t_val and t_val != "-":
                    try: target_level = int(t_val)
                    except ValueError: pass
            
            if target_level <= current_level: continue

            costs = []
            if name == "Castle": costs = self.castle_costs
            elif name in ["Ore Mine 1", "Ore Mine 2"]: costs = self.ore_mine_costs
            else: costs = self.other_building_costs
            
            limit = min(target_level, self.building_max_level)
            for i in range(current_level, limit):
                if i < len(costs):
                    c = costs[i]
                    total_time += c[0] * mul_speed
                    total_lumber += math.ceil(c[1] * mul_lumber)
                    total_ore += math.ceil(c[2] * mul_ore)

        self.lbl_target_time.config(text=f"Time: {self.format_seconds(total_time)}")
        self.lbl_target_lumber.config(text=f"Lumber: {total_lumber:,}")
        self.lbl_target_ore.config(text=f"Ore: {total_ore:,}")

    def set_all_targets(self, event=None):
        val = self.entry_target_all.get().strip()
        if not val: return
        
        try:
            target_val = int(val)
            if not (0 <= target_val <= self.building_max_level):
                self.show_build_status(f"Target level must be between 0 and {self.building_max_level}.", "#ffb74d")
                return
            
            for name, entry in self.building_target_entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, str(target_val))
                self.update_building_stats(name)
            
            self.update_total_target_summary()
            self.show_build_status(f"All targets set to {target_val}.", "#66bb6a")
            
        except ValueError:
            self.show_build_status("Target level must be a number.", "#ef5350")

    def max_all_buildings(self):
        castle_entry = self.building_entries.get("Castle")
        if not castle_entry: return

        level_str = castle_entry.get().strip()
        if level_str == "" or level_str == "-":
             self.show_build_status("Castle level must be set first.", "#ffb74d")
             return
        
        try:
            level_val = int(level_str)
            self.run_query("UPDATE buildings SET level = ? WHERE name != 'Castle'", (level_val,))

            for name, entry in self.building_entries.items():
                if name != "Castle":
                    entry.delete(0, tk.END)
                    entry.insert(0, str(level_val))
                    self.update_building_stats(name)
            
            self.update_global_data()
            self.update_total_spent_summary()
            self.update_total_target_summary()
            self.show_build_status(f"All buildings updated to Level {level_val}.", "#66bb6a")
        except ValueError:
             self.show_build_status("Invalid Castle level.", "#ef5350")

    def save_building_level(self, name, entry_widget):
        level = entry_widget.get().strip()
        self.show_build_status("", self.fg_color)
        try:
            if level == "" or level == "-":
                level_val = "-"
            else:
                level_val = int(level)
                if not (0 <= level_val <= 14):
                    entry_widget.delete(0, tk.END)
                    self.show_build_status(f"Level must be between 0 and {self.building_max_level}.", "#ffb74d")
                    return 
            
            if name != "Castle" and level_val != "-":
                c = self.conn.cursor()
                c.execute("SELECT level FROM buildings WHERE name = 'Castle'")
                result = c.fetchone()
                castle_level_str = result[0] if result else "-"
                
                castle_level = 0 if castle_level_str == "-" else int(castle_level_str)
                
                if level_val > castle_level:
                    entry_widget.delete(0, tk.END)
                    self.show_build_status(f"Building level cannot exceed Castle level ({castle_level}).", "#ffb74d")
                    return
            
            self.run_query("UPDATE buildings SET level = ? WHERE name = ?", (level_val, name))

            if name == "Castle":
                castle_limit = 0 if level_val == "-" else level_val
                c = self.conn.cursor()
                c.execute("SELECT name, level FROM buildings WHERE name != 'Castle'")
                rows = c.fetchall()
                
                updates_made = False
                for r_name, r_level in rows:
                    current_lvl = 0 if r_level == "-" else int(r_level)
                    if current_lvl > castle_limit:
                        self.run_query("UPDATE buildings SET level = ? WHERE name = ?", (level_val, r_name))
                        if r_name in self.building_entries:
                            self.building_entries[r_name].delete(0, tk.END)
                            self.building_entries[r_name].insert(0, str(level_val))
                            self.update_building_stats(r_name)
                        updates_made = True
                
                if updates_made:
                    self.show_build_status(f"Other buildings reduced to match Castle level ({castle_limit}).", "#ffb74d")

            self.update_building_stats(name)
            self.update_global_data()
            self.update_total_spent_summary()
            self.update_total_target_summary()
        except ValueError:
            pass 

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path: return
        
        try:
            c = self.conn.cursor()
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Type", "Name/Key", "Val1", "Val2", "Val3", "Val4", "Val5"])
                
                c.execute("SELECT name, sterne, xp_level, dust_used, dust_needed, rarity FROM daten")
                for row in c.fetchall():
                    writer.writerow(["HERO", row[0], row[1], row[2], row[3], row[4], row[5]])
                    
                c.execute("SELECT name, sterne, bond_level, feathers_used, feathers_needed FROM pets")
                for row in c.fetchall():
                    writer.writerow(["PET", row[0], row[1], row[2], row[3], row[4], ""])
                    
                c.execute("SELECT name, level FROM buildings")
                for row in c.fetchall():
                    writer.writerow(["BUILDING", row[0], row[1], "", "", "", ""])
                    
                c.execute("SELECT name, level FROM equipment")
                for row in c.fetchall():
                    writer.writerow(["EQUIPMENT", row[0], row[1], "", "", "", ""])
                    
                c.execute("SELECT key, value FROM settings")
                for row in c.fetchall():
                    writer.writerow(["SETTING", row[0], row[1], "", "", "", ""])

                c.execute("SELECT date, total_elixir FROM elixir_data ORDER BY date ASC")
                for row in c.fetchall():
                    writer.writerow(["ELIXIR", row[0], row[1], "", "", "", ""])
            
            self.show_settings_status("Data exported successfully!", "#66bb6a")
        except Exception as e:
            self.show_settings_status(f"Export failed: {e}", "#ef5350")

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path: return
            
        try:
            c = self.conn.cursor()
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None) 
                
                for row in reader:
                    if not row: continue
                    type_ = row[0]
                    
                    if type_ == "HERO":
                        if len(row) >= 7:
                            c.execute("UPDATE daten SET sterne=?, xp_level=?, dust_used=?, dust_needed=?, rarity=? WHERE name=?", 
                                      (row[2], row[3], row[4], row[5], row[6], row[1]))
                    elif type_ == "PET":
                        if len(row) >= 6:
                            c.execute("UPDATE pets SET sterne=?, bond_level=?, feathers_used=?, feathers_needed=? WHERE name=?", 
                                      (row[2], row[3], row[4], row[5], row[1]))
                        elif len(row) >= 4:
                            c.execute("UPDATE pets SET sterne=?, bond_level=? WHERE name=?", 
                                      (row[2], row[3], row[1]))
                    elif type_ == "BUILDING":
                        if len(row) >= 3:
                            c.execute("UPDATE buildings SET level=? WHERE name=?", 
                                      (row[2], row[1]))
                    elif type_ == "EQUIPMENT":
                        if len(row) >= 3:
                            c.execute("UPDATE equipment SET level=? WHERE name=?", 
                                      (row[2], row[1]))
                    elif type_ == "SETTING":
                        if len(row) >= 3:
                            c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", 
                                      (row[1], row[2]))
                    elif type_ == "ELIXIR":
                        if len(row) >= 3:
                            date_val = row[1]
                            elixir_val = row[2]
                            c.execute("SELECT id FROM elixir_data WHERE date = ?", (date_val,))
                            existing = c.fetchone()
                            if existing:
                                c.execute("UPDATE elixir_data SET total_elixir=? WHERE id=?", (elixir_val, existing[0]))
                            else:
                                c.execute("INSERT INTO elixir_data (date, total_elixir) VALUES (?, ?)", (date_val, elixir_val))
            
            self.conn.commit()
            
            self.load_data()
            self.load_pets_data()
            self.update_global_data()
            self.load_elixir_data()
            self.load_saved_equipment_levels()
            self.load_equipment_data()
            
            c.execute("SELECT name, level FROM buildings")
            for r in c.fetchall():
                if r[0] in self.building_entries:
                    self.building_entries[r[0]].delete(0, tk.END)
                    if r[1] != "-":
                        self.building_entries[r[0]].insert(0, r[1])
                    self.update_building_stats(r[0])
            
            self.show_settings_status("Data imported successfully!", "#66bb6a")
        except Exception as e:
            self.show_settings_status(f"Import failed: {e}", "#ef5350")

    def ask_reset_progress(self):
        self.btn_reset.pack_forget()
        self.reset_confirm_frame.pack(side="left", padx=10)
        self.show_settings_status("Waiting for confirmation...", "#ffb74d")

    def cancel_reset(self):
        self.reset_confirm_frame.pack_forget()
        self.btn_reset.pack(side="left", padx=10)
        self.show_settings_status("Reset cancelled.", self.fg_color)

    def perform_reset_progress(self):
        try:
            c = self.conn.cursor()
            c.execute("UPDATE daten SET sterne='-', xp_level='-', dust_used='-', dust_needed='-'")
            c.execute("UPDATE pets SET sterne='-', bond_level='-', feathers_used='-', feathers_needed='-'")
            c.execute("UPDATE buildings SET level='-'")
            c.execute("DELETE FROM elixir_data")
            c.execute("DELETE FROM sqlite_sequence WHERE name='elixir_data'")
            self.conn.commit()
            
            self.load_data()
            self.load_pets_data()
            self.update_global_data()
            self.load_elixir_data()
            
            for name, entry in self.building_entries.items():
                entry.delete(0, tk.END)
                self.update_building_stats(name)
            
            self.cancel_reset()
            self.show_settings_status("All progress has been reset.", "#66bb6a")
        except Exception as e:
            self.show_settings_status(f"Reset failed: {e}", "#ef5350")

if __name__ == "__main__":
    root = tk.Tk()
    app = DatenVerwaltungApp(root)
    root.mainloop()
