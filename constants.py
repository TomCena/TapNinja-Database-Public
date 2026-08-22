"""
Constants and static game data for the TapNinja Database application.
Contains all base scores, cost tables, probabilities, prefix sum calculations,
and Windows 11 Dark Mica design palette tokens.
"""

from typing import Any, Dict, List, Optional, Tuple

# Base Scores for Hero Evaluation in Team Calculator
HERO_BASE_SCORES: Dict[str, float] = {
    "Akira": 4.75, "Alekas": 7.75, "Alivia": 7.50, "Belu": 6.00, "Blazer": 3.67,
    "Demid": 4.67, "Dia": 7.50, "Duncan": 6.00, "Ekho": 8.25, "Elyanna": 4.00,
    "Falkron": 9.50, "Fang": 2.00, "Fin": 9.25, "Hiro": 9.75, "Husk": 7.75,
    "Irbinok": 4.00, "Jari": 2.00, "Jie": 2.00, "Kaoru": 2.33, "Kenju": 3.00,
    "Kito": 10.00, "Locke": 5.67, "Maki": 9.75, "Momo": 5.75, "Ninja": 1.67,
    "Papyrus": 5.67, "Ray": 6.75, "Sayid": 9.25, "Scarlet": 3.00, "Scorn": 7.75,
    "Scythe": 5.00, "Sketchy": 1.00, "Snow": 4.33, "Tateju": 3.00, "Terra": 3.00,
    "Tier": 7.25, "Tomak": 5.67, "Ulrik": 9.00, "Waju": 4.33, "Wasp": 3.67, "Xyzl": 5.33
}

# Hero Registry
HERO_NAMES: List[str] = [
    "Ninja", "Fang", "Jari", "Jie", "Waju", "Tateju", "Kenju", "Sketchy", "Ray", "Kaoru",
    "Belu", "Terra", "Demid", "Momo", "Locke", "Duncan", "Sayid", "Scorn", "Tomak", "Scarlet",
    "Blazer", "Maki", "Hiro", "Akira", "Scythe", "Irbinok", "Husk", "Alivia", "Wasp", "Elyanna",
    "Fin", "Kito", "Tier", "Falkron", "Snow", "Alekas", "Papyrus", "Xyzl", "Ulrik", "Dia", "Ekho"
]

RARE_HEROES: List[str] = ["Ninja", "Fang", "Jari", "Jie", "Waju", "Tateju", "Kenju", "Sketchy"]
EPIC_HEROES: List[str] = ["Ray", "Kaoru", "Belu", "Terra", "Demid", "Momo", "Locke", "Duncan", "Sayid"]

