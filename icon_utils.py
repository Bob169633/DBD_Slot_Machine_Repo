import os
import re

from config import (
  CHARACTER_PORTRAIT_EXACT_FILES,
  OFFERING_EXACT_ICON_FILES,
  SOURCE_ADDON_ICON_FOLDER,
  SOURCE_CHARACTER_PORTRAIT_FOLDER,
  SOURCE_ICON_FOLDER,
  SOURCE_ITEM_ICON_FOLDER,
  SOURCE_OFFERING_ICON_FOLDER,
  SOURCE_POWER_ICON_FOLDER
)
from game_rules import get_all_offering_options, get_killer_power_name
from normalization import (
  camel_to_words,
  get_icon_search_keys,
  normalize_dbd_terms,
  normalize_icon_search_text,
  normalize_text,
  remove_perk_prefix_terms
)

def get_png_files_from_folder(source_folder):
  files = []

  if not os.path.exists(source_folder):
    print(f"Source folder not found: {source_folder}")
    return files

  for current_folder, subfolders, file_names in os.walk(source_folder):
    for file_name in file_names:
      if file_name.lower().endswith(".png"):
        files.append(os.path.join(current_folder, file_name))

  return files

def clean_icon_file_name(file_path):
  name = os.path.splitext(os.path.basename(file_path))[0]
  name = re.sub(r"^iconperks[_\-]?", "", name, flags=re.IGNORECASE)
  name = re.sub(r"^iconperk[_\-]?", "", name, flags=re.IGNORECASE)
  name = re.sub(r"^perk[_\-]?", "", name, flags=re.IGNORECASE)
  return camel_to_words(name)

def clean_character_file_name(file_path):
  name = os.path.splitext(os.path.basename(file_path))[0]
  name = re.sub(r"^[SK]\d+[_\-]?", "", name, flags=re.IGNORECASE)
  name = re.sub(r"[_\-]?portrait$", "", name, flags=re.IGNORECASE)
  name = re.sub(r"^charportrait[_\-]?", "", name, flags=re.IGNORECASE)
  name = re.sub(r"^portrait[_\-]?", "", name, flags=re.IGNORECASE)
  name = re.sub(r"^icon[_\-]?", "", name, flags=re.IGNORECASE)
  return camel_to_words(name)

def clean_unlockable_file_name(file_path):
  name = os.path.splitext(os.path.basename(file_path))[0]

  for prefix in (
    r"^t_ui[_\-]?",
    r"^icons[_\-]?",
    r"^icon[_\-]?",
    r"^iconitems[_\-]?",
    r"^iconitemaddons[_\-]?",
    r"^iconaddon[_\-]?",
    r"^iconfavors[_\-]?",
    r"^items[_\-]?",
    r"^itemaddons[_\-]?",
    r"^addon[_\-]?",
    r"^favors[_\-]?"
  ):
    name = re.sub(prefix, "", name, flags=re.IGNORECASE)

  return camel_to_words(name)

def clean_power_file_name(file_path):
  name = os.path.splitext(os.path.basename(file_path))[0]

  for prefix in (
    r"^t_ui[_\-]?",
    r"^iconpowers[_\-]?",
    r"^iconpower[_\-]?",
    r"^icon[_\-]?",
    r"^power[_\-]?",
    r"^powers[_\-]?"
  ):
    name = re.sub(prefix, "", name, flags=re.IGNORECASE)

  return camel_to_words(name)

def build_perk_icon_files(perk_names):
  icon_files = get_png_files_from_folder(SOURCE_ICON_FOLDER)
  normalized_icon_files = {
    normalize_text(clean_icon_file_name(file_path)): file_path
    for file_path in icon_files
  }

  perk_icon_files = {}

  for perk_name in perk_names:
    search_perk_name = normalize_dbd_terms(remove_perk_prefix_terms(perk_name))
    normalized_perk_name = normalize_text(search_perk_name)

    if normalized_perk_name in normalized_icon_files:
      perk_icon_files[perk_name] = normalized_icon_files[normalized_perk_name]
      continue

    perk_words = re.findall(r"[a-zA-Z0-9]+", search_perk_name.replace("&", "and"))
    regex_pattern = ".*".join(re.escape(word.lower()) for word in perk_words)

    for file_path in icon_files:
      normalized_file_name = normalize_text(clean_icon_file_name(file_path))

      if re.search(regex_pattern, normalized_file_name):
        perk_icon_files[perk_name] = file_path
        break

  return perk_icon_files

