## YOU NEED 
-MATPLOTLIB FOR GRAPHS TO WORK

-PYTHON 3.6 OR NEWER

-macOS/LUNUX NEED TKINTER

### HOW TO GET:
1. Install the latest version of python from [python.org](https://www.python.org/)
2. Install Matplot lib by pasting this is a Terminal/Command Prompt: python -m pip install matplotlib
3. For macOS/Linux install Tkinter (no idea what to do here, I don't use either of those OSs)


## 🛠️ Tutorial: How to Export Tap Ninja Site Data to the Tracking App

If you've been using the [Tap Ninja Calculator Website](https://a11v1r15.github.io/Tap_Ninja_Calc/) and want to move your progress into this App go to the "Storage" Tab of the Site and click  <img width="180" height="17" alt="image" src="https://github.com/user-attachments/assets/afe66852-a055-4e6a-9db3-a165b363ef03" />



# GAME INFO & DOCUMENTATION

### General Disclaimer
### AI was used to help code this as I don't have enough coding knowledge, especially with databases. This Information tab tells you most if not all important information about what this program does. This was made by @i.eatchildren on discord if you find any issues or want something added, please DM me.
---

## Core Architecture & Features

*   **Database & Real-Time Auto-Save**: Local persistent storage in `datenbank.db` with auto-saves in real time.
*   **Table Sorting & Interactions**: Click any column header to sort in ascending order; click again to reverse. Click anywhere on the background to clear table selection and entry fields. Press `<Enter>` in entry fields to submit records. Press `<Delete>` or `<Backspace>` to trigger safe deletion.
*   **Dual-Format Portability**: Full native SQLite database (`.db`) backup/restore and modular CSV (`.csv`) export/import across all entities.

---

## Detailed Section Guides

### [Stats Tab (Master Overview)]
*   **5-Pillar Comprehensive Overview**:
    *   **Heroes Overview**: Count Obtained, Total Stars, Total XP Levels, Total XP, Total Dust Used, Total Dust Needed, individual `Saved (Net)` for Blue, Green, Yellow, and Red, Total Saved Dust, Net Dust Needed, and **XP Time Remaining** (Days and Years projection based on active hourly rate).
    *   **Pets Overview**: Count Obtained, Total Stars, Total Bond Levels, Feathers Used, Feathers Needed, individual counts for Blue (Aquatic), Green (Critter), Yellow (Bird), and Red (Beast), Total Saved Feathers, Net Feathers Needed, Time Spent, and **Training Time Remaining** (Days and Years breakdown).
    *   **Conquest Buildings Overview**: Total Building Levels, Net Lumber Spent & Needed, Net Ore Spent & Needed, Time Invested, and Active Construction Multipliers.
    *   **Elixir Overview**: Current Total Elixir, Total Logged Datapoints, and Average Weekly Gain rate.
    *   **Equipment Overview**: Total item tiers (out of 175 max), Amber Spent, and Amber Needed to max all gear.

### [Heroes Tab]
*   **Stars & XP Levels**: Stars range from 0★ to 12★; XP Levels range from 1 to 140.
*   **Side-by-Side Header Layout**:
    *   **Dust Inventory (4 Elemental Types)**:
        *   🔵 **Blue Dust** (Water heroes: Akane, Hoshi, etc.)
        *   🟢 **Green Dust** (Wind heroes: Ayaka, Jari, etc.)
        *   🟡 **Yellow Dust** (Earth heroes: Hiro, Kaito, etc.)
        *   🔴 **Red Dust** (Fire heroes: Ketsueki, Fang, etc.)
        *   Auto-saves each inventory count individually to database settings (`saved_dust_blue`, `saved_dust_green`, `saved_dust_yellow`, `saved_dust_red`).
    *   **Streamlined Data Entry**: Single-row inputs for `Name`, `Stars`, `XP Level` with instant action buttons:
        *   `Add` (Green): Inserts or updates the hero.
        *   `Update` (Yellow): Modifies the selected hero record.
        *   `Delete` (Red): Safely prompts confirmation before removing a record.
        *   `Clear Fields` (Slate): Resets all entry boxes.
    *   **Search & Filters**: Real-time name search, `Hide unobtained` (0★) checkbox, and Rarity filter (`All`, `Legendary`, `Epic`, `Rare`).
    *   **Summary Statistics Card**: Total Stars, Total XP Levels, Cumulative Total XP, XP Needed to max all heroes, Dust Used, Dust Needed, and Dust Saved.
*   **XP Time Calculator Sub-tab**:
    *   **Configurable Rates**: Separate inputs for `Training Grounds Rate (XP/h)` (default: 34,692 XP/h) and `Away Rate (XP/h)` (default: 31,996 XP/h) combined into total hourly throughput (default: 66,688 XP/h).
    *   **Dynamic Projections**: Computes remaining time in Hours, Days, and Years (with standalone Training Grounds and Away breakdowns).
*   **Team Calculator Sub-tab**:
    *   Evaluates optimal 5-hero lineup (2 Frontline, 3 Backline) based on Base Power Scores, Star Levels, and Faction Counter Advantage.
    *   **Faction Advantage Cycle**: Fire > Wind > Earth > Water > Fire (+50% damage bonus).
    *   Configurable class compositions (Warriors, Assassins, Mages, Supports) with alternative candidate suggestions.
*   **Fashion Wardrobe System**:
    *   **Equipped Loadout**: 4 visual loadout slots (Slot A, B, C, D) with color preview swatches.
    *   **Skin Collection Grid**: Interactive unlock checkboxes for all 30 official hero outfits and colorways.
    *   **Randomize Fashion**: Generates a random cosmetic loadout chosen exclusively from your unlocked skins.
    *   **Batch Operations**: One-click `Select All` and `Deselect All` buttons.

### [Pets Tab]
*   **Stars & Bond Levels**: Stars range from 0★ to 12★; Bond Levels range from 1 to 15.
*   **Pet Category System (4 Types)**:
    *   🔵 **Blue Feathers (Aquatic)**: Frog, Turtle, Penguin, Crab, Otter
    *   🟢 **Green Feathers (Critter)**: Bunny, Mouse/Capybara, Hedgehog, Snake, Squirrel, Chicken/Duck
    *   🟡 **Yellow Feathers (Bird)**: Crane, Raven, Dragonfly, Dragonling/Luckdragon, Parrot/Peafowl
    *   🔴 **Red Feathers (Beast)**: Cat, Dog/Wolf, Fox, Panda, Racoon
*   **Side-by-Side Header Layout**:
    *   **Feathers Inventory (4 Types)**: 🔵 Blue (Aquatic) | 🟢 Green (Critter) | 🟡 Yellow (Bird) | 🔴 Red (Beast) with auto-save.
    *   **Streamlined Data Entry**: Single-row inputs for `Name`, `Stars`, `Bond Level` with `Add`, `Update`, `Delete`, and `Clear Fields`.
    *   **Search & Filters**: Instant name filter and `Hide unobtained` (0★) toggle.
    *   **Summary Statistics Card**: Total Stars, Total Bond Levels, Feathers Used, Feathers Needed, Feathers Saved, Time Spent, and Time Left.

### [Progress Tab]
*   **Weighted Completion Bar**: Dynamically combines overall progress across Heroes, Pets, and Conquest Buildings into a unified completion %.
*   **Color Scale**: Progress bars transition dynamically from Red (0-39%) -> Yellow (40-69%) -> Green (70-99%) -> Gold (100%).
*   **Detailed Category Progress Bars**:
    *   `Hero Stars`, `Hero XP Levels`, `Hero Total XP`, and `Hero Dust` (includes `+saved [B, G, Y, R]` breakdown).
    *   `Pet Stars`, `Pet Bond Levels`, `Pet Feathers` (includes `+saved [B, G, Y, R]` breakdown), and `Pet Training Time`.
    *   `Conquest Buildings` (overall building level progress toward max 14).
    *   `Equipment Mastery` (overall equipment levels toward max 25).

### [Pulls Tab (Scrolls & Eggs)]
*   **Smart Sync**: Logging scrolls or eggs automatically updates the hero/pet in your database if the pulled star rating exceeds your current level.
*   **Luck Analytics Sub-tab**:
    *   Live Matplotlib charts comparing your pull percentages against official game drop rates.
    *   **Official Probabilities Table**: Star chances (1★: 20% to 12★: 0.083% for scrolls; 1★: 20% to 12★: 0.045% for eggs) and Scroll Quality rates (Rare Scroll: 2% Leg / 38% Epic / 60% Rare; Epic Scroll: 15% Leg / 85% Epic).
    *   **Weighted Luck Index**: Score relative to statistical expectation (>100% indicates lucky streaks).
*   **Pacing & Achievements Sub-tab**:
    *   **Dual Starting Dates & Timelines**:
        *   📜 **Scrolls Timeline**: Starts **07.Jan.2024** (with custom days elapsed input and `📅 Reset` button).
        *   🥚 **Pet Eggs Timeline**: Starts **07.Nov.2022** (with custom days elapsed input and `📅 Reset` button).
    *   **3-Column Milestone Dashboard**:
        *   📜 **Rare Scrolls**: Velocity (Per Day, Per Week, Per Year) and days/weeks to reach Goal 1 (default 1,500) and Goal 2 (default 3,000).
        *   📜 **Epic Scrolls**: Velocity (Per Day, Per Week, Per Year) and days/weeks to reach Goal 1 (default 1,500) and Goal 2 (default 3,000).
        *   🥚 **Pet Eggs**: Velocity (Per Day, Per Week, Per Year) and days/weeks to reach Goal 1 (default 2,500) and Goal 2 (default 5,000).
*   **Log History Sub-tabs**: Full scroll and egg history tables with inline updates, deletions, and CSV import support.

### [Conquest (Buildings)]
*   **Max Level**: Level 14 for all buildings.
*   **Castle Level Constraint**: No building level can exceed the Castle level.
*   **Construction Multipliers**: Adjust Speed, Lumber, and Ore multipliers (0.1% to 100%) to match research and ascension bonuses.
*   **Stored Resources & Afford Time**:
    *   Inputs for `Stored Lumber`, `Stored Ore`, and hourly production rates for Sawmills and Ore Mines.
    *   Calculates exact Net Lumber and Net Ore needed and live Time to Afford next upgrade for every building and the Castle.
*   **Target Cost Planner**: Calculates the exact net lumber, ore, and time needed to upgrade from current levels to custom goal levels.

### [Elixir Tab]
*   **Compounding Growth Projection**: Calculates exact future dates, weeks, and days required to reach custom target elixir milestones.
*   **Dual-Axis Analytics Chart**: Interactive line chart showing 6-month growth trajectory, secondary weekly gain bars, and variance boxplot.
*   **CSV Import Conflict Resolver**: Custom dialog with `Overwrite`, `Skip`, `Overwrite All`, and `Skip All` for handling duplicate date logs.

### [Equipment Tab]
*   **Items**: Kimono, Katana, Kabuto, Geta, Kote, Yubiwa, Menpo (max level 25).
*   **Live Metrics**: Stat boost %, Amber cost for next level, and Amber required to max each piece.
*   **Batch Controls**: Step upgrade buttons (`+`, `-`) or instant `Max All Equipment to Cap` batch planner.

### [Seasonal Tab]
*   **Data & Bulk Editor**:
    *   **Multi-Season Management**: Dynamic schema columns for Season 1, 2, ..., N.
    *   **Automatic Empty Season Purge**: Empty seasons with no data (`-` or empty) are automatically detected and dropped from the SQLite schema and UI table.
    *   **New Season Creation**: Instantly adds next numerical season to SQLite database with one click.
    *   **Modern Card Bulk Editor**: 4-column tile grid for entering values across all 12 seasonal resources (Gold, Elixir, Buildings, Research, Coins, Eggs, Scrolls, Amber, Dust, Feathers, etc.).
    *   **Dynamic Matrix Table**: Auto-expanding Treeview showing only active seasons with alternating row fills.
    *   **Dedicated CSV Portability**: Direct Seasonal CSV export and import.
*   **Resource Analytics / Graphs**:
    *   **Visual Growth Charts**: Matplotlib line and bar charts displaying the acquired quantity of any selected resource across all seasons (Y-axis: Amount Acquired, X-axis: Season Number).
    *   **Adaptive Numeric Scaling**: Smart parsing supporting raw numbers, commas, and metric suffixes (`K`, `M`, `B`, `T`, and scientific notation `1.21e+50`).
    *   **Summary Metrics Panel**: Instant calculations for Total Acquired (All Seasons), Average per Season, Peak Season, and Latest Season amount.

### [Misc Tab (Calculators & Game References)]
*   **Drop References Sub-tab**:
    *   🪰 **Firefly Drops**: Base coin yields, spawn cooldowns, and special buff drop chances (Extra Coins, Speed Boost, Frenzy, Diamond Shards).
    *   ⚔️ **Enemy Coins**: Base coins per tier, kill multipliers, and zone scaling formulas.
    *   💎 **Gem Mine**: Yield progression, extraction cycle times, and gem yields.
    *   🎒 **Offline Bag of Goods**: Idle generation caps, hourly resource accumulation rates, and offline multipliers.
    *   ⭐ **Star Dust & Pet Feather Upgrade Costs Reference**: Complete level-by-level cost table from 1★ to 12★ for all 4 rarities/categories.
*   **Chest Reward Calculator Sub-tab**:
    *   Configurable inputs for custom Gold and Elixir amounts in each chest tier (Rare, Epic, Legendary, Mythic).
    *   Configurable daily chest drops, chest multiplier, and evaluation period (Days).
    *   Expected yields matrix breakdown table detailing rewards for all 8 resources (Gold, Elixir, Medals, Amber, Star Dust, Pet Feathers, Scrolls, Pet Eggs) broken down by chest rarity and combined total with daily averages.
*   **Element of Water Calculator Sub-tab**:
    *   Configurable base cost, multiplier, and scaling formulas (scaling by 10x every 4 levels).
    *   Current level, target level, next level step cost, and cumulative cost calculation.
    *   Level-by-level step cost preview table with internal dark scrolling.
*   **Secret Achievements Sub-tab**:
    *   Interactive checklist for all 8 official secret achievements with requirement descriptions and auto-persisted unlock states.
*   **Promo Codes Sub-tab**:
    *   Directory of all active redeemable promo codes with one-click copy buttons and reward descriptions.

### [Notepad Tab]
*   **Interactive Checklist**: Click `☑ Checklist` to insert `☐`. Clicking any checkbox directly in the text editor toggles between `☐` and `☑`.
*   **Debounced Auto-Save**: Seamlessly persists notes to SQLite in the background without lag.

### [Settings Tab]
*   **Dual-Format Database Backup & Portability**:
    *   **SQLite Database Files (`.db`)**: Export and import complete native SQLite database snapshots with single-click transactional integrity and automatic schema migration checks.
    *   **Universal CSV Files (`.csv`)**: Export and import human-readable spreadsheets across all system tables (Heroes, Pets, Buildings, Equipment, Fashion, Seasonal, Elixir, Settings).
*   **Theme Studio**: Color pickers for Background, Surface, Buttons, and Accents with live palette reload.
*   **Reset Data**: Safe factory reset with confirmation prompt.
