# game_engine.py - Tap Ninja Mathematical Logic & Calculation Engine

import math

# ==========================================
# 1. UNBOUNDED WATER ELEMENT SCALING
# ==========================================
def get_water_element_cost(level: int) -> int:
    """
    Calculates exact Water Element cost for any arbitrary level (no max cap).
    The cost increases by 10x every 4 levels with base offsets [1.0, 2.5, 5.0, 7.5].
    """
    if level < 1:
        return 0
    k = (level - 1) // 4
    rem = (level - 1) % 4
    base_mult = [1.0, 2.5, 5.0, 7.5][rem]
    return int(round(base_mult * (10 ** (k + 5))))

def get_water_element_range_cost(from_level: int, to_level: int) -> int:
    """
    Calculates total cumulative Water Element cost between any two levels.
    """
    if to_level <= from_level or from_level < 0:
        return 0
    return sum(get_water_element_cost(lvl) for lvl in range(from_level + 1, to_level + 1))

# ==========================================
# 2. CHEST SIMULATOR & EXPECTED REWARDS
# ==========================================
CHEST_TIER_CHANCES = {
    "Rare": 0.296,
    "Epic": 0.629,
    "Legendary": 0.069,
    "Mythic": 0.006
}

# Base rewards per single chest of each tier
CHEST_TIER_REWARDS = {
    "Rare": {
        "elixir": 59_700_000_000, "medals": 6, "amber": 15,
        "eggs": 2, "keys": 2, "rare_scrolls": 2, "epic_scrolls": 2
    },
    "Epic": {
        "elixir": 79_600_000_000, "medals": 8, "amber": 25,
        "eggs": 3, "keys": 2, "rare_scrolls": 3, "epic_scrolls": 2
    },
    "Legendary": {
        "elixir": 111_000_000_000, "medals": 12, "amber": 75,
        "eggs": 4, "keys": 3, "rare_scrolls": 4, "epic_scrolls": 3
    },
    "Mythic": {
        "elixir": 298_000_000_000, "medals": 50, "amber": 250,
        "eggs": 10, "keys": 15, "rare_scrolls": 10, "epic_scrolls": 10
    }
}

def calculate_expected_chest_rewards(chests_per_day: float, days: float) -> dict:
    """
    Excel Formulas from 'Chests' sheet:
        Total Chests = chests_per_day * days
        Tier Chests = Total Chests * Tier Chance
        Total Resource = Sum(Tier Chests * Reward Per Tier)
    """
    total_chests = chests_per_day * days
    tier_counts = {tier: total_chests * chance for tier, chance in CHEST_TIER_CHANCES.items()}
    
    total_rewards = {
        "total_chests": total_chests,
        "rare_chests": tier_counts["Rare"],
        "epic_chests": tier_counts["Epic"],
        "legendary_chests": tier_counts["Legendary"],
        "mythic_chests": tier_counts["Mythic"],
        "elixir": 0.0,
        "medals": 0.0,
        "amber": 0.0,
        "eggs": 0.0,
        "keys": 0.0,
        "rare_scrolls": 0.0,
        "epic_scrolls": 0.0
    }
    
    for tier, count in tier_counts.items():
        for res, amount in CHEST_TIER_REWARDS[tier].items():
            total_rewards[res] += count * amount
            
    return total_rewards

# ==========================================
# 3. HERO XP & PACING FORMULAS
# ==========================================
def calculate_xp_time(stored_xp: float, goal_xp: float, tg_rate_hr: float, away_rate_hr: float) -> dict:
    """
    Excel Formulas from 'Heroes&Scrolls' (cols EX-EY):
        Net XP = max(0, Goal XP - Stored XP)
        Combined Rate / Hr = tg_rate_hr + away_rate_hr
        Hours = Net XP / Combined Rate
        Days = Hours / 24
        Years = Days / 365
    """
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

