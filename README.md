# YOU NEED 
# -MATPLOTLIB FOR GRAPHS TO WORK 
# -PYTHON 3.6 OR NEWER
# -macOS/LUNUX NEED TKINTER



# INFORMATION

## General Disclamer
*AI was used to help code this as I don't have enough coding knowledge, especially with databases.*
Base code was written by me but optimized with AI so it'll run on anything less than a NASA PC.
I have no idea if this will even work on PCs other than mine because quite frankly the saving mechanism is a mystery to me, sometimes it doesn't create a datenbank.db file but it still saves all the info you input.
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