def build_character_portrait_files(character_data):
  portrait_files = get_png_files_from_folder(SOURCE_CHARACTER_PORTRAIT_FOLDER)
  normalized_portrait_files = {
    normalize_text(clean_character_file_name(file_path)): file_path
    for file_path in portrait_files
  }
  exact_portrait_files = {
    normalize_text(normalize_dbd_terms(character_name)): os.path.join(SOURCE_CHARACTER_PORTRAIT_FOLDER, relative_path)
    for character_name, relative_path in CHARACTER_PORTRAIT_EXACT_FILES.items()
  }

  character_portrait_files = {}

  for character in character_data:
    character_name = character["name"]
    normalized_character_name = normalize_text(normalize_dbd_terms(character_name))

    if normalized_character_name in exact_portrait_files:
      character_portrait_files[character_name] = exact_portrait_files[normalized_character_name]
      continue

    if normalized_character_name in normalized_portrait_files:
      character_portrait_files[character_name] = normalized_portrait_files[normalized_character_name]
      continue

    for normalized_file_name, file_path in normalized_portrait_files.items():
      if normalized_character_name in normalized_file_name:
        character_portrait_files[character_name] = file_path
        break

  return character_portrait_files

def build_unlockable_icon_files(unlockables, source_folder):
  icon_files = get_png_files_from_folder(source_folder)
  matched_icons = {}
  normalized_icon_files = {}

  for file_path in icon_files:
    for normalized_name in get_icon_search_keys(clean_unlockable_file_name(file_path)):
      normalized_icon_files[normalized_name] = file_path

  for unlockable in unlockables:
    unlockable_name = unlockable["name"]

    for search_key in get_icon_search_keys(unlockable_name):
      if search_key in normalized_icon_files:
        matched_icons[unlockable_name] = normalized_icon_files[search_key]
        break

    if unlockable_name in matched_icons:
      continue

    words = re.findall(r"[a-zA-Z0-9]+", unlockable_name)
    regex_pattern = ".*".join(re.escape(normalize_icon_search_text(word)) for word in words)

    for normalized_file_name, file_path in normalized_icon_files.items():
      if re.search(regex_pattern, normalized_file_name):
        matched_icons[unlockable_name] = file_path
        break

  return matched_icons

def build_offering_option_icon_files():
  icon_files = get_png_files_from_folder(SOURCE_OFFERING_ICON_FOLDER)
  matched_icons = {}
  normalized_icon_files = {}

  for file_path in icon_files:
    for normalized_name in get_icon_search_keys(clean_unlockable_file_name(file_path)):
      normalized_icon_files[normalized_name] = file_path

  exact_icon_files = {
    icon_name: os.path.join(SOURCE_OFFERING_ICON_FOLDER, relative_path)
    for icon_name, relative_path in OFFERING_EXACT_ICON_FILES.items()
  }

  for offering_option in get_all_offering_options():
    icon_name = offering_option.get("icon_name")
    icon_key = offering_option.get("icon_key")

    if icon_name is None:
      continue

    exact_icon_path = exact_icon_files.get(icon_name)

    if exact_icon_path is not None and os.path.exists(exact_icon_path):
      matched_icons[icon_key] = exact_icon_path
      continue

    for search_key in get_icon_search_keys(icon_name):
      if search_key in normalized_icon_files:
        matched_icons[icon_key] = normalized_icon_files[search_key]
        break

  return matched_icons

def build_killer_power_icon_files(killer_characters):
  icon_files = get_png_files_from_folder(SOURCE_POWER_ICON_FOLDER)
  normalized_icon_files = {}

  for file_path in icon_files:
    for normalized_name in get_icon_search_keys(clean_power_file_name(file_path)):
      normalized_icon_files[normalized_name] = file_path

  power_icon_files = {}

  for character in killer_characters:
    power_name = get_killer_power_name(character)

    for search_key in get_icon_search_keys(power_name):
      if search_key in normalized_icon_files:
        power_icon_files[power_name] = normalized_icon_files[search_key]
        break

  return power_icon_files

def print_missing_icon_matches(label, icon_files, names_or_unlockables, icon_key_getter=None):
  missing = []

  for entry in names_or_unlockables:
    if isinstance(entry, dict):
      display_name = entry["name"]
      lookup_name = icon_key_getter(entry) if icon_key_getter else entry.get("icon_key", display_name)
    else:
      display_name = entry
      lookup_name = entry

    if lookup_name not in icon_files:
      missing.append(display_name)

  if not missing:
    print(f"\nAll {label} icons were matched.")
    return

  print(f"\n{label.title()} with no matching icon:")
  for name in missing:
    print(f"- {name}")
