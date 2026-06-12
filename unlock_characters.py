import csv
import json
import os
import tkinter as tk
from datetime import datetime

from PIL import Image, ImageTk

from config import BG_COLOR, SLOT_BG_COLOR
from theme import apply_dark_theme

SAVE_FILE_NAMES = {
  "Survivor": "survivor_saves.csv",
  "Killer": "killer_saves.csv"
}

SAVE_COLUMNS = (
  "timestamp",
  "event",
  "role",
  "character",
  "result",
  "safe_count",
  "safe_characters",
  "build_json",
  "data_json"
)

class CharacterUnlockStore:
  def __init__(self, base_folder=None):
    self.base_folder = base_folder or os.path.dirname(os.path.abspath(__file__))

  def get_save_file(self, role):
    return os.path.join(self.base_folder, SAVE_FILE_NAMES[role])

  @staticmethod
  def get_character_names(characters):
    return sorted({
      character["name"]
      for character in characters
      if isinstance(character, dict) and character.get("name")
    })

  def get_unlocked_character_names(self, role, characters):
    all_character_names = self.get_character_names(characters)
    save_file = self.get_save_file(role)

    if not os.path.exists(save_file):
      return set(all_character_names)

    latest_unlocked_names = None

    try:
      with open(save_file, "r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
          if row.get("event") != "character_unlock_state":
            continue

          try:
            latest_unlocked_names = set(json.loads(row.get("data_json", "[]")))
          except json.JSONDecodeError:
            latest_unlocked_names = set()
    except OSError:
      return set(all_character_names)

    if latest_unlocked_names is None:
      return set(all_character_names)

    return latest_unlocked_names.intersection(all_character_names)

  def save_unlocked_character_names(self, role, unlocked_character_names):
    save_file = self.get_save_file(role)
    rows = []

    if os.path.exists(save_file):
      try:
        with open(save_file, "r", newline="", encoding="utf-8") as csv_file:
          reader = csv.DictReader(csv_file)

          for row in reader:
            if row.get("event") != "character_unlock_state":
              rows.append(row)
      except OSError:
        rows = []

    rows.append({
      "timestamp": datetime.now().isoformat(timespec="seconds"),
      "event": "character_unlock_state",
      "role": role,
      "character": "",
      "result": "",
      "safe_count": "",
      "safe_characters": "",
      "build_json": "",
      "data_json": json.dumps(sorted(unlocked_character_names), ensure_ascii=False)
    })

    with open(save_file, "w", newline="", encoding="utf-8") as csv_file:
      writer = csv.DictWriter(csv_file, fieldnames=SAVE_COLUMNS)
      writer.writeheader()

      for row in rows:
        writer.writerow({
          column: row.get(column, "")
          for column in SAVE_COLUMNS
        })


def grab_window_attention(window, parent):
  window.transient(parent)
  window.lift()
  window.focus_force()
  window.grab_set()

  try:
    window.attributes("-topmost", True)
    window.after(250, lambda: window.attributes("-topmost", False))
  except tk.TclError:
    pass


def open_unlock_characters_window(
  parent,
  role,
  characters,
  portrait_files,
  unlocked_character_names,
  on_save,
  icon_size=64
):
  window = tk.Toplevel(parent)
  window.title(f"Unlock {role} Characters")
  window.geometry("900x650")
  window.minsize(650, 420)
  window.resizable(True, True)
  window.config(bg=BG_COLOR)
  grab_window_attention(window, parent)

  title_label = tk.Label(
    window,
    text=f"Select Unlocked {role}s",
    font=("Arial", 18, "bold"),
    bg=BG_COLOR,
    fg="white"
  )
  title_label.pack(pady=8)

  instruction_label = tk.Label(
    window,
    text="Click a character to toggle whether they can appear in random rolls.",
    font=("Arial", 11, "bold"),
    bg=BG_COLOR,
    fg="white"
  )
  instruction_label.pack(pady=(0, 8))

  canvas_frame = tk.Frame(window, bg=BG_COLOR)
  canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)

  canvas = tk.Canvas(canvas_frame, bg=BG_COLOR, highlightthickness=0)
  scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
  character_frame = tk.Frame(canvas, bg=BG_COLOR)

  character_frame.bind(
    "<Configure>",
    lambda event: canvas.configure(scrollregion=canvas.bbox("all"))
  )

  canvas_window = canvas.create_window((0, 0), window=character_frame, anchor="nw")
  canvas.configure(yscrollcommand=scrollbar.set)
  canvas.pack(side="left", fill="both", expand=True)
  scrollbar.pack(side="right", fill="y")

  selected_names = set(unlocked_character_names)
  portrait_images = []
  tile_widgets = {}
  tile_width = 100
  tile_height = 120

  def resize_character_frame(event):
    canvas.itemconfig(canvas_window, width=event.width)

  def on_mouse_wheel(event):
    if getattr(event, "delta", 0):
      canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    elif getattr(event, "num", None) == 4:
      canvas.yview_scroll(-1, "units")
    elif getattr(event, "num", None) == 5:
      canvas.yview_scroll(1, "units")

  def bind_mouse_wheel(event=None):
    canvas.bind_all("<MouseWheel>", on_mouse_wheel)
    canvas.bind_all("<Button-4>", on_mouse_wheel)
    canvas.bind_all("<Button-5>", on_mouse_wheel)

  def unbind_mouse_wheel(event=None):
    canvas.unbind_all("<MouseWheel>")
    canvas.unbind_all("<Button-4>")
    canvas.unbind_all("<Button-5>")

  canvas.bind("<Enter>", bind_mouse_wheel)
  canvas.bind("<Leave>", unbind_mouse_wheel)
  window.bind("<Destroy>", unbind_mouse_wheel)

  def update_tile_style(character_name):
    tile = tile_widgets[character_name]["tile"]
    status_label = tile_widgets[character_name]["status"]

    if character_name in selected_names:
      tile.config(highlightbackground="#50c878", highlightcolor="#50c878")
      status_label.config(text="Unlocked", fg="#50c878")
    else:
      tile.config(highlightbackground="#777777", highlightcolor="#777777")
      status_label.config(text="Locked", fg="#ff6666")

  def toggle_character(character_name):
    if character_name in selected_names:
      selected_names.remove(character_name)
    else:
      selected_names.add(character_name)

    update_tile_style(character_name)

  def build_character_tile(character):
    character_name = character["name"]

    tile = tk.Frame(
      character_frame,
      bg=BG_COLOR,
      width=tile_width,
      height=tile_height,
      highlightthickness=2,
      highlightbackground="#777777"
    )
    tile.grid_propagate(False)

    portrait_label = tk.Label(tile, bg=BG_COLOR)
    portrait_label.pack(pady=(5, 2))

    portrait_path = portrait_files.get(character_name)

    if portrait_path and os.path.exists(portrait_path):
      try:
        image = Image.open(portrait_path).resize((icon_size, icon_size))
        portrait_image = ImageTk.PhotoImage(image)
        portrait_images.append(portrait_image)
        portrait_label.config(image=portrait_image)
        portrait_label.image = portrait_image
      except Exception:
        portrait_label.config(text="No\nPortrait", font=("Arial", 8, "bold"), fg="white", bg=SLOT_BG_COLOR)
    else:
      portrait_label.config(text="No\nPortrait", font=("Arial", 8, "bold"), fg="white", bg=SLOT_BG_COLOR)

    name_label = tk.Label(
      tile,
      text=character_name,
      font=("Arial", 8, "bold"),
      wraplength=88,
      justify="center",
      bg=BG_COLOR,
      fg="white"
    )
    name_label.pack()

    status_label = tk.Label(tile, text="", font=("Arial", 8, "bold"), bg=BG_COLOR)
    status_label.pack()

    tile_widgets[character_name] = {
      "tile": tile,
      "status": status_label
    }

    for widget in (tile, portrait_label, name_label, status_label):
      widget.bind("<Button-1>", lambda event, name=character_name: toggle_character(name))

    update_tile_style(character_name)
    return tile

  sorted_characters = sorted(characters, key=lambda character: character["name"])
  tiles = [build_character_tile(character) for character in sorted_characters]

  def arrange_character_tiles(event=None):
    available_width = max(canvas.winfo_width(), 1)
    columns = max(1, available_width // (tile_width + 14))

    for index, tile in enumerate(tiles):
      row = index // columns
      column = index % columns
      tile.grid(row=row, column=column, padx=6, pady=6, sticky="n")

    character_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

  canvas.bind("<Configure>", lambda event: (resize_character_frame(event), arrange_character_tiles(event)))
  window.after(50, arrange_character_tiles)

  button_frame = tk.Frame(window, bg=BG_COLOR)
  button_frame.pack(fill="x", pady=8)

  def select_all():
    selected_names.clear()
    selected_names.update(character["name"] for character in characters)
    for character_name in tile_widgets:
      update_tile_style(character_name)

  def clear_all():
    selected_names.clear()
    for character_name in tile_widgets:
      update_tile_style(character_name)

  def save_and_close():
    on_save(set(selected_names))
    window.destroy()

  tk.Button(
    button_frame,
    text="Select All",
    font=("Arial", 11, "bold"),
    command=select_all
  ).pack(side="left", padx=8)

  tk.Button(
    button_frame,
    text="Clear All",
    font=("Arial", 11, "bold"),
    command=clear_all
  ).pack(side="left", padx=8)

  tk.Button(
    button_frame,
    text="Save",
    font=("Arial", 11, "bold"),
    command=save_and_close
  ).pack(side="right", padx=8)

  tk.Button(
    button_frame,
    text="Cancel",
    font=("Arial", 11, "bold"),
    command=window.destroy
  ).pack(side="right", padx=8)

  window.portrait_images = portrait_images
  apply_dark_theme(window)
