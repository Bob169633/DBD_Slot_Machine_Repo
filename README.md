# DBD Build Slot Machine


## File layout

- `spinthewheel.py` - wrapper/entry point. Loads API data and starts the GUI.
- `app.py` - Tkinter GUI and build randomization display logic.
- `config.py` - paths, URLs, colors, mappings, blocked add-ons, and DBD constants.
- `api_client.py` - all API requests and API parsing helpers.
- `filters.py` - survivor item and add-on filtering.
- `game_rules.py` - killer powers, add-on ownership, offerings, and add-on selection rules.
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

## Building `spinthewheel.exe`

1. Visit my other repo, https://github.com/Bob169633/portable_python to download the portable python install
2. If you already have python installed, you can instead only download packager.py
3. Unzip the portable python install to the same folder you extracted this repository to
4. Copy the file path from Windows Explorer (Control + Shift + C)
5. Open command prompt (Win + R, type cmd, hit enter)
6. type cd then paste what you just copied (the command line should look like cd c:/Users/<user>/folderA/folderB/)
7. type .\portable_python\python.exe .\portable_python\packager.py spinthewheel.py

## Note
This also searches for local Python installs
