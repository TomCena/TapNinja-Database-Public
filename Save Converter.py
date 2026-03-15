import json
import csv
import os

# --- Configuration & Mappings ---
HERO_NAMES = [
    "Ninja", "Fang", "Jari", "Jie", "Waju", "Tateju", "Kenju", "Sketchy", "Ray", "Kaoru", 
    "Belu", "Terra", "Demid", "Momo", "Locke", "Duncan", "Sayid", "Scorn", "Tomak", "Scarlet", 
    "Blazer", "Maki", "Hiro", "Akira", "Scythe", "Irbinok", "Husk", "Alivia", "Wasp", "Elyanna", 
    "Fin", "Kito", "Tier", "Tièr", "Falkron", "Snow", "Alekas", "Papyrus", "Xyzl", "Ulrik", "Dia", "Ekho"
]

PET_NAME_MAP = {
    "Mouse": "Mouse/Capybara", "Capybara": "Mouse/Capybara",
    "Chicken": "Chicken/Duck", "Duck": "Chicken/Duck",
    "Dragonling": "Dragonling/Luckdragon", "LuckDragon": "Dragonling/Luckdragon",
    "Parrot": "Parrot/Peafowl", "Peafowl": "Parrot/Peafowl",
    "Dog": "Dog/Wolf", "Wolf": "Dog/Wolf",
    "Frog": "Frog", "Turtle": "Turtle", "Penguin": "Penguin", "Crab": "Crab", 
    "Otter": "Otter", "Bunny": "Bunny", "Hedgehog": "Hedgehog", "Snake": "Snake", 
    "Squirrel": "Squirrel", "Crane": "Crane", "Raven": "Raven", "Dragonfly": "Dragonfly", 
    "Cat": "Cat", "Fox": "Fox", "Panda": "Panda", "Racoon": "Racoon"
}

EQUIPMENT_DATA = {
    "Kimono": [0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 375, 400, 425, 450, 475, 500, 525, 550, 575, 600, 625],
    "Katana": [0, 7.5, 15, 22.5, 30, 37.5, 45, 52.5, 60, 67.5, 75, 82.5, 90, 97.5, 105, 112.5, 120, 127.5, 135, 142.5, 150, 157.5, 165, 172.5, 180, 187.5],
    "Kabuto": [0, 2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25, 27.5, 30, 32.5, 35, 37.5, 40, 42.5, 45, 47.5, 50, 52.5, 55, 57.5, 60, 62.5],
    "Geta": [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345, 360, 375],
    "Kote": [0, 0.4, 0.8, 1.2, 1.6, 2, 2.4, 2.8, 3.2, 3.6, 4, 4.4, 4.8, 5.2, 5.6, 6, 6.4, 6.8, 7.2, 7.6, 8, 8.4, 8.8, 9.2, 9.6, 10],
    "Yubiwa": [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 100],
    "Menpo": [0, 0.4, 0.8, 1.2, 1.6, 2, 2.4, 2.8, 3.2, 3.6, 4, 4.4, 4.8, 5.2, 5.6, 6, 6.4, 6.8, 7.2, 7.6, 8, 8.4, 8.8, 9.2, 9.6, 10]
}

def convert_save():
    input_file = 'save.json'
    output_file = 'TapNinjaData.csv'

    if not os.path.exists(input_file):
        print(f"Error: Could not find '{input_file}'. Please save your JSON data into this file and try again.")
        return

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return

    heroes = {}
    pets = {}
    equipment = {}

    # --- Parse JSON Data ---
    for key, value in data.items():
        # Parse Heroes
        if key.endswith("Level") and key[:-5] in HERO_NAMES:
            name = key[:-5]
            if name not in heroes: heroes[name] = {"stars": "-", "level": "-"}
            heroes[name]["level"] = value
        elif key.endswith("Stars") and key[:-5] in HERO_NAMES:
            name = key[:-5]
            if name not in heroes: heroes[name] = {"stars": "-", "level": "-"}
            heroes[name]["stars"] = value

        # Parse Pets
        elif key.endswith("Bond"):
            name = key[:-4]
            if name in PET_NAME_MAP:
                mapped = PET_NAME_MAP[name]
                if mapped not in pets: pets[mapped] = {"stars": "-", "bond": "-"}
                pets[mapped]["bond"] = value
        elif key.endswith("Stars"):
            name = key[:-5]
            if name in PET_NAME_MAP:
                mapped = PET_NAME_MAP[name]
                if mapped not in pets: pets[mapped] = {"stars": "-", "bond": "-"}
                pets[mapped]["stars"] = value

        # Parse Equipment
        elif key.endswith("Bonus"):
            name = key[:-5]
            if name in EQUIPMENT_DATA:
                try:
                    bonus_val = float(value)
                    # Find the index (level) of this bonus value
                    level = EQUIPMENT_DATA[name].index(bonus_val)
                    equipment[name] = level
                except ValueError:
                    # If the exact bonus isn't found, default to 0
                    equipment[name] = 0

    # --- Write to CSV ---
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write Header
            writer.writerow(["Type", "Name/Key", "Val1", "Val2", "Val3", "Val4", "Val5"])
            
            # Write Heroes
            for name, d in heroes.items():
                writer.writerow(["HERO", name, d["stars"], d["level"], "-", "-", "Legendary"])
            
            # Write Pets
            for name, d in pets.items():
                writer.writerow(["PET", name, d["stars"], d["bond"], "-", "-", ""])
            
            # Write Equipment
            for name, level in equipment.items():
                writer.writerow(["EQUIPMENT", name, level, "", "", "", ""])

        print(f"Success! Data has been converted and saved to '{output_file}'.")
        print("You can now import this file into the Desktop Tracking App.")

    except Exception as e:
        print(f"Error writing to CSV: {e}")

if __name__ == "__main__":
    convert_save()