from config import (
  BG_COLOR,
  BUTTON_ACTIVE_BG_COLOR,
  BUTTON_BG_COLOR,
  FG_COLOR
)

def apply_dark_theme(widget):
  widget_type = widget.winfo_class()

  if widget_type in ("Frame", "Tk"):
    widget.config(bg=BG_COLOR)

  elif widget_type == "Label":
    widget.config(bg=BG_COLOR, fg=FG_COLOR)

  elif widget_type == "Button":
    widget.config(
      bg=BUTTON_BG_COLOR,
      fg=FG_COLOR,
      activebackground=BUTTON_ACTIVE_BG_COLOR,
      activeforeground=FG_COLOR
    )

  elif widget_type in ("Radiobutton", "Checkbutton"):
    widget.config(
      bg=BUTTON_BG_COLOR,
      fg=FG_COLOR,
      activebackground=BUTTON_ACTIVE_BG_COLOR,
      activeforeground=FG_COLOR,
      selectcolor=BUTTON_BG_COLOR
    )

  elif widget_type == "Scale":
    widget.config(
      bg=BG_COLOR,
      fg=FG_COLOR,
      troughcolor=BUTTON_BG_COLOR,
      activebackground=BUTTON_ACTIVE_BG_COLOR,
      highlightbackground=BG_COLOR
    )

  for child in widget.winfo_children():
    apply_dark_theme(child)

def reset_image_label(label):
  label.config(
    image="",
    text="",
    width=0,
    height=0,
    font=("Arial", 10),
    bg=BG_COLOR
  )
  label.image = None

def grab_window_attention(root):
  root.lift()
  root.focus_force()
  root.attributes("-topmost", True)
  root.after(500, lambda: root.attributes("-topmost", False))