def calculate_combined_level_achievement(
    achievement_target: int,
    unlocked_heroes_count: int,
    main_heroes_count: int,
    main_heroes_combined_level: int,
    hero_xp_cumulative: list,
    tg_rate_hr: float,
    away_rate_hr: float
) -> dict:
    """
    Excel Formulas from 'Heroes&Scrolls' (cols EE-EF):
        Lvl 1 Heroes Count = unlocked_heroes_count - main_heroes_count
        Target Level Needed = round((achievement_target - main_heroes_combined_level - Lvl 1 Count) / Lvl 1 Count)
        XP Needed Per Hero = cumulative_xp_table[Target Level]
        Total XP Needed = XP Needed Per Hero * Lvl 1 Count
        Days = Total XP / (Hourly Rate * 24)
    """
    lvl1_heroes_count = max(1, unlocked_heroes_count - main_heroes_count)
    levels_needed_total = max(0, achievement_target - main_heroes_combined_level - lvl1_heroes_count)
    target_level_per_hero = int(round(levels_needed_total / lvl1_heroes_count))
    
    clamped_lvl = max(1, min(target_level_per_hero, len(hero_xp_cumulative) - 1))
    xp_per_hero = hero_xp_cumulative[clamped_lvl - 1] if clamped_lvl > 1 else 0
    total_xp_needed = xp_per_hero * lvl1_heroes_count
    
    time_res = calculate_xp_time(0, total_xp_needed, tg_rate_hr, away_rate_hr)
    
    return {
        "lvl1_heroes_count": lvl1_heroes_count,
        "target_level_per_hero": target_level_per_hero,
        "xp_per_hero": xp_per_hero,
        "total_xp_needed": total_xp_needed,
        "days_both": time_res["days_both"],
        "days_tg_only": time_res["days_tg_only"],
        "days_away_only": time_res["days_away_only"]
    }

# ==========================================
# 4. PULLS & PACING CALCULATOR
# ==========================================
def calculate_pulls_pacing(total_opened: int, days_elapsed: float, milestone_target: int) -> dict:
    """
    Excel Formulas from 'Heroes&Scrolls' & 'Pets&Eggs':
        Pulls Per Day = total_opened / days_elapsed
        Pulls Per Week = Pulls Per Day * 7
        Pulls Per Year = Pulls Per Day * 365
        Pulls Left = max(0, milestone_target - total_opened)
        Days To Goal = Pulls Left / Pulls Per Day
    """
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
        "pulls_left": pulls_left,
        "days_to_goal": days_to_goal,
        "weeks_to_goal": days_to_goal / 7.0,
        "years_to_goal": days_to_goal / 365.0
    }

# ==========================================
# 5. CONQUEST PRODUCTION & TIME ENGINE
# ==========================================
def calculate_conquest_upgrade_time(
    target_lumber_cost: int,
    stored_lumber: int,
    sawmill_total_rate_hr: float,
    target_ore_cost: int,
    stored_ore: int,
    oremine_total_rate_hr: float,
    current_upgrade_hours_left: float = 0.0
) -> dict:
    """
    Excel Formulas from 'Conquest Upgrades':
        Net Lumber = max(0, target_lumber_cost - stored_lumber)
        Hours Lumber = (Net Lumber / sawmill_total_rate_hr) + current_upgrade_hours_left
        Net Ore = max(0, target_ore_cost - stored_ore)
        Hours Ore = (Net Ore / oremine_total_rate_hr) + current_upgrade_hours_left
    """
    net_lumber = max(0, target_lumber_cost - stored_lumber)
    hours_lumber = (net_lumber / sawmill_total_rate_hr if sawmill_total_rate_hr > 0 else 0.0) + current_upgrade_hours_left
    
    net_ore = max(0, target_ore_cost - stored_ore)
    hours_ore = (net_ore / oremine_total_rate_hr if oremine_total_rate_hr > 0 else 0.0) + current_upgrade_hours_left
    
    max_hours = max(hours_lumber, hours_ore)
    
    return {
        "net_lumber": net_lumber,
        "hours_lumber": hours_lumber,
        "days_lumber": hours_lumber / 24.0,
        "net_ore": net_ore,
        "hours_ore": hours_ore,
        "days_ore": hours_ore / 24.0,
        "max_hours": max_hours,
        "max_days": max_hours / 24.0
    }

