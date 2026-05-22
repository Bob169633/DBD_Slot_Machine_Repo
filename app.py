import math
import os
import random
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk

from config import (
  BG_COLOR,
  KILLER_POWER_EXACT_ICON_FILES,
  KILLER_POWER_RANDOM_ICON_ALIASES,
  SLOT_BG_COLOR,
  SOURCE_ADDON_ICON_FOLDER,
  SOURCE_ITEM_ICON_FOLDER,
  SOURCE_POWER_ICON_FOLDER
)
from game_rules import (
  choose_matching_addons,
  get_killer_addon_terms,
  get_killer_power_name,
  get_offering_options_for_role,
  get_survivor_item_addon_terms
)
from gauntlet_history import BuildHistoryStore
from icon_utils import (
  build_character_portrait_files,
  build_killer_power_icon_files,
  build_offering_option_icon_files,
  build_perk_icon_files,
  build_unlockable_icon_files,
  clean_power_file_name,
  get_png_files_from_folder,
  print_missing_icon_matches
)
from normalization import normalize_icon_search_text
from theme import apply_dark_theme, reset_image_label

class BuildSlotMachineApp:
  def __init__(
    self,
    root,
    survivor_perks,
    killer_perks,
    survivor_characters,
    killer_characters,
    survivor_items,
    survivor_addons,
    killer_addons,
    debug_mode=False
  ):
    self.root = root
    self.root.title("DBD Build Slot Machine")
    self.root.geometry("1600x1200")
    self.root.minsize(1100, 760)
    self.root.resizable(True, True)
    self.root.config(bg=BG_COLOR)
    self.debug_mode = debug_mode

    self.survivor_perks = survivor_perks
    self.killer_perks = killer_perks
    self.survivor_characters = survivor_characters
    self.killer_characters = killer_characters
    self.survivor_items = survivor_items
    self.survivor_addons = survivor_addons
    self.killer_addons = killer_addons

    self.selected_role = tk.StringVar(value="Survivor")
    self.current_role = "Survivor"
    self.loading_role_settings = False

    self.role_settings = {
      "Survivor": {
        "perk_count": 4,
        "addon_count": 2,
        "include_character": True,
        "include_item": True,
        "include_offering": True
      },
      "Killer": {
        "perk_count": 4,
        "addon_count": 2,
        "include_character": True,
        "include_item": False,
        "include_offering": True
      }
    }

    self.last_rolls = {"Survivor": None, "Killer": None}
    self.history_store = BuildHistoryStore()
    self.gauntlet_stats = {
      "Survivor": {
        "current_streak": 0,
        "max_streak": 0,
        "failure_count": 0
      },
      "Killer": {
        "current_streak": 0,
        "max_streak": 0,
        "failure_count": 0
      }
    }
    self.gauntlet_result_pending = {
      "Survivor": False,
      "Killer": False
    }

    self.addon_count = tk.IntVar(value=2)
    self.include_character = tk.BooleanVar(value=True)
    self.include_item = tk.BooleanVar(value=True)
    self.include_offering = tk.BooleanVar(value=True)
    self.save_builds_to_csv = tk.BooleanVar(value=False)
    self.gauntlet_enabled = tk.BooleanVar(value=False)

    self.debug_character_choice = tk.StringVar(value="Random")
    self.debug_item_choice = tk.StringVar(value="Random")
    self.debug_addon_1_choice = tk.StringVar(value="Random")
    self.debug_addon_2_choice = tk.StringVar(value="Random")
    self.debug_offering_choice = tk.StringVar(value="Random")
    self.debug_gauntlet_spin_count = tk.StringVar(value="10")
    self.debug_auto_gauntlet_running = False
    self.debug_auto_gauntlet_remaining = 0

    self.icon_images = {}
    self.character_portrait_images = {}
    self.item_images = {}
    self.addon_images = {}
    self.offering_images = {}
    self.power_images = {}
    self.background_images = []
    self.background_items = []
    self.background_animation_job = None
    self.background_rebuild_job = None
    self.background_spawn_job = None
    self.pending_background_paths = []
    self.pending_background_cells = []
    self.background_shared_speed = 0.75
    self.fullscreen_enabled = False
    self.ui_scale = 1.0
    self.resize_job = None
    self.perk_icon_size = 140
    self.character_portrait_size = 155
    self.extra_icon_size = 54
    self.gauntlet_portrait_size = 48
    self.background_icon_size = 64
    self.background_icon_gap = 14
    self.background_icon_count = 42
    self.spin_animation_jobs = []
    self.is_spinning = False
    self.spin_frame_count = 34
    self.spin_frame_delay_ms = 55
    self.spin_slow_frame_count = 9
    self.spin_final_fake_min_delay_ms = 700
    self.spin_final_fake_max_delay_ms = 1800
    self.final_flash_count = 16
    self.final_flash_delay_ms = 150
    self.debug_auto_gauntlet_speed_multiplier = 0.25
    self.spin_slot_frame_colors = [
      "#c2185b",
      "#7b1fa2",
      "#303f9f",
      "#0288d1",
      "#00796b",
      "#689f38",
      "#fbc02d",
      "#f57c00",
      "#d32f2f"
    ]
    # Tkinter child widgets do not support true alpha transparency.
    # Use glass-style slot panels instead of opaque filled panels so the
    # animated background remains visually dominant around the slot content.
    self.slot_panel_bg_color = BG_COLOR
    self.slot_panel_border_color = "#555555"

    self.load_icon_maps()
    self.build_background_effect()
    self.build_gui()
    self.bind_responsive_events()

    apply_dark_theme(root)
    self.update_role_display()
    self.apply_responsive_layout(force=True)

  def load_icon_maps(self):
    all_perks = self.get_all_perks()
    all_characters = self.get_all_characters()
    all_addons = self.get_all_addons()

    self.perk_icon_files = build_perk_icon_files(all_perks)
    self.character_portrait_files = build_character_portrait_files(all_characters)
    self.item_icon_files = build_unlockable_icon_files(self.survivor_items, SOURCE_ITEM_ICON_FOLDER)
    self.addon_icon_files = build_unlockable_icon_files(all_addons, SOURCE_ADDON_ICON_FOLDER)
    self.offering_icon_files = build_offering_option_icon_files()
    self.power_icon_files = build_killer_power_icon_files(self.killer_characters)

    print_missing_icon_matches("perk", self.perk_icon_files, all_perks)
    print_missing_icon_matches("character portrait", self.character_portrait_files, [character["name"] for character in all_characters])
    print_missing_icon_matches("item", self.item_icon_files, self.survivor_items)
    print_missing_icon_matches("add-on", self.addon_icon_files, all_addons)

    for perk_name, file_path in self.perk_icon_files.items():
      if os.path.exists(file_path):
        image = Image.open(file_path).resize((self.perk_icon_size, self.perk_icon_size))
        self.icon_images[perk_name] = ImageTk.PhotoImage(image)

  def build_background_effect(self):
    self.background_canvas = tk.Canvas(
      self.root,
      bg=BG_COLOR,
      highlightthickness=0,
      borderwidth=0
    )
    self.background_canvas.place(x=0, y=0, relwidth=1, relheight=1)
    self.lower_background_canvas()
    self.background_canvas.bind("<Configure>", self.schedule_background_rebuild)
    self.root.after(250, lambda: self.schedule_background_rebuild(clear_now=True))


  def lower_background_canvas(self):
    if not hasattr(self, "background_canvas"):
      return

    try:
      self.background_canvas.tk.call("lower", self.background_canvas._w)
    except tk.TclError:
      pass

  def get_available_background_portrait_paths(self):
    portrait_paths = []

    for portrait_path in self.character_portrait_files.values():
      if portrait_path and os.path.exists(portrait_path):
        portrait_paths.append(portrait_path)

    return sorted(set(portrait_paths))

  def schedule_background_rebuild(self, event=None, clear_now=True):
    if not hasattr(self, "background_canvas"):
      return

    if self.background_rebuild_job is not None:
      self.root.after_cancel(self.background_rebuild_job)
      self.background_rebuild_job = None

    if self.background_spawn_job is not None:
      self.root.after_cancel(self.background_spawn_job)
      self.background_spawn_job = None

    if clear_now:
      self.clear_background_icons()

    self.reset_background_icons()

  def clear_background_icons(self):
    if not hasattr(self, "background_canvas"):
      return

    if self.background_animation_job is not None:
      self.root.after_cancel(self.background_animation_job)
      self.background_animation_job = None

    self.background_canvas.delete("all")
    self.background_images = []
    self.background_items = []
    self.pending_background_paths = []
    self.pending_background_cells = []
    self.background_canvas.config(bg=BG_COLOR)
    self.lower_background_canvas()

  def reset_background_icons(self, event=None):
    if not hasattr(self, "background_canvas"):
      return

    self.background_rebuild_job = None
    portrait_paths = self.get_available_background_portrait_paths()
    self.clear_background_icons()

    if not portrait_paths:
      return

    width = max(self.background_canvas.winfo_width(), self.root.winfo_width(), 800)
    height = max(self.background_canvas.winfo_height(), self.root.winfo_height(), 600)
    cell_size = self.background_icon_size + self.background_icon_gap
    columns = max(1, width // cell_size)
    visible_rows = max(1, height // cell_size + 3)
    max_non_overlapping_icons = columns * visible_rows
    icon_count = min(self.background_icon_count, max_non_overlapping_icons)

    cells = [(column, row) for row in range(visible_rows) for column in range(columns)]
    random.shuffle(cells)

    self.pending_background_paths = portrait_paths
    self.pending_background_cells = cells[:icon_count]
    self.background_shared_speed = random.uniform(0.55, 0.9)
    self.spawn_background_icons_batch()

  def spawn_background_icons_batch(self):
    if not hasattr(self, "background_canvas") or not self.pending_background_cells:
      self.background_spawn_job = None
      if self.background_items:
        self.animate_background_icons()
      return

    width = max(self.background_canvas.winfo_width(), self.root.winfo_width(), 800)
    cell_size = self.background_icon_size + self.background_icon_gap
    batch_size = max(4, min(12, self.background_icon_count // 10))

    for _ in range(min(batch_size, len(self.pending_background_cells))):
      column, row = self.pending_background_cells.pop(0)
      portrait_path = random.choice(self.pending_background_paths)

      try:
        image = Image.open(portrait_path).convert("RGBA").resize(
          (self.background_icon_size, self.background_icon_size)
        )
        image.putalpha(58)
        photo_image = ImageTk.PhotoImage(image)
      except Exception:
        continue

      x_position = min(
        max(0, column * cell_size + self.background_icon_gap // 2),
        max(0, width - self.background_icon_size)
      )
      # Start every background icon above the visible window so icons drift in
      # naturally instead of appearing already spawned inside the GUI.
      y_position = -((row + 1) * cell_size)
      horizontal_speed = random.choice([-1, 1]) * random.uniform(0.2, 0.75)
      vertical_speed = self.background_shared_speed + random.uniform(-0.08, 0.12)

      item_id = self.background_canvas.create_image(
        x_position,
        y_position,
        image=photo_image,
        anchor="nw"
      )

      self.background_images.append(photo_image)
      self.background_items.append({
        "item_id": item_id,
        "dx": horizontal_speed,
        "dy": vertical_speed,
        "column": column,
        "cell_size": cell_size
      })

    self.lower_background_canvas()

    if self.pending_background_cells:
      self.background_spawn_job = self.root.after(80, self.spawn_background_icons_batch)
    else:
      self.background_spawn_job = None
      self.animate_background_icons()

  def animate_background_icons(self):
    if not hasattr(self, "background_canvas") or not self.background_items:
      return

    width = max(self.background_canvas.winfo_width(), self.root.winfo_width(), 800)
    height = max(self.background_canvas.winfo_height(), self.root.winfo_height(), 600)
    icon_size = self.background_icon_size

    for background_item in self.background_items:
      item_id = background_item["item_id"]
      self.background_canvas.move(
        item_id,
        background_item.get("dx", 0.35),
        background_item.get("dy", 0.75)
      )
      coords = self.background_canvas.coords(item_id)

      if not coords:
        continue

      x_position, y_position = coords

      if x_position <= 0:
        x_position = 0
        background_item["dx"] = abs(background_item.get("dx", 0.35))
        self.background_canvas.coords(item_id, x_position, y_position)
      elif x_position >= width - icon_size:
        x_position = max(0, width - icon_size)
        background_item["dx"] = -abs(background_item.get("dx", 0.35))
        self.background_canvas.coords(item_id, x_position, y_position)

      if y_position > height + icon_size:
        top_y = min(
          [self.background_canvas.coords(other["item_id"])[1] for other in self.background_items if other is not background_item and self.background_canvas.coords(other["item_id"])]
          or [0]
        )
        y_position = top_y - background_item.get("cell_size", icon_size + self.background_icon_gap)
        x_position = random.randint(0, max(0, width - icon_size))
        background_item["dx"] = random.choice([-1, 1]) * random.uniform(0.2, 0.75)
        self.background_canvas.coords(item_id, x_position, y_position)

    self.resolve_background_icon_collisions(width, height)
    self.lower_background_canvas()
    self.background_animation_job = self.root.after(35, self.animate_background_icons)

  def resolve_background_icon_collisions(self, width, height):
    icon_size = self.background_icon_size
    padding = max(2, self.background_icon_gap // 3)
    minimum_distance = icon_size + padding

    for index, first_item in enumerate(self.background_items):
      first_coords = self.background_canvas.coords(first_item["item_id"])

      if not first_coords:
        continue

      first_x, first_y = first_coords

      for second_item in self.background_items[index + 1:]:
        second_coords = self.background_canvas.coords(second_item["item_id"])

        if not second_coords:
          continue

        second_x, second_y = second_coords
        horizontal_overlap = abs(first_x - second_x) < minimum_distance
        vertical_overlap = abs(first_y - second_y) < minimum_distance

        if not horizontal_overlap or not vertical_overlap:
          continue

        if first_x <= second_x:
          push_direction = -1
        else:
          push_direction = 1

        overlap_amount = minimum_distance - abs(first_x - second_x)
        push_amount = max(1, overlap_amount / 2)

        first_x = max(0, min(width - icon_size, first_x + push_direction * push_amount))
        second_x = max(0, min(width - icon_size, second_x - push_direction * push_amount))

        first_item["dx"] = -abs(first_item.get("dx", 0.35)) if push_direction < 0 else abs(first_item.get("dx", 0.35))
        second_item["dx"] = abs(second_item.get("dx", 0.35)) if push_direction < 0 else -abs(second_item.get("dx", 0.35))

        self.background_canvas.coords(first_item["item_id"], first_x, first_y)
        self.background_canvas.coords(second_item["item_id"], second_x, second_y)

  def bind_responsive_events(self):
    self.root.bind("<F11>", self.toggle_fullscreen)
    self.root.bind("<Escape>", self.exit_fullscreen)
    self.root.bind("<Configure>", self.schedule_responsive_layout)

  def toggle_fullscreen(self, event=None):
    self.fullscreen_enabled = not self.fullscreen_enabled
    try:
      self.root.attributes("-fullscreen", self.fullscreen_enabled)
    except tk.TclError:
      if self.fullscreen_enabled:
        self.root.state("zoomed")
      else:
        self.root.state("normal")
    self.apply_responsive_layout(force=True)

  def exit_fullscreen(self, event=None):
    if not self.fullscreen_enabled:
      return

    self.fullscreen_enabled = False
    try:
      self.root.attributes("-fullscreen", False)
    except tk.TclError:
      self.root.state("normal")
    self.apply_responsive_layout(force=True)

  def schedule_responsive_layout(self, event=None):
    if event is not None and event.widget is not self.root:
      return

    if self.resize_job is not None:
      self.root.after_cancel(self.resize_job)

    self.resize_job = self.root.after(120, self.apply_responsive_layout)

  def get_responsive_scale(self):
    width = max(self.root.winfo_width(), 1)
    height = max(self.root.winfo_height(), 1)
    width_scale = width / 1600
    height_scale = height / 1200
    return max(0.62, min(1.25, min(width_scale, height_scale)))

  def scaled(self, value, minimum=None):
    scaled_value = int(round(value * self.ui_scale))

    if minimum is not None:
      scaled_value = max(minimum, scaled_value)

    return scaled_value

  def scaled_font(self, size, minimum=7):
    return max(minimum, int(round(size * self.ui_scale)))

  def apply_responsive_layout(self, force=False):
    self.resize_job = None
    new_scale = self.get_responsive_scale()

    if not force and abs(new_scale - self.ui_scale) < 0.04:
      return

    self.ui_scale = new_scale
    self.perk_icon_size = self.scaled(140, 78)
    self.character_portrait_size = self.scaled(155, 86)
    self.extra_icon_size = self.scaled(54, 34)
    self.gauntlet_portrait_size = self.scaled(48, 32)
    self.background_icon_size = self.scaled(105, 54)
    self.background_icon_gap = self.scaled(14, 8)
    self.background_icon_count = max(48, min(140, int(88 * max(0.75, self.ui_scale))))

    if hasattr(self, "title_label"):
      self.title_label.config(font=("Arial", self.scaled_font(24, 14), "bold"))

    if hasattr(self, "role_label"):
      self.role_label.config(font=("Arial", self.scaled_font(14, 9), "bold"))

    for widget_name in ("survivor_role_button", "killer_role_button"):
      if hasattr(self, widget_name):
        getattr(self, widget_name).config(font=("Arial", self.scaled_font(14, 9)), width=max(9, self.scaled(12, 9)))

    if hasattr(self, "lever_label"):
      self.lever_label.config(font=("Arial", self.scaled_font(13, 9), "bold"))

    if hasattr(self, "character_slot_container"):
      self.character_slot_container.config(width=self.scaled(220, 132), height=self.scaled(250, 150))
      self.character_title_label.config(font=("Arial", self.scaled_font(14, 9), "bold"))
      self.character_name_label.config(font=("Arial", self.scaled_font(13, 8), "bold"), wraplength=self.scaled(200, 110))

    if hasattr(self, "slots"):
      for slot in self.slots:
        slot["container"].config(width=self.scaled(190, 112), height=self.scaled(250, 150))
        slot["name"].config(font=("Arial", self.scaled_font(10, 7), "bold"), wraplength=self.scaled(170, 95))
        if slot["title"] is not None:
          slot["title"].config(font=("Arial", self.scaled_font(9, 7), "bold"))

    if hasattr(self, "extra_slots"):
      for slot in self.extra_slots:
        slot["container"].config(width=self.scaled(190, 112), height=self.scaled(120, 78))
        slot["name"].config(font=("Arial", self.scaled_font(8, 7), "bold"), wraplength=self.scaled(170, 95))
        if slot["title"] is not None:
          slot["title"].config(font=("Arial", self.scaled_font(9, 7), "bold"))

    if hasattr(self, "perk_count_label"):
      self.perk_count_label.config(font=("Arial", self.scaled_font(13, 8), "bold"))
      self.perk_count_slider.config(length=self.scaled(220, 130))
      self.addon_count_label.config(font=("Arial", self.scaled_font(13, 8), "bold"))
      self.addon_count_slider.config(length=self.scaled(160, 100))

    for widget_name in (
      "include_character_checkbox", "include_item_checkbox", "include_offering_checkbox",
      "save_builds_checkbox", "gauntlet_checkbox",
      "debug_character_label", "debug_item_label", "debug_addon_1_label",
      "debug_addon_2_label", "debug_offering_label", "debug_gauntlet_spin_label"
    ):
      if hasattr(self, widget_name):
        getattr(self, widget_name).config(font=("Arial", self.scaled_font(12, 8), "bold"))

    if hasattr(self, "result_label"):
      self.result_label.config(font=("Arial", self.scaled_font(12, 8)))
      self.randomize_button.config(font=("Arial", self.scaled_font(14, 9), "bold"), width=max(10, self.scaled(14, 10)))
      self.gauntlet_success_button.config(font=("Arial", self.scaled_font(11, 8), "bold"), width=max(8, self.scaled(10, 8)))
      self.gauntlet_failure_button.config(font=("Arial", self.scaled_font(11, 8), "bold"), width=max(8, self.scaled(10, 8)))
      self.clear_gauntlet_button.config(font=("Arial", self.scaled_font(11, 8), "bold"), width=max(15, self.scaled(18, 15)))
      self.load_survivor_build_button.config(font=("Arial", self.scaled_font(10, 8), "bold"), width=max(11, self.scaled(14, 11)))
      self.load_killer_build_button.config(font=("Arial", self.scaled_font(10, 8), "bold"), width=max(11, self.scaled(14, 11)))
      self.gauntlet_streak_label.config(font=("Arial", self.scaled_font(10, 8), "bold"))
      self.gauntlet_played_title_label.config(font=("Arial", self.scaled_font(9, 8), "bold"))

    self.refresh_scaled_images()
    self.update_gauntlet_played_display()
    self.root.after(50, lambda: self.schedule_background_rebuild(clear_now=True))

  def refresh_scaled_images(self):
    self.icon_images = {}

    for perk_name, file_path in self.perk_icon_files.items():
      if os.path.exists(file_path):
        try:
          image = Image.open(file_path).resize((self.perk_icon_size, self.perk_icon_size))
          self.icon_images[perk_name] = ImageTk.PhotoImage(image)
        except Exception:
          pass

    current_roll = self.last_rolls.get(self.current_role)

    if current_roll is None:
      return

    self.display_character(current_roll.get("character"))
    self.display_perks(current_roll.get("perks", []))
    self.display_extra_roll(self.current_role, current_roll.get("character"), current_roll.get("extra_roll", {}))

  def build_gui(self):
    self.title_label = tk.Label(self.root, text="DBD Build Slot Machine", font=("Arial", 24, "bold"))
    self.title_label.pack(pady=2)

    self.build_role_controls()
    self.build_character_and_perk_slots()
    self.build_extra_slots()
    self.build_slider_controls()
    self.build_debug_controls()
    self.build_randomize_controls()

  def build_role_controls(self):
    self.role_frame = tk.Frame(self.root)
    self.role_frame.pack(pady=1)

    self.role_label = tk.Label(self.role_frame, text="Role:", font=("Arial", 14, "bold"))
    self.role_label.pack(side="left", padx=10)

    self.survivor_role_button = tk.Radiobutton(
      self.role_frame,
      text="Survivor",
      variable=self.selected_role,
      value="Survivor",
      font=("Arial", 14),
      indicatoron=False,
      width=12,
      command=self.update_role_display
    )
    self.survivor_role_button.pack(side="left", padx=5)

    self.killer_role_button = tk.Radiobutton(
      self.role_frame,
      text="Killer",
      variable=self.selected_role,
      value="Killer",
      font=("Arial", 14),
      indicatoron=False,
      width=12,
      command=self.update_role_display
    )
    self.killer_role_button.pack(side="left", padx=5)


    self.lever_label = tk.Label(self.root, text="Lever set to: Survivor", font=("Arial", 13, "bold"))
    self.lever_label.pack(pady=1)

  def build_character_and_perk_slots(self):
    self.main_slot_frame = tk.Frame(self.root)
    self.main_slot_frame.pack(pady=2)

    self.character_slot_container = tk.Frame(
      self.main_slot_frame,
      relief="ridge",
      borderwidth=2,
      highlightthickness=1,
      highlightbackground=self.slot_panel_border_color,
      width=220,
      height=250,
      bg=self.slot_panel_bg_color
    )
    self.character_slot_container.pack(side="left", padx=5)
    self.character_slot_container.pack_propagate(False)

    self.character_title_label = tk.Label(self.character_slot_container, text="Survivor Slot", font=("Arial", 14, "bold"), bg=self.slot_panel_bg_color)
    self.character_title_label.pack(pady=2)

    self.character_portrait_label = tk.Label(self.character_slot_container, bg=self.slot_panel_bg_color)
    self.character_portrait_label.pack(pady=2)

    self.character_name_label = tk.Label(
      self.character_slot_container,
      text="???",
      font=("Arial", 13, "bold"),
      wraplength=200,
      justify="center",
      bg=self.slot_panel_bg_color
    )
    self.character_name_label.pack(pady=2)

    self.slot_frame = tk.Frame(self.main_slot_frame)
    self.slot_frame.pack(side="left", padx=8)

    self.slots = [self.create_slot(self.slot_frame, 190, 250, ("Arial", 10, "bold"), 170) for _ in range(4)]

  def build_extra_slots(self):
    self.extra_slot_frame = tk.Frame(self.root)
    self.extra_slot_frame.pack(pady=2)

    self.extra_slots = []

    for slot_title in ("Item", "Add-on 1", "Add-on 2", "Offering"):
      slot = self.create_slot(self.extra_slot_frame, 190, 120, ("Arial", 8, "bold"), 170, title=slot_title)
      self.extra_slots.append(slot)

  def create_slot(self, parent, width, height, name_font, wraplength, title=None):
    slot_container = tk.Frame(
      parent,
      relief="ridge",
      borderwidth=2,
      highlightthickness=1,
      highlightbackground=self.slot_panel_border_color,
      width=width,
      height=height,
      bg=self.slot_panel_bg_color
    )
    slot_container.pack(side="left", padx=5)
    slot_container.pack_propagate(False)

    title_label = None
    if title is not None:
      title_label = tk.Label(slot_container, text=title, font=("Arial", 9, "bold"), bg=self.slot_panel_bg_color)
      title_label.pack(pady=2)

    icon_label = tk.Label(slot_container, bg=self.slot_panel_bg_color)
    icon_label.pack(pady=6 if title is None else 1)

    name_label = tk.Label(slot_container, text="???", font=name_font, wraplength=wraplength, justify="center", bg=self.slot_panel_bg_color)
    name_label.pack(pady=3 if title is None else 1)

    return {
      "container": slot_container,
      "title": title_label,
      "icon": icon_label,
      "name": name_label
    }

  def build_slider_controls(self):
    self.slider_frame = tk.Frame(self.root)
    self.slider_frame.pack(pady=2)

    self.perk_count_label = tk.Label(self.slider_frame, text="Number of Perks: 4", font=("Arial", 13, "bold"))
    self.perk_count_label.pack(side="left", padx=10)

    self.perk_count_slider = tk.Scale(
      self.slider_frame,
      from_=0,
      to=4,
      orient="horizontal",
      length=220,
      tickinterval=1,
      command=self.update_perk_count_label
    )
    self.perk_count_slider.set(4)
    self.perk_count_slider.pack(side="left")

    self.addon_count_label = tk.Label(self.slider_frame, text="Number of Add-ons: 2", font=("Arial", 13, "bold"))
    self.addon_count_label.pack(side="left", padx=(35, 10))

    self.addon_count_slider = tk.Scale(
      self.slider_frame,
      from_=0,
      to=2,
      orient="horizontal",
      length=160,
      tickinterval=1,
      variable=self.addon_count,
      command=self.update_addon_count_label
    )
    self.addon_count_slider.pack(side="left", padx=10)

    self.extra_control_frame = tk.Frame(self.root)
    self.extra_control_frame.pack(pady=2)

    self.include_character_checkbox = tk.Checkbutton(
      self.extra_control_frame,
      text="Random Character",
      variable=self.include_character,
      font=("Arial", 12, "bold"),
      command=self.update_include_character_setting
    )
    self.include_character_checkbox.pack(side="left", padx=10)

    self.include_item_checkbox = tk.Checkbutton(
      self.extra_control_frame,
      text="Include Item",
      variable=self.include_item,
      font=("Arial", 12, "bold"),
      command=self.update_include_item_setting
    )
    self.include_item_checkbox.pack(side="left", padx=10)

    self.include_offering_checkbox = tk.Checkbutton(
      self.extra_control_frame,
      text="Include Offering",
      variable=self.include_offering,
      font=("Arial", 12, "bold"),
      command=self.update_include_offering_setting
    )
    self.include_offering_checkbox.pack(side="left", padx=10)

    self.save_builds_checkbox = tk.Checkbutton(
      self.extra_control_frame,
      text="Save Builds",
      variable=self.save_builds_to_csv,
      font=("Arial", 12, "bold")
    )
    self.save_builds_checkbox.pack(side="left", padx=10)

    self.gauntlet_checkbox = tk.Checkbutton(
      self.extra_control_frame,
      text="Gauntlet",
      variable=self.gauntlet_enabled,
      font=("Arial", 12, "bold"),
      command=self.update_gauntlet_controls
    )
    self.gauntlet_checkbox.pack(side="left", padx=10)


  def build_debug_controls(self):
    if not self.debug_mode:
      return

    self.debug_frame = tk.LabelFrame(
      self.root,
      text="Debug Selectors",
      font=("Arial", 10, "bold"),
      bg=BG_COLOR,
      fg="white",
      padx=6,
      pady=4
    )
    self.debug_frame.pack(pady=2)

    self.debug_character_label, self.debug_character_menu = self.create_debug_dropdown(
      self.debug_frame,
      "Character:",
      self.debug_character_choice,
      self.on_debug_character_changed,
      0
    )
    self.debug_item_label, self.debug_item_menu = self.create_debug_dropdown(
      self.debug_frame,
      "Item:",
      self.debug_item_choice,
      self.on_debug_item_changed,
      1
    )
    self.debug_addon_1_label, self.debug_addon_1_menu = self.create_debug_dropdown(
      self.debug_frame,
      "Add-on 1:",
      self.debug_addon_1_choice,
      self.on_debug_addon_changed,
      2
    )
    self.debug_addon_2_label, self.debug_addon_2_menu = self.create_debug_dropdown(
      self.debug_frame,
      "Add-on 2:",
      self.debug_addon_2_choice,
      self.on_debug_addon_changed,
      3
    )
    self.debug_offering_label, self.debug_offering_menu = self.create_debug_dropdown(
      self.debug_frame,
      "Offering:",
      self.debug_offering_choice,
      self.on_debug_offering_changed,
      4
    )
    self.debug_gauntlet_spin_label = tk.Label(
      self.debug_frame,
      text="Auto Gauntlet Spins:",
      font=("Arial", 10, "bold"),
      bg=BG_COLOR,
      fg="white"
    )
    self.debug_gauntlet_spin_label.grid(row=1, column=0, padx=(5, 2), pady=4, sticky="e")

    self.debug_gauntlet_spin_entry = tk.Entry(
      self.debug_frame,
      textvariable=self.debug_gauntlet_spin_count,
      width=8
    )
    self.debug_gauntlet_spin_entry.grid(row=1, column=1, padx=(0, 5), pady=4, sticky="w")

    self.debug_auto_gauntlet_button = tk.Button(
      self.debug_frame,
      text="Run Auto Gauntlet Successes",
      font=("Arial", 10, "bold"),
      command=self.start_debug_auto_gauntlet
    )
    self.debug_auto_gauntlet_button.grid(row=1, column=2, columnspan=4, padx=5, pady=4, sticky="w")
    self.update_debug_dropdowns(reset_invalid=True)

  def create_debug_dropdown(self, parent, label_text, variable, command, column):
    label = tk.Label(parent, text=label_text, font=("Arial", 10, "bold"), bg=BG_COLOR, fg="white")
    label.grid(row=0, column=column * 2, padx=(5, 2), pady=2, sticky="e")

    option_menu = tk.OptionMenu(parent, variable, "Random", command=command)
    option_menu.config(width=17)
    option_menu.grid(row=0, column=column * 2 + 1, padx=(0, 5), pady=2, sticky="w")
    return label, option_menu

  def set_debug_menu_options(self, option_menu, variable, options, command, reset_invalid=True):
    if not self.debug_mode:
      return

    options = ["Random"] + sorted({option for option in options if option})
    menu = option_menu["menu"]
    menu.delete(0, "end")

    for option in options:
      menu.add_command(label=option, command=lambda value=option: self.set_debug_choice(variable, value, command))

    if reset_invalid and variable.get() not in options:
      variable.set("Random")

  def set_debug_choice(self, variable, value, command):
    variable.set(value)
    if command is not None:
      command(value)

  def on_debug_character_changed(self, value=None):
    self.update_debug_dropdowns(reset_invalid=True)

  def on_debug_item_changed(self, value=None):
    self.update_debug_dropdowns(reset_invalid=True)

  def on_debug_addon_changed(self, value=None):
    pass

  def on_debug_offering_changed(self, value=None):
    pass

  def update_debug_dropdowns(self, reset_invalid=True):
    if not self.debug_mode or not hasattr(self, "debug_frame"):
      return

    role = self.current_role
    character_names = [character["name"] for character in self.get_current_character_list()]
    self.set_debug_menu_options(
      self.debug_character_menu,
      self.debug_character_choice,
      character_names,
      self.on_debug_character_changed,
      reset_invalid=reset_invalid
    )

    if role == "Survivor":
      item_names = [item["name"] for item in self.survivor_items]
      self.debug_item_menu.config(state="normal")
      self.set_debug_menu_options(
        self.debug_item_menu,
        self.debug_item_choice,
        item_names,
        self.on_debug_item_changed,
        reset_invalid=reset_invalid
      )
    else:
      self.debug_item_choice.set("Random")
      self.debug_item_menu.config(state="disabled")
      self.set_debug_menu_options(
        self.debug_item_menu,
        self.debug_item_choice,
        [],
        self.on_debug_item_changed,
        reset_invalid=True
      )

    addon_options = self.get_debug_addon_options(role)
    self.set_debug_menu_options(
      self.debug_addon_1_menu,
      self.debug_addon_1_choice,
      addon_options,
      self.on_debug_addon_changed,
      reset_invalid=reset_invalid
    )
    self.set_debug_menu_options(
      self.debug_addon_2_menu,
      self.debug_addon_2_choice,
      addon_options,
      self.on_debug_addon_changed,
      reset_invalid=reset_invalid
    )

    offering_options = [offering["name"] for offering in get_offering_options_for_role(role)]
    self.set_debug_menu_options(
      self.debug_offering_menu,
      self.debug_offering_choice,
      offering_options,
      self.on_debug_offering_changed,
      reset_invalid=reset_invalid
    )

  def get_debug_addon_options(self, role):
    if role == "Survivor":
      selected_item = self.get_debug_selected_item()
      if selected_item is None:
        return [addon["name"] for addon in self.survivor_addons]

      return [
        addon["name"]
        for addon in choose_matching_addons(
          self.survivor_addons,
          get_survivor_item_addon_terms(selected_item),
          len(self.survivor_addons)
        )
      ]

    selected_character = self.get_debug_selected_character("Killer")
    if selected_character is None:
      return [addon["name"] for addon in self.killer_addons]

    return [
      addon["name"]
      for addon in choose_matching_addons(
        self.killer_addons,
        get_killer_addon_terms(selected_character),
        len(self.killer_addons),
        prefer_explicit_owner=True
      )
    ]

  def get_debug_selected_character(self, role):
    if not self.debug_mode or self.debug_character_choice.get() == "Random":
      return None

    character_pool = self.killer_characters if role == "Killer" else self.survivor_characters
    return self.find_by_name(character_pool, self.debug_character_choice.get())

  def get_debug_selected_item(self):
    if not self.debug_mode or self.debug_item_choice.get() == "Random":
      return None

    return self.find_by_name(self.survivor_items, self.debug_item_choice.get())

  def get_debug_selected_offering(self, role):
    if not self.debug_mode or self.debug_offering_choice.get() == "Random":
      return None

    return self.find_by_name(get_offering_options_for_role(role), self.debug_offering_choice.get())

  def get_debug_selected_addons(self, role, chosen_character, chosen_item, addon_count):
    if not self.debug_mode or addon_count <= 0:
      return []

    if role == "Survivor" and chosen_item is not None:
      valid_addons = choose_matching_addons(
        self.survivor_addons,
        get_survivor_item_addon_terms(chosen_item),
        len(self.survivor_addons)
      )
    elif role == "Killer" and chosen_character is not None:
      valid_addons = choose_matching_addons(
        self.killer_addons,
        get_killer_addon_terms(chosen_character),
        len(self.killer_addons),
        prefer_explicit_owner=True
      )
    else:
      valid_addons = []

    selected_addons = []
    selected_names = [self.debug_addon_1_choice.get(), self.debug_addon_2_choice.get()]

    for addon_name in selected_names[:addon_count]:
      if addon_name == "Random":
        continue

      addon = self.find_by_name(valid_addons, addon_name)
      if addon is not None and addon.get("name") not in {selected.get("name") for selected in selected_addons}:
        selected_addons.append(addon)

    return selected_addons

  def build_randomize_controls(self):
    self.result_label = tk.Label(self.root, text="Choose Survivor or Killer, then press Randomize!", font=("Arial", 12))
    self.result_label.pack(pady=0)

    self.action_button_frame = tk.Frame(self.root)
    self.action_button_frame.pack(pady=2)

    self.randomize_button = tk.Button(
      self.action_button_frame,
      text="RANDOMIZE",
      font=("Arial", 14, "bold"),
      width=14,
      command=self.randomize_build
    )
    self.randomize_button.pack(side="left", padx=6)

    self.gauntlet_result_frame = tk.Frame(self.action_button_frame)

    self.gauntlet_success_button = tk.Button(
      self.gauntlet_result_frame,
      text="Escaped",
      font=("Arial", 11, "bold"),
      width=10,
      command=self.record_gauntlet_success
    )
    self.gauntlet_success_button.pack(side="left", padx=4)

    self.gauntlet_failure_button = tk.Button(
      self.gauntlet_result_frame,
      text="Died",
      font=("Arial", 11, "bold"),
      width=10,
      command=self.record_gauntlet_failure
    )
    self.gauntlet_failure_button.pack(side="left", padx=4)

    self.gauntlet_clear_frame = tk.Frame(self.action_button_frame)
    self.clear_gauntlet_button = tk.Button(
      self.gauntlet_clear_frame,
      text="Clear Current Gauntlet",
      font=("Arial", 11, "bold"),
      width=18,
      command=self.clear_current_gauntlet
    )
    self.clear_gauntlet_button.pack(side="left", padx=4)

    self.saved_build_button_frame = tk.Frame(self.action_button_frame)
    self.saved_build_button_frame.pack(side="left", padx=6)

    self.load_survivor_build_button = tk.Button(
      self.saved_build_button_frame,
      text="Load Survivor",
      font=("Arial", 10, "bold"),
      width=14,
      command=lambda: self.open_saved_build_picker("Survivor")
    )

    self.load_killer_build_button = tk.Button(
      self.saved_build_button_frame,
      text="Load Killer",
      font=("Arial", 10, "bold"),
      width=14,
      command=lambda: self.open_saved_build_picker("Killer")
    )


    self.update_saved_build_button_visibility()

    self.gauntlet_streak_label = tk.Label(self.root, text="", font=("Arial", 10, "bold"))

    self.gauntlet_played_frame = tk.Frame(self.root)
    self.gauntlet_played_title_label = tk.Label(
      self.gauntlet_played_frame,
      text="",
      font=("Arial", 9, "bold")
    )
    self.gauntlet_played_title_label.pack(pady=(0, 1))

    self.gauntlet_played_icon_frame = tk.Frame(self.gauntlet_played_frame, bg=BG_COLOR)
    self.gauntlet_played_icon_frame.pack()
    self.gauntlet_played_icon_images = []
    self.gauntlet_played_max_columns = 10

    self.update_gauntlet_controls()

  def get_all_perks(self):
    return sorted(set(self.survivor_perks + self.killer_perks))

  def get_all_characters(self):
    return sorted(self.survivor_characters + self.killer_characters, key=lambda character: character["name"])

  def get_all_addons(self):
    return sorted(self.survivor_addons + self.killer_addons, key=lambda addon: addon["name"])

  def save_current_role_settings(self):
    role = self.current_role
    self.role_settings[role]["perk_count"] = self.perk_count_slider.get()
    self.role_settings[role]["addon_count"] = self.addon_count.get()
    self.role_settings[role]["include_character"] = self.include_character.get()
    self.role_settings[role]["include_offering"] = self.include_offering.get()

    if role == "Survivor":
      self.role_settings[role]["include_item"] = self.include_item.get()

  def load_role_settings(self, role):
    self.loading_role_settings = True

    settings = self.role_settings[role]
    self.perk_count_slider.set(settings["perk_count"])
    self.addon_count.set(settings["addon_count"])
    self.include_character.set(settings["include_character"])
    self.include_offering.set(settings["include_offering"])
    self.include_item.set(settings["include_item"] if role == "Survivor" else False)

    self.update_perk_count_label(settings["perk_count"])
    self.update_addon_count_label(settings["addon_count"])

    self.loading_role_settings = False

  def update_role_display(self):
    if not self.loading_role_settings:
      self.save_current_role_settings()

    selected_role = self.selected_role.get()

    self.current_role = selected_role
    self.load_role_settings(selected_role)
    self.apply_role_slot_labels(selected_role)
    self.restore_last_roll(selected_role)
    self.update_debug_dropdowns(reset_invalid=True)
    self.update_saved_build_button_visibility()
    self.update_gauntlet_controls()

  def apply_role_slot_labels(self, role):
    self.lever_label.config(text=f"Lever set to: {role}")
    self.character_title_label.config(text=f"{role} Slot")

    if role == "Killer":
      self.include_item_checkbox.config(state="disabled")
      self.extra_slots[0]["title"].config(text="Power")
    else:
      self.include_item_checkbox.config(state="normal")
      self.extra_slots[0]["title"].config(text="Item")

  def resolve_roll_role(self):
    return self.selected_role.get()

  def prepare_role_for_roll(self, role):
    self.current_role = role
    self.load_role_settings(role)
    self.apply_role_slot_labels(role)

  def restore_last_roll(self, role):
    last_roll = self.last_rolls.get(role)
    self.clear_slots()
    self.clear_extra_slots()

    if last_roll is None:
      self.character_name_label.config(text="???")
      reset_image_label(self.character_portrait_label)
      self.result_label.config(text=f"{role} selected.")
      return

    self.display_character(last_roll["character"])
    self.display_perks(last_roll["perks"])
    self.display_extra_roll(role, last_roll["character"], last_roll["extra_roll"])
    self.result_label.config(text=f"Restored previous {role} build.")

  def update_perk_count_label(self, value):
    perk_count = int(value)
    self.perk_count_label.config(text=f"Number of Perks: {perk_count}")

    if not self.loading_role_settings:
      self.role_settings[self.current_role]["perk_count"] = perk_count

  def update_addon_count_label(self, value):
    addon_count = int(value)
    self.addon_count_label.config(text=f"Number of Add-ons: {addon_count}")

    if not self.loading_role_settings:
      self.role_settings[self.current_role]["addon_count"] = addon_count

  def update_include_character_setting(self):
    self.role_settings[self.current_role]["include_character"] = self.include_character.get()

  def update_include_item_setting(self):
    if self.current_role == "Survivor":
      self.role_settings["Survivor"]["include_item"] = self.include_item.get()

  def update_include_offering_setting(self):
    self.role_settings[self.current_role]["include_offering"] = self.include_offering.get()

  def get_current_perk_list(self):
    return self.killer_perks if self.current_role == "Killer" else self.survivor_perks

  def get_current_character_list(self):
    return self.killer_characters if self.current_role == "Killer" else self.survivor_characters

  def clear_slots(self):
    for slot in self.slots:
      slot["name"].config(text="---")
      reset_image_label(slot["icon"])

  def clear_extra_slots(self):
    for slot in self.extra_slots:
      slot["name"].config(text="---")
      reset_image_label(slot["icon"])

  def get_result_slot_containers(self):
    containers = []

    if hasattr(self, "character_slot_container"):
      containers.append(self.character_slot_container)

    if hasattr(self, "slots"):
      containers.extend(slot["container"] for slot in self.slots)

    if hasattr(self, "extra_slots"):
      containers.extend(slot["container"] for slot in self.extra_slots)

    return containers

  def set_result_slot_frame_color(self, color=None):
    frame_color = color or self.slot_panel_border_color

    for container in self.get_result_slot_containers():
      try:
        container.config(
          highlightbackground=frame_color,
          highlightcolor=frame_color
        )
      except tk.TclError:
        pass

  def update_spin_slot_frame_color(self, frame_index):
    if not self.spin_slot_frame_colors:
      return

    color = self.spin_slot_frame_colors[frame_index % len(self.spin_slot_frame_colors)]
    self.set_result_slot_frame_color(color)

  def flash_final_slot_frames(self, on_complete, flash_index=0):
    if flash_index < self.final_flash_count:
      flash_color = "#ffd700" if flash_index % 2 == 0 else "#ffffff"
      self.set_result_slot_frame_color(flash_color)
      job = self.root.after(
        self.get_animation_delay(self.final_flash_delay_ms),
        lambda: self.flash_final_slot_frames(on_complete, flash_index + 1)
      )
      self.spin_animation_jobs.append(job)
      return

    self.set_result_slot_frame_color()
    self.spin_animation_jobs = []
    self.is_spinning = False
    on_complete()
    self.set_controls_locked_for_spin(False)

  def get_spin_lock_widgets(self):
    widget_names = [
      "survivor_role_button",
      "killer_role_button",
      "perk_count_slider",
      "addon_count_slider",
      "include_character_checkbox",
      "include_item_checkbox",
      "include_offering_checkbox",
      "save_builds_checkbox",
      "gauntlet_checkbox",
      "randomize_button",
      "gauntlet_success_button",
      "gauntlet_failure_button",
      "clear_gauntlet_button",
      "load_survivor_build_button",
      "load_killer_build_button",
      "debug_character_menu",
      "debug_item_menu",
      "debug_addon_1_menu",
      "debug_addon_2_menu",
      "debug_offering_menu",
      "debug_gauntlet_spin_entry",
      "debug_auto_gauntlet_button",
    ]

    widgets = []
    for widget_name in widget_names:
      widget = getattr(self, widget_name, None)
      if widget is not None:
        widgets.append(widget)

    return widgets

  def set_controls_locked_for_spin(self, locked):
    state = "disabled" if locked else "normal"

    for widget in self.get_spin_lock_widgets():
      try:
        widget.config(state=state)
      except tk.TclError:
        pass

    if locked:
      return

    self.apply_role_slot_labels(self.current_role)
    self.update_debug_dropdowns(reset_invalid=False)
    self.update_saved_build_button_visibility()
    self.update_gauntlet_controls()

  def display_character(self, character):
    if character is None:
      self.character_name_label.config(text="No character found")
      reset_image_label(self.character_portrait_label)
      return

    character_name = character["name"]
    self.character_name_label.config(text=character_name)
    reset_image_label(self.character_portrait_label)

    portrait_path = self.character_portrait_files.get(character_name)

    if portrait_path is not None and os.path.exists(portrait_path):
      image = Image.open(portrait_path).resize((self.character_portrait_size, self.character_portrait_size))
      portrait_image = ImageTk.PhotoImage(image)
      self.character_portrait_images[character_name] = portrait_image
      self.character_portrait_label.config(image=portrait_image, text="")
      self.character_portrait_label.image = portrait_image
    else:
      self.character_portrait_label.config(text="No Portrait", font=("Arial", 12, "bold"), bg=self.slot_panel_bg_color)

  def get_available_characters_for_roll(self):
    available_characters = list(self.get_current_character_list())

    if self.gauntlet_enabled.get():
      completed_characters = self.history_store.get_safe_character_names(self.current_role)
      available_characters = [
        character for character in available_characters
        if character["name"] not in completed_characters
      ]

    return available_characters

  def randomize_character(self, display=True):
    if not self.include_character.get():
      if display:
        self.character_name_label.config(text="---")
        reset_image_label(self.character_portrait_label)
      return None

    available_characters = self.get_available_characters_for_roll()

    if len(available_characters) == 0:
      if display:
        self.display_character(None)
      return None

    debug_character = self.get_debug_selected_character(self.current_role)

    if debug_character is not None and debug_character in available_characters:
      chosen_character = debug_character
    elif debug_character is not None and self.gauntlet_enabled.get():
      chosen_character = None
    else:
      chosen_character = random.choice(available_characters)

    if display:
      self.display_character(chosen_character)
    return chosen_character

  def display_perks(self, chosen_perks):
    self.clear_slots()

    for slot, perk_name in zip(self.slots, chosen_perks):
      slot["name"].config(text=perk_name)
      reset_image_label(slot["icon"])

      if self.icon_images.get(perk_name) is not None:
        slot["icon"].config(image=self.icon_images[perk_name], text="")
        slot["icon"].image = self.icon_images[perk_name]
      else:
        slot["icon"].config(text="No Icon", font=("Arial", 16, "bold"), bg=self.slot_panel_bg_color)

  def set_extra_slot(self, slot_index, slot_title, unlockable, icon_files):
    slot = self.extra_slots[slot_index]
    slot["title"].config(text=slot_title)
    reset_image_label(slot["icon"])

    if unlockable is None:
      slot["name"].config(text="---")
      return

    unlockable_name = unlockable["name"]
    icon_lookup_name = unlockable.get("icon_key", unlockable_name)
    slot["name"].config(text=unlockable_name)

    icon_path = icon_files.get(icon_lookup_name)

    if icon_path is not None and os.path.exists(icon_path):
      image = Image.open(icon_path).resize((self.extra_icon_size, self.extra_icon_size))
      icon_image = ImageTk.PhotoImage(image)

      if slot_title.startswith("Item"):
        self.item_images[unlockable_name] = icon_image
      elif slot_title.startswith("Add-on"):
        self.addon_images[unlockable_name] = icon_image
      else:
        self.offering_images[icon_lookup_name] = icon_image

      slot["icon"].config(image=icon_image, text="")
      slot["icon"].image = icon_image
    else:
      slot["icon"].config(text="No Icon", font=("Arial", 10, "bold"), bg=self.slot_panel_bg_color)

  def get_random_power_icon_path(self, power_name):
    exact_file_name = KILLER_POWER_EXACT_ICON_FILES.get(power_name)

    if exact_file_name:
      exact_path = exact_file_name if os.path.isabs(exact_file_name) else os.path.join(SOURCE_POWER_ICON_FOLDER, exact_file_name)
      exact_path = os.path.normpath(exact_path)

      if os.path.exists(exact_path):
        return exact_path

      print(f"\nExact power icon path not found for {power_name}:")
      print(f"- Tried: {exact_path}")

    possible_icon_keys = KILLER_POWER_RANDOM_ICON_ALIASES.get(power_name)

    if possible_icon_keys:
      possible_icon_paths = []

      for icon_key in possible_icon_keys:
        normalized_icon_key = normalize_icon_search_text(icon_key)

        for file_path in get_png_files_from_folder(SOURCE_POWER_ICON_FOLDER):
          if normalize_icon_search_text(clean_power_file_name(file_path)) == normalized_icon_key:
            possible_icon_paths.append(file_path)

      if possible_icon_paths:
        return random.choice(possible_icon_paths)

    return self.power_icon_files.get(power_name)

  def set_power_slot(self, chosen_character):
    if chosen_character is None:
      self.set_extra_slot(0, "Power", None, {})
      return

    power_name = get_killer_power_name(chosen_character)
    power_icon_path = self.get_random_power_icon_path(power_name)

    slot = self.extra_slots[0]
    slot["title"].config(text="Power")
    slot["name"].config(text=power_name)
    reset_image_label(slot["icon"])

    if power_icon_path is not None and os.path.exists(power_icon_path):
      image = Image.open(power_icon_path).resize((self.extra_icon_size, self.extra_icon_size))
      power_image = ImageTk.PhotoImage(image)

      self.power_images[power_name] = power_image
      slot["icon"].config(image=power_image, text="")
      slot["icon"].image = power_image
    else:
      slot["icon"].config(text="No Icon", font=("Arial", 10, "bold"), bg=self.slot_panel_bg_color)

  def build_extra_roll(self, chosen_character):
    role = self.current_role
    addon_count = self.addon_count.get()

    chosen_item = None
    chosen_addons = []
    chosen_offering = None

    if role == "Survivor" and self.include_item.get() and self.survivor_items:
      debug_item = self.get_debug_selected_item()
      chosen_item = debug_item if debug_item is not None else random.choice(self.survivor_items)

    debug_selected_addons = self.get_debug_selected_addons(role, chosen_character, chosen_item, addon_count)

    if role == "Survivor" and chosen_item is not None:
      matching_addons = choose_matching_addons(
        self.survivor_addons,
        get_survivor_item_addon_terms(chosen_item),
        addon_count
      )
      chosen_addons = self.merge_debug_and_random_addons(debug_selected_addons, matching_addons, addon_count)

    elif role == "Killer" and chosen_character is not None:
      matching_addons = choose_matching_addons(
        self.killer_addons,
        get_killer_addon_terms(chosen_character),
        addon_count,
        prefer_explicit_owner=True
      )
      chosen_addons = self.merge_debug_and_random_addons(debug_selected_addons, matching_addons, addon_count)

    if self.include_offering.get():
      debug_offering = self.get_debug_selected_offering(role)

      if debug_offering is not None:
        chosen_offering = debug_offering
      else:
        offering_pool = get_offering_options_for_role(role)

        if offering_pool:
          chosen_offering = random.choice(offering_pool)

    return {
      "item": chosen_item,
      "addons": chosen_addons,
      "offering": chosen_offering
    }

  @staticmethod
  def merge_debug_and_random_addons(debug_addons, matching_addons, addon_count):
    chosen_addons = []
    used_names = set()

    for addon in debug_addons:
      if addon is None or addon.get("name") in used_names:
        continue

      chosen_addons.append(addon)
      used_names.add(addon.get("name"))

      if len(chosen_addons) >= addon_count:
        return chosen_addons

    for addon in matching_addons:
      if addon is None or addon.get("name") in used_names:
        continue

      chosen_addons.append(addon)
      used_names.add(addon.get("name"))

      if len(chosen_addons) >= addon_count:
        break

    return chosen_addons

  def display_extra_roll(self, role, chosen_character, extra_roll):
    self.clear_extra_slots()

    if role == "Survivor":
      self.set_extra_slot(0, "Item", extra_roll.get("item"), self.item_icon_files)
    else:
      self.set_power_slot(chosen_character)

    chosen_addons = extra_roll.get("addons", [])

    for index in range(2):
      unlockable = chosen_addons[index] if index < len(chosen_addons) else None
      self.set_extra_slot(index + 1, f"Add-on {index + 1}", unlockable, self.addon_icon_files)

    self.set_extra_slot(3, "Offering", extra_roll.get("offering"), self.offering_icon_files)

  def cancel_spin_animations(self):
    for job in self.spin_animation_jobs:
      try:
        self.root.after_cancel(job)
      except tk.TclError:
        pass

    self.spin_animation_jobs = []
    self.is_spinning = False
    self.set_result_slot_frame_color()

    if hasattr(self, "randomize_button"):
      self.set_controls_locked_for_spin(False)

  def get_spin_character_pool(self, role):
    character_pool = self.killer_characters if role == "Killer" else self.survivor_characters
    return [character for character in character_pool if character]

  def get_spin_perk_pool(self, role):
    perk_pool = self.killer_perks if role == "Killer" else self.survivor_perks
    return [perk for perk in perk_pool if perk]

  def get_spin_extra_roll(self, role, character_pool):
    random_character = random.choice(character_pool) if character_pool else None
    random_item = None
    random_addons = []
    random_offering = None

    if role == "Survivor":
      if self.survivor_items:
        random_item = random.choice(self.survivor_items)
        random_addons = choose_matching_addons(
          self.survivor_addons,
          get_survivor_item_addon_terms(random_item),
          min(2, self.addon_count.get())
        )
    elif random_character is not None:
      random_addons = choose_matching_addons(
        self.killer_addons,
        get_killer_addon_terms(random_character),
        min(2, self.addon_count.get()),
        prefer_explicit_owner=True
      )

    offering_pool = get_offering_options_for_role(role)

    if offering_pool:
      random_offering = random.choice(offering_pool)

    return random_character, {
      "item": random_item,
      "addons": random_addons,
      "offering": random_offering
    }

  def display_spin_frame(self, role, perk_count):
    character_pool = self.get_spin_character_pool(role)
    perk_pool = self.get_spin_perk_pool(role)

    random_character = random.choice(character_pool) if character_pool else None
    random_perks = random.sample(perk_pool, min(perk_count, len(perk_pool))) if perk_pool and perk_count > 0 else []
    extra_character, random_extra_roll = self.get_spin_extra_roll(role, character_pool)

    self.display_character(random_character)
    self.display_perks(random_perks)
    self.display_extra_roll(role, extra_character if role == "Killer" else random_character, random_extra_roll)

  def get_animation_delay(self, delay_ms):
    if self.debug_mode and self.debug_auto_gauntlet_running:
      return max(1, int(delay_ms * self.debug_auto_gauntlet_speed_multiplier))

    return delay_ms
  
  def get_spin_frame_delay(self, frame_index):
    slow_start = max(0, self.spin_frame_count - self.spin_slow_frame_count)

    if frame_index < slow_start:
      delay = self.spin_frame_delay_ms + int(frame_index * 3)
    else:
      slow_index = frame_index - slow_start
      slow_delays = [160, 260, 400, 620, 850]
      delay = slow_delays[min(slow_index, len(slow_delays) - 1)]

    return self.get_animation_delay(delay)

  def animate_build_result(self, role, final_character, final_perks, final_extra_roll, on_complete):
    self.cancel_spin_animations()
    self.is_spinning = True
    self.set_controls_locked_for_spin(True)
    self.result_label.config(text="Spinning...")

    perk_count = len(final_perks)

    def reveal_final_result():
      self.display_character(final_character)
      self.display_perks(final_perks)
      self.display_extra_roll(role, final_character, final_extra_roll)
      self.result_label.config(text="Final build selected!")
      self.flash_final_slot_frames(on_complete)

    def show_final_fake_frame():
      # One last fake build stays on screen longer to create a near-miss
      # slot-machine pause before the real selected build appears.
      self.display_spin_frame(role, perk_count)
      self.update_spin_slot_frame_color(self.spin_frame_count)
      final_fake_delay = self.get_animation_delay(
        random.randint(
          self.spin_final_fake_min_delay_ms,
          self.spin_final_fake_max_delay_ms
        )
      )
      job = self.root.after(final_fake_delay, reveal_final_result)
      self.spin_animation_jobs.append(job)

    def run_frame(frame_index=0):
      if frame_index < self.spin_frame_count:
        self.display_spin_frame(role, perk_count)
        self.update_spin_slot_frame_color(frame_index)
        delay = self.get_spin_frame_delay(frame_index)
        job = self.root.after(delay, lambda: run_frame(frame_index + 1))
        self.spin_animation_jobs.append(job)
        return

      show_final_fake_frame()

    run_frame()

  def start_debug_auto_gauntlet(self):
    if not self.debug_mode:
      return

    if self.debug_auto_gauntlet_running:
      return

    try:
      spin_count = int(self.debug_gauntlet_spin_count.get())
    except ValueError:
      messagebox.showerror("Debug Auto Gauntlet", "Enter a whole number of spins.")
      return

    if spin_count <= 0:
      messagebox.showerror("Debug Auto Gauntlet", "Enter a spin count greater than 0.")
      return

    if not self.gauntlet_enabled.get():
      self.gauntlet_enabled.set(True)
      self.update_gauntlet_controls()

    self.debug_auto_gauntlet_running = True
    self.debug_auto_gauntlet_remaining = spin_count
    self.result_label.config(text=f"Debug auto gauntlet started: {spin_count} successes queued.")
    self.run_next_debug_auto_gauntlet_spin()

  def run_next_debug_auto_gauntlet_spin(self):
    if not self.debug_auto_gauntlet_running:
      return

    if self.debug_auto_gauntlet_remaining <= 0:
      self.debug_auto_gauntlet_running = False
      self.result_label.config(text="Debug auto gauntlet complete.")
      self.update_gauntlet_controls()
      return

    if self.is_spinning:
      self.root.after(
        self.get_animation_delay(250),
        self.run_next_debug_auto_gauntlet_spin
      )
      return

    if len(self.get_available_characters_for_roll()) == 0:
      self.debug_auto_gauntlet_running = False
      self.result_label.config(text=f"Debug auto gauntlet stopped: all {self.current_role.lower()}s are safe.")
      self.update_gauntlet_controls()
      return

    self.randomize_build()

  def finish_debug_auto_gauntlet_spin(self):
    if not self.debug_auto_gauntlet_running:
      return

    role = self.current_role
    last_roll = self.last_rolls.get(role)

    if last_roll is None or last_roll.get("character") is None:
      self.debug_auto_gauntlet_running = False
      self.result_label.config(text="Debug auto gauntlet stopped: no character was rolled.")
      self.update_gauntlet_controls()
      return

    self.record_gauntlet_success()
    self.debug_auto_gauntlet_remaining -= 1
    self.root.after(
      self.get_animation_delay(350),
      self.run_next_debug_auto_gauntlet_spin
    )

  def randomize_build(self):
    if self.is_spinning:
      return

    role = self.resolve_roll_role()
    self.prepare_role_for_roll(role)

    if self.include_character.get() and self.gauntlet_enabled.get() and len(self.get_available_characters_for_roll()) == 0:
      self.display_character(None)
      self.clear_slots()
      self.clear_extra_slots()
      self.result_label.config(text=f"All {role} characters have been cleared in gauntlet mode.")
      self.update_gauntlet_controls()
      return

    perk_count = self.perk_count_slider.get()
    available_perks = self.get_current_perk_list()

    chosen_character = self.randomize_character(display=False)
    extra_roll = self.build_extra_roll(chosen_character)

    if perk_count == 0:
      chosen_perks = []
    elif perk_count > len(available_perks):
      self.result_label.config(text="Not enough perks in this role list.")
      return
    else:
      chosen_perks = random.sample(available_perks, perk_count)

    self.update_debug_dropdowns(reset_invalid=False)

    self.last_rolls[role] = {
      "character": chosen_character,
      "perks": chosen_perks,
      "extra_roll": extra_roll
    }

    build_data = self.history_store.serialize_build(role, chosen_character, chosen_perks, extra_roll)

    if self.save_builds_to_csv.get():
      self.history_store.record_build(role, build_data)

    def finish_randomize():
      if self.gauntlet_enabled.get() and chosen_character is not None:
        self.gauntlet_result_pending[role] = True

      self.update_gauntlet_controls()

      if chosen_character is None:
        self.result_label.config(text=f"Your random {role} perk build is ready!")
      else:
        self.result_label.config(text=f"Your random {role} build is ready!")
      
      if self.debug_auto_gauntlet_running:
        self.root.after(
          self.get_animation_delay(350),
          self.finish_debug_auto_gauntlet_spin
        )

    self.animate_build_result(role, chosen_character, chosen_perks, extra_roll, finish_randomize)

  def open_saved_build_picker(self, role):
    saved_builds = self.history_store.get_saved_builds(role)

    if not saved_builds:
      messagebox.showinfo("Saved Builds", f"No saved {role} builds found.")
      return

    picker = tk.Toplevel(self.root)
    picker.title(f"Saved {role} Builds")
    picker.geometry("720x360")
    picker.config(bg=BG_COLOR)

    tk.Label(
      picker,
      text=f"Saved {role} Builds",
      font=("Arial", 16, "bold")
    ).pack(pady=6)

    listbox = tk.Listbox(picker, font=("Arial", 11), width=100, height=11)
    listbox.pack(padx=10, pady=5, fill="both", expand=True)

    for saved_build in saved_builds:
      build_data = saved_build["build_data"]
      perks = ", ".join(build_data.get("perks", [])) or "No perks"
      character = build_data.get("character") or "No character"
      timestamp = saved_build.get("timestamp") or "Unknown time"
      listbox.insert("end", f"{timestamp} | {character} | {perks}")

    def load_selected_build():
      selection = listbox.curselection()

      if not selection:
        messagebox.showinfo("Saved Builds", "Select a build to load.")
        return

      self.load_saved_build(role, saved_builds[selection[0]]["build_data"])
      picker.destroy()

    listbox.bind("<Double-Button-1>", lambda event: load_selected_build())

    tk.Button(
      picker,
      text="Load Selected Build",
      font=("Arial", 12, "bold"),
      command=load_selected_build
    ).pack(pady=6)

    apply_dark_theme(picker)

  def load_saved_build(self, role, build_data):
    self.selected_role.set(role)
    self.prepare_role_for_roll(role)
    self.update_saved_build_button_visibility()

    character = self.find_character_by_name(role, build_data.get("character", ""))
    perks = [perk for perk in build_data.get("perks", []) if perk]
    extra_roll = self.deserialize_extra_roll(role, build_data)

    self.display_character(character)
    self.display_perks(perks)
    self.display_extra_roll(role, character, extra_roll)

    self.last_rolls[role] = {
      "character": character,
      "perks": perks,
      "extra_roll": extra_roll
    }

    self.result_label.config(text=f"Loaded saved {role} build.")
    self.update_gauntlet_controls()

  def find_character_by_name(self, role, character_name):
    if not character_name:
      return None

    character_pool = self.killer_characters if role == "Killer" else self.survivor_characters
    return self.find_by_name(character_pool, character_name)

  def deserialize_extra_roll(self, role, build_data):
    if role == "Survivor":
      item = self.find_by_name(self.survivor_items, build_data.get("item", ""))
      addons = [
        addon for addon_name in build_data.get("addons", [])
        if (addon := self.find_by_name(self.survivor_addons, addon_name)) is not None
      ]
    else:
      item = None
      addons = [
        addon for addon_name in build_data.get("addons", [])
        if (addon := self.find_by_name(self.killer_addons, addon_name)) is not None
      ]

    offering = self.find_by_name(get_offering_options_for_role(role), build_data.get("offering", ""))

    return {
      "item": item,
      "addons": addons,
      "offering": offering
    }

  @staticmethod
  def find_by_name(items, name):
    if not name:
      return None

    for item in items:
      if isinstance(item, dict) and item.get("name") == name:
        return item

      if isinstance(item, str) and item == name:
        return item

    return None

  def show_gauntlet_complete_fireworks(self, role):
    self.root.update_idletasks()

    x_position = self.root.winfo_rootx()
    y_position = self.root.winfo_rooty()
    width = max(self.root.winfo_width(), 800)
    height = max(self.root.winfo_height(), 600)

    fireworks_window = tk.Toplevel(self.root)
    fireworks_window.title("Gauntlet Complete")
    fireworks_window.geometry(f"{width}x{height}+{x_position}+{y_position}")
    fireworks_window.config(bg="black")
    fireworks_window.lift()
    fireworks_window.focus_force()

    try:
      fireworks_window.overrideredirect(True)
      fireworks_window.attributes("-alpha", 0.92)
      fireworks_window.attributes("-topmost", True)
    except tk.TclError:
      pass

    canvas = tk.Canvas(
      fireworks_window,
      width=width,
      height=height,
      bg="black",
      highlightthickness=0
    )
    canvas.pack(fill="both", expand=True)

    canvas.create_text(
      width // 2,
      max(60, height // 6),
      text=f"{role.upper()} GAUNTLET COMPLETE!",
      fill="gold",
      font=("Arial", 34, "bold")
    )
    canvas.create_text(
      width // 2,
      max(105, height // 6 + 45),
      text="Every character has been cleared!",
      fill="white",
      font=("Arial", 18, "bold")
    )

    colors = ["gold", "red", "cyan", "lime", "orange", "magenta", "white", "deepskyblue"]
    particles = []

    for _ in range(9):
      burst_x = random.randint(120, max(121, width - 120))
      burst_y = random.randint(150, max(151, height - 120))
      burst_color = random.choice(colors)

      for _ in range(34):
        angle = random.uniform(0, 6.28318)
        speed = random.uniform(3.0, 9.0)
        size = random.randint(3, 7)
        particles.append({
          "x": float(burst_x),
          "y": float(burst_y),
          "vx": speed * math.cos(angle),
          "vy": speed * math.sin(angle),
          "size": size,
          "color": burst_color,
          "life": random.randint(28, 48)
        })

    def animate_fireworks(frame=0):
      canvas.delete("particle")

      for particle in particles:
        if particle["life"] <= 0:
          continue

        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["vy"] += 0.10
        particle["vx"] *= 0.985
        particle["life"] -= 1

        size = particle["size"]
        canvas.create_oval(
          particle["x"] - size,
          particle["y"] - size,
          particle["x"] + size,
          particle["y"] + size,
          fill=particle["color"],
          outline="",
          tags="particle"
        )

      if frame < 70 and any(particle["life"] > 0 for particle in particles):
        fireworks_window.after(35, lambda: animate_fireworks(frame + 1))
      else:
        fireworks_window.destroy()

    canvas.bind("<Button-1>", lambda event: fireworks_window.destroy())
    fireworks_window.after(250, animate_fireworks)
    fireworks_window.after(6000, lambda: fireworks_window.winfo_exists() and fireworks_window.destroy())

  def update_gauntlet_streak_label(self):
    role = self.current_role
    if not hasattr(self, "gauntlet_streak_label"):
      return

    if not self.gauntlet_enabled.get():
      self.gauntlet_streak_label.pack_forget()
      self.gauntlet_streak_label.config(text="")
      return

    survivor_state = self.history_store.get_gauntlet_state("Survivor")
    killer_state = self.history_store.get_gauntlet_state("Killer")

    survivor_safe = len(survivor_state["safe_characters"])
    survivor_checkpoint = survivor_state["checkpoint_count"]
    survivor_streak = self.gauntlet_stats["Survivor"]["current_streak"]
    survivor_max_streak = self.gauntlet_stats["Survivor"]["max_streak"]
    survivor_failure_count = self.gauntlet_stats["Survivor"]["failure_count"]

    killer_safe = len(killer_state["safe_characters"])
    killer_checkpoint = killer_state["checkpoint_count"]
    killer_streak = self.gauntlet_stats["Killer"]["current_streak"]
    killer_max_streak = self.gauntlet_stats["Killer"]["max_streak"]
    killer_failure_count = self.gauntlet_stats["Killer"]["failure_count"]

    if role == "Killer":
      self.gauntlet_streak_label.config(
        text=(
          f"Killer Streak: {killer_streak} | "
          f"Max Streak: {killer_max_streak} | "
          f"Fails: {killer_failure_count} | "
          f"Safe: {killer_safe} | "
          f"Checkpoint: {killer_checkpoint}"
        )
      )
    else:
      self.gauntlet_streak_label.config(
        text=(
          f"Survivor Streak: {survivor_streak} | "
          f"Max Streak: {survivor_max_streak} | "
          f"Fails: {survivor_failure_count} | "
          f"Safe: {survivor_safe} | "
          f"Checkpoint: {survivor_checkpoint}"
        )
      )

    if not self.gauntlet_streak_label.winfo_ismapped():
      self.gauntlet_streak_label.pack(pady=1)

  def update_gauntlet_played_display(self):
    if not hasattr(self, "gauntlet_played_frame"):
      return

    if not self.gauntlet_enabled.get():
      self.gauntlet_played_frame.pack_forget()
      return

    role = self.current_role
    display_rows = self.history_store.get_gauntlet_display_rows(role)
    safe_character_names = [
      character_name
      for display_row in display_rows
      for character_name in display_row
    ]

    self.gauntlet_played_title_label.config(text=f"{role}s Played So Far")

    for child in self.gauntlet_played_icon_frame.winfo_children():
      child.destroy()

    self.gauntlet_played_icon_images = []

    if not safe_character_names:
      empty_label = tk.Label(
        self.gauntlet_played_icon_frame,
        text=f"No {role.lower()}s played yet",
        font=("Arial", self.scaled_font(10, 8)),
        bg=BG_COLOR,
        fg="white"
      )
      empty_label.pack(padx=10, pady=20)
    else:
      visual_row = 0

      for display_row in display_rows:
        for column, character_name in enumerate(display_row[:self.gauntlet_played_max_columns]):
          tile_width = self.scaled(76, 50)
          tile_height = self.scaled(80, 56)
          character_tile = tk.Frame(self.gauntlet_played_icon_frame, bg=BG_COLOR, width=tile_width, height=tile_height)
          character_tile.grid(row=visual_row, column=column, padx=max(1, self.scaled(3, 1)), pady=max(1, self.scaled(2, 1)), sticky="n")
          character_tile.grid_propagate(False)

          portrait_label = tk.Label(character_tile, bg=BG_COLOR)
          portrait_label.pack(pady=(0, 2))

          portrait_path = self.character_portrait_files.get(character_name)

          if portrait_path is not None and os.path.exists(portrait_path):
            image = Image.open(portrait_path).resize((self.gauntlet_portrait_size, self.gauntlet_portrait_size))
            portrait_image = ImageTk.PhotoImage(image)
            self.gauntlet_played_icon_images.append(portrait_image)
            portrait_label.config(image=portrait_image, text="")
            portrait_label.image = portrait_image
          else:
            portrait_label.config(
              text="No\nPortrait",
              font=("Arial", self.scaled_font(8, 6), "bold"),
              width=max(6, self.scaled(8, 6)),
              height=max(3, self.scaled(4, 3)),
              fg="white",
              bg=SLOT_BG_COLOR
            )

          tk.Label(
            character_tile,
            text=character_name,
            font=("Arial", self.scaled_font(7, 6)),
            wraplength=self.scaled(72, 46),
            justify="center",
            bg=BG_COLOR,
            fg="white"
          ).pack()

        visual_row += 1

    if not self.gauntlet_played_frame.winfo_ismapped():
      self.gauntlet_played_frame.pack(pady=1)

  def apply_gauntlet_pending_button_locks(self):
    if not hasattr(self, "randomize_button"):
      return

    role = self.current_role
    should_lock = self.gauntlet_enabled.get() and self.gauntlet_result_pending.get(role, False)
    button_state = "disabled" if should_lock else "normal"

    self.randomize_button.config(state=button_state)

    if role == "Survivor" and hasattr(self, "load_survivor_build_button"):
      self.load_survivor_build_button.config(state=button_state)

    if role == "Killer" and hasattr(self, "load_killer_build_button"):
      self.load_killer_build_button.config(state=button_state)

  def update_saved_build_button_visibility(self):
    if not hasattr(self, "load_survivor_build_button") or not hasattr(self, "load_killer_build_button"):
      return

    role = self.selected_role.get()

    self.load_survivor_build_button.pack_forget()
    self.load_killer_build_button.pack_forget()

    if role == "Killer":
      self.load_killer_build_button.pack(side="left", padx=3)
    else:
      self.load_survivor_build_button.pack(side="left", padx=3)

    self.apply_gauntlet_pending_button_locks()

  def update_gauntlet_controls(self):
    if not hasattr(self, "gauntlet_result_frame"):
      return

    self.update_gauntlet_streak_label()
    self.update_gauntlet_played_display()

    if not self.gauntlet_enabled.get():
      self.gauntlet_result_pending[self.current_role] = False
      self.gauntlet_result_frame.pack_forget()
      if hasattr(self, "gauntlet_clear_frame"):
        self.gauntlet_clear_frame.pack_forget()
      self.apply_gauntlet_pending_button_locks()
      return

    if not self.gauntlet_result_frame.winfo_ismapped():
      self.gauntlet_result_frame.pack(side="left", padx=4)

    if hasattr(self, "gauntlet_clear_frame") and not self.gauntlet_clear_frame.winfo_ismapped():
      self.gauntlet_clear_frame.pack(side="left", padx=4)

    role = self.current_role

    if role == "Killer":
      self.gauntlet_success_button.config(text="4K")
      self.gauntlet_failure_button.config(text="0-3K")
    else:
      self.gauntlet_success_button.config(text="Escaped")
      self.gauntlet_failure_button.config(text="Died")

    last_roll = self.last_rolls.get(role)
    has_character = last_roll is not None and last_roll.get("character") is not None
    character_already_safe = False

    if has_character:
      character_name = last_roll["character"]["name"]
      character_already_safe = character_name in self.history_store.get_safe_character_names(role)

    button_state = "normal" if has_character and not character_already_safe else "disabled"
    self.gauntlet_success_button.config(state=button_state)
    self.gauntlet_failure_button.config(state=button_state)
    self.apply_gauntlet_pending_button_locks()

  def clear_current_gauntlet(self):
    role = self.current_role

    should_clear = messagebox.askyesno(
      "Clear Gauntlet",
      f"Clear all {role} gauntlet progress and checkpoints? Saved build history will stay untouched."
    )

    if not should_clear:
      return

    self.history_store.clear_gauntlet(role)
    self.gauntlet_stats[role]["current_streak"] = 0
    self.gauntlet_stats[role]["max_streak"] = 0
    self.gauntlet_stats[role]["failure_count"] = 0
    self.gauntlet_result_pending[role] = False
    self.result_label.config(text=f"{role} gauntlet progress cleared.")
    self.update_gauntlet_controls()

  def record_gauntlet_success(self):
    role = self.current_role
    last_roll = self.last_rolls.get(role)

    if last_roll is None or last_roll.get("character") is None:
      return

    character_name = last_roll["character"]["name"]
    result = "4K" if role == "Killer" else "Escaped"
    safe_count = self.history_store.record_gauntlet_success(role, character_name, result)
    total_characters = len(self.killer_characters if role == "Killer" else self.survivor_characters)

    self.gauntlet_stats[role]["current_streak"] += 1

    if self.gauntlet_stats[role]["current_streak"] > self.gauntlet_stats[role]["max_streak"]:
      self.gauntlet_stats[role]["max_streak"] = self.gauntlet_stats[role]["current_streak"]
    
    if safe_count >= total_characters and total_characters > 0:
      self.result_label.config(text=f"{role} gauntlet complete! Every {role.lower()} is safe!")
      self.show_gauntlet_complete_fireworks(role)
    else:
      self.result_label.config(text=f"{character_name} marked safe for {role}. Safe count: {safe_count}.")

    self.gauntlet_success_button.config(state="disabled")
    self.gauntlet_failure_button.config(state="disabled")
    self.gauntlet_result_pending[role] = False
    self.update_gauntlet_controls()

  def record_gauntlet_failure(self):
    role = self.current_role
    last_roll = self.last_rolls.get(role)

    if last_roll is None or last_roll.get("character") is None:
      return

    character_name = last_roll["character"]["name"]
    result = "0-3K" if role == "Killer" else "Death"
    checkpoint_count = self.history_store.get_gauntlet_state(role)["checkpoint_count"]

    messagebox.showwarning(
      "Gauntlet Reset",
      f"{result} recorded for {character_name}. Your {role} gauntlet save will be reset to the most recent checkpoint: {checkpoint_count} safe characters."
    )

    self.gauntlet_stats[role]["failure_count"] += 1
    self.gauntlet_stats[role]["current_streak"] = 0
    
    reset_count = self.history_store.record_gauntlet_failure_reset(role, character_name, result)
    self.result_label.config(text=f"{role} gauntlet reset to checkpoint: {reset_count} safe characters.")
    self.gauntlet_success_button.config(state="disabled")
    self.gauntlet_failure_button.config(state="disabled")
    self.gauntlet_result_pending[role] = False
    self.update_gauntlet_controls()