# Hero Faction & Class Mapping
HERO_DETAILS_MAP: Dict[str, Tuple[str, str]] = {
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

# Element Color Mapping (4 Types: Blue, Green, Yellow, Red)
ELEMENT_COLORS: List[str] = ["Blue", "Green", "Yellow", "Red"]
FACTION_TO_COLOR: Dict[str, str] = {
    "Water": "Blue",
    "Wind": "Green",
    "Earth": "Yellow",
    "Fire": "Red"
}
COLOR_TO_FACTION: Dict[str, str] = {v: k for k, v in FACTION_TO_COLOR.items()}
ELEMENT_COLOR_TOKENS: Dict[str, str] = {
    "Blue": "#60cdff",
    "Green": "#6ccb5f",
    "Yellow": "#fce100",
    "Red": "#ff99a4"
}

# Hero Star Dust Upgrade Costs per Rarity
DUST_COSTS: Dict[str, List[int]] = {
    "Legendary": [100, 500, 1000, 2500, 5000, 7500, 10000, 25000, 50000, 100000, 250000, 1000000],
    "Epic": [50, 250, 500, 1250, 2500, 3750, 5000, 12500, 25000, 50000, 125000, 500000],
    "Rare": [25, 125, 250, 625, 1250, 1875, 2500, 6250, 12500, 25000, 62500, 250000]
}

# Hero XP Costs per Level (Levels 1 to 140)
HERO_XP_COSTS: List[int] = [
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

# Pet Registry
PET_NAMES: List[str] = [
    "Frog", "Turtle", "Penguin", "Crab", "Otter", "Bunny", "Mouse/Capybara", "Hedgehog",
    "Snake", "Squirrel", "Chicken/Duck", "Crane", "Raven", "Dragonfly", "Dragonling/Luckdragon",
    "Parrot/Peafowl", "Cat", "Dog/Wolf", "Fox", "Panda", "Racoon"
]

# Pet Categories: Aquatic (Blue), Critter (Green), Bird (Yellow), Beast (Red)
PET_CATEGORIES_MAP: Dict[str, str] = {
    # Aquatic (Blue)
    "Frog": "Blue", "Turtle": "Blue", "Penguin": "Blue", "Crab": "Blue", "Otter": "Blue",
    # Critter (Green)
    "Bunny": "Green", "Mouse/Capybara": "Green", "Hedgehog": "Green", "Snake": "Green", "Squirrel": "Green", "Chicken/Duck": "Green",
    # Bird (Yellow)
    "Crane": "Yellow", "Raven": "Yellow", "Dragonfly": "Yellow", "Dragonling/Luckdragon": "Yellow", "Parrot/Peafowl": "Yellow",
    # Beast (Red)
    "Cat": "Red", "Dog/Wolf": "Red", "Fox": "Red", "Panda": "Red", "Racoon": "Red"
}
PET_ELEMENTS_MAP = PET_CATEGORIES_MAP

PET_FEATHER_COSTS: List[int] = [5, 10, 25, 50, 200, 500, 1000, 2500, 5000, 10000, 25000, 100000]

EGG_STAR_CHANCES: List[float] = [20.0, 24.0, 22.5, 15.0, 9.2, 4.6, 2.8, 1.2, 0.45, 0.18, 0.072, 0.045]
SCROLL_STAR_CHANCES: List[float] = [20.0, 16.0, 12.8, 25.6, 12.8, 6.4, 3.2, 1.9, 0.77, 0.31, 0.124, 0.083]

PET_BOND_TIME_COSTS: List[int] = [
    200, 11520, 46080, 103680, 172800, 270720, 368640, 460800, 604800, 806400, 1152000, 1152000, 1152000, 1152000
]

# Equipment Data: [Amber Cost, Bonus %] for each level
EQUIPMENT_DATA: Dict[str, List[List[float]]] = {
    "Kimono": [[50, 0], [140, 25], [268, 50], [403, 75], [526, 100], [569, 125], [750, 150], [871, 175], [992, 200], [1113, 225], [1234, 250], [1355, 275], [1476, 300], [1598, 325], [1719, 350], [1840, 375], [1961, 400], [2082, 425], [2203, 450], [2324, 475], [2425, 500], [2505, 525], [2565, 550], [2605, 575], [2625, 600], [0, 625]],
    "Katana": [[75, 0], [142, 7.5], [241, 15], [408, 22.5], [536, 30], [664, 37.5], [792, 45], [920, 52.5], [1048, 60], [1176, 67.5], [1304, 75], [1431, 82.5], [1559, 90], [1687, 97.5], [1815, 105], [1943, 112.5], [2071, 120], [2199, 127.5], [2327, 135], [2455, 142.5], [2456, 150], [2457, 157.5], [2458, 165], [2459, 172.5], [2460, 180], [0, 187.5]],
    "Kabuto": [[100, 0], [221, 2.5], [349, 5], [484, 7.5], [607, 10], [727, 12.5], [842, 15], [952, 17.5], [1057, 20], [1158, 22.5], [1259, 25], [1360, 27.5], [1461, 30], [1562, 32.5], [1663, 35], [1764, 37.5], [1865, 40], [1966, 42.5], [2067, 45], [2168, 47.5], [2269, 50], [2370, 52.5], [2471, 55], [2572, 57.5], [2673, 60], [0, 62.5]],
    "Geta": [[50, 0], [100, 15], [175, 30], [250, 45], [330, 60], [410, 75], [490, 90], [570, 105], [650, 120], [735, 135], [820, 150], [905, 165], [990, 180], [1075, 195], [1165, 210], [1255, 225], [1345, 240], [1435, 255], [1525, 270], [1620, 285], [1715, 300], [1810, 315], [1905, 330], [2000, 345], [2095, 360], [0, 375]],
    "Kote": [[200, 0], [220, 0.4], [378, 0.8], [559, 1.2], [678, 1.6], [814, 2], [997, 2.4], [1154, 2.8], [1250, 3.2], [1437, 3.6], [1614, 4], [1767, 4.4], [1882, 4.8], [2072, 5.2], [2253, 5.6], [2418, 6], [2560, 6.4], [2782, 6.8], [2754, 7.2], [2779, 7.6], [3057, 8], [3026, 8.4], [3126, 8.8], [3267, 9.2], [3420, 9.6], [0, 10]],
    "Yubiwa": [[500, 0], [625, 4], [750, 8], [875, 12], [1000, 16], [1125, 20], [1250, 24], [1375, 28], [1500, 32], [1625, 36], [1750, 40], [1875, 44], [2000, 48], [2125, 52], [2250, 56], [2375, 60], [2500, 64], [2625, 68], [2750, 72], [2875, 76], [3000, 80], [3125, 84], [3250, 88], [3375, 92], [3500, 96], [0, 100]],
    "Menpo": [[250, 0], [300, 0.4], [400, 0.8], [500, 1.2], [600, 1.6], [800, 2], [1000, 2.4], [1100, 2.8], [1250, 3.2], [1500, 3.6], [1600, 4], [1750, 4.4], [1900, 4.8], [2000, 5.2], [2250, 5.6], [2400, 6], [2500, 6.4], [2600, 6.8], [2750, 7.2], [2800, 7.6], [2900, 8], [3000, 8.4], [3100, 8.8], [3250, 9.2], [3500, 9.6], [0, 10]]
}

# Conquest (Buildings) Configuration
BUILDINGS_LIST: List[str] = [
    "Castle", "Tavern", "School", "Storage", "Training Grounds",
    "Saw Mill 1", "Saw Mill 2", "Ore Mine 1", "Ore Mine 2"
]
BUILDING_MAX_LEVEL: int = 14

# Castle Costs: (Time in seconds, Lumber, Ore) per Level
CASTLE_COSTS: List[Tuple[int, int, int]] = [
    (4, 200, 500), (300, 4000, 2000), (7200, 10000, 5000), (86400, 24000, 12000),
    (172800, 57600, 28800), (260000, 105000, 52500), (300000, 160000, 80000),
    (370000, 225000, 112500), (440000, 300000, 150000), (520000, 437500, 218750),
    (656000, 630000, 315000), (820000, 880000, 440000), (1020000, 1200000, 600000),
    (1270000, 1600000, 800000), (1550000, 2200000, 1100000)
]

# Other Buildings Costs: (Time in seconds, Lumber, Ore)
OTHER_BUILDING_COSTS: List[Tuple[int, int, int]] = [
    (2, 100, 250), (150, 2000, 1000), (3600, 5000, 2500), (43200, 12000, 6000),
    (86400, 28800, 14400), (130000, 52500, 26250), (150000, 80000, 40000),
    (185000, 112500, 56250), (220000, 150000, 75000), (260000, 218750, 109375),
    (328000, 315000, 157500), (410000, 440000, 220000), (510000, 600000, 300000),
    (635000, 800000, 400000), (775000, 1100000, 550000)
]

# Ore Mine Costs: (Time in seconds, Lumber, 0)
ORE_MINE_COSTS: List[Tuple[int, int, int]] = [(t, l, 0) for t, l, o in OTHER_BUILDING_COSTS]


def get_prefix_sums(lst: List[int]) -> List[int]:
    """Calculates prefix sums for efficient O(1) range summation."""
    sums = [0]
    curr = 0
    for x in lst:
        curr += x
        sums.append(curr)
    return sums


# Precomputed Cumulative Sums for O(1) Cost Lookups
HERO_XP_CUMULATIVE: List[int] = get_prefix_sums(HERO_XP_COSTS)
PET_FEATHER_CUMULATIVE: List[int] = get_prefix_sums(PET_FEATHER_COSTS)
PET_BOND_TIME_CUMULATIVE: List[int] = get_prefix_sums(PET_BOND_TIME_COSTS)
DUST_COSTS_CUMULATIVE: Dict[str, List[int]] = {k: get_prefix_sums(v) for k, v in DUST_COSTS.items()}

# Fashion System Items and Colors
FASHION_ITEMS: List[str] = [
    "Default", "Ruby Red", "Bamboo", "Lapis Lazuli", "Iris", "Amber", "Lime",
    "Navy Blue", "Magenta", "Citrine", "Moss Green", "Opal", "Chestnut",
    "Bellflower", "Jasmine", "Crimson", "Pear", "Granite", "Charcoal",
    "Bronze", "Sage", "Peach", "Azure", "Lavender", "Amethyst", "Orchid",
    "Sandy Brown", "Apple Green", "Sapphire", "Night Black"
]

FASHION_COLORS: Dict[str, str] = {
    "Ruby Red": "#9B111E", "Bamboo": "#006442", "Lapis Lazuli": "#26619C", "Iris": "#5D3FD3",
    "Amber": "#FF7E00", "Lime": "#00FF00", "Navy Blue": "#000080", "Magenta": "#FF1DCE",
    "Citrine": "#E4D00A", "Moss Green": "#4A5D23", "Opal": "#A8C3BC", "Chestnut": "#954535",
    "Bellflower": "#5D3F6A", "Jasmine": "#F8DE7E", "Crimson": "#DC143C", "Pear": "#D1E231",
    "Granite": "#676767", "Charcoal": "#36454F", "Bronze": "#CD7F32", "Sage": "#BCB88A",
    "Peach": "#F47983", "Azure": "#007FFF", "Lavender": "#B57EDC", "Amethyst": "#9966CC",
    "Orchid": "#DA70D6", "Sandy Brown": "#F4A460", "Apple Green": "#8DB600", "Sapphire": "#082567",
    "Night Black": "#292C36"
}

# Seasonal Resources
SEASONAL_RESOURCES: List[str] = sorted([
    "Gold", "Elixir", "Buildings", "Research", "Coins", "Eggs",
    "Rare Scrolls", "Epic Scrolls", "Towns Conquered", "Amber", "Dust", "Feathers"
])

# Windows 11 Dark Mica Aesthetic Design Palette Tokens
DEFAULT_THEME: Dict[str, str] = {
    "bg_color": "#202020",       # Mica Base Window Background
    "fg_color": "#ffffff",       # Primary Foreground Text
    "entry_bg": "#2b2b2b",       # Card / Section Container Background
    "input_bg": "#1f1f1f",       # Input Entries / Fields Background
    "btn_bg": "#323232",         # Standard Button Background
    "accent_blue": "#60cdff",    # Windows 11 Accent Blue (Primary)
    "accent_blue_dark": "#0078d4", # Windows 11 Deep Accent Blue
    "accent_green": "#6ccb5f",   # Windows 11 Fluent Success Green
    "accent_yellow": "#fce100",  # Windows 11 Warning / Amber Gold
    "accent_red": "#ff99a4",     # Windows 11 Danger / Soft Red
    "accent_purple": "#c29bfa",  # Windows 11 Fluent Purple Accent
    "border_color": "#3a3a3a",   # Subtle Surface 1px Outline Border
    "border_focus": "#60cdff",   # Active Focus Highlight Border
    "text_dim": "#9d9d9d"        # Secondary Subdued Text
}


def format_seconds(seconds: float | int) -> str:
    """Formats a duration in seconds into a human-readable 'Xh Ym Zs' string."""
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {s}s"


def parse_resource_value(val_str: str) -> float:
    """Parses arbitrary string values (e.g. '1.5M', '10,000', '1.21e50', '250k', '-') into floats."""
    if not val_str or str(val_str).strip() in ['-', '', 'none', 'null']:
        return 0.0
    s = str(val_str).strip().replace(',', '').lower()
    try:
        return float(s)
    except ValueError:
        pass

    multipliers = {
        'k': 1e3, 'm': 1e6, 'b': 1e9, 't': 1e12,
        'qa': 1e15, 'qi': 1e18, 'sx': 1e21, 'sp': 1e24, 'oc': 1e27, 'no': 1e30, 'dc': 1e33
    }
    for suffix, mult in sorted(multipliers.items(), key=lambda x: len(x[0]), reverse=True):
        if s.endswith(suffix):
            try:
                return float(s[:-len(suffix)]) * mult
            except ValueError:
                pass

    try:
        import re
        digits = re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?', s)
        if digits:
            return float(digits[0])
    except (ValueError, IndexError):
        pass
    return 0.0


def format_resource_value(val: float | int) -> str:
    """Formats numbers nicely, automatically converting very large numbers to scientific notation."""
    try:
        f_val = float(val)
    except (ValueError, TypeError):
        return str(val)

    abs_val = abs(f_val)
    if abs_val >= 1e15:
        return f"{f_val:.2e}"
    if abs_val >= 1e12:
        return f"{f_val / 1e12:.2f}T"
    if abs_val >= 1e9:
        return f"{f_val / 1e9:.2f}B"
    if abs_val >= 1e6:
        return f"{f_val / 1e6:.2f}M"
    if abs_val >= 1e3:
        return f"{f_val / 1e3:.2f}K"
    if f_val == int(f_val):
        return f"{int(f_val):,}"
    return f"{f_val:,.2f}"


# ==========================================
# MISC REFERENCE CONSTANTS & FORMULAS
# ==========================================

FIREFLY_CHANCES: Dict[str, float] = {
    "Regular Coins": 0.638562,
    "gps Increase": 0.131467,
    "Gemstone Fever": 0.052397,
    "Samurai Frenzy": 0.039973,
    "BIG Coins": 0.015567,
    "Firefly Storm": 0.012103,
    "Firefly Swarm": 0.010421,
    "MEGA Coins": 0.010384
}

DYE_DROP_RATE = 1 / 45000  # 0.00222%

ENEMY_COIN_DROPS: Dict[str, int] = {
    "Samurai": 53,
    "Hellhound": 51,
    "Spearmen": 54,
    "Shieldbearer": 59
}

GEM_DROP_CHANCES: Dict[str, float] = {
    "Coins": 0.839,
    "Emerald": 0.100,
    "Sapphire": 0.050,
    "Ruby": 0.010,
    "Diamond": 0.001
}

OFFLINE_BAG_OF_GOODS: Dict[str, Dict[str, float]] = {
    "+": {"amber_price": 200, "offline_hours": 1.0, "price_per_hour": 200.0},
    "++": {"amber_price": 600, "offline_hours": 6.5, "price_per_hour": 92.31},
    "+++": {"amber_price": 1400, "offline_hours": 33.0, "price_per_hour": 42.42}
}

SECRET_ACHIEVEMENTS: List[Dict[str, Any]] = [
    {"id": 1, "name": "Eye see you", "hint": "Gaze upon the six eyes", "solution": "Click every eye in the game until it moves."},
    {"id": 2, "name": "What goes up", "hint": "Must come down", "solution": "Scroll from top to bottom in every tab."},
    {"id": 3, "name": "Scared to Death", "hint": "This is nuts", "solution": "Spam click the squirrel in the pets tab."},
    {"id": 4, "name": "Let's enhance", "hint": "and see all of the details", "solution": "Zoom into the conquest map from being zoomed out all the way."},
    {"id": 5, "name": "Slow and steady", "hint": "Where is the rush?", "solution": "Play a conquest match at 0.5x speed."},
    {"id": 6, "name": "Master tapper", "hint": "Tap the ninja 100,000 times", "solution": "Click the ninja 100,000 times."},
    {"id": 7, "name": "You would not believe your eyes", "hint": "Calm the storm without any help", "solution": "Defeat a firefly storm without any help only by tapping."},
    {"id": 8, "name": "Yarr", "hint": "Shiver me timbers", "solution": "Use shuriken vortex while using Locke during the Pirate event."}
]

PROMO_CODES: List[Dict[str, str]] = [
    {"code": "tapninja", "source": "_zarach"},
    {"code": "panda", "source": "vitas_9501"},
    {"code": "idleslayer", "source": "wawaga"},
    {"code": "kg/molly", "source": "wawaga"},
    {"code": "laser", "source": "wawaga"},
    {"code": "ghostmokomo", "source": "qweasd#2330"},
    {"code": "amk", "source": "diabolik97"},
    {"code": "armyveterangamer", "source": "zztopgun"},
    {"code": "freeamber", "source": "zztopgun"},
    {"code": "insane", "source": "i.eatchildren"},
    {"code": "savethechildren", "source": "qweasd#2330"},
    {"code": "giveamber", "source": "unistragin"},
    {"code": "bestgame", "source": "i.eatchildren"},
    {"code": "opensesame", "source": "TheVolid"},
    {"code": "420", "source": "Community"},
    {"code": "nevergonnagiveyouup", "source": "Rickroll"},
    {"code": "nevergonnaletyoudown", "source": "Rickroll"},
    {"code": "dangerouslyfunny", "source": "i.eatchildren"},
    {"code": "imcade", "source": "Cade"}
]

CHEST_TIER_CHANCES: Dict[str, float] = {
    "Rare": 0.296,
    "Epic": 0.629,
    "Legendary": 0.069,
    "Mythic": 0.006
}

CHEST_TIER_REWARDS: Dict[str, Dict[str, float]] = {
    "Rare": {
        "gold": 0.0, "elixir": 59_700_000_000, "medals": 6, "amber": 15,
        "eggs": 2, "keys": 2, "rare_scrolls": 2, "epic_scrolls": 2
    },
    "Epic": {
        "gold": 0.0, "elixir": 79_600_000_000, "medals": 8, "amber": 25,
        "eggs": 3, "keys": 2, "rare_scrolls": 3, "epic_scrolls": 2
    },
    "Legendary": {
        "gold": 0.0, "elixir": 111_000_000_000, "medals": 12, "amber": 75,
        "eggs": 4, "keys": 3, "rare_scrolls": 4, "epic_scrolls": 3
    },
    "Mythic": {
        "gold": 0.0, "elixir": 298_000_000_000, "medals": 50, "amber": 250,
        "eggs": 10, "keys": 15, "rare_scrolls": 10, "epic_scrolls": 10
    }
}


def get_water_element_cost(level: int) -> int:
    """
    Calculates exact Water Element cost for any arbitrary level (unbounded, no max cap).
    Increases by 10x every 4 levels with base multipliers [1.0, 2.5, 5.0, 7.5].
    """
    if level < 1:
        return 0
    k = (level - 1) // 4
    rem = (level - 1) % 4
    base_mult = [1.0, 2.5, 5.0, 7.5][rem]
    return int(round(base_mult * (10 ** (k + 5))))


def get_water_element_range_cost(from_level: int, to_level: int) -> int:
    """Calculates total cumulative Water Element cost between any two levels."""
    if to_level <= from_level or from_level < 0:
        return 0
    return sum(get_water_element_cost(lvl) for lvl in range(from_level + 1, to_level + 1))


def calculate_expected_chest_rewards(
    chests_per_day: float,
    days: float,
    tier_chances: Optional[Dict[str, float]] = None,
    custom_tier_rewards: Optional[Dict[str, Dict[str, float]]] = None
) -> Dict[str, Any]:
    """Calculates expected chest drop counts and total cumulative resource yields per rarity tier and combined."""
    chances = tier_chances if tier_chances is not None else CHEST_TIER_CHANCES
    total_chests = chests_per_day * days
    tier_counts = {tier: total_chests * chances.get(tier, 0.0) for tier in ["Rare", "Epic", "Legendary", "Mythic"]}

    rewards_map = custom_tier_rewards if custom_tier_rewards is not None else CHEST_TIER_REWARDS

    per_tier_yields: Dict[str, Dict[str, float]] = {}
    for tier in ["Rare", "Epic", "Legendary", "Mythic"]:
        c_count = tier_counts.get(tier, 0.0)
        t_rew = rewards_map.get(tier, CHEST_TIER_REWARDS.get(tier, {}))
        per_tier_yields[tier] = {
            "chests": c_count,
            "gold": c_count * t_rew.get("gold", 0.0),
            "elixir": c_count * t_rew.get("elixir", 0.0),
            "medals": c_count * t_rew.get("medals", 0.0),
            "amber": c_count * t_rew.get("amber", 0.0),
            "eggs": c_count * t_rew.get("eggs", 0.0),
            "keys": c_count * t_rew.get("keys", 0.0),
            "rare_scrolls": c_count * t_rew.get("rare_scrolls", 0.0),
            "epic_scrolls": c_count * t_rew.get("epic_scrolls", 0.0),
        }

    total_rewards: Dict[str, Any] = {
        "total_chests": total_chests,
        "rare_chests": tier_counts.get("Rare", 0.0),
        "epic_chests": tier_counts.get("Epic", 0.0),
        "legendary_chests": tier_counts.get("Legendary", 0.0),
        "mythic_chests": tier_counts.get("Mythic", 0.0),
        "gold": sum(per_tier_yields[t]["gold"] for t in per_tier_yields),
        "elixir": sum(per_tier_yields[t]["elixir"] for t in per_tier_yields),
        "medals": sum(per_tier_yields[t]["medals"] for t in per_tier_yields),
        "amber": sum(per_tier_yields[t]["amber"] for t in per_tier_yields),
        "eggs": sum(per_tier_yields[t]["eggs"] for t in per_tier_yields),
        "keys": sum(per_tier_yields[t]["keys"] for t in per_tier_yields),
        "rare_scrolls": sum(per_tier_yields[t]["rare_scrolls"] for t in per_tier_yields),
        "epic_scrolls": sum(per_tier_yields[t]["epic_scrolls"] for t in per_tier_yields),
        "per_tier": per_tier_yields
    }

    return total_rewards


def calculate_xp_time(stored_xp: float, goal_xp: float, tg_rate_hr: float, away_rate_hr: float) -> Dict[str, float]:
    """Calculates hours, days, and years remaining to reach target XP based on Training Grounds + Away rates."""
    net_xp = max(0.0, goal_xp - stored_xp)
    combined_rate = tg_rate_hr + away_rate_hr

    hours_both = (net_xp / combined_rate) if combined_rate > 0 else 0.0
    hours_tg_only = (net_xp / tg_rate_hr) if tg_rate_hr > 0 else 0.0
    hours_away_only = (net_xp / away_rate_hr) if away_rate_hr > 0 else 0.0

    return {
        "net_xp": net_xp,
        "hours_both": hours_both,
        "days_both": hours_both / 24.0,
        "years_both": (hours_both / 24.0) / 365.0,
        "days_tg_only": hours_tg_only / 24.0,
        "days_away_only": hours_away_only / 24.0
    }


def calculate_pulls_pacing(total_opened: int, days_elapsed: float, milestone_target: int) -> Dict[str, float]:
    """Calculates pulls per day/week/year and remaining time to milestone achievements."""
    if days_elapsed <= 0:
        days_elapsed = 1.0

    per_day = total_opened / days_elapsed
    per_week = per_day * 7.0
    per_year = per_day * 365.0

    pulls_left = max(0, milestone_target - total_opened)
    days_to_goal = (pulls_left / per_day) if per_day > 0 else 0.0

    return {
        "per_day": per_day,
        "per_week": per_week,
        "per_year": per_year,
        "pulls_left": float(pulls_left),
        "days_to_goal": days_to_goal,
        "weeks_to_goal": days_to_goal / 7.0,
        "years_to_goal": days_to_goal / 365.0
    }


def calculate_conquest_upgrade_time(
    target_lumber_cost: int,
    stored_lumber: int,
    sawmill_total_rate_hr: float,
    target_ore_cost: int,
    stored_ore: int,
    oremine_total_rate_hr: float,
    current_upgrade_hours_left: float = 0.0
) -> Dict[str, float]:
    """Calculates net lumber/ore needed and time to afford next building upgrade."""
    net_lumber = max(0, target_lumber_cost - stored_lumber)
    hours_lumber = (net_lumber / sawmill_total_rate_hr if sawmill_total_rate_hr > 0 else 0.0) + current_upgrade_hours_left

    net_ore = max(0, target_ore_cost - stored_ore)
    hours_ore = (net_ore / oremine_total_rate_hr if oremine_total_rate_hr > 0 else 0.0) + current_upgrade_hours_left

    max_hours = max(hours_lumber, hours_ore)

    return {
        "net_lumber": float(net_lumber),
        "hours_lumber": hours_lumber,
        "days_lumber": hours_lumber / 24.0,
        "net_ore": float(net_ore),
        "hours_ore": hours_ore,
        "days_ore": hours_ore / 24.0,
        "max_hours": max_hours,
        "max_days": max_hours / 24.0
    }