# ==========================================
# 6. STATIC DATA CONSTANTS
# ==========================================
FIREFLY_CHANCES = {
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

ENEMY_COIN_DROPS = {
    "Samurai": 53,
    "Hellhound": 51,
    "Spearmen": 54,
    "Shieldbearer": 59
}

GEM_DROP_CHANCES = {
    "Coins": 0.839,
    "Emerald": 0.100,
    "Sapphire": 0.050,
    "Ruby": 0.010,
    "Diamond": 0.001
}

OFFLINE_BAG_OF_GOODS = {
    "+": {"amber_price": 200, "offline_hours": 1.0, "price_per_hour": 200.0},
    "++": {"amber_price": 600, "offline_hours": 6.5, "price_per_hour": 92.31},
    "+++": {"amber_price": 1400, "offline_hours": 33.0, "price_per_hour": 42.42}
}

SECRET_ACHIEVEMENTS = [
    {"id": 1, "name": "Eye see you", "hint": "Gaze upon the six eyes", "solution": "Click every eye in the game until it moves."},
    {"id": 2, "name": "What goes up", "hint": "Must come down", "solution": "Scroll from top to bottom in every tab."},
    {"id": 3, "name": "Scared to Death", "hint": "This is nuts", "solution": "Spam click the squirrel in the pets tab."},
    {"id": 4, "name": "Let's enhance", "hint": "and see all of the details", "solution": "Zoom into the conquest map from being zoomed out all the way."},
    {"id": 5, "name": "Slow and steady", "hint": "Where is the rush?", "solution": "Play a conquest match at 0.5x speed."},
    {"id": 6, "name": "Master tapper", "hint": "Tap the ninja 100,000 times", "solution": "Click the ninja 100,000 times."},
    {"id": 7, "name": "You would not believe your eyes", "hint": "Calm the storm without any help", "solution": "Defeat a firefly storm without any help only by tapping."},
    {"id": 8, "name": "Yarr", "hint": "Shiver me timbers", "solution": "Use shuriken vortex while using Locke during the Pirate event."}
]

PROMO_CODES = [
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

# Baseline yellow-cell configuration values from workbook
DEFAULT_INPUT_SETTINGS = {
    "training_exp_per_hr": "34692",
    "away_exp_per_hr": "31996",
    "exp_stored": "914873",
    "exp_goal": "75000000",
    "levels_achievement_target": "4000",
    "stored_dust_blue": "146925",
    "stored_dust_green": "50075",
    "stored_dust_yellow": "454750",
    "stored_dust_red": "283925",
    "epic_scrolls_opened": "1158",
    "rare_scrolls_opened": "2316",
    "eggs_opened": "4623",
    "pulls_days_elapsed": "958",
    "scrolls_milestone_1": "1500",
    "scrolls_milestone_2": "3000",
    "eggs_milestone": "5000",
    "eggs_opened_aquatic": "8650",
    "eggs_opened_critter": "44417",
    "eggs_opened_beast": "65330",
    "eggs_opened_bird": "73037",
    "const_speed": "50.45",
    "const_lumber": "75.61",
    "const_ore": "88.89",
    "sawmill_1_rate": "9091",
    "sawmill_2_rate": "9091",
    "oremine_1_rate": "3382",
    "oremine_2_rate": "3382",
    "stored_lumber": "1030056",
    "stored_ore": "451304",
    "current_upgrade_hours_left": "0",
    "chest_board_level": "9",
    "chests_per_day": "8",
    "chest_eval_days": "365"
}