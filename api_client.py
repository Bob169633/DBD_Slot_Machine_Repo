import requests

from config import (
  SURVIVOR_PERKS_URL,
  KILLER_PERKS_URL,
  CHARACTERS_URL
)

def extract_name(data, fallback_name):
  if isinstance(data, str):
    return data

  if not isinstance(data, dict):
    return fallback_name

  possible_name_keys = (
    "name",
    "Name",
    "displayName",
    "display_name",
    "perkName",
    "perk_name",
    "characterName",
    "character_name",
    "fullName",
    "full_name",
    "itemName",
    "item_name",
    "addonName",
    "addon_name",
    "offeringName",
    "offering_name"
  )

  for key in possible_name_keys:
    value = data.get(key)

    if isinstance(value, str) and value.strip():
      return value.strip()

  return fallback_name

def get_perk_names(role):
  url = SURVIVOR_PERKS_URL if role == "survivor" else KILLER_PERKS_URL
  response = requests.get(url, timeout=10)
  response.raise_for_status()

  data = response.json()
  perk_names = []

  if isinstance(data, list):
    iterable = enumerate(data)
  elif isinstance(data, dict):
    iterable = data.items()
  else:
    return perk_names

  for key, perk_data in iterable:
    perk_name = extract_name(perk_data, str(key))

    if perk_name:
      perk_names.append(perk_name)

  return sorted(set(perk_names))

def get_character_role(character_data):
  if not isinstance(character_data, dict):
    return ""

  for key in ("role", "Role", "type", "Type", "characterType", "character_type"):
    value = character_data.get(key)

    if isinstance(value, str):
      return value.lower()

  return ""

def role_matches(character_data, role):
  character_role = get_character_role(character_data)

  if role == "survivor":
    return "survivor" in character_role or "camper" in character_role

  return "killer" in character_role or "slasher" in character_role

def get_character_data(role):
  response = requests.get(CHARACTERS_URL, timeout=10)
  response.raise_for_status()

  data = response.json()
  characters = []

  if isinstance(data, list):
    iterable = enumerate(data)
  elif isinstance(data, dict):
    iterable = data.items()
  else:
    return characters

  for key, character_data in iterable:
    if isinstance(character_data, dict) and not role_matches(character_data, role):
      continue

    character_name = extract_name(character_data, str(key))

    if character_name:
      raw_character_data = character_data

      if isinstance(character_data, dict):
        raw_character_data = dict(character_data)
        raw_character_data["_api_key"] = str(key)

      characters.append({
        "name": character_name,
        "raw": raw_character_data,
        "api_key": str(key)
      })

  return sorted(characters, key=lambda character: character["name"])

def get_entry_role(entry):
  if not isinstance(entry, dict):
    return ""

  for key in ("role", "Role", "type", "Type", "ownerRole", "owner_role", "category", "Category"):
    value = entry.get(key)

    if isinstance(value, str):
      return value.lower()

  return ""

def get_searchable_entry_text(entry):
  if not isinstance(entry, dict):
    return str(entry).lower()

  text_parts = []

  for value in entry.values():
    if isinstance(value, str):
      text_parts.append(value)
    elif isinstance(value, (int, float)):
      text_parts.append(str(value))
    elif isinstance(value, list):
      for item in value:
        if isinstance(item, str):
          text_parts.append(item)
        elif isinstance(item, dict):
          text_parts.extend(str(v) for v in item.values() if isinstance(v, str))
    elif isinstance(value, dict):
      text_parts.extend(str(v) for v in value.values() if isinstance(v, str))

  return " ".join(text_parts).lower()

def unlockable_matches_role(entry, role):
  entry_role = get_entry_role(entry)

  if entry_role == "":
    return True

  if role == "survivor":
    return "survivor" in entry_role or "camper" in entry_role

  return "killer" in entry_role or "slasher" in entry_role

def get_unlockable_data(url, role=None):
  response = requests.get(url, timeout=10)
  response.raise_for_status()

  data = response.json()
  unlockables = []

  if isinstance(data, list):
    iterable = enumerate(data)
  elif isinstance(data, dict):
    iterable = data.items()
  else:
    return unlockables

  for key, entry in iterable:
    if role is not None and isinstance(entry, dict):
      if not unlockable_matches_role(entry, role):
        continue

    name = extract_name(entry, str(key))

    if name:
      raw_entry = entry

      if isinstance(entry, dict):
        raw_entry = dict(entry)
        raw_entry["_api_key"] = str(key)

      unlockables.append({
        "name": name,
        "raw": raw_entry,
        "api_key": str(key)
      })

  return sorted(unlockables, key=lambda unlockable: unlockable["name"])
