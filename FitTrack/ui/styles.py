"""
ui/styles.py
============
Glassmorphism Space Station Design System for FitTrack.
Two themes:
  Dark  — Deep Space: near-void black + aurora violet/teal/rose neon
  Light — Aurora Day: soft sky white + rich violet/cyan/pink accents

All colour, typography, spacing constants and shared widget factories live here.
NOTE: All font sizes are integers to comply with Tkinter / Tcl strict type rules.
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from typing import Optional, Dict, Any

# ---------------------------------------------------------------------------
# AURORA ACCENT CONSTANTS
# ---------------------------------------------------------------------------

AURORA_VIOLET  = "#A78BFA"   # Soft violet / amethyst
AURORA_TEAL    = "#2DD4BF"   # Electric teal / cyan-green
AURORA_ROSE    = "#F472B6"   # Neon rose / pink
AURORA_AMBER   = "#FBBF24"   # Warm amber / gold

# ---------------------------------------------------------------------------
# THEME PALETTES
# Dark Mode  — Deep Space (near-void black + aurora neons)
# Light Mode — Aurora Day (sky-white + rich violet/cyan accents)
# ---------------------------------------------------------------------------

THEMES: Dict[str, Dict[str, str]] = {
    "light": {
        "bg":                  "#F3F0FF",   # Soft lavender-white background
        "card":                "#FFFFFF",   # Pure white glass panel
        "card_shadow":         "#DDD6FE",   # Violet shadow
        "border":              "#DDD6FE",   # Soft violet border
        "border_focus":        "#7C3AED",   # Vivid violet focus ring
        "primary":             "#6D28D9",   # Deep aurora violet
        "primary_hover":       "#5B21B6",   # Darker violet hover
        "primary_dark":        "#4C1D95",   # Ultra-deep violet pressed
        "accent_teal":         "#0891B2",   # Vivid cyan-teal
        "accent_teal_hover":   "#0E7490",   # Deep teal
        "accent_rose":         "#DB2777",   # Vivid aurora rose
        "accent_rose_hover":   "#BE185D",   # Deep rose
        "accent_gold":         "#B45309",   # Rich amber
        "accent_gold_hover":   "#92400E",   # Deep amber
        "success":             "#047857",   # Deep emerald
        "success_hover":       "#065F46",   # Darker emerald
        "danger":              "#BE123C",   # Deep rose danger
        "danger_hover":        "#9F1239",   # Ultra-deep rose
        "warning":             "#B45309",   # Rich amber
        "warning_hover":       "#92400E",   # Deep amber
        "text":                "#1E1B4B",   # Deep indigo text — very readable
        "text_muted":          "#6366F1",   # Medium indigo muted
        "table_alt":           "#F5F3FF",   # Lavender alternating row
        "table_heading_bg":    "#2D1B69",   # Ultra-deep violet heading
        "table_heading_fg":    "#E9D5FF",   # Light lavender heading text
        "status_bg":           "#EDE9FE",   # Violet-tinted status strip
        "header_l":            "#2D1B69",   # Ultra-deep violet left header
        "header_r":            "#4C1D95",   # Deep violet right header
        "input_bg":            "#FAFAFF",   # Near-white with faint violet tint
        "suggestion_bg":       "#F5F3FF",   # Lavender suggestion area
        "tab_bar_bg":          "#EDE9FE",
        "tab_btn_bg":          "#EDE9FE",
        "scrollbar_trough":    "#EDE9FE",
        "scrollbar_thumb":     "#C4B5FD",
        "scrollbar_active":    "#6D28D9",
        "badge_gold_bg":       "#FEF3C7",
        "badge_gold_fg":       "#92400E",
        "hud_cyan":            "#0891B2",   # Vivid teal for orb zones
        "hud_green":           "#047857",   # Rich emerald
        "hud_amber":           "#B45309",   # Deep amber
        "hud_crimson":         "#BE123C",   # Deep rose/crimson
        "glass_tint":          "#FFFFFF",   # Pure white glass surface
        "glass_border":        "#C4B5FD",   # Light violet glass border
        "star_bg":             "#DDD6FE",   # Subtle violet wash
    },
    "dark": {
        "bg":                  "#050811",   # Near-void deep space black
        "card":                "#0C1428",   # Deep violet-glass panel
        "card_shadow":         "#020408",   # Pure void shadow
        "border":              "#1E2A45",   # Deep space hairline border
        "border_focus":        "#A78BFA",   # Aurora violet focused border
        "primary":             "#A78BFA",   # Aurora violet primary
        "primary_hover":       "#C4B5FD",   # Bright violet hover
        "primary_dark":        "#7C3AED",   # Deep violet pressed
        "accent_teal":         "#2DD4BF",   # Electric teal accent
        "accent_teal_hover":   "#5EEAD4",   # Bright teal hover
        "accent_rose":         "#F472B6",   # Aurora rose/pink accent
        "accent_rose_hover":   "#F9A8D4",   # Bright rose hover
        "accent_gold":         "#FBBF24",   # Warm amber gold
        "accent_gold_hover":   "#FCD34D",   # Bright amber
        "success":             "#34D399",   # Emerald green success
        "success_hover":       "#6EE7B7",   # Bright emerald
        "danger":              "#F87171",   # Coral danger / obese
        "danger_hover":        "#FCA5A5",   # Bright coral
        "warning":             "#FBBF24",   # Amber warning
        "warning_hover":       "#FCD34D",   # Bright amber
        "text":                "#E2E8FF",   # Luminous blue-white text
        "text_muted":          "#8892B0",   # Muted slate-blue text
        "table_alt":           "#0F1C35",   # Deep alternating row
        "table_heading_bg":    "#07111F",   # Ultra-deep heading
        "table_heading_fg":    "#A78BFA",   # Violet heading text
        "status_bg":           "#040810",   # Void status dock
        "header_l":            "#060C1A",   # Deep space header left
        "header_r":            "#0C1630",   # Deep violet-navy right
        "input_bg":            "#0A1525",   # Dark cyber input field
        "suggestion_bg":       "#080F1F",   # Telemetry box background
        "tab_bar_bg":          "#0A1525",
        "tab_btn_bg":          "#0A1525",
        "scrollbar_trough":    "#06101E",
        "scrollbar_thumb":     "#1E2A45",
        "scrollbar_active":    "#A78BFA",
        "badge_gold_bg":       "#1F1500",
        "badge_gold_fg":       "#FBBF24",
        "hud_cyan":            "#2DD4BF",
        "hud_green":           "#34D399",
        "hud_amber":           "#FBBF24",
        "hud_crimson":         "#F87171",
        "glass_tint":          "#0C1428",   # Glass panel tint
        "glass_border":        "#2A3A5E",   # Glass panel border
        "star_bg":             "#0A1525",   # Aurora wash for star-field
    }
}

CURRENT_THEME = "dark"

# Active Theme Colors (module-level globals for backward compatibility)
COLOR_BG            = THEMES["dark"]["bg"]
COLOR_CARD          = THEMES["dark"]["card"]
COLOR_CARD_SHADOW   = THEMES["dark"]["card_shadow"]
COLOR_BORDER        = THEMES["dark"]["border"]
COLOR_BORDER_FOCUS  = THEMES["dark"]["border_focus"]
COLOR_PRIMARY       = THEMES["dark"]["primary"]
COLOR_PRIMARY_HOVER = THEMES["dark"]["primary_hover"]
COLOR_PRIMARY_DARK  = THEMES["dark"]["primary_dark"]
COLOR_SUCCESS       = THEMES["dark"]["success"]
COLOR_SUCCESS_HOVER = THEMES["dark"]["success_hover"]
COLOR_DANGER        = THEMES["dark"]["danger"]
COLOR_DANGER_HOVER  = THEMES["dark"]["danger_hover"]
COLOR_WARNING       = THEMES["dark"]["warning"]
COLOR_WARNING_HOVER = THEMES["dark"]["warning_hover"]
COLOR_TEXT          = THEMES["dark"]["text"]
COLOR_TEXT_MUTED    = THEMES["dark"]["text_muted"]
COLOR_TABLE_ALT     = THEMES["dark"]["table_alt"]
COLOR_HEADER_L      = THEMES["dark"]["header_l"]
COLOR_HEADER_R      = THEMES["dark"]["header_r"]

# ---------------------------------------------------------------------------
# TYPOGRAPHY
# ---------------------------------------------------------------------------
FONT_FAMILY = "Segoe UI"


def get_best_font_family(root: Optional[tk.Tk] = None) -> str:
    """Returns the best available modern font on this system."""
    try:
        available = tkfont.families(root)
    except Exception:
        available = []
    for candidate in ("Poppins", "Segoe UI Variable Display", "Segoe UI Variable Text",
                      "Segoe UI", "Inter", "Roboto", "Helvetica Neue", "Arial"):
        if candidate in available:
            return candidate
    return "Arial"


def get_font(size: float = 10, weight: str = "normal", slant: str = "roman") -> tuple:
    """Returns a validated font tuple — always converts size to int (Tkinter requirement)."""
    return (FONT_FAMILY, int(round(float(size))), weight, slant)


def get_header_font(size: float = 16, weight: str = "bold") -> tuple:
    """Convenience font factory for section and page headers."""
    return (FONT_FAMILY, int(round(float(size))), weight)


def get_micro_font(size: float = 8, weight: str = "bold") -> tuple:
    """Convenience font factory for uppercase micro-labels and badges."""
    return (FONT_FAMILY, int(round(float(size))), weight)


# ---------------------------------------------------------------------------
# THEME MANAGER
# ---------------------------------------------------------------------------

def set_theme(theme_name: str, root: Optional[tk.Tk] = None) -> None:
    """Update global color constants to match the requested theme."""
    global CURRENT_THEME
    global COLOR_BG, COLOR_CARD, COLOR_CARD_SHADOW, COLOR_BORDER, COLOR_BORDER_FOCUS
    global COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_PRIMARY_DARK
    global COLOR_SUCCESS, COLOR_SUCCESS_HOVER, COLOR_DANGER, COLOR_DANGER_HOVER
    global COLOR_WARNING, COLOR_WARNING_HOVER, COLOR_TEXT, COLOR_TEXT_MUTED
    global COLOR_TABLE_ALT, COLOR_HEADER_L, COLOR_HEADER_R

    theme_key = theme_name.lower() if theme_name.lower() in THEMES else "dark"
    theme = THEMES[theme_key]
    CURRENT_THEME = theme_key

    COLOR_BG            = theme["bg"]
    COLOR_CARD          = theme["card"]
    COLOR_CARD_SHADOW   = theme["card_shadow"]
    COLOR_BORDER        = theme["border"]
    COLOR_BORDER_FOCUS  = theme["border_focus"]
    COLOR_PRIMARY       = theme["primary"]
    COLOR_PRIMARY_HOVER = theme["primary_hover"]
    COLOR_PRIMARY_DARK  = theme["primary_dark"]
    COLOR_SUCCESS       = theme["success"]
    COLOR_SUCCESS_HOVER = theme["success_hover"]
    COLOR_DANGER        = theme["danger"]
    COLOR_DANGER_HOVER  = theme["danger_hover"]
    COLOR_WARNING       = theme["warning"]
    COLOR_WARNING_HOVER = theme["warning_hover"]
    COLOR_TEXT          = theme["text"]
    COLOR_TEXT_MUTED    = theme["text_muted"]
    COLOR_TABLE_ALT     = theme["table_alt"]
    COLOR_HEADER_L      = theme["header_l"]
    COLOR_HEADER_R      = theme["header_r"]

    if root:
        configure_styles(root)


def get_theme_dict() -> Dict[str, str]:
    """Get active theme dictionary."""
    return THEMES.get(CURRENT_THEME, THEMES["dark"])


# ---------------------------------------------------------------------------
# GLOBAL TTK STYLE CONFIGURATION
# ---------------------------------------------------------------------------

def configure_styles(root: tk.Tk) -> None:
    """Applies the FitTrack Aurora Space Station design to every ttk widget."""
    global FONT_FAMILY
    FONT_FAMILY = get_best_font_family(root)
    theme = get_theme_dict()
    is_dark = (CURRENT_THEME == "dark")

    s = ttk.Style(root)
    try:
        s.theme_use("clam")
    except Exception:
        pass

    # Base reset
    s.configure(".", background=COLOR_BG, foreground=COLOR_TEXT, font=get_font(10))

    # Frames
    s.configure("Card.TFrame",   background=COLOR_CARD, relief="flat", borderwidth=0)
    s.configure("Header.TFrame", background=COLOR_PRIMARY, relief="flat", borderwidth=0)

    # Labels
    s.configure("TLabel",                background=COLOR_BG,      foreground=COLOR_TEXT,       font=get_font(10))
    s.configure("HeaderTitle.TLabel",    background=COLOR_PRIMARY,  foreground=COLOR_TEXT,       font=get_font(16, "bold"))
    s.configure("HeaderSubtitle.TLabel", background=COLOR_PRIMARY,  foreground=AURORA_TEAL,      font=get_font(9))
    s.configure("CardTitle.TLabel",      background=COLOR_CARD,     foreground=COLOR_TEXT,       font=get_font(11, "bold"))
    s.configure("CardText.TLabel",       background=COLOR_CARD,     foreground=COLOR_TEXT,       font=get_font(10))
    s.configure("CardMuted.TLabel",      background=COLOR_CARD,     foreground=COLOR_TEXT_MUTED, font=get_font(9))
    s.configure("CardValue.TLabel",      background=COLOR_CARD,     foreground=COLOR_PRIMARY,    font=get_font(28, "bold"))
    s.configure("FormLabel.TLabel",      background=COLOR_CARD,     foreground=COLOR_TEXT,       font=get_font(9, "bold"))
    s.configure("StatLabel.TLabel",      background=COLOR_CARD,     foreground=COLOR_TEXT_MUTED, font=get_font(8, "bold"))
    s.configure("StatVal.TLabel",        background=COLOR_CARD,     foreground=COLOR_TEXT,       font=get_font(20, "bold"))

    # Entry
    s.configure("TEntry",
                fieldbackground=theme.get("input_bg", COLOR_CARD),
                background=COLOR_BORDER,
                foreground=COLOR_TEXT,
                insertcolor=COLOR_TEXT,
                font=get_font(10))
    s.map("TEntry",
          fieldbackground=[("focus", theme.get("input_bg", COLOR_CARD))],
          bordercolor=[("focus", COLOR_BORDER_FOCUS)])

    # Combobox
    s.configure("TCombobox",
                fieldbackground=theme.get("input_bg", COLOR_CARD),
                background=COLOR_BORDER,
                foreground=COLOR_TEXT,
                arrowcolor=COLOR_PRIMARY,
                selectforeground=COLOR_TEXT,
                selectbackground=theme.get("input_bg", COLOR_CARD),
                font=get_font(10))
    s.map("TCombobox",
          fieldbackground=[("readonly", theme.get("input_bg", COLOR_CARD)),
                           ("focus",    theme.get("input_bg", COLOR_CARD))],
          foreground=[("readonly", COLOR_TEXT)],
          selectbackground=[("readonly", theme.get("input_bg", COLOR_CARD))],
          selectforeground=[("readonly", COLOR_TEXT)])

    # Button
    s.configure("TButton",
                font=get_font(10, "bold"),
                background=COLOR_BORDER,
                foreground=COLOR_TEXT,
                borderwidth=0,
                focuscolor="none")
    s.map("TButton",
          background=[("active", theme["border_focus"]), ("pressed", theme["primary_dark"])])

    # Scale
    scale_trough = theme.get("input_bg", "#0A1525") if is_dark else "#DDD6FE"
    s.configure("TScale",
                background=COLOR_CARD,
                troughcolor=scale_trough,
                sliderlength=18,
                sliderrelief="flat")
    s.map("TScale", background=[("active", COLOR_PRIMARY)])

    # Treeview
    select_fg = COLOR_BG if is_dark else "#FFFFFF"
    s.configure("Treeview",
                background=COLOR_CARD,
                foreground=COLOR_TEXT,
                fieldbackground=COLOR_CARD,
                rowheight=36,
                font=get_font(10),
                borderwidth=0)
    s.configure("Treeview.Heading",
                background=theme["table_heading_bg"],
                foreground=theme["table_heading_fg"],
                font=get_font(9, "bold"),
                relief="flat",
                borderwidth=0,
                padding=7)
    s.map("Treeview",
          background=[("selected", COLOR_PRIMARY)],
          foreground=[("selected", select_fg)])
    s.map("Treeview.Heading",
          background=[("active", theme["border"])])

    # Custom scrollbars
    s.layout("Vertical.TScrollbar", [
        ("Vertical.Scrollbar.trough", {
            "children": [("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})],
            "sticky": "ns"
        })
    ])
    s.configure("Vertical.TScrollbar",
                troughcolor=theme["scrollbar_trough"],
                background=theme["scrollbar_thumb"],
                borderwidth=0,
                gripcount=0,
                arrowsize=0)

    s.layout("Horizontal.TScrollbar", [
        ("Horizontal.Scrollbar.trough", {
            "children": [("Horizontal.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})],
            "sticky": "ew"
        })
    ])
    s.configure("Horizontal.TScrollbar",
                troughcolor=theme["scrollbar_trough"],
                background=theme["scrollbar_thumb"],
                borderwidth=0,
                gripcount=0,
                arrowsize=0)

    s.map("Vertical.TScrollbar",   background=[("active", theme["scrollbar_active"])])
    s.map("Horizontal.TScrollbar", background=[("active", theme["scrollbar_active"])])


# ---------------------------------------------------------------------------
# WIDGET FACTORIES
# ---------------------------------------------------------------------------

def make_modern_button(
    parent,
    text: str,
    style_type: str = "primary",
    command=None,
    width: int = 15
) -> tk.Button:
    """
    Creates a flat styled tk.Button with animated hover feedback.
    Uses Aurora Space Station palette colors.
    """
    theme = get_theme_dict()
    is_dark = (CURRENT_THEME == "dark")

    if is_dark:
        themes_map = {
            "primary":   (AURORA_VIOLET,   "#C4B5FD",   "#7C3AED",   "#050811"),
            "success":   ("#065F46",        "#34D399",   "#064E3B",   "#FFFFFF"),
            "danger":    ("#7F1D1D",        "#F87171",   "#450A0A",   "#FFFFFF"),
            "warning":   ("#78350F",        "#FBBF24",   "#451A03",   "#050811"),
            "secondary": ("#121D35",        "#1E2A45",   "#0D1425",   "#E2E8FF"),
        }
    else:
        themes_map = {
            "primary":   ("#6D28D9",        "#5B21B6",   "#4C1D95",   "#FFFFFF"),
            "success":   ("#047857",        "#065F46",   "#064E3B",   "#FFFFFF"),
            "danger":    ("#BE123C",        "#9F1239",   "#881337",   "#FFFFFF"),
            "warning":   ("#B45309",        "#92400E",   "#78350F",   "#FFFFFF"),
            "secondary": ("#EDE9FE",        "#DDD6FE",   "#C4B5FD",   "#1E1B4B"),
        }

    bg, hover, pressed, fg = themes_map.get(style_type, themes_map["secondary"])

    btn = tk.Button(
        parent,
        text=text,
        command=command,
        font=get_font(10, "bold"),
        bg=bg,
        fg=fg,
        activebackground=pressed,
        activeforeground=fg,
        relief="flat",
        bd=0,
        width=width,
        cursor="hand2",
        padx=12,
        pady=8,
    )
    btn.style_type = style_type

    def _enter(_e):
        animate_color(btn, btn.cget("background"), hover)

    def _leave(_e):
        animate_color(btn, btn.cget("background"), bg)

    def _focus_in(_e):
        btn.config(highlightthickness=1,
                   highlightbackground=COLOR_BORDER_FOCUS,
                   highlightcolor=COLOR_BORDER_FOCUS)

    def _focus_out(_e):
        btn.config(highlightthickness=0)

    btn.bind("<Enter>",    _enter)
    btn.bind("<Leave>",    _leave)
    btn.bind("<FocusIn>",  _focus_in,  add="+")
    btn.bind("<FocusOut>", _focus_out, add="+")
    return btn


def retheme_button(btn: tk.Button) -> None:
    """Updates an existing modern button's colors to match the active CURRENT_THEME."""
    if not hasattr(btn, "style_type"):
        return
    is_dark = (CURRENT_THEME == "dark")
    if is_dark:
        themes_map = {
            "primary":   (AURORA_VIOLET,  "#C4B5FD",  "#7C3AED",  "#050811"),
            "success":   ("#065F46",       "#34D399",  "#064E3B",  "#FFFFFF"),
            "danger":    ("#7F1D1D",       "#F87171",  "#450A0A",  "#FFFFFF"),
            "warning":   ("#78350F",       "#FBBF24",  "#451A03",  "#050811"),
            "secondary": ("#121D35",       "#1E2A45",  "#0D1425",  "#E2E8FF"),
        }
    else:
        themes_map = {
            "primary":   ("#6D28D9",       "#5B21B6",  "#4C1D95",  "#FFFFFF"),
            "success":   ("#047857",       "#065F46",  "#064E3B",  "#FFFFFF"),
            "danger":    ("#BE123C",       "#9F1239",  "#881337",  "#FFFFFF"),
            "warning":   ("#B45309",       "#92400E",  "#78350F",  "#FFFFFF"),
            "secondary": ("#EDE9FE",       "#DDD6FE",  "#C4B5FD",  "#1E1B4B"),
        }
    bg, hover, pressed, fg = themes_map.get(btn.style_type, themes_map["secondary"])
    try:
        btn.config(bg=bg, fg=fg, activebackground=pressed, activeforeground=fg)
    except Exception:
        pass


