## YOU NEED 
-MATPLOTLIB FOR GRAPHS TO WORK

-PYTHON 3.6 OR NEWER

-macOS/LUNUX NEED TKINTER

### HOW TO GET:
1. Install the latest version of python from [python.org](https://www.python.org/)
2. Install Matplot lib by pasting this is a Terminal/Command Prompt: python -m pip install matplotlib
3. For macOS/Linux install Tkinter (no idea what to do here, I don't use either of those OSes


## 🛠️ Tutorial: How to Export Tap Ninja Site Data to the Tracking App

If you've been using the [Tap Ninja Calculator Website](https://a11v1r15.github.io/Tap_Ninja_Calc/) and want to move your progress into this App, follow these steps.

### Step 1: Extract Your Data from the Website
Because the website saves your data locally in your browser, you need to pull it out using your browser's Developer Tools.

1. Open the **Tap Ninja Calculator website**.
2. Press **F12** (or `Ctrl + Shift + I` / `Cmd + Option + I` on Mac) to open the Developer Tools.
3. Click on the **Console** tab at the top of the Developer Tools window.
4. Paste the following exact command into the console and press **Enter**:
   ```javascript
   JSON.stringify(localStorage)
   ```
5. A large block of text will appear (it looks like `{"HeroLevel":"85", ...}`). Right-click this text and select **Copy string contents** (or highlight it all and copy it).

---

### Step 2: Convert the Data (Choose Option A or Option B)
The tracking app requires a specific CSV format to read your data correctly. You can either use an AI to convert it quickly, or run the local Python script included in this repository.

#### Option A: Use an AI Prompt (No coding required)
Copy the prompt below, paste it into an AI (like Gemini or ChatGPT), and replace the `[INSERT COPIED DATA HERE]` part with the text you copied in Step 1.

**Copy this prompt:**
```text
Act as a data parser. I am going to give you a JSON string representing my Tap Ninja save data. I need you to convert it into a specific CSV format.

CSV Format Requirements:
* Header row: Type,Name/Key,Val1,Val2,Val3,Val4,Val5
* Heroes: HERO,[Hero Name],[Stars],[Level],-,-,Legendary (Look for keys ending in "Level" and "Stars". E.g., "ElyannaLevel":"85" -> Level 85. If a hero is missing Stars or Level, use "-").
* Pets: PET,[Pet Name],[Stars],[Bond],-,-, (Look for keys ending in "Bond" and "Stars").
* Equipment: EQUIPMENT,[Equipment Name],[Level],,,, (Look for keys ending in "Bonus". Match the bonus value to its index/level based on the lists below).

Special Naming Rules:
* If a pet is named Mouse or Capybara, output Mouse/Capybara.
* Chicken or Duck -> Chicken/Duck
* Dragonling or LuckDragon -> Dragonling/Luckdragon
* Parrot or Peafowl -> Parrot/Peafowl
* Dog or Wolf -> Dog/Wolf

Equipment Bonus-to-Level Mapping (Index 0 is Level 0, Index 1 is Level 1, etc.):
* Kimono: 0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 375, 400, 425, 450, 475, 500, 525, 550, 575, 600, 625
* Katana: 0, 7.5, 15, 22.5, 30, 37.5, 45, 52.5, 60, 67.5, 75, 82.5, 90, 97.5, 105, 112.5, 120, 127.5, 135, 142.5, 150, 157.5, 165, 172.5, 180, 187.5
* Kabuto: 0, 2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25, 27.5, 30, 32.5, 35, 37.5, 40, 42.5, 45, 47.5, 50, 52.5, 55, 57.5, 60, 62.5
* Geta: 0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345, 360, 375
* Kote: 0, 0.4, 0.8, 1.2, 1.6, 2, 2.4, 2.8, 3.2, 3.6, 4, 4.4, 4.8, 5.2, 5.6, 6, 6.4, 6.8, 7.2, 7.6, 8, 8.4, 8.8, 9.2, 9.6, 10
* Yubiwa: 0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 100
* Menpo: 0, 0.4, 0.8, 1.2, 1.6, 2, 2.4, 2.8, 3.2, 3.6, 4, 4.4, 4.8, 5.2, 5.6, 6, 6.4, 6.8, 7.2, 7.6, 8, 8.4, 8.8, 9.2, 9.6, 10

Please output ONLY the raw CSV text inside a code block so I can copy it easily. Here is my JSON data:

[INSERT COPIED DATA HERE]
```
Once the AI generates your CSV code, copy it, open Notepad (or any basic text editor), paste the code, and save the file as `TapNinjaData.csv`. *(Make sure it saves as a `.csv` file and not a `.txt` file!)*

#### Option B: Use the Python Script (Local conversion)
If you prefer running a local script, use the `Save Converter.py` file included in this repository.
1. Save the JSON string you copied in Step 1 into a text file named `save.json` in the exact same folder as `Save Converter.py`.
2. Run `Save Converter.py` (double-click it or run it from your terminal/command prompt).
3. The script will automatically generate a `TapNinjaData.csv` file for you in that same folder.

---

### Step 3: Import into the App
1. Open the App.
2. Navigate to the **Settings** tab and click **Import Data from CSV**. 
3. Select the `TapNinjaData.csv` file you just generated, and your data will instantly populate across all tabs!


# INFORMATION

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
* Includes summaries for **Total Resources Spent** and **Total Resources Needed** across all buildings.
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

### [Seasonal]
* **Purpose**: Track your resource gains and progress across different game seasons.
* **Features**:
    * Track stats like Gold, Elixir, Buildings, Research, Coins, Eggs, Scrolls, Towns Conquered, Amber, Dust, and Feathers.
    * `Create New Season`: Adds a new column to track data for the next season.
    * `Edit Season`: Opens a bulk-edit interface to quickly input or update all resource values for the selected season.
    * `Clear Season`: Wipes all data for the currently selected season.
    * `Import/Export CSV`: Save or load your seasonal data independently.

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
