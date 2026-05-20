import csv
import json
import os
from datetime import datetime

CHECKPOINT_COUNTS = (10, 20, 30, 40)
MAX_SAVED_BUILDS_PER_ROLE = 10

CSV_COLUMNS = (
  "timestamp",
  "event",
  "role",
  "character",
  "result",
  "safe_count",
  "safe_characters",
  "build_json"
)

class BuildHistoryStore:
  def __init__(self, base_folder=None):
    self.base_folder = base_folder or os.path.dirname(os.path.abspath(__file__))

  def get_csv_path(self, role):
    file_name = f"{role.lower()}_build_history.csv"
    return os.path.join(self.base_folder, file_name)

  def ensure_csv_exists(self, role):
    csv_path = self.get_csv_path(role)

    if not os.path.exists(csv_path):
      with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()

    return csv_path

  def append_event(self, role, event, character="", result="", safe_characters=None, build_data=None):
    safe_characters = sorted(safe_characters or [])
    build_data = build_data or {}
    csv_path = self.ensure_csv_exists(role)

    row = {
      "timestamp": datetime.now().isoformat(timespec="seconds"),
      "event": event,
      "role": role,
      "character": character or "",
      "result": result or "",
      "safe_count": len(safe_characters),
      "safe_characters": json.dumps(safe_characters, ensure_ascii=False),
      "build_json": json.dumps(build_data, ensure_ascii=False)
    }

    with open(csv_path, "a", newline="", encoding="utf-8") as csv_file:
      writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
      writer.writerow(row)

  def read_events(self, role):
    csv_path = self.get_csv_path(role)

    if not os.path.exists(csv_path):
      return []

    with open(csv_path, "r", newline="", encoding="utf-8") as csv_file:
      return list(csv.DictReader(csv_file))

  def get_gauntlet_state(self, role):
    safe_characters = set()
    checkpoint_characters = set()
    checkpoint_count = 0

    for row in self.read_events(role):
      event = row.get("event", "")
      character = row.get("character", "")

      if event == "gauntlet_success" and character:
        safe_characters.add(character)

      elif event == "gauntlet_checkpoint":
        stored_characters = self.parse_json_list(row.get("safe_characters", "[]"))
        checkpoint_characters = set(stored_characters)
        checkpoint_count = len(checkpoint_characters)
        safe_characters = set(stored_characters)

      elif event == "gauntlet_reset":
        stored_characters = self.parse_json_list(row.get("safe_characters", "[]"))
        safe_characters = set(stored_characters)
        checkpoint_characters = set(stored_characters)
        checkpoint_count = len(checkpoint_characters)

      elif event == "gauntlet_clear":
        safe_characters = set()
        checkpoint_characters = set()
        checkpoint_count = 0

    return {
      "safe_characters": safe_characters,
      "checkpoint_characters": checkpoint_characters,
      "checkpoint_count": checkpoint_count
    }

  def get_safe_character_names(self, role):
    return self.get_gauntlet_state(role)["safe_characters"]

  def get_gauntlet_display_rows(self, role):
    safe_characters = set()
    checkpoint_snapshots = []

    for row in self.read_events(role):
      event = row.get("event", "")
      character = row.get("character", "")

      if event == "gauntlet_success" and character:
        safe_characters.add(character)

      elif event == "gauntlet_checkpoint":
        stored_characters = set(self.parse_json_list(row.get("safe_characters", "[]")))
        safe_characters = set(stored_characters)
        checkpoint_snapshots.append(set(stored_characters))

      elif event == "gauntlet_reset":
        stored_characters = set(self.parse_json_list(row.get("safe_characters", "[]")))
        safe_characters = set(stored_characters)
        checkpoint_snapshots = [
          snapshot for snapshot in checkpoint_snapshots
          if snapshot.issubset(safe_characters)
        ]

      elif event == "gauntlet_clear":
        safe_characters = set()
        checkpoint_snapshots = []

    display_rows = []
    previous_checkpoint_characters = set()

    for snapshot in checkpoint_snapshots:
      checkpoint_row = sorted(snapshot - previous_checkpoint_characters)
      if checkpoint_row:
        display_rows.append(checkpoint_row)
      previous_checkpoint_characters = set(snapshot)

    current_at_risk_row = sorted(safe_characters - previous_checkpoint_characters)
    if current_at_risk_row:
      if len(previous_checkpoint_characters) >= 40:
        for start_index in range(0, len(current_at_risk_row), 10):
          display_rows.append(current_at_risk_row[start_index:start_index + 10])
      else:
        display_rows.append(current_at_risk_row)

    return display_rows

  def record_build(self, role, build_data):
    state = self.get_gauntlet_state(role)
    character = build_data.get("character") or ""
    self.append_event(
      role,
      "build",
      character=character,
      safe_characters=state["safe_characters"],
      build_data=build_data
    )
    self.trim_saved_builds(role)

  def get_saved_builds(self, role, limit=MAX_SAVED_BUILDS_PER_ROLE):
    builds = []

    for row in reversed(self.read_events(role)):
      if row.get("event") != "build":
        continue

      build_data = self.parse_json_dict(row.get("build_json", "{}"))
      if not build_data:
        continue

      builds.append({
        "timestamp": row.get("timestamp", ""),
        "character": row.get("character", ""),
        "build_data": build_data
      })

      if len(builds) >= limit:
        break

    return builds

  def trim_saved_builds(self, role, max_builds=MAX_SAVED_BUILDS_PER_ROLE):
    csv_path = self.get_csv_path(role)
    events = self.read_events(role)

    if not events:
      return

    build_indices = [index for index, row in enumerate(events) if row.get("event") == "build"]

    if len(build_indices) <= max_builds:
      return

    keep_build_indices = set(build_indices[-max_builds:])
    trimmed_events = [
      row for index, row in enumerate(events)
      if row.get("event") != "build" or index in keep_build_indices
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
      writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
      writer.writeheader()
      writer.writerows(trimmed_events)

  def record_gauntlet_success(self, role, character, result):
    state = self.get_gauntlet_state(role)
    safe_characters = set(state["safe_characters"])
    previous_count = len(safe_characters)
    safe_characters.add(character)

    self.append_event(
      role,
      "gauntlet_success",
      character=character,
      result=result,
      safe_characters=safe_characters
    )

    new_count = len(safe_characters)

    if previous_count < new_count and new_count in CHECKPOINT_COUNTS:
      self.append_event(
        role,
        "gauntlet_checkpoint",
        character=character,
        result=f"Checkpoint reached at {new_count}",
        safe_characters=safe_characters
      )

    return new_count

  def clear_gauntlet(self, role):
    self.append_event(
      role,
      "gauntlet_clear",
      result="Gauntlet cleared",
      safe_characters=[]
    )

  def record_gauntlet_failure_reset(self, role, character, result):
    state = self.get_gauntlet_state(role)
    checkpoint_characters = set(state["checkpoint_characters"])

    self.append_event(
      role,
      "gauntlet_reset",
      character=character,
      result=result,
      safe_characters=checkpoint_characters
    )

    return len(checkpoint_characters)

  def serialize_build(self, role, character, perks, extra_roll):
    addons = extra_roll.get("addons", []) if extra_roll else []
    item = extra_roll.get("item") if extra_roll else None
    offering = extra_roll.get("offering") if extra_roll else None

    return {
      "role": role,
      "character": self.get_name(character),
      "perks": list(perks or []),
      "item": self.get_name(item),
      "addons": [self.get_name(addon) for addon in addons],
      "offering": self.get_name(offering)
    }

  @staticmethod
  def get_name(value):
    if value is None:
      return ""

    if isinstance(value, dict):
      return value.get("name", "")

    return str(value)

  @staticmethod
  def parse_json_list(value):
    try:
      parsed_value = json.loads(value or "[]")
    except json.JSONDecodeError:
      return []

    if isinstance(parsed_value, list):
      return parsed_value

    return []

  @staticmethod
  def parse_json_dict(value):
    try:
      parsed_value = json.loads(value or "{}")
    except json.JSONDecodeError:
      return {}

    if isinstance(parsed_value, dict):
      return parsed_value

    return {}