def make_card(parent, border_color: Optional[str] = None) -> tuple:
    """
    Returns (wrapper, inner_card) — a standard card with 1px border.
    Use make_glass_card() for the new glassmorphism look.
    """
    bdr = border_color if border_color else COLOR_BORDER
    wrapper = tk.Frame(parent, bg=bdr, bd=0)
    wrapper.rowconfigure(0, weight=1)
    wrapper.columnconfigure(0, weight=1)
    card = tk.Frame(wrapper, bg=COLOR_CARD, bd=0)
    card.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
    return wrapper, card


def make_glass_card(parent, tint: Optional[str] = None) -> tuple:
    """
    Returns (wrapper, inner_card) for the Glassmorphism Space Station style.
    Creates a frosted-glass floating card effect with:
    - A colored aurora accent border
    - A top refraction highlight line (lighter shade at top)
    - The inner bg is the glass tinted surface
    """
    theme = get_theme_dict()
    glass_border = tint if tint else theme.get("glass_border", COLOR_BORDER)
    glass_bg     = theme.get("glass_tint", COLOR_CARD)

    # Outer wrapper = colored aurora border
    wrapper = tk.Frame(parent, bg=glass_border, bd=0)
    wrapper.rowconfigure(0, weight=1)
    wrapper.columnconfigure(0, weight=1)

    # Inner card = dark glass tinted surface
    card = tk.Frame(wrapper, bg=glass_bg, bd=0)
    card.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

    return wrapper, card


