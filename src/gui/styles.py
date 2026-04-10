"""
Styles for the Stack Evaluator GUI.
Dark industrial theme — monospace-forward, amber accent, clean grid.
"""

# ── Palette ──────────────────────────────────────────────────────────────────
BG_DARK      = "#0f1117"   # root / deepest background
BG_PANEL     = "#161b22"   # card / panel background
BG_SURFACE   = "#1e2530"   # input fields, canvases
BORDER       = "#2d3748"   # subtle borders
BORDER_BRIGHT= "#3d4f63"   # highlighted borders

AMBER        = "#f59e0b"   # primary accent
AMBER_DIM    = "#92611a"   # muted amber
AMBER_BRIGHT = "#fcd34d"   # highlight

TEAL         = "#2dd4bf"   # secondary accent (conversions)
RED          = "#f87171"   # errors
GREEN        = "#4ade80"   # success / results

TEXT_PRIMARY = "#e2e8f0"
TEXT_MUTED   = "#64748b"
TEXT_DIM     = "#94a3b8"

# Stack box colours (bottom → top gradient effect via list index)
STACK_COLORS = ["#1e3a5f", "#1e4976", "#1d5c8a", "#1a6fa0", "#1782b6"]
STACK_TOP_COLOR  = "#f59e0b"
QUEUE_COLOR      = "#7c3aed"
QUEUE_LAST_COLOR = "#2dd4bf"

# ── Typography ────────────────────────────────────────────────────────────────
FONT_MONO    = ("Cascadia Code", 11)
FONT_MONO_LG = ("Cascadia Code", 14, "bold")
FONT_MONO_SM = ("Cascadia Code", 9)
FONT_UI      = ("Segoe UI", 10)
FONT_UI_SM   = ("Segoe UI", 9)
FONT_UI_LG   = ("Segoe UI", 13, "bold")
FONT_TITLE   = ("Segoe UI", 18, "bold")
FONT_LABEL   = ("Segoe UI", 8)

# ── Widget defaults ───────────────────────────────────────────────────────────
ENTRY_OPTS = dict(
    font=("Cascadia Code", 13),
    bg=BG_SURFACE,
    fg=TEXT_PRIMARY,
    insertbackground=AMBER,
    relief="flat",
    bd=0,
)

RADIO_OPTS = dict(
    font=FONT_UI_SM,
    bg=BG_PANEL,
    fg=TEXT_DIM,
    selectcolor=BG_PANEL,
    activebackground=BG_PANEL,
    activeforeground=AMBER,
)

BTN_PRIMARY = dict(
    font=("Segoe UI", 10, "bold"),
    bg=AMBER,
    fg="#000000",
    relief="flat",
    cursor="hand2",
    padx=16,
    pady=7,
    activebackground=AMBER_BRIGHT,
    activeforeground="#000000",
)

BTN_SECONDARY = dict(
    font=FONT_UI_SM,
    bg=BG_SURFACE,
    fg=TEXT_DIM,
    relief="flat",
    cursor="hand2",
    padx=12,
    pady=5,
    activebackground=BORDER_BRIGHT,
    activeforeground=TEXT_PRIMARY,
)

BTN_DANGER = dict(
    font=FONT_UI_SM,
    bg="#450a0a",
    fg=RED,
    relief="flat",
    cursor="hand2",
    padx=12,
    pady=5,
    activebackground="#7f1d1d",
    activeforeground=RED,
)

CANVAS_OPTS = dict(
    bg=BG_SURFACE,
    highlightthickness=1,
    highlightbackground=BORDER,
)

LOG_OPTS = dict(
    font=("Cascadia Code", 9),
    bg=BG_SURFACE,
    fg=TEXT_DIM,
    relief="flat",
    bd=0,
    wrap="word",
    padx=8,
    pady=4,
)

# log tag configs  {tag_name: {option: value}}
LOG_TAGS = {
    "step":   {"foreground": TEXT_DIM},
    "token":  {"foreground": TEAL,         "font": ("Cascadia Code", 9, "bold")},
    "result": {"foreground": GREEN,        "font": ("Cascadia Code", 9, "bold")},
    "error":  {"foreground": RED,          "font": ("Cascadia Code", 9, "bold")},
    "header": {"foreground": AMBER,        "font": ("Cascadia Code", 9, "bold")},
    "push":   {"foreground": "#60a5fa"},
    "pop":    {"foreground": "#f472b6"},
}