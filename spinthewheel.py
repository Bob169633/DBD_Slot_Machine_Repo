import tkinter as tk
import requests

from api_client import get_character_data, get_perk_names, get_unlockable_data
from app import BuildSlotMachineApp
from config import ADDONS_URL, ITEMS_URL
from filters import addon_is_allowed, survivor_item_is_allowed
from theme import grab_window_attention

DEBUG_MODE = False

def load_game_data():
  survivor_perks = get_perk_names("survivor")
  killer_perks = get_perk_names("killer")
  survivor_characters = get_character_data("survivor")
  killer_characters = get_character_data("killer")

  survivor_items = [
    item for item in get_unlockable_data(ITEMS_URL, "survivor")
    if survivor_item_is_allowed(item)
  ]

  survivor_addons = [
    addon for addon in get_unlockable_data(ADDONS_URL, "survivor")
    if addon_is_allowed(addon)
  ]

  killer_addons = [
    addon for addon in get_unlockable_data(ADDONS_URL, "killer")
    if addon_is_allowed(addon)
  ]

  return {
    "survivor_perks": survivor_perks,
    "killer_perks": killer_perks,
    "survivor_characters": survivor_characters,
    "killer_characters": killer_characters,
    "survivor_items": survivor_items,
    "survivor_addons": survivor_addons,
    "killer_addons": killer_addons
  }

def start_app():
  try:
    game_data = load_game_data()
  except requests.RequestException as error:
    print(f"Could not load data from the API: {error}")
    return

  root = tk.Tk()
  BuildSlotMachineApp(root, debug_mode=DEBUG_MODE, **game_data)
  grab_window_attention(root)
  root.mainloop()

if __name__ == "__main__":
  start_app()
