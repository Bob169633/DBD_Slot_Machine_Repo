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

- Slot "Spinning" Animation
- Fireworks upon completion of a gauntlet
- 10 most recent build saves (10 for survivor, 10 for killer)
- Automatically imports custom icons from downloaded icon packs
- Background DVD-logo-esque animation of character portraits
- Slot icon borders flash gold and white when final build is selected

## Building `spinthewheel.exe` with the portable packager

1. Copy the file path from Windows Explorer (Control + Shift + C)
2. Open command prompt (Win + R, type cmd, hit enter)
3. type cd then paste what you just copied
4. type .\portable_python\python.exe packager.py spinthewheel.py

