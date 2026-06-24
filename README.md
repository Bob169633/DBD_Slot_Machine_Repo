# DBD Build Slot Machine

## Version Number
- Version 1.2.0

## File layout

- `spinthewheel.py` - wrapper/entry point. Loads API data and starts the GUI.
- `app.py` - Tkinter GUI and build randomization display logic.
- `adept_rules.py` - character perk mapping
- `config.py` - paths, URLs, colors, mappings, blocked add-ons, and DBD constants.
- `api_client.py` - all API requests and API parsing helpers.
- `filters.py` - survivor item and add-on filtering.
- `game_rules.py` - killer powers, add-on ownership, offerings, and add-on selection rules.
- `gauntlet_history.py` - handles zerbs survivor/killer gauntlet information.
- `icon_utils.py` - icon filename cleanup, matching, and missing-icon printouts.
- `normalization.py` - all text normalization and icon alias logic.
- `theme.py` - dark theme, image reset, and window attention helper.

## Current Features

- Random character, perks, items, add-ons, and offerings (and amount of for perks/add-ons)
- Slot "Spinning" Animation
- Fireworks upon completion of a gauntlet
- 10 most recent build saves (10 for survivor, 10 for killer)
- Automatically imports custom icons from downloaded icon packs
- Background DVD-logo-esque animation of character portraits
- Slot icon borders flash gold and white when final build is selected
- Character enabling (toggle owned characters)
- Trophy Case to display best gauntlet runs
- Adept and Adept Hardmode challenges added

## Building `spinthewheel.exe`

1. Click the green button, download zip
2. Extract files (I recommend a folder on your desktop)
3. See my local_python repository for detailed instructions on creating the executable (https://github.com/Bob169633/portable_python)
