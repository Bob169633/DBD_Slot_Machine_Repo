from api_client import get_searchable_entry_text
from config import BLOCKED_ADDON_NAMES, BLOCKED_ADDON_TOKENS
from normalization import normalize_icon_search_text, normalize_text

def survivor_item_is_allowed(item):
  name = item.get("name", "")
  raw = item.get("raw", {})
  searchable_text = normalize_text(f"{name} {get_searchable_entry_text(raw)}")

  blocked_terms = (
    "special",
    "event",
    "limited",
    "killer",
    "belonging",
    "collectable",
    "firecracker",
    "flashbang",
    "vaccine",
    "spray",
    "lamentconfiguration",
    "vhs",
    "emp",
    "keycard",
    "turret",
    "invitation",
    "void",
    "haunt",
    "snowball",
    "anniversary",
    "magicitem",
    "magic item",
    "bracers",
    "boots",
    "bootsof",
    "boots of"
  )

  return not any(normalize_text(term) in searchable_text for term in blocked_terms)

def addon_is_allowed(addon):
  addon_name = addon.get("name", "")
  raw = addon.get("raw", {})

  normalized_addon_name = normalize_text(addon_name)
  normalized_icon_addon_name = normalize_icon_search_text(addon_name)
  searchable_text = normalize_text(f"{addon_name} {get_searchable_entry_text(raw)}")

  if normalized_addon_name in BLOCKED_ADDON_NAMES:
    return False

  if normalized_icon_addon_name in BLOCKED_ADDON_NAMES:
    return False

  if any(blocked_name in searchable_text for blocked_name in BLOCKED_ADDON_NAMES):
    return False

  for blocked_token in BLOCKED_ADDON_TOKENS:
    if blocked_token in normalized_addon_name:
      return False
    if blocked_token in normalized_icon_addon_name:
      return False
    if blocked_token in searchable_text:
      return False

  return True
