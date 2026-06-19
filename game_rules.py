import random

from api_client import get_searchable_entry_text
from killer_addon_map import get_manual_killer_addons
from config import (
  KILLER_ADDON_EXACT_POWER_BY_ADDON,
  KILLER_ONLY_OFFERING_OPTION_NAMES,
  KILLER_POWER_BY_KILLER,
  OFFERING_ICON_NAME_BY_ROLE,
  OFFERING_OPTION_NAMES,
  SURVIVOR_ONLY_OFFERING_OPTION_NAMES
)
from normalization import normalize_icon_search_text

OWNER_FIELD_KEYWORDS = (
  "character",
  "killer",
  "owner",
  "power",
  "parent",
  "associated",
  "unlockable",
  "item",
  "category",
  "path",
  "image",
  "icon",
  "api_key"
)

def flatten_owner_values(value):
  if value is None:
    return []

  if isinstance(value, str):
    return [value]

  if isinstance(value, (int, float)):
    return [str(value)]

  if isinstance(value, list):
    values = []

    for item in value:
      values.extend(flatten_owner_values(item))

    return values

  if isinstance(value, dict):
    values = []

    for nested_key, nested_value in value.items():
      values.append(str(nested_key))
      values.extend(flatten_owner_values(nested_value))

    return values

  return [str(value)]

def get_addon_explicit_owner_chunks(addon):
  raw = addon.get("raw", {})

  if not isinstance(raw, dict):
    return []

  owner_values = []

  for key, value in raw.items():
    normalized_key = normalize_icon_search_text(str(key))

    if any(keyword in normalized_key for keyword in OWNER_FIELD_KEYWORDS):
      owner_values.append(str(key))
      owner_values.extend(flatten_owner_values(value))

  owner_values.extend(flatten_owner_values(addon.get("api_key")))

  return [
    normalized_value
    for owner_value in owner_values
    if (normalized_value := normalize_icon_search_text(owner_value))
  ]

def addon_has_explicit_owner_match(addon, owner_terms):
  owner_chunks = get_addon_explicit_owner_chunks(addon)

  if not owner_chunks:
    return None

  normalized_terms = [
    normalize_icon_search_text(owner_term)
    for owner_term in owner_terms
    if normalize_icon_search_text(owner_term)
  ]

  if not normalized_terms:
    return None

  for term in normalized_terms:
    for chunk in owner_chunks:
      if term == chunk:
        return True

      if len(term) >= 5 and term in chunk:
        return True

  return False

def get_offering_option_key(role, option_name):
  return f"{role}:{option_name}"

def get_offering_options_for_role(role):
  option_names = list(OFFERING_OPTION_NAMES)

  if role == "Survivor":
    option_names.extend(SURVIVOR_ONLY_OFFERING_OPTION_NAMES)
  elif role == "Killer":
    option_names.extend(KILLER_ONLY_OFFERING_OPTION_NAMES)

  return [
    {
      "name": option_name,
      "icon_name": OFFERING_ICON_NAME_BY_ROLE[role].get(option_name),
      "icon_key": get_offering_option_key(role, option_name)
    }
    for option_name in option_names
  ]

def get_all_offering_options():
  options = []

  for role in ("Survivor", "Killer"):
    options.extend(get_offering_options_for_role(role))

  return options

def get_survivor_item_addon_terms(item):
  item_name = normalize_icon_search_text(item.get("name", ""))
  raw_text = normalize_icon_search_text(get_searchable_entry_text(item.get("raw", {})))
  combined_text = f"{item_name} {raw_text}"

  if "medkit" in combined_text or "aidkit" in combined_text:
    return ["medkit", "aidkit"]

  if "toolbox" in combined_text or "tools" in combined_text:
    return ["toolbox", "tools"]

  if "flashlight" in combined_text:
    return ["flashlight"]

  if "map" in combined_text:
    return ["map"]

  if "key" in combined_text:
    return ["key"]

  if "vial" in combined_text or "vials" in combined_text:
    return ["vial", "vials"]

  return [item.get("name", "")]

def get_killer_power_name(character):
  character_name = character.get("name", "")

  if character_name in KILLER_POWER_BY_KILLER:
    return KILLER_POWER_BY_KILLER[character_name]

  normalized_character_name = normalize_icon_search_text(character_name)

  for killer_name, power_name in KILLER_POWER_BY_KILLER.items():
    if normalize_icon_search_text(killer_name) == normalized_character_name:
      return power_name

  return "Unknown Power"

def get_killer_addon_terms(character):
  character_name = character.get("name", "")
  power_name = get_killer_power_name(character)

  terms = [
    character_name,
    character_name.replace("The ", "", 1),
    power_name
  ]

  unique_terms = []

  for term in terms:
    normalized_term = normalize_icon_search_text(term)

    if normalized_term and normalized_term not in unique_terms:
      unique_terms.append(normalized_term)

  return unique_terms

def addon_matches_any_owner_term(addon, owner_terms):
  raw = addon.get("raw", {})
  addon_name = addon.get("name", "")

  normalized_addon_name = normalize_icon_search_text(addon_name)
  normalized_basic_addon_name = "".join(ch for ch in addon_name.lower() if ch.isalnum())

  exact_power_key = None

  if normalized_basic_addon_name in KILLER_ADDON_EXACT_POWER_BY_ADDON:
    exact_power_key = KILLER_ADDON_EXACT_POWER_BY_ADDON[normalized_basic_addon_name]
  elif normalized_addon_name in KILLER_ADDON_EXACT_POWER_BY_ADDON:
    exact_power_key = KILLER_ADDON_EXACT_POWER_BY_ADDON[normalized_addon_name]

  if exact_power_key is not None:
    return any(normalize_icon_search_text(owner_term) == exact_power_key for owner_term in owner_terms)

  text = normalize_icon_search_text(f"{addon_name} {get_searchable_entry_text(raw)}")
  return any(normalize_icon_search_text(owner_term) in text for owner_term in owner_terms if normalize_icon_search_text(owner_term))

def choose_matching_addons(addons, owner_terms, addon_count, prefer_explicit_owner=False):
  if addon_count <= 0:
    return []

  if isinstance(owner_terms, str):
    owner_terms = [owner_terms]

  manual_matches = get_manual_killer_addons(addons, owner_terms)
  if manual_matches is not None:
    if len(manual_matches) >= addon_count:
      return random.sample(manual_matches, addon_count)
    return manual_matches

  if prefer_explicit_owner:
    explicit_matches = []
    explicit_non_matches = []

    for addon in addons:
      explicit_match = addon_has_explicit_owner_match(addon, owner_terms)

      if explicit_match is True:
        explicit_matches.append(addon)
      elif explicit_match is False:
        explicit_non_matches.append(addon)

    if len(explicit_matches) >= addon_count:
      return random.sample(explicit_matches, addon_count)

    if explicit_matches and len(explicit_non_matches) > 0:
      return explicit_matches

  matching_addons = [
    addon for addon in addons
    if addon_matches_any_owner_term(addon, owner_terms)
  ]

  if len(matching_addons) >= addon_count:
    return random.sample(matching_addons, addon_count)

  return matching_addons