# ---------------------------------------------------------------------------
# TOOLTIP
# ---------------------------------------------------------------------------

class ToolTip:
    """Lightweight borderless luxury tooltip shown on hover."""

    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self._window: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")

    def _show(self, _event=None) -> None:
        if self._window or not self.text:
            return
        try:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        except Exception:
            return
        self._window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        is_dark = (CURRENT_THEME == "dark")
        tip_bg    = "#0C1428" if is_dark else "#1E1B4B"
        tip_fg    = "#A78BFA" if is_dark else "#FFFFFF"
        bdr_color = "#A78BFA" if is_dark else "#7C3AED"

        frame = tk.Frame(tw, bg=bdr_color, bd=1)
        frame.pack()
        tk.Label(
            frame,
            text=self.text,
            justify=tk.LEFT,
            background=tip_bg,
            foreground=tip_fg,
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=5,
            font=get_font(9),
        ).pack()

    def _hide(self, _event=None) -> None:
        if self._window:
            try:
                self._window.destroy()
            except Exception:
                pass
            self._window = None


def add_tooltip(widget: tk.Widget, text: str) -> "ToolTip":
    """Convenience wrapper — attaches and returns a ToolTip."""
    return ToolTip(widget, text)


# ---------------------------------------------------------------------------
# ANIMATION HELPERS
# ---------------------------------------------------------------------------

def animate_color(
    widget: tk.Widget,
    start_hex: str,
    end_hex: str,
    duration_ms: int = 120,
    step_ms: int = 15,
    current_step: int = 0,
    target_prop: str = "background",
) -> None:
    """Smooth background/foreground colour transition using after()."""
    key = f"_anim_{target_prop}"

    if current_step == 0 and hasattr(widget, key):
        try:
            widget.after_cancel(getattr(widget, key))
        except Exception:
            pass

    try:
        r1, g1, b1 = int(start_hex[1:3], 16), int(start_hex[3:5], 16), int(start_hex[5:7], 16)
        r2, g2, b2 = int(end_hex[1:3],   16), int(end_hex[3:5],   16), int(end_hex[5:7],   16)
    except Exception:
        return

    total = max(1, duration_ms // step_ms)

    if current_step >= total:
        try:
            widget.config(**{target_prop: end_hex})
        except Exception:
            pass
        try:
            delattr(widget, key)
        except Exception:
            pass
        return

    ratio = current_step / total
    color = "#{:02x}{:02x}{:02x}".format(
        int(r1 + (r2 - r1) * ratio),
        int(g1 + (g2 - g1) * ratio),
        int(b1 + (b2 - b1) * ratio),
    )
    try:
        widget.config(**{target_prop: color})
        after_id = widget.after(
            step_ms,
            lambda: animate_color(widget, start_hex, end_hex,
                                  duration_ms, step_ms, current_step + 1, target_prop),
        )
        setattr(widget, key, after_id)
    except Exception:
        pass


def highlight_card(card_frame: tk.Frame,
                   highlight: Optional[str] = None,
                   final: Optional[str] = None) -> None:
    """Flash a card with subtle accent highlight then fade back."""
    if highlight is None:
        highlight = AURORA_VIOLET if CURRENT_THEME == "dark" else "#7C3AED"
    if final is None:
        final = COLOR_CARD
    try:
        animate_color(card_frame, highlight, final, duration_ms=400, step_ms=25)
    except Exception:
        pass
