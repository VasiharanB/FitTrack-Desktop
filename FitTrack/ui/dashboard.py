"""
ui/dashboard.py
===============
FitTrackDashboard — Glassmorphism Space Station Edition.

Layout: Animated star-field background → frosted-glass floating panels
  Header  : Translucent glass strip with aurora gradient + live clock
  Body    : 3-column glass panels (Bio Entry | Orbital Sphere | Analytics)
  Lower   : Biometric Constellation glass table
  Footer  : Frosted status strip
"""

import getpass
import math
import random
import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
from typing import Optional, List

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as ticker

from models.person import HealthRecord
from database.db import DatabaseManager
from services.bmi_service import BMIService
from services.validator import InputValidator, ValidationError
from services.export_service import ExportService

from ui import styles
from ui.dialogs import AlertDialog, ConfirmDialog, SettingsDialog
from ui.table import HealthRecordTable
from ui.gauge import OrbitalBMISphere, BiometricAvatar


class FitTrackDashboard(tk.Frame):
    """Central application dashboard — Glassmorphism Space Station aesthetic."""

    APP_VERSION = "3.0.0-ORBITAL"

    def __init__(self, parent: tk.Tk, db_manager: DatabaseManager) -> None:
        super().__init__(parent, bg=styles.COLOR_BG)
        self.parent = parent
        self.db = db_manager

        # State
        self.selected_record_id: Optional[int] = None
        self._selected_record_created_at: Optional[str] = None
        self._chart_anim_job: Optional[str] = None
        self._status_timer_id: Optional[str] = None
        self._chart_view_mode: str = "auto"
        self._syncing_inputs: bool = False
        self._star_job: Optional[str] = None

        # Card frame refs
        self._bmi_card_frame: Optional[tk.Frame] = None
        self._form_card_frame: Optional[tk.Frame] = None

        # Star field data
        self._stars: list = []

        self.pack(fill=tk.BOTH, expand=True)
        self._build_layout()
        self._bind_shortcuts()
        self.refresh_dashboard()
        self.name_entry.focus_set()

    # ======================================================================
    # LAYOUT CONSTRUCTION
    # ======================================================================

    def _build_layout(self) -> None:
        """Assemble: starfield background → header → scrollable body → status bar."""
        self._build_header()
        self._build_status_bar()

        # Scrollable container
        self.scroll_container = tk.Frame(self, bg=styles.COLOR_BG)
        self.scroll_container.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        self.body_scrollbar = ttk.Scrollbar(self.scroll_container, orient="vertical",
                                             style="Vertical.TScrollbar")
        self.body_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.body_canvas = tk.Canvas(
            self.scroll_container, bg=styles.COLOR_BG, highlightthickness=0,
            yscrollcommand=self.body_scrollbar.set
        )
        self.body_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.body_scrollbar.config(command=self.body_canvas.yview)

        # Draw star-field on the body_canvas background
        self._init_stars()
        self.body_canvas.bind("<Configure>", self._on_canvas_configure_with_stars)

        self.scrollable_frame = tk.Frame(self.body_canvas, bg=styles.COLOR_BG)
        self._window_id = self.body_canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )

        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self._bind_mousewheel_and_keyboard()
        self._build_body()

    def _init_stars(self) -> None:
        """Create random star data for the background star-field."""
        self._stars = []
        for _ in range(180):
            self._stars.append({
                "x": random.random(),       # fraction of canvas width
                "y": random.random(),       # fraction of canvas height
                "r": random.choice([1, 1, 1, 2, 2, 3]),
                "speed": random.uniform(0.00008, 0.00022),
                "brightness": random.choice(["#FFFFFF", "#A78BFA", "#2DD4BF",
                                              "#C4B5FD", "#5EEAD4", "#F9A8D4"]),
                "layer": random.choice([1, 2, 3]),
            })

    def _draw_starfield(self) -> None:
        """Render the animated star-field on the body canvas background."""
        self.body_canvas.delete("stars")
        theme = styles.get_theme_dict()
        is_dark = (styles.CURRENT_THEME == "dark")
        if not is_dark:
            return   # Stars not shown in light mode

        w = self.body_canvas.winfo_width()
        h = self.body_canvas.winfo_height()
        if w < 10 or h < 10:
            return

        for star in self._stars:
            sx = int(star["x"] * w)
            sy = int(star["y"] * h)
            r  = star["r"]
            col = star["brightness"]
            if r == 1:
                self.body_canvas.create_rectangle(
                    sx, sy, sx + 1, sy + 1, fill=col, outline="", tags="stars"
                )
            else:
                self.body_canvas.create_oval(
                    sx - r, sy - r, sx + r, sy + r,
                    fill=col, outline="", tags="stars"
                )

        self.body_canvas.tag_lower("stars")

    def _animate_stars(self) -> None:
        """Slowly drift stars horizontally for parallax effect."""
        is_dark = (styles.CURRENT_THEME == "dark")
        if not is_dark:
            return
        w = self.body_canvas.winfo_width()
        for star in self._stars:
            star["x"] = (star["x"] + star["speed"] * star["layer"]) % 1.0
        self._draw_starfield()
        try:
            self._star_job = self.after(50, self._animate_stars)
        except Exception:
            pass

    def _on_canvas_configure_with_stars(self, event: tk.Event) -> None:
        """Handle body canvas resize + re-draw stars and aurora gradient."""
        self.body_canvas.itemconfig(self._window_id, width=event.width)
        req_height = self.scrollable_frame.winfo_reqheight()
        if event.height > req_height:
            self.body_canvas.itemconfig(self._window_id, height=event.height)
        else:
            self.body_canvas.itemconfig(self._window_id, height=req_height)
        self.body_canvas.configure(scrollregion=self.body_canvas.bbox("all"))
        self._draw_aurora_wash(event.width, max(event.height, req_height))
        self._draw_starfield()

    def _draw_aurora_wash(self, w: int, h: int) -> None:
        """Draw soft aurora gradient wash bands on the body canvas background."""
        self.body_canvas.delete("aurora")
        is_dark = (styles.CURRENT_THEME == "dark")
        if not is_dark:
            return

        # Three subtle diagonal color washes
        washes = [
            ("#0C1050", 0.00, 0.25),   # deep indigo at top-left
            ("#0A2020", 0.30, 0.60),   # teal wash in middle
            ("#1A0520", 0.65, 1.00),   # rose wash at bottom
        ]
        for (col, y_start_frac, y_end_frac) in washes:
            y0 = int(h * y_start_frac)
            y1 = int(h * y_end_frac)
            strip_h = max(1, y1 - y0)
            for row in range(0, strip_h, 3):
                ratio = row / strip_h
                # Alpha fade in/out: peak at center
                fade = math.sin(math.pi * ratio)
                r = int(int(col[1:3], 16) * fade * 0.5)
                g = int(int(col[3:5], 16) * fade * 0.5)
                b = int(int(col[5:7], 16) * fade * 0.5)
                c = f"#{max(0,min(255,r)):02x}{max(0,min(255,g)):02x}{max(0,min(255,b)):02x}"
                yy = y0 + row
                self.body_canvas.create_rectangle(
                    0, yy, w, yy + 3, fill=c, outline="", tags="aurora"
                )
        self.body_canvas.tag_lower("aurora")
        self.body_canvas.tag_raise("stars", "aurora")

    def _on_frame_configure(self, _event: Optional[tk.Event] = None) -> None:
        self.body_canvas.configure(scrollregion=self.body_canvas.bbox("all"))
        canvas_height = self.body_canvas.winfo_height()
        req_height = self.scrollable_frame.winfo_reqheight()
        if canvas_height > req_height:
            self.body_canvas.itemconfig(self._window_id, height=canvas_height)
        else:
            self.body_canvas.itemconfig(self._window_id, height=req_height)

    # ------------------------------------------------------------------
    # MOUSEWHEEL & KEYBOARD SCROLLING
    # ------------------------------------------------------------------

    def _bind_mousewheel_and_keyboard(self) -> None:
        self.parent.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.parent.bind_all("<Button-4>",   self._on_mousewheel, add="+")
        self.parent.bind_all("<Button-5>",   self._on_mousewheel, add="+")
        self.parent.bind_all("<Prior>", lambda e: self._on_keypress_scroll("page_up"),   add="+")
        self.parent.bind_all("<Next>",  lambda e: self._on_keypress_scroll("page_down"), add="+")
        self.parent.bind_all("<Home>",  lambda e: self._on_keypress_scroll("home"),      add="+")
        self.parent.bind_all("<End>",   lambda e: self._on_keypress_scroll("end"),       add="+")
        self.parent.bind_all("<Up>",    lambda e: self._on_keypress_scroll("up"),        add="+")
        self.parent.bind_all("<Down>",  lambda e: self._on_keypress_scroll("down"),      add="+")

    def _resolve_widget(self, widget_ref) -> Optional[tk.Widget]:
        if widget_ref is None:
            return None
        if isinstance(widget_ref, str):
            try:
                return self.nametowidget(widget_ref)
            except Exception:
                return None
        return widget_ref

    def _is_over_table(self, widget) -> bool:
        if not hasattr(self, "record_table"):
            return False
        tree = getattr(self.record_table, "tree", None)
        table_ref = self.record_table
        temp = widget
        while temp:
            if temp == table_ref or temp == tree:
                return True
            try:
                temp = temp.master
            except (AttributeError, KeyError):
                break
        if widget and tree:
            w_str = str(widget)
            if str(tree) in w_str or str(table_ref) in w_str:
                return True
        return False

    def _on_mousewheel(self, event) -> None:
        widget = self._resolve_widget(event.widget)
        if event.num == 4:
            scroll_units = -1
        elif event.num == 5:
            scroll_units = 1
        elif getattr(event, "delta", 0) != 0:
            scroll_units = int(-1 * (event.delta / 120))
            if scroll_units == 0:
                scroll_units = -1 if event.delta > 0 else 1
        else:
            return

        if self._is_over_table(widget) and hasattr(self, "record_table"):
            try:
                self.record_table.tree.yview_scroll(scroll_units, "units")
            except Exception:
                pass
            return

        if hasattr(self, "body_canvas"):
            try:
                self.body_canvas.yview_scroll(scroll_units, "units")
            except Exception:
                pass

    def _on_keypress_scroll(self, action: str) -> str:
        focused = self.focus_get()
        if isinstance(focused, (tk.Entry, ttk.Combobox, ttk.Treeview)):
            return ""
        if action == "page_up":
            self.body_canvas.yview_scroll(-1, "pages")
        elif action == "page_down":
            self.body_canvas.yview_scroll(1, "pages")
        elif action == "home":
            self.body_canvas.yview_moveto(0.0)
        elif action == "end":
            self.body_canvas.yview_moveto(1.0)
        elif action == "up":
            self.body_canvas.yview_scroll(-1, "units")
        elif action == "down":
            self.body_canvas.yview_scroll(1, "units")
        return "break"

    # ------------------------------------------------------------------
    # HEADER — Frosted-glass strip
    # ------------------------------------------------------------------

    def _build_header(self) -> None:
        theme = styles.get_theme_dict()
        is_dark = (styles.CURRENT_THEME == "dark")

        self.header_canvas = tk.Canvas(self, bg=theme["header_l"], height=70, highlightthickness=0)
        self.header_canvas.pack(fill=tk.X, side=tk.TOP)

        # --- LEFT: logo + title ---
        self.header_left = tk.Frame(self.header_canvas, bg=theme["header_l"], height=70)
        logo_c = tk.Canvas(self.header_left, width=44, height=44,
                            bg=theme["header_l"], highlightthickness=0)
        logo_c.pack(side=tk.LEFT, padx=(16, 10), pady=13)
        self.logo_canvas = logo_c
        self._draw_logo(logo_c)

        text_col = tk.Frame(self.header_left, bg=theme["header_l"])
        text_col.pack(side=tk.LEFT, fill=tk.Y, pady=10)
        self.header_text_col = text_col

        title_row = tk.Frame(text_col, bg=theme["header_l"])
        title_row.pack(anchor=tk.W)
        self.header_title_row = title_row

        self.title_lbl = tk.Label(
            title_row, text="🌌 FitTrack  ORBITAL STATION",
            bg=theme["header_l"], fg="#FFFFFF",
            font=styles.get_font(14, "bold")
        )
        self.title_lbl.pack(side=tk.LEFT)

        # Version badge
        badge_bg  = theme.get("badge_gold_bg", "#1F1500")
        badge_fg  = theme.get("badge_gold_fg", "#FBBF24")
        badge_bdr = styles.AURORA_VIOLET if is_dark else "#7C3AED"
        self.badge_box = tk.Frame(
            title_row, bg=badge_bg,
            highlightthickness=1, highlightbackground=badge_bdr,
            padx=7, pady=2
        )
        self.badge_box.pack(side=tk.LEFT, padx=(10, 0))
        self.badge_box_lbl = tk.Label(
            self.badge_box, text=f"v{self.APP_VERSION}",
            bg=badge_bg, fg=badge_fg,
            font=styles.get_font(8, "bold")
        )
        self.badge_box_lbl.pack()

        self.subtitle_lbl = tk.Label(
            text_col, text="✦ GLASSMORPHISM SPACE STATION · BIOMETRIC ORBITAL CORE",
            bg=theme["header_l"], fg=styles.AURORA_TEAL if is_dark else "#0891B2",
            font=styles.get_font(8, "bold")
        )
        self.subtitle_lbl.pack(anchor=tk.W, pady=(2, 0))

        # --- CENTER: live clock ---
        clock_bg  = "#0C1050" if is_dark else "#312E81"
        clock_bdr = "#A78BFA" if is_dark else "#7C3AED"
        self.clock_capsule = tk.Frame(
            self.header_canvas, bg=clock_bg,
            highlightthickness=1, highlightbackground=clock_bdr,
            padx=14, pady=4
        )
        self.header_center = self.clock_capsule

        self.date_lbl = tk.Label(
            self.clock_capsule, text="--", bg=clock_bg,
            fg=styles.AURORA_TEAL if is_dark else "#A5B4FC",
            font=styles.get_font(8)
        )
        self.date_lbl.pack()
        self.time_lbl = tk.Label(
            self.clock_capsule, text="--", bg=clock_bg,
            fg="#FFFFFF",
            font=styles.get_font(13, "bold")
        )
        self.time_lbl.pack()

        # --- RIGHT: Nav buttons ---
        self.header_right = tk.Frame(self.header_canvas, bg=theme["header_r"], height=70)

        # Connected badge
        conn_bg  = "#0C1050" if is_dark else "#312E81"
        conn_bdr = "#34D399" if is_dark else "#059669"
        self.db_status_box = tk.Frame(
            self.header_right, bg=conn_bg,
            highlightthickness=1, highlightbackground=conn_bdr,
            padx=8, pady=4
        )
        self.db_status_box.pack(side=tk.LEFT, padx=(0, 10), pady=18)
        self.db_status_lbl = tk.Label(
            self.db_status_box, text="● Connected",
            bg=conn_bg, fg="#34D399",
            font=styles.get_font(9, "bold")
        )
        self.db_status_lbl.pack()

        # Theme toggle
        theme_txt = "☾ Dark" if styles.CURRENT_THEME == "light" else "☀ Light"
        btn_bg  = "#1A0A3E" if is_dark else "#4C1D95"
        btn_bdr = styles.AURORA_VIOLET if is_dark else "#A78BFA"
        self.theme_btn = tk.Button(
            self.header_right, text=theme_txt,
            bg=btn_bg, fg="#FFFFFF",
            activebackground=styles.AURORA_VIOLET,
            activeforeground="#050811",
            relief="flat", bd=0, cursor="hand2",
            padx=11, pady=5,
            highlightthickness=1, highlightbackground=btn_bdr,
            font=styles.get_font(9, "bold"),
            command=self._toggle_theme,
        )
        self.theme_btn.pack(side=tk.LEFT, padx=3, pady=18)

        self.nav_buttons = [self.theme_btn]
        for label, cmd in [
            ("⚙ Settings", self._on_settings),
            ("ℹ About",    self._on_about),
        ]:
            b = tk.Button(
                self.header_right, text=label,
                bg=btn_bg, fg="#FFFFFF",
                activebackground=styles.AURORA_VIOLET,
                activeforeground="#050811",
                relief="flat", bd=0, cursor="hand2",
                padx=10, pady=5,
                highlightthickness=1, highlightbackground=styles.COLOR_BORDER,
                font=styles.get_font(9, "bold"),
                command=cmd,
            )
            b.pack(side=tk.LEFT, padx=3, pady=18)
            self.nav_buttons.append(b)

        # Place windows
        self._left_id   = self.header_canvas.create_window(0,   0,  anchor="nw", window=self.header_left,   height=70)
        self._center_id = self.header_canvas.create_window(640, 35, anchor="center", window=self.header_center)
        self._right_id  = self.header_canvas.create_window(1280, 0, anchor="ne", window=self.header_right,  height=70)

        self.header_canvas.bind("<Configure>", self._on_header_resize)
        self._update_clock()
        # Start star animation after layout
        self.after(500, self._animate_stars)

    def _draw_logo(self, canvas: tk.Canvas) -> None:
        canvas.delete("all")
        theme = styles.get_theme_dict()
        is_dark = (styles.CURRENT_THEME == "dark")
        ring_col = styles.AURORA_VIOLET if is_dark else "#7C3AED"
        orb_col  = styles.AURORA_TEAL   if is_dark else "#0891B2"
        # Orbital ring
        canvas.create_oval(2, 2, 42, 42, fill="", outline=ring_col, width=2)
        # Central orb
        canvas.create_oval(14, 14, 30, 30, fill=orb_col, outline="", width=0)
        # Diagonal orbit ring
        canvas.create_oval(6, 12, 38, 32, fill="", outline=ring_col, width=1,
                            dash=(3, 3))

    def _on_header_resize(self, event: Optional[tk.Event] = None) -> None:
        w = event.width  if event and hasattr(event, "width")  and event.width  > 1 else self.header_canvas.winfo_width()
        h = event.height if event and hasattr(event, "height") and event.height > 1 else self.header_canvas.winfo_height()
        if w < 10: w = 1280
        if h < 10: h = 70

        self.header_canvas.delete("grad")
        theme = styles.get_theme_dict()
        r1, g1, b1 = int(theme["header_l"][1:3], 16), int(theme["header_l"][3:5], 16), int(theme["header_l"][5:7], 16)
        r2, g2, b2 = int(theme["header_r"][1:3], 16), int(theme["header_r"][3:5], 16), int(theme["header_r"][5:7], 16)
        step = 4
        for i in range(0, w, step):
            ratio = i / max(1, w)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            clr = f"#{r:02x}{g:02x}{b:02x}"
            self.header_canvas.create_rectangle(i, 0, i + step, h,
                                                fill=clr, outline=clr, tags="grad")

        # Aurora bottom border
        is_dark = (styles.CURRENT_THEME == "dark")
        border_col = styles.AURORA_VIOLET if is_dark else "#7C3AED"
        self.header_canvas.create_line(0, h - 1, w, h - 1, fill=border_col, width=2, tags="grad")

        self.header_canvas.tag_lower("grad")
        self.header_canvas.coords(self._center_id, w // 2, h // 2)
        self.header_canvas.coords(self._right_id,  w,      0)

    # ------------------------------------------------------------------
    # STATUS BAR
    # ------------------------------------------------------------------

    def _build_status_bar(self) -> None:
        theme = styles.get_theme_dict()
        self.status_bar = tk.Frame(self, bg=theme["status_bg"], height=26, bd=0)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)

        db_path = str(self.db.db_path)
        if len(db_path) > 55:
            db_path = "..." + db_path[-52:]
        try:
            user = getpass.getuser()
        except Exception:
            user = "user"

        def _sep():
            tk.Label(self.status_bar, text="|", bg=theme["status_bg"],
                     fg=styles.COLOR_TEXT_MUTED, font=styles.get_font(9)).pack(side=tk.LEFT, padx=2)

        self.sb_db_lbl = tk.Label(self.status_bar, text=f"  ✦ {db_path}",
                                   bg=theme["status_bg"], fg=styles.COLOR_TEXT, font=styles.get_font(9))
        self.sb_db_lbl.pack(side=tk.LEFT, padx=4, pady=3)
        _sep()
        self.sb_user_lbl = tk.Label(self.status_bar, text=f"◎ {user}",
                                    bg=theme["status_bg"], fg=styles.COLOR_TEXT, font=styles.get_font(9))
        self.sb_user_lbl.pack(side=tk.LEFT, padx=4, pady=3)
        _sep()
        self.sb_ver_lbl = tk.Label(self.status_bar, text=f"v{self.APP_VERSION}",
                                   bg=theme["status_bg"], fg=styles.COLOR_TEXT, font=styles.get_font(9))
        self.sb_ver_lbl.pack(side=tk.LEFT, padx=4, pady=3)
        _sep()

        self.status_msg_lbl = tk.Label(
            self.status_bar, text="● System Nominal",
            bg=theme["status_bg"], fg=styles.AURORA_TEAL, font=styles.get_font(9, "bold")
        )
        self.status_msg_lbl.pack(side=tk.LEFT, padx=12, pady=3)

        self.status_time_lbl = tk.Label(
            self.status_bar, text="--:--:--",
            bg=theme["status_bg"], fg=styles.COLOR_TEXT, font=styles.get_font(9)
        )
        self.status_time_lbl.pack(side=tk.RIGHT, padx=16, pady=3)

    # ------------------------------------------------------------------
    # BODY — 3-column glass cockpit
    # ------------------------------------------------------------------

    def _build_body(self) -> None:
        # Top section: 3 glass panels
        self.top_section = tk.Frame(self.scrollable_frame, bg=styles.COLOR_BG, padx=14, pady=10)
        self.top_section.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        self.top_section.columnconfigure(0, weight=3, minsize=300)
        self.top_section.columnconfigure(1, weight=4, minsize=380)
        self.top_section.columnconfigure(2, weight=3, minsize=320)
        self.top_section.rowconfigure(0, weight=1, minsize=480)

        # Left: Bio Entry Panel
        lborder, linner = styles.make_glass_card(self.top_section,
                                                  tint=styles.AURORA_VIOLET if styles.CURRENT_THEME == "dark" else "#7C3AED")
        lborder.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._form_card_frame = linner
        self._build_bio_entry_panel(linner)

        # Center: Orbital Core
        cborder, cinner = styles.make_glass_card(self.top_section,
                                                  tint=styles.AURORA_TEAL if styles.CURRENT_THEME == "dark" else "#0891B2")
        cborder.grid(row=0, column=1, sticky="nsew", padx=(0, 8))
        self._build_orbital_core(cinner)

        # Right: Analytics Wing
        rborder, rinner = styles.make_glass_card(self.top_section,
                                                  tint=styles.AURORA_ROSE if styles.CURRENT_THEME == "dark" else "#DB2777")
        rborder.grid(row=0, column=2, sticky="nsew")
        self._build_analytics_wing(rinner)

        self._top_card_borders = [lborder, cborder, rborder]
        self._top_card_inners  = [linner,  cinner,  rinner]
        self._top_card_tints   = [
            styles.AURORA_VIOLET if styles.CURRENT_THEME == "dark" else "#7C3AED",
            styles.AURORA_TEAL   if styles.CURRENT_THEME == "dark" else "#0891B2",
            styles.AURORA_ROSE   if styles.CURRENT_THEME == "dark" else "#DB2777",
        ]

        # Bottom section
        self.bottom_section = tk.Frame(self.scrollable_frame, bg=styles.COLOR_BG)
        self.bottom_section.pack(fill=tk.BOTH, expand=True, side=tk.TOP, padx=14, pady=(0, 14))

        self._build_stats_footer(self.bottom_section)
        self._build_table_section(self.bottom_section)

    # ------------------------------------------------------------------
    # LEFT PANEL: BIO ENTRY
    # ------------------------------------------------------------------

    def _build_bio_entry_panel(self, container: tk.Frame) -> None:
        theme = styles.get_theme_dict()
        is_dark = (styles.CURRENT_THEME == "dark")
        glass_bg = theme.get("glass_tint", styles.COLOR_CARD)

        # Section header
        hdr = tk.Frame(container, bg=glass_bg)
        hdr.pack(fill=tk.X, padx=16, pady=(14, 6))

        self.form_title_lbl = tk.Label(
            hdr, text="🔮 BIO ENTRY",
            bg=glass_bg, fg=styles.AURORA_VIOLET if is_dark else "#7C3AED",
            font=styles.get_font(12, "bold")
        )
        self.form_title_lbl.pack(side=tk.LEFT)
        tk.Label(hdr, text="// SUBJECT PROFILE",
                 bg=glass_bg, fg=styles.COLOR_TEXT_MUTED,
                 font=styles.get_font(8, "bold")).pack(side=tk.LEFT, padx=(8, 0))

        # Quick Presets
        preset_frame = tk.Frame(container, bg=glass_bg)
        preset_frame.pack(fill=tk.X, padx=16, pady=(0, 10))
        tk.Label(preset_frame, text="PRESETS:", bg=glass_bg,
                 fg=styles.COLOR_TEXT_MUTED, font=styles.get_font(8, "bold")).pack(side=tk.LEFT, padx=(0, 4))

        presets = [
            ("🏃 Athlete",  180.0, 74.0, 26, "Male"),
            ("🧘 Standard", 168.0, 62.0, 29, "Female"),
            ("🌱 Youth",    156.0, 48.0, 17, "Female"),
            ("🏋 Power",    182.0, 92.0, 31, "Male"),
        ]
        self._preset_buttons = []
        for p_name, p_h, p_w, p_a, p_g in presets:
            pb = tk.Button(
                preset_frame, text=p_name,
                bg=theme.get("input_bg", "#0A1525") if is_dark else "#EEF2FF",
                fg=styles.AURORA_VIOLET if is_dark else "#7C3AED",
                activebackground=styles.AURORA_VIOLET,
                activeforeground="#050811" if is_dark else "#FFFFFF",
                relief="flat", bd=0, cursor="hand2",
                font=styles.get_font(8, "bold"),
                padx=5, pady=2,
                command=lambda h=p_h, w=p_w, a=p_a, g=p_g, n=p_name: self._apply_preset(n, h, w, a, g)
            )
            pb.pack(side=tk.LEFT, padx=2)
            self._preset_buttons.append(pb)

        # Form grid
        self.form_grid = tk.Frame(container, bg=glass_bg)
        self.form_grid.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 4))
        self.form_grid.columnconfigure(0, weight=1)
        self.form_grid.columnconfigure(1, weight=1)

        self.name_val   = tk.StringVar()
        self.age_val    = tk.StringVar()
        self.height_val = tk.StringVar()
        self.weight_val = tk.StringVar()
        self.gender_val = tk.StringVar()

        self._entry_borders = []
        self._form_labels   = []

        input_bg  = theme.get("input_bg", "#0A1525")
        bdr_col   = styles.COLOR_BORDER
        focus_col = styles.AURORA_VIOLET if is_dark else "#7C3AED"

        def _make_label(parent, text, row, col=0, colspan=2, padtop=2):
            lbl = tk.Label(parent, text=text, bg=glass_bg,
                           fg=styles.COLOR_TEXT_MUTED, font=styles.get_font(8, "bold"))
            lbl.grid(row=row, column=col, columnspan=colspan, sticky="w", pady=(padtop, 1))
            self._form_labels.append(lbl)
            return lbl

        def _make_entry_border(parent, row, col=0, colspan=2, padx_r=0, padx_l=0):
            bd = tk.Frame(parent, bg=bdr_col, bd=1)
            bd.grid(row=row, column=col, columnspan=colspan, sticky="ew",
                    pady=(0, 6), padx=(padx_l, padx_r))
            self._entry_borders.append(bd)
            return bd

        # Name
        _make_label(self.form_grid, "◎ SUBJECT NAME", 0)
        bd_name = _make_entry_border(self.form_grid, 1)
        self.name_entry = tk.Entry(bd_name, textvariable=self.name_val,
                                    bg=input_bg, fg=styles.COLOR_TEXT,
                                    insertbackground=styles.COLOR_TEXT, font=styles.get_font(10),
                                    bd=0, relief="flat", highlightthickness=0)
        self.name_entry.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)
        self._setup_placeholder(self.name_entry, "Enter full name")
        self.name_entry.bind("<FocusIn>",  lambda _e, b=bd_name: b.config(bg=focus_col), add="+")
        self.name_entry.bind("<FocusOut>", lambda _e, b=bd_name: b.config(bg=bdr_col),   add="+")

        # Age + Gender
        _make_label(self.form_grid, "AGE (YRS)", 2, col=0, colspan=1)
        _make_label(self.form_grid, "GENDER", 2, col=1, colspan=1)

        bd_age = _make_entry_border(self.form_grid, 3, col=0, colspan=1, padx_r=4)
        self.age_entry = tk.Entry(bd_age, textvariable=self.age_val,
                                   bg=input_bg, fg=styles.COLOR_TEXT,
                                   insertbackground=styles.COLOR_TEXT, font=styles.get_font(10),
                                   bd=0, relief="flat", highlightthickness=0)
        self.age_entry.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        self._setup_placeholder(self.age_entry, "1 – 120")
        self.age_entry.bind("<FocusIn>",  lambda _e, b=bd_age: b.config(bg=focus_col), add="+")
        self.age_entry.bind("<FocusOut>", lambda _e, b=bd_age: b.config(bg=bdr_col),   add="+")

        bd_gen = _make_entry_border(self.form_grid, 3, col=1, colspan=1, padx_l=4)
        self.gender_combo = ttk.Combobox(bd_gen, textvariable=self.gender_val,
                                          values=["Male", "Female"], state="readonly",
                                          font=styles.get_font(9))
        self.gender_combo.pack(fill=tk.BOTH, expand=True, padx=1, pady=2)
        self.gender_combo.set("Select gender")
        self.gender_combo.bind("<<ComboboxSelected>>", lambda _e: self._live_recalculate())
        self.gender_combo.bind("<FocusIn>",  lambda _e: bd_gen.config(bg=focus_col), add="+")
        self.gender_combo.bind("<FocusOut>", lambda _e: bd_gen.config(bg=bdr_col),   add="+")

        # Height
        h_hdr = tk.Frame(self.form_grid, bg=glass_bg)
        h_hdr.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(4, 1))
        lbl_h = tk.Label(h_hdr, text="HEIGHT (CM)", bg=glass_bg,
                          fg=styles.COLOR_TEXT_MUTED, font=styles.get_font(8, "bold"))
        lbl_h.pack(side=tk.LEFT)
        self._form_labels.append(lbl_h)
        self.height_display_lbl = tk.Label(h_hdr, text="175.0 cm", bg=glass_bg,
                                            fg=styles.COLOR_PRIMARY, font=styles.get_font(8, "bold"))
        self.height_display_lbl.pack(side=tk.RIGHT)

        bd_h = _make_entry_border(self.form_grid, 5)
        self.height_entry = tk.Entry(bd_h, textvariable=self.height_val,
                                      bg=input_bg, fg=styles.COLOR_TEXT,
                                      insertbackground=styles.COLOR_TEXT, font=styles.get_font(10),
                                      bd=0, relief="flat", highlightthickness=0)
        self.height_entry.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        self._setup_placeholder(self.height_entry, "50 – 250 cm")
        self.height_entry.bind("<FocusIn>",  lambda _e, b=bd_h: b.config(bg=focus_col), add="+")
        self.height_entry.bind("<FocusOut>", lambda _e, b=bd_h: b.config(bg=bdr_col),   add="+")

        self.height_scale = ttk.Scale(self.form_grid, from_=50.0, to=240.0,
                                       orient="horizontal", command=self._on_height_slider)
        self.height_scale.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self.height_scale.set(175.0)

        # Weight
        w_hdr = tk.Frame(self.form_grid, bg=glass_bg)
        w_hdr.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(4, 1))
        lbl_w = tk.Label(w_hdr, text="WEIGHT (KG)", bg=glass_bg,
                          fg=styles.COLOR_TEXT_MUTED, font=styles.get_font(8, "bold"))
        lbl_w.pack(side=tk.LEFT)
        self._form_labels.append(lbl_w)
        self.weight_display_lbl = tk.Label(w_hdr, text="70.0 kg", bg=glass_bg,
                                            fg=styles.COLOR_PRIMARY, font=styles.get_font(8, "bold"))
        self.weight_display_lbl.pack(side=tk.RIGHT)

        bd_w = _make_entry_border(self.form_grid, 8)
        self.weight_entry = tk.Entry(bd_w, textvariable=self.weight_val,
                                      bg=input_bg, fg=styles.COLOR_TEXT,
                                      insertbackground=styles.COLOR_TEXT, font=styles.get_font(10),
                                      bd=0, relief="flat", highlightthickness=0)
        self.weight_entry.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        self._setup_placeholder(self.weight_entry, "10 – 300 kg")
        self.weight_entry.bind("<FocusIn>",  lambda _e, b=bd_w: b.config(bg=focus_col), add="+")
        self.weight_entry.bind("<FocusOut>", lambda _e, b=bd_w: b.config(bg=bdr_col),   add="+")

        self.weight_scale = ttk.Scale(self.form_grid, from_=20.0, to=190.0,
                                       orient="horizontal", command=self._on_weight_slider)
        self.weight_scale.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self.weight_scale.set(70.0)

        # Traces
        self.height_val.trace_add("write", lambda *_: self._on_numeric_text_change("height"))
        self.weight_val.trace_add("write", lambda *_: self._on_numeric_text_change("weight"))
        self.age_val.trace_add("write", lambda *_: self._live_recalculate())

        # Command buttons
        self.btn_panel = tk.Frame(container, bg=glass_bg, pady=4)
        self.btn_panel.pack(fill=tk.X, side=tk.BOTTOM, padx=16, pady=(0, 12))
        self.btn_panel.columnconfigure(0, weight=1)
        self.btn_panel.columnconfigure(1, weight=1)

        self.calc_btn = styles.make_modern_button(
            self.btn_panel, "✦  Analyse & Save", "primary", self._handle_save, width=26)
        self.calc_btn.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))

        self.update_btn = styles.make_modern_button(
            self.btn_panel, "↺  Update", "success", self._handle_update, width=11)
        self.update_btn.grid(row=1, column=0, sticky="ew", padx=(0, 2), pady=(0, 5))

        self.clear_btn = styles.make_modern_button(
            self.btn_panel, "◌  Reset", "secondary", self._handle_clear, width=11)
        self.clear_btn.grid(row=1, column=1, sticky="ew", padx=(2, 0), pady=(0, 5))

        self.delete_btn = styles.make_modern_button(
            self.btn_panel, "✕  Delete", "danger", self._handle_delete, width=11)
        self.delete_btn.grid(row=2, column=0, sticky="ew", padx=(0, 2))

        self.export_btn = styles.make_modern_button(
            self.btn_panel, "↑  Export", "warning", self._handle_export, width=11)
        self.export_btn.grid(row=2, column=1, sticky="ew", padx=(2, 0))

        self.form_buttons = [self.calc_btn, self.update_btn, self.delete_btn,
                             self.clear_btn, self.export_btn]

        styles.add_tooltip(self.calc_btn,   "Compute BMI and save record (Ctrl+S)")
        styles.add_tooltip(self.update_btn, "Update loaded record")
        styles.add_tooltip(self.delete_btn, "Delete selected record (Delete)")
        styles.add_tooltip(self.clear_btn,  "Reset all fields (Ctrl+N)")
        styles.add_tooltip(self.export_btn, "Export records to CSV")

    # ------------------------------------------------------------------
    # CENTER PANEL: ORBITAL CORE
    # ------------------------------------------------------------------

    def _build_orbital_core(self, container: tk.Frame) -> None:
        theme = styles.get_theme_dict()
        is_dark = (styles.CURRENT_THEME == "dark")
        glass_bg = theme.get("glass_tint", styles.COLOR_CARD)

        # Header
        hdr = tk.Frame(container, bg=glass_bg)
        hdr.pack(fill=tk.X, padx=16, pady=(14, 4))
        self.hud_core_title = tk.Label(
            hdr, text="◎ ORBITAL BMI CORE",
            bg=glass_bg, fg=styles.AURORA_TEAL if is_dark else "#0891B2",
            font=styles.get_font(12, "bold")
        )
        self.hud_core_title.pack(side=tk.LEFT)
        tk.Label(hdr, text="// REAL-TIME ORBITAL SCANNER",
                 bg=glass_bg, fg=styles.COLOR_TEXT_MUTED,
                 font=styles.get_font(8, "bold")).pack(side=tk.LEFT, padx=(8, 0))

        # Orbital BMI Sphere
        self.radial_gauge = OrbitalBMISphere(
            container, width=360, height=220, initial_bmi=22.8,
            bg=glass_bg
        )
        self.radial_gauge.pack(fill=tk.X, padx=8, pady=(0, 6))
        self._bmi_card_frame = self.radial_gauge

        # Backward-compat virtual labels
        self.bmi_value_lbl = tk.Label(container, text="22.8")
        self.badge_frame   = tk.Frame(container)
        self.badge_lbl     = tk.Label(self.badge_frame, text="NORMAL")

        # Thin divider
        tk.Frame(container, bg=theme.get("glass_border", styles.COLOR_BORDER), height=1).pack(
            fill=tk.X, padx=16, pady=4)

        # Lower: Avatar + Telemetry Cards
        lower = tk.Frame(container, bg=glass_bg)
        lower.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 6))
        lower.columnconfigure(0, weight=4)
        lower.columnconfigure(1, weight=6)

        # Avatar
        av_frame = tk.Frame(lower, bg=glass_bg)
        av_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.avatar_canvas = BiometricAvatar(av_frame, width=120, height=155, bg=glass_bg)
        self.avatar_canvas.pack(fill=tk.BOTH, expand=True)

        # Telemetry mini-cards
        tele_deck = tk.Frame(lower, bg=glass_bg)
        tele_deck.grid(row=0, column=1, sticky="nsew")
        tele_deck.columnconfigure(0, weight=1)
        for r in range(3):
            tele_deck.rowconfigure(r, weight=1)

        def _tele_card(row, title, icon, accent):
            card_bg = theme.get("input_bg", "#0A1525") if is_dark else "#F5F3FF"
            bd = tk.Frame(tele_deck, bg=accent, bd=0)
            bd.grid(row=row, column=0, sticky="nsew", pady=3)
            inner = tk.Frame(bd, bg=card_bg, padx=8, pady=5)
            inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

            strip = tk.Frame(inner, bg=accent, width=3)
            strip.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

            txt = tk.Frame(inner, bg=card_bg)
            txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            tk.Label(txt, text=f"{icon}  {title}", bg=card_bg,
                     fg=styles.COLOR_TEXT_MUTED, font=styles.get_font(8, "bold")).pack(anchor=tk.W)
            val_lbl = tk.Label(txt, text="--", bg=card_bg,
                               fg=styles.COLOR_TEXT, font=styles.get_font(10, "bold"))
            val_lbl.pack(anchor=tk.W)
            return val_lbl, bd, inner

        self.range_lbl,   self._c1_bd, self._c1_in = _tele_card(0, "OPTIMAL TARGET DELTA", "⊕", styles.AURORA_TEAL   if is_dark else "#059669")
        self.bmr_val_lbl, self._c2_bd, self._c2_in = _tele_card(1, "METABOLIC BMR (BURN)",  "∿", styles.AURORA_VIOLET if is_dark else "#7C3AED")
        self.bsa_val_lbl, self._c3_bd, self._c3_in = _tele_card(2, "BODY SURFACE AREA",      "◻", styles.AURORA_AMBER  if is_dark else "#D97706")

        # Advisory box
        sugg_bg = theme.get("input_bg", "#080F1F") if is_dark else "#F5F3FF"
        sugg_bdr_col = theme.get("glass_border", styles.COLOR_BORDER)
        self._sugg_bd = tk.Frame(container, bg=sugg_bdr_col, bd=1)
        self._sugg_bd.pack(fill=tk.X, padx=12, pady=(4, 12))

        self.suggestion_area = tk.Frame(self._sugg_bd, bg=sugg_bg, padx=10, pady=6)
        self.suggestion_area.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.suggestion_area, text="✦  ORBITAL CLINICAL ADVISORY",
                 bg=sugg_bg, fg=styles.COLOR_PRIMARY,
                 font=styles.get_font(8, "bold")).pack(anchor=tk.W)

        self.suggestion_lbl = tk.Label(
            self.suggestion_area,
            text="Enter subject measurements to generate real-time clinical guidance.",
            bg=sugg_bg, fg=styles.COLOR_TEXT,
            font=styles.get_font(9), justify=tk.LEFT,
        )
        self.suggestion_lbl.pack(fill=tk.BOTH, expand=True, pady=(2, 0))
        self.suggestion_lbl.bind(
            "<Configure>",
            lambda e: self.suggestion_lbl.config(wraplength=max(100, e.width - 15)),
        )

    # ------------------------------------------------------------------
    # RIGHT PANEL: ANALYTICS WING
    # ------------------------------------------------------------------

    def _build_analytics_wing(self, container: tk.Frame) -> None:
        theme = styles.get_theme_dict()
        is_dark = (styles.CURRENT_THEME == "dark")
        glass_bg = theme.get("glass_tint", styles.COLOR_CARD)

        # Header
        hdr = tk.Frame(container, bg=glass_bg)
        hdr.pack(fill=tk.X, padx=16, pady=(14, 4))

        self.waveform_title = tk.Label(
            hdr, text="◈ ANALYTICS WING",
            bg=glass_bg, fg=styles.AURORA_ROSE if is_dark else "#DB2777",
            font=styles.get_font(12, "bold")
        )
        self.waveform_title.pack(side=tk.LEFT)

        ctrl_box = tk.Frame(hdr, bg=glass_bg)
        ctrl_box.pack(side=tk.RIGHT)

        btn_bg_active   = styles.AURORA_ROSE if is_dark else "#DB2777"
        btn_fg_active   = "#050811" if is_dark else "#FFFFFF"
        btn_bg_inactive = theme.get("input_bg", "#0A1525") if is_dark else "#EEF2FF"

        self.btn_view_trend = tk.Button(
            ctrl_box, text="∿ Trend",
            bg=btn_bg_active, fg=btn_fg_active,
            relief="flat", bd=0, cursor="hand2",
            font=styles.get_font(8, "bold"), padx=6, pady=2,
            command=lambda: self._set_chart_mode("trend")
        )
        self.btn_view_trend.pack(side=tk.LEFT, padx=2)

        self.btn_view_dist = tk.Button(
            ctrl_box, text="≡ Spectrum",
            bg=btn_bg_inactive, fg=styles.COLOR_TEXT_MUTED,
            relief="flat", bd=0, cursor="hand2",
            font=styles.get_font(8, "bold"), padx=6, pady=2,
            command=lambda: self._set_chart_mode("distribution")
        )
        self.btn_view_dist.pack(side=tk.LEFT, padx=2)

        # Chart
        chart_wrap = tk.Frame(container, bg=glass_bg)
        chart_wrap.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))

        chart_bg = glass_bg
        self.fig = Figure(figsize=(4.8, 3.0), dpi=100, facecolor=chart_bg)
        self.fig.patch.set_facecolor(chart_bg)
        self.mpl_canvas = FigureCanvasTkAgg(self.fig, master=chart_wrap)
        widget = self.mpl_canvas.get_tk_widget()
        widget.configure(bg=chart_bg, highlightthickness=0)
        widget.pack(fill=tk.BOTH, expand=True)
        widget.bind("<Configure>", self._on_chart_resize)

        # Fleet stat orbs
        kpi_row = tk.Frame(container, bg=glass_bg)
        kpi_row.pack(fill=tk.X, padx=12, pady=(0, 12))
        for i in range(3):
            kpi_row.columnconfigure(i, weight=1)

        def _orb(col, title):
            orb_bg = theme.get("input_bg", "#0A1525") if is_dark else "#EEF2FF"
            orb_bdr_col = theme.get("glass_border", styles.COLOR_BORDER)
            bd = tk.Frame(kpi_row, bg=orb_bdr_col, bd=1)
            bd.grid(row=0, column=col, sticky="ew", padx=3)
            inner = tk.Frame(bd, bg=orb_bg, padx=5, pady=5)
            inner.pack(fill=tk.BOTH, expand=True)
            tk.Label(inner, text=title, bg=orb_bg,
                     fg=styles.COLOR_TEXT_MUTED, font=styles.get_font(7, "bold")).pack(anchor=tk.N)
            vl = tk.Label(inner, text="--", bg=orb_bg,
                          fg=styles.COLOR_PRIMARY, font=styles.get_font(10, "bold"))
            vl.pack(anchor=tk.N)
            return vl

        self.fleet_scans_lbl = _orb(0, "SCANS")
        self.fleet_avg_lbl   = _orb(1, "AVG BMI")
        self.fleet_opt_lbl   = _orb(2, "OPTIMAL %")

    def _set_chart_mode(self, mode: str) -> None:
        self._chart_view_mode = mode
        is_dark = (styles.CURRENT_THEME == "dark")
        active_bg   = styles.AURORA_ROSE if is_dark else "#DB2777"
        active_fg   = "#050811" if is_dark else "#FFFFFF"
        inactive_bg = styles.get_theme_dict().get("input_bg", "#0A1525") if is_dark else "#EEF2FF"
        inactive_fg = styles.COLOR_TEXT_MUTED

        if mode == "trend":
            self.btn_view_trend.config(bg=active_bg, fg=active_fg)
            self.btn_view_dist.config(bg=inactive_bg, fg=inactive_fg)
        else:
            self.btn_view_trend.config(bg=inactive_bg, fg=inactive_fg)
            self.btn_view_dist.config(bg=active_bg, fg=active_fg)
        self._refresh_chart()

    def _on_chart_resize(self, event: tk.Event) -> None:
        w = max(3.0, event.width  / 100.0)
        h = max(2.0, event.height / 100.0)
        self.fig.set_size_inches(w, h, forward=True)
        glass_bg = styles.get_theme_dict().get("glass_tint", styles.COLOR_CARD)
        self.fig.patch.set_facecolor(glass_bg)
        self.mpl_canvas.get_tk_widget().configure(bg=glass_bg, highlightthickness=0)
        self.mpl_canvas.draw_idle()

    # ------------------------------------------------------------------
    # LIVE INPUT SYNCHRONIZATION
    # ------------------------------------------------------------------

    def _on_height_slider(self, val: str) -> None:
        if self._syncing_inputs:
            return
        try:
            self._syncing_inputs = True
            h = float(val)
            self.height_val.set(f"{h:.1f}")
            self.height_display_lbl.config(text=f"{h:.1f} cm")
            self.height_entry.is_placeholder_active = False
            self.height_entry.config(fg=styles.COLOR_TEXT)
        finally:
            self._syncing_inputs = False
        self._live_recalculate()

    def _on_weight_slider(self, val: str) -> None:
        if self._syncing_inputs:
            return
        try:
            self._syncing_inputs = True
            w = float(val)
            self.weight_val.set(f"{w:.1f}")
            self.weight_display_lbl.config(text=f"{w:.1f} kg")
            self.weight_entry.is_placeholder_active = False
            self.weight_entry.config(fg=styles.COLOR_TEXT)
        finally:
            self._syncing_inputs = False
        self._live_recalculate()

    def _on_numeric_text_change(self, field: str) -> None:
        if self._syncing_inputs:
            return
        try:
            if field == "height":
                raw = self._get_field(self.height_entry, self.height_val)
                if raw:
                    h = float(raw)
                    if 50.0 <= h <= 240.0:
                        self._syncing_inputs = True
                        self.height_scale.set(h)
                        self.height_display_lbl.config(text=f"{h:.1f} cm")
                        self._syncing_inputs = False
            elif field == "weight":
                raw = self._get_field(self.weight_entry, self.weight_val)
                if raw:
                    w = float(raw)
                    if 20.0 <= w <= 190.0:
                        self._syncing_inputs = True
                        self.weight_scale.set(w)
                        self.weight_display_lbl.config(text=f"{w:.1f} kg")
                        self._syncing_inputs = False
        except Exception:
            pass
        self._live_recalculate()

    def _apply_preset(self, name: str, h: float, w: float, age: int, gender: str) -> None:
        self._syncing_inputs = True
        self.height_val.set(f"{h:.1f}")
        self.weight_val.set(f"{w:.1f}")
        self.age_val.set(str(age))
        self.gender_val.set(gender)
        self.gender_combo.set(gender)
        self.height_scale.set(h)
        self.weight_scale.set(w)
        self.height_display_lbl.config(text=f"{h:.1f} cm")
        self.weight_display_lbl.config(text=f"{w:.1f} kg")
        for e in (self.height_entry, self.weight_entry, self.age_entry):
            e.is_placeholder_active = False
            e.config(fg=styles.COLOR_TEXT)
        self._syncing_inputs = False
        self._live_recalculate()

    def _live_recalculate(self) -> None:
        try:
            h_str = self._get_field(self.height_entry, self.height_val)
            w_str = self._get_field(self.weight_entry, self.weight_val)
            if not h_str or not w_str:
                return
            h = float(h_str)
            w = float(w_str)
            if h <= 40 or h > 260 or w <= 5 or w > 350:
                return
            a_str  = self._get_field(self.age_entry, self.age_val)
            age    = float(a_str) if a_str else 25.0
            gender = self.gender_val.get() if self.gender_val.get() not in ("", "Select gender") else "Male"

            analysis = BMIService.get_suggestion_and_details(h, w, age, gender)
            self._update_summary_telemetry(analysis)
        except Exception:
            pass

    def _update_summary_telemetry(self, analysis: dict) -> None:
        bmi    = analysis["bmi"]
        status = analysis["status"]
        self.radial_gauge.set_bmi(bmi, status, animate=True)
        col = self.radial_gauge._get_color_for_bmi(bmi)
        self.avatar_canvas.set_status_color(col)

        self.range_lbl.config(
            text=f"Mid: {analysis['ideal_weight']:.1f} kg | Δ {analysis['delta_str']}"
        )
        self.bmr_val_lbl.config(text=f"{analysis['bmr']:,} kcal/day")
        self.bsa_val_lbl.config(text=f"{analysis['bsa']:.2f} m²")
        self.suggestion_lbl.config(text=analysis["suggestion"])
        self.bmi_value_lbl.config(text=f"{bmi:.1f}")
        self.badge_lbl.config(text=status.upper())

    # ------------------------------------------------------------------
    # TABLE SECTION
    # ------------------------------------------------------------------

    def _build_table_section(self, container: tk.Frame) -> None:
        bar = tk.Frame(container, bg=styles.COLOR_BG)
        bar.pack(fill=tk.X, pady=(0, 6))
        self.table_bar = bar

        self.table_title_lbl = tk.Label(
            bar, text="✦  Biometric Constellation — Health Records",
            bg=styles.COLOR_BG, fg=styles.COLOR_TEXT,
            font=styles.get_font(12, "bold")
        )
        self.table_title_lbl.pack(side=tk.LEFT)

        sf = tk.Frame(bar, bg=styles.COLOR_BG)
        sf.pack(side=tk.RIGHT)
        self.search_frame = sf

        self.search_label = tk.Label(sf, text="⊕  Search by name:", bg=styles.COLOR_BG,
                                     fg=styles.COLOR_TEXT_MUTED, font=styles.get_font(9, "bold"))
        self.search_label.pack(side=tk.LEFT, padx=(0, 6))

        self.search_var = tk.StringVar(value="")
        self.search_var.trace_add("write", self._on_search_change)

        self.search_border = tk.Frame(sf, bg=styles.COLOR_BORDER, bd=1)
        self.search_border.pack(side=tk.LEFT)

        theme = styles.get_theme_dict()
        self.search_entry = tk.Entry(
            self.search_border, textvariable=self.search_var,
            bg=theme.get("input_bg", styles.COLOR_CARD), fg=styles.COLOR_TEXT,
            insertbackground=styles.COLOR_TEXT,
            font=styles.get_font(9), bd=0, width=22, relief="flat", highlightthickness=0,
        )
        self.search_entry.pack(padx=6, pady=3)
        self._setup_placeholder(self.search_entry, "Type name to filter…")
        focus_col = styles.AURORA_VIOLET if styles.CURRENT_THEME == "dark" else "#7C3AED"
        self.search_entry.bind("<FocusIn>",  lambda _e: self.search_border.config(bg=focus_col))
        self.search_entry.bind("<FocusOut>", lambda _e: self.search_border.config(bg=styles.COLOR_BORDER))

        # Table
        is_dark = (styles.CURRENT_THEME == "dark")
        t_bdr_col = styles.AURORA_VIOLET if is_dark else "#7C3AED"
        self.t_border = tk.Frame(container, bg=t_bdr_col, bd=1)
        self.t_border.pack(fill=tk.BOTH, expand=True)
        self.record_table = HealthRecordTable(
            self.t_border,
            on_select_callback=self._on_table_select,
            on_double_click_callback=self._on_table_double_click,
        )
        self.record_table.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # STATS FOOTER
    # ------------------------------------------------------------------

    def _build_stats_footer(self, container: tk.Frame) -> None:
        theme = styles.get_theme_dict()
        is_dark = (styles.CURRENT_THEME == "dark")
        self.stats_footer_frame = tk.Frame(container, bg=styles.COLOR_BG, height=90)
        self.stats_footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(8, 0))
        self.stats_footer_frame.pack_propagate(False)

        for i in range(4):
            self.stats_footer_frame.columnconfigure(i, weight=1)
        self.stats_footer_frame.rowconfigure(0, weight=1)

        self.stat_widgets: dict = {}
        self._stat_card_borders = []
        self._stat_card_inners  = []
        self._stat_accents      = []
        self._stat_content_frames = []
        self._stat_header_frames  = []
        self._stat_labels         = []

        cards = [
            ("Total Records", "◈", styles.AURORA_VIOLET if is_dark else "#7C3AED"),
            ("Average BMI",   "◎", styles.AURORA_TEAL   if is_dark else "#0891B2"),
            ("Highest BMI",   "▲", styles.AURORA_ROSE    if is_dark else "#DB2777"),
            ("Lowest BMI",    "▼", styles.AURORA_AMBER   if is_dark else "#D97706"),
        ]
        for idx, (title, icon, color) in enumerate(cards):
            bdr, inner = styles.make_glass_card(self.stats_footer_frame, tint=color)
            pad_r = 0 if idx == 3 else 8
            bdr.grid(row=0, column=idx, sticky="nsew", padx=(0, pad_r))
            self._stat_card_borders.append(bdr)
            self._stat_card_inners.append(inner)

            accent = tk.Frame(inner, bg=color, width=4)
            accent.pack(side=tk.LEFT, fill=tk.Y)
            self._stat_accents.append(accent)

            content = tk.Frame(inner, bg=styles.COLOR_CARD, padx=12, pady=6)
            content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self._stat_content_frames.append(content)

            hl = tk.Frame(content, bg=styles.COLOR_CARD)
            hl.pack(anchor=tk.W)
            self._stat_header_frames.append(hl)

            lbl_icon = tk.Label(hl, text=icon, bg=styles.COLOR_CARD, fg=color,
                                font=styles.get_font(10))
            lbl_icon.pack(side=tk.LEFT, padx=(0, 4))
            self._stat_labels.append(lbl_icon)

            lbl_title = tk.Label(hl, text=title.upper(), bg=styles.COLOR_CARD,
                                 fg=styles.COLOR_TEXT_MUTED, font=styles.get_font(8, "bold"))
            lbl_title.pack(side=tk.LEFT)
            self._stat_labels.append(lbl_title)

            val_lbl = tk.Label(content, text="0", bg=styles.COLOR_CARD,
                               fg=styles.COLOR_TEXT, font=styles.get_font(20, "bold"))
            val_lbl.pack(anchor=tk.W, pady=(2, 0))

            key = title.lower().replace(" ", "_")
            self.stat_widgets[key] = val_lbl

    # ======================================================================
    # PLACEHOLDER HELPER
    # ======================================================================

    def _setup_placeholder(self, entry: tk.Entry, text: str) -> None:
        entry.placeholder = text
        entry.is_placeholder_active = False

        def _show():
            current_val = entry.get()
            if not current_val.strip() or current_val == text:
                entry.delete(0, tk.END)
                entry.insert(0, text)
                entry.config(fg=styles.COLOR_TEXT_MUTED)
                entry.is_placeholder_active = True

        def _on_in(_e):
            if getattr(entry, "is_placeholder_active", False) or entry.get() == text:
                entry.delete(0, tk.END)
                entry.config(fg=styles.COLOR_TEXT)
                entry.is_placeholder_active = False

        def _on_out(_e):
            if not entry.get().strip():
                _show()

        entry.bind("<FocusIn>",  _on_in,  add="+")
        entry.bind("<FocusOut>", _on_out, add="+")
        entry.reset_placeholder = _show
        _show()

    def _get_field(self, entry: tk.Entry, var: tk.StringVar) -> str:
        val = var.get().strip()
        if getattr(entry, "is_placeholder_active", False) or (hasattr(entry, "placeholder") and val == entry.placeholder):
            return ""
        return val

    # ======================================================================
    # KEYBOARD SHORTCUTS
    # ======================================================================

    def _bind_shortcuts(self) -> None:
        self.parent.bind("<Control-s>", lambda _e: self._handle_save())
        self.parent.bind("<Control-S>", lambda _e: self._handle_save())
        self.parent.bind("<Control-n>", lambda _e: self._handle_clear())
        self.parent.bind("<Control-N>", lambda _e: self._handle_clear())
        self.parent.bind("<Delete>",    lambda _e: self._handle_delete())
        for entry in [self.name_entry, self.age_entry,
                      self.height_entry, self.weight_entry]:
            entry.bind("<Return>", lambda _e: self._handle_save())

    # ======================================================================
    # THEME MANAGEMENT
    # ======================================================================

    def _toggle_theme(self) -> None:
        new_theme = "dark" if styles.CURRENT_THEME == "light" else "light"
        self.apply_theme(new_theme)

    def apply_theme(self, theme_name: str) -> None:
        """Apply aurora light or dark theme across all dashboard widgets."""
        # Stop star animation while switching
        if self._star_job:
            try:
                self.after_cancel(self._star_job)
            except Exception:
                pass
            self._star_job = None

        styles.set_theme(theme_name, self.parent)
        theme = styles.get_theme_dict()
        is_dark = (theme_name == "dark")
        glass_bg = theme.get("glass_tint", styles.COLOR_CARD)

        # Root & frame backgrounds
        self.parent.configure(bg=styles.COLOR_BG)
        self.configure(bg=styles.COLOR_BG)
        self.scroll_container.configure(bg=styles.COLOR_BG)
        self.body_canvas.configure(bg=styles.COLOR_BG)
        self.scrollable_frame.configure(bg=styles.COLOR_BG)
        self.top_section.configure(bg=styles.COLOR_BG)
        self.bottom_section.configure(bg=styles.COLOR_BG)

        # Redraw aurora and stars
        w = self.body_canvas.winfo_width()
        h = max(self.body_canvas.winfo_height(), self.scrollable_frame.winfo_reqheight())
        self.body_canvas.delete("aurora")
        self.body_canvas.delete("stars")
        if is_dark:
            self._draw_aurora_wash(w, h)
            self._draw_starfield()
            self.after(500, self._animate_stars)

        # Top glass panels — re-tint borders
        tints = [
            styles.AURORA_VIOLET if is_dark else "#7C3AED",
            styles.AURORA_TEAL   if is_dark else "#0891B2",
            styles.AURORA_ROSE   if is_dark else "#DB2777",
        ]
        for bdr, tnt in zip(getattr(self, "_top_card_borders", []), tints):
            bdr.configure(bg=tnt)
        for inn in getattr(self, "_top_card_inners", []):
            inn.configure(bg=glass_bg)

        # Header
        self.header_canvas.configure(bg=theme["header_l"])
        self.header_left.configure(bg=theme["header_l"])
        self.header_right.configure(bg=theme["header_r"])
        self.logo_canvas.configure(bg=theme["header_l"])
        self._draw_logo(self.logo_canvas)
        self.header_text_col.configure(bg=theme["header_l"])
        self.header_title_row.configure(bg=theme["header_l"])
        self.title_lbl.configure(bg=theme["header_l"], fg="#FFFFFF")

        badge_bg  = theme.get("badge_gold_bg", "#1F1500")
        badge_fg  = theme.get("badge_gold_fg", "#FBBF24")
        badge_bdr = styles.AURORA_VIOLET if is_dark else "#7C3AED"
        self.badge_box.configure(bg=badge_bg, highlightbackground=badge_bdr)
        self.badge_box_lbl.configure(bg=badge_bg, fg=badge_fg)
        self.subtitle_lbl.configure(
            bg=theme["header_l"],
            fg=styles.AURORA_TEAL if is_dark else "#0891B2"
        )

        clock_bg  = "#0C1050" if is_dark else "#312E81"
        clock_bdr = "#A78BFA" if is_dark else "#7C3AED"
        self.clock_capsule.configure(bg=clock_bg, highlightbackground=clock_bdr)
        self.date_lbl.configure(bg=clock_bg, fg=styles.AURORA_TEAL if is_dark else "#A5B4FC")
        self.time_lbl.configure(bg=clock_bg, fg="#FFFFFF")

        conn_bg  = "#0C1050" if is_dark else "#312E81"
        conn_bdr = "#34D399" if is_dark else "#059669"
        self.db_status_box.configure(bg=conn_bg, highlightbackground=conn_bdr)
        self.db_status_lbl.configure(bg=conn_bg)

        btn_bg  = "#1A0A3E" if is_dark else "#4C1D95"
        btn_bdr = styles.AURORA_VIOLET if is_dark else "#A78BFA"
        self.theme_btn.configure(
            text="☾ Dark" if theme_name == "light" else "☀ Light",
            bg=btn_bg, fg="#FFFFFF", highlightbackground=btn_bdr
        )
        for b in getattr(self, "nav_buttons", []):
            b.configure(bg=btn_bg, fg="#FFFFFF")

        self._on_header_resize()

        # Status bar
        self.status_bar.configure(bg=theme["status_bg"])
        self.sb_db_lbl.configure(bg=theme["status_bg"], fg=styles.COLOR_TEXT)
        self.sb_user_lbl.configure(bg=theme["status_bg"], fg=styles.COLOR_TEXT)
        self.sb_ver_lbl.configure(bg=theme["status_bg"], fg=styles.COLOR_TEXT)
        self.status_msg_lbl.configure(bg=theme["status_bg"], fg=styles.AURORA_TEAL if is_dark else "#059669")
        self.status_time_lbl.configure(bg=theme["status_bg"], fg=styles.COLOR_TEXT)

        # Form panel
        for lbl in getattr(self, "_form_labels", []):
            lbl.configure(bg=glass_bg, fg=styles.COLOR_TEXT_MUTED)
        if hasattr(self, "form_title_lbl"):
            self.form_title_lbl.configure(bg=glass_bg, fg="#6D28D9" if not is_dark else styles.AURORA_VIOLET)
        if hasattr(self, "form_grid"):
            self.form_grid.configure(bg=glass_bg)
        if hasattr(self, "btn_panel"):
            self.btn_panel.configure(bg=glass_bg)
        for bd in getattr(self, "_entry_borders", []):
            bd.configure(bg=styles.COLOR_BORDER)
        input_bg = theme.get("input_bg", styles.COLOR_CARD)
        for e in [self.name_entry, self.age_entry,
                  self.height_entry, self.weight_entry, self.search_entry]:
            e.configure(bg=input_bg, insertbackground=styles.COLOR_TEXT)
            if getattr(e, "is_placeholder_active", False):
                e.configure(fg=styles.COLOR_TEXT_MUTED)
            else:
                e.configure(fg=styles.COLOR_TEXT)
        for pb in getattr(self, "_preset_buttons", []):
            pb.configure(
                bg=theme.get("input_bg", "#0A1525") if is_dark else "#EDE9FE",
                fg=styles.AURORA_VIOLET if is_dark else "#6D28D9",
                activebackground=styles.AURORA_VIOLET if is_dark else "#6D28D9",
                activeforeground="#050811" if is_dark else "#FFFFFF",
            )
        for btn in getattr(self, "form_buttons", []):
            styles.retheme_button(btn)

        # Height/weight display labels
        for lbl_attr in ("height_display_lbl", "weight_display_lbl"):
            lbl = getattr(self, lbl_attr, None)
            if lbl:
                lbl.configure(bg=glass_bg, fg=styles.COLOR_PRIMARY)

        # Orbital core
        if hasattr(self, "radial_gauge"):
            self.radial_gauge.configure(bg=glass_bg)
            self.radial_gauge._render()
        if hasattr(self, "avatar_canvas"):
            self.avatar_canvas.configure(bg=glass_bg)
            self.avatar_canvas._draw_frame()
        if hasattr(self, "hud_core_title"):
            self.hud_core_title.configure(bg=glass_bg, fg=styles.AURORA_TEAL if is_dark else "#0891B2")

        # Telemetry mini-cards
        tele_colors = [
            styles.AURORA_TEAL   if is_dark else "#0891B2",
            styles.AURORA_VIOLET if is_dark else "#6D28D9",
            styles.AURORA_AMBER  if is_dark else "#B45309",
        ]
        card_bg = theme.get("input_bg", "#0A1525") if is_dark else "#F5F3FF"
        for bd, col in zip(
            [getattr(self, "_c1_bd", None), getattr(self, "_c2_bd", None), getattr(self, "_c3_bd", None)],
            tele_colors
        ):
            if bd:
                bd.configure(bg=col)
        for inn in [getattr(self, "_c1_in", None), getattr(self, "_c2_in", None), getattr(self, "_c3_in", None)]:
            if inn:
                inn.configure(bg=card_bg)

        sugg_bg = theme.get("input_bg", "#080F1F") if is_dark else "#F5F3FF"
        if hasattr(self, "_sugg_bd"):
            self._sugg_bd.configure(bg=theme.get("glass_border", styles.COLOR_BORDER))
        if hasattr(self, "suggestion_area"):
            self.suggestion_area.configure(bg=sugg_bg)
        if hasattr(self, "suggestion_lbl"):
            self.suggestion_lbl.configure(bg=sugg_bg, fg=styles.COLOR_TEXT)

        # Analytics wing
        if hasattr(self, "waveform_title"):
            self.waveform_title.configure(bg=glass_bg, fg=styles.AURORA_ROSE if is_dark else "#DB2777")

        # Chart
        chart_bg = glass_bg
        self.fig.set_facecolor(chart_bg)
        self.fig.patch.set_facecolor(chart_bg)
        self.mpl_canvas.get_tk_widget().configure(bg=chart_bg, highlightthickness=0)
        self._refresh_chart()

        # Table section
        self.table_bar.configure(bg=styles.COLOR_BG)
        self.search_frame.configure(bg=styles.COLOR_BG)
        self.table_title_lbl.configure(bg=styles.COLOR_BG, fg=styles.COLOR_TEXT)
        self.search_label.configure(bg=styles.COLOR_BG, fg=styles.COLOR_TEXT_MUTED)
        self.search_border.configure(bg=styles.COLOR_BORDER)
        self.search_entry.configure(bg=input_bg)
        t_bdr_col = styles.AURORA_VIOLET if is_dark else "#7C3AED"
        self.t_border.configure(bg=t_bdr_col)
        self.record_table.apply_theme()

        # Stats footer
        self.stats_footer_frame.configure(bg=styles.COLOR_BG)
        stat_colors = [
            styles.AURORA_VIOLET if is_dark else "#6D28D9",
            styles.AURORA_TEAL   if is_dark else "#0891B2",
            styles.AURORA_ROSE   if is_dark else "#DB2777",
            styles.AURORA_AMBER  if is_dark else "#B45309",
        ]
        for bdr, col in zip(getattr(self, "_stat_card_borders", []), stat_colors):
            bdr.configure(bg=col)
        for inner in getattr(self, "_stat_card_inners", []):
            inner.configure(bg=styles.COLOR_CARD)
        for cf in getattr(self, "_stat_content_frames", []):
            cf.configure(bg=styles.COLOR_CARD)
        for hf in getattr(self, "_stat_header_frames", []):
            hf.configure(bg=styles.COLOR_CARD)
        for lbl in getattr(self, "_stat_labels", []):
            lbl.configure(bg=styles.COLOR_CARD)
        for lbl in self.stat_widgets.values():
            lbl.configure(bg=styles.COLOR_CARD, fg=styles.COLOR_TEXT)

        self._show_status(f"Theme switched to {'Aurora Day' if theme_name == 'light' else 'Deep Space'}")

    # ======================================================================
    # DASHBOARD REFRESH
    # ======================================================================

    def refresh_dashboard(self) -> None:
        records = self.db.get_all_records()
        self.record_table.populate(records)

        stats = self.db.get_statistics()
        total = stats.get("total", 0)
        self._animate_count(self.stat_widgets["total_records"], total, is_float=False)
        self._animate_count(self.stat_widgets["average_bmi"],   stats.get("avg_bmi", 0.0) if total else 0.0)
        self._animate_count(self.stat_widgets["highest_bmi"],   stats.get("max_bmi", 0.0) if total else 0.0)
        self._animate_count(self.stat_widgets["lowest_bmi"],    stats.get("min_bmi", 0.0) if total else 0.0)
        self._refresh_chart()

    # ======================================================================
    # CHART
    # ======================================================================

    def _refresh_chart(self, target_name: Optional[str] = None) -> None:
        if self._chart_anim_job:
            try:
                self.after_cancel(self._chart_anim_job)
            except Exception:
                pass
            self._chart_anim_job = None

        name = target_name
        if not name:
            name = self._get_field(self.name_entry, self.name_val)
        if not name and self.selected_record_id is not None:
            sel_rec = self.record_table.get_selected_record()
            if sel_rec:
                name = sel_rec.name
            else:
                db_rec = self.db.get_record_by_id(self.selected_record_id)
                if db_rec:
                    name = db_rec.name

        # Fleet orbs update
        try:
            records = self.db.get_all_records()
            total   = len(records)
            if total > 0:
                avg_b   = sum(r.bmi for r in records) / total
                opt_c   = sum(1 for r in records if r.status == "Normal")
                opt_pct = f"{int(round(opt_c / total * 100))}%"
                if hasattr(self, "fleet_scans_lbl"):
                    self.fleet_scans_lbl.config(text=str(total))
                if hasattr(self, "fleet_avg_lbl"):
                    self.fleet_avg_lbl.config(text=f"{avg_b:.1f}")
                if hasattr(self, "fleet_opt_lbl"):
                    self.fleet_opt_lbl.config(text=opt_pct)
            else:
                for a in ["fleet_scans_lbl", "fleet_avg_lbl", "fleet_opt_lbl"]:
                    if hasattr(self, a):
                        getattr(self, a).config(text="--")
        except Exception:
            pass

        glass_bg = styles.get_theme_dict().get("glass_tint", styles.COLOR_CARD)
        tk_w = self.mpl_canvas.get_tk_widget()
        cw = tk_w.winfo_width()
        ch = tk_w.winfo_height()
        if cw > 50 and ch > 50:
            self.fig.set_size_inches(cw / 100.0, ch / 100.0, forward=True)
        self.fig.patch.set_facecolor(glass_bg)
        tk_w.configure(bg=glass_bg, highlightthickness=0)

        history = self.db.get_history_by_name(name) if name else []
        total_frames = 12

        def _animate(frame: int) -> None:
            if frame > total_frames:
                self._chart_anim_job = None
                return
            try:
                self.fig.clear()
                self.fig.patch.set_facecolor(glass_bg)
                ax = self.fig.add_subplot(111)
                ax.set_facecolor(glass_bg)
                ratio = frame / total_frames

                mode = getattr(self, "_chart_view_mode", "auto")
                if mode == "distribution":
                    self._draw_distribution(ax, ratio, frame == total_frames)
                elif mode == "trend":
                    if len(history) >= 1:
                        self._draw_trend(ax, history, ratio, name, frame == total_frames)
                    else:
                        self._draw_no_trend(ax, name)
                else:
                    if len(history) >= 2:
                        self._draw_trend(ax, history, ratio, name, frame == total_frames)
                    else:
                        self._draw_distribution(ax, ratio, frame == total_frames)

                for spine in ("top", "right"):
                    ax.spines[spine].set_visible(False)
                ax.spines["left"].set_color(styles.COLOR_BORDER)
                ax.spines["bottom"].set_color(styles.COLOR_BORDER)

                self.fig.subplots_adjust(left=0.12, right=0.96, top=0.88, bottom=0.22)
                self.mpl_canvas.draw()
                self._chart_anim_job = self.after(16, lambda: _animate(frame + 1))
            except Exception:
                pass

        _animate(1)

    def _draw_trend(self, ax, history, ratio, name, annotate):
        dates  = [h["date"][:10] for h in history]
        bmis   = [h["bmi"]       for h in history]
        scaled = [v * ratio for v in bmis]
        is_dark = (styles.CURRENT_THEME == "dark")
        line_col = styles.AURORA_TEAL  if is_dark else "#0891B2"
        pt_face  = styles.COLOR_BG     if is_dark else "#FFFFFF"
        zone_col = styles.AURORA_TEAL  if is_dark else "#059669"

        ax.plot(dates, scaled, color=line_col, marker="o", linewidth=2.5,
                markersize=6, markerfacecolor=pt_face,
                markeredgecolor=line_col, markeredgewidth=2,
                label="BMI Waveform")
        ax.axhspan(18.5, 24.9, color=zone_col, alpha=0.10, label="Optimal (18.5–24.9)")
        ax.axhline(18.5, color=zone_col, linestyle=":", linewidth=1, alpha=0.5)
        ax.axhline(24.9, color=zone_col, linestyle=":", linewidth=1, alpha=0.5)

        if annotate:
            for i, val in enumerate(bmis):
                ax.annotate(f"{val:.1f}", (dates[i], bmis[i]),
                            textcoords="offset points", xytext=(0, 7),
                            ha="center", fontsize=8, fontweight="bold",
                            color=styles.COLOR_TEXT)

        title_text = f"Orbital Waveform — {name}" if name else "Orbital Waveform"
        ax.set_title(title_text, fontsize=10, fontweight="bold", pad=8, color=styles.COLOR_TEXT)
        ax.set_xlabel("Scan Date", fontsize=8, color=styles.COLOR_TEXT_MUTED, labelpad=4)
        ax.set_ylabel("BMI", fontsize=8, color=styles.COLOR_TEXT_MUTED, labelpad=4)
        ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.2, color=styles.COLOR_BORDER)
        ax.tick_params(axis="both", labelsize=8, labelcolor=styles.COLOR_TEXT_MUTED)
        glass_bg = styles.get_theme_dict().get("glass_tint", styles.COLOR_CARD)
        ax.legend(fontsize=8, frameon=True, facecolor=glass_bg,
                  edgecolor=styles.COLOR_BORDER, labelcolor=styles.COLOR_TEXT)
        if len(dates) > 5:
            ax.set_xticks(dates[::max(1, len(dates) // 4)])

    def _draw_no_trend(self, ax, name):
        subj = f"'{name}'" if name else "selected subject"
        msg = f"Insufficient data for {subj}\n\nLog 2+ scans to plot waveform."
        ax.text(0.5, 0.50, msg, fontsize=9, color=styles.COLOR_TEXT_MUTED,
                ha="center", va="center", transform=ax.transAxes)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title("Orbital Waveform Scanner", fontsize=10, fontweight="bold",
                     pad=8, color=styles.COLOR_TEXT)
        for s in ax.spines.values():
            s.set_visible(False)

    def _draw_distribution(self, ax, ratio, annotate):
        records = self.db.get_all_records()
        cats    = {"Underweight": 0, "Normal": 0, "Overweight": 0, "Obese": 0}
        for rec in records:
            if rec.status in cats:
                cats[rec.status] += 1

        labels = ["Under", "Optimal", "Over", "Obese"]
        counts = list(cats.values())
        is_dark = (styles.CURRENT_THEME == "dark")
        clrs = [styles.AURORA_TEAL, styles.AURORA_TEAL, styles.AURORA_AMBER, styles.AURORA_ROSE] \
               if is_dark else ["#0891B2", "#059669", "#D97706", "#DB2777"]

        glass_bg = styles.get_theme_dict().get("glass_tint", styles.COLOR_CARD)
        if not records:
            ax.text(0.5, 0.50, "No records yet\n\nAdd scans to see distribution",
                    fontsize=9, color=styles.COLOR_TEXT_MUTED,
                    ha="center", va="center", transform=ax.transAxes)
            ax.set_xticks([]); ax.set_yticks([])
            ax.set_title("Constellation Map", fontsize=10, fontweight="bold",
                         pad=8, color=styles.COLOR_TEXT)
            for s in ax.spines.values():
                s.set_visible(False)
            return

        bars = ax.bar(labels, [c * ratio for c in counts], color=clrs, width=0.42,
                      edgecolor=styles.COLOR_BORDER, linewidth=0.8)
        max_c = max(counts) if counts else 0
        ax.set_ylim(0, max(max_c * 1.35, 3))
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        if annotate:
            for bar in bars:
                h = bar.get_height()
                if h > 0:
                    ax.annotate(str(int(h)),
                                xy=(bar.get_x() + bar.get_width() / 2, h),
                                xytext=(0, 3), textcoords="offset points",
                                ha="center", va="bottom",
                                fontsize=9, fontweight="bold", color=styles.COLOR_TEXT)

        ax.set_title("Constellation Map", fontsize=10, fontweight="bold",
                     pad=8, color=styles.COLOR_TEXT)
        ax.set_ylabel("Subjects", fontsize=8, color=styles.COLOR_TEXT_MUTED, labelpad=4)
        ax.grid(True, axis="y", linestyle="--", linewidth=0.5, alpha=0.2, color=styles.COLOR_BORDER)
        ax.tick_params(axis="both", labelsize=8, labelcolor=styles.COLOR_TEXT_MUTED)

    # ======================================================================
    # SUMMARY CARDS (backward-compat)
    # ======================================================================

    @classmethod
    def get_status_theme(cls, status: str) -> dict:
        is_dark = (styles.CURRENT_THEME == "dark")
        if is_dark:
            themes = {
                "Underweight": {"badge_bg": "#0A1A2A", "badge_fg": styles.AURORA_TEAL,   "bmi_fg": styles.AURORA_TEAL},
                "Normal":      {"badge_bg": "#0A1A1A", "badge_fg": styles.AURORA_TEAL,   "bmi_fg": styles.AURORA_TEAL},
                "Overweight":  {"badge_bg": "#1A150A", "badge_fg": styles.AURORA_AMBER,  "bmi_fg": styles.AURORA_AMBER},
                "Obese":       {"badge_bg": "#1A0A12", "badge_fg": styles.AURORA_ROSE,   "bmi_fg": styles.AURORA_ROSE},
            }
        else:
            themes = {
                "Underweight": {"badge_bg": "#E0F7FA", "badge_fg": "#0891B2", "bmi_fg": "#0891B2"},
                "Normal":      {"badge_bg": "#D1FAE5", "badge_fg": "#059669", "bmi_fg": "#059669"},
                "Overweight":  {"badge_bg": "#FEF3C7", "badge_fg": "#D97706", "bmi_fg": "#D97706"},
                "Obese":       {"badge_bg": "#FCE7F3", "badge_fg": "#DB2777", "bmi_fg": "#DB2777"},
            }
        return themes.get(status, {
            "badge_bg": styles.COLOR_BORDER,
            "badge_fg": styles.COLOR_TEXT_MUTED,
            "bmi_fg":   styles.COLOR_PRIMARY,
        })

    def _update_summary(self, bmi: float, status: str,
                        min_w: float, max_w: float, suggestion: str) -> None:
        self.radial_gauge.set_bmi(bmi, status, animate=True)
        col = self.radial_gauge._get_color_for_bmi(bmi)
        self.avatar_canvas.set_status_color(col)
        mid_w = round((min_w + max_w) / 2.0, 1)
        try:
            w_str = self._get_field(self.weight_entry, self.weight_val)
            w_val = float(w_str) if w_str else 0.0
        except Exception:
            w_val = 0.0
        if w_val > 0:
            delta = round(w_val - mid_w, 1)
            delta_str = f"+{delta:.1f} kg" if delta > 0 else f"{delta:.1f} kg"
            self.range_lbl.config(text=f"Mid: {mid_w:.1f} kg | Δ {delta_str}")
        else:
            self.range_lbl.config(text=f"{min_w:.1f} – {max_w:.1f} kg")
        self.suggestion_lbl.config(text=suggestion)
        self.bmi_value_lbl.config(text=f"{bmi:.1f}")
        self.badge_lbl.config(text=status.upper())

    def _clear_summary(self) -> None:
        self.radial_gauge.set_bmi(22.0, "NORMAL", animate=True)
        self.avatar_canvas.set_status_color(self.radial_gauge._get_color_for_bmi(22.0))
        self.bmi_value_lbl.config(text="--", fg=styles.COLOR_PRIMARY)
        self.range_lbl.config(text="--")
        if hasattr(self, "bmr_val_lbl"):
            self.bmr_val_lbl.config(text="--")
        if hasattr(self, "bsa_val_lbl"):
            self.bsa_val_lbl.config(text="--")
        self.suggestion_lbl.config(
            text="Enter subject measurements to generate real-time clinical guidance."
        )

    # ======================================================================
    # CRUD HANDLERS
    # ======================================================================

    def _collect_inputs(self) -> dict:
        return InputValidator.validate_inputs(
            name=self._get_field(self.name_entry,   self.name_val),
            age_str=self._get_field(self.age_entry, self.age_val),
            height_str=self._get_field(self.height_entry, self.height_val),
            weight_str=self._get_field(self.weight_entry, self.weight_val),
            gender="" if self.gender_val.get() in ("", "Select gender")
                    else self.gender_val.get().strip(),
        )

    def _handle_save(self) -> None:
        try:
            inp      = self._collect_inputs()
            analysis = BMIService.get_suggestion_and_details(inp["height"], inp["weight"], inp["age"], inp["gender"])
            rec = HealthRecord(
                id=None,
                name=inp["name"], age=inp["age"], gender=inp["gender"],
                height=inp["height"], weight=inp["weight"],
                bmi=analysis["bmi"], status=analysis["status"],
                created_at=datetime.now().isoformat(),
            )
            new_id = self.db.add_record(rec)
            self.refresh_dashboard()
            self.record_table.select_record_by_id(new_id)
            self.selected_record_id = new_id
            self._selected_record_created_at = rec.created_at
            self._update_summary_telemetry(analysis)
            self._refresh_chart(target_name=inp["name"])
            if self._bmi_card_frame:
                styles.highlight_card(self._bmi_card_frame)
            self._show_status("✦  Record saved successfully!")
        except ValidationError as err:
            AlertDialog(self, "Validation Error", str(err), "error")
        except Exception as err:
            AlertDialog(self, "System Error", f"Failed to save record:\n{err}", "error")

    def _handle_update(self) -> None:
        if self.selected_record_id is None:
            AlertDialog(self, "No Selection",
                        "Double-click a record in the table to load it for editing.", "warning")
            return
        try:
            inp      = self._collect_inputs()
            analysis = BMIService.get_suggestion_and_details(inp["height"], inp["weight"], inp["age"], inp["gender"])
            created_at = self._selected_record_created_at
            if not created_at:
                existing = self.db.get_record_by_id(self.selected_record_id)
                created_at = existing.created_at if existing else datetime.now().isoformat()
            rec = HealthRecord(
                id=self.selected_record_id,
                name=inp["name"], age=inp["age"], gender=inp["gender"],
                height=inp["height"], weight=inp["weight"],
                bmi=analysis["bmi"], status=analysis["status"],
                created_at=created_at,
            )
            self.db.update_record(rec)
            self.refresh_dashboard()
            self.record_table.select_record_by_id(self.selected_record_id)
            self._update_summary_telemetry(analysis)
            self._refresh_chart(target_name=inp["name"])
            if self._bmi_card_frame:
                styles.highlight_card(self._bmi_card_frame)
            self._show_status("✦  Record updated successfully!")
        except ValidationError as err:
            AlertDialog(self, "Validation Error", str(err), "error")
        except Exception as err:
            AlertDialog(self, "System Error", f"Failed to update record:\n{err}", "error")

    def _handle_delete(self) -> None:
        rec = self.record_table.get_selected_record()
        if not rec and self.selected_record_id is not None:
            rec = self.db.get_record_by_id(self.selected_record_id)
        if not rec:
            AlertDialog(self, "No Selection", "Select a record in the table to delete.", "warning")
            return
        dlg = ConfirmDialog(self, "Delete Record",
                            f"Permanently delete the record for '{rec.name}'?\n\nThis cannot be undone.")
        if dlg.result:
            try:
                self.db.delete_record(rec.id)
                self._handle_clear()
                self.refresh_dashboard()
                self._show_status("✕  Record deleted.")
            except Exception as err:
                AlertDialog(self, "Delete Error", f"Failed to delete record:\n{err}", "error")

    def _handle_clear(self) -> None:
        self.selected_record_id = None
        self._selected_record_created_at = None
        self.name_val.set("")
        self.age_val.set("")
        self.height_val.set("")
        self.weight_val.set("")
        self.gender_val.set("")
        self.gender_combo.set("Select gender")
        self.search_var.set("")
        for entry in [self.name_entry, self.age_entry,
                      self.height_entry, self.weight_entry, self.search_entry]:
            if hasattr(entry, "reset_placeholder"):
                entry.reset_placeholder()
        self.record_table.clear_selection()
        self._clear_summary()
        self._refresh_chart()
        self._show_status("◌  Form cleared.")

    def _handle_export(self) -> None:
        records = self.db.get_all_records()
        if not records:
            AlertDialog(self, "No Data", "There are no records to export.", "warning")
            return
        path = filedialog.asksaveasfilename(
            parent=self, title="Export Records to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="fittrack_records.csv",
        )
        if path:
            try:
                ExportService.export_to_csv(path, records)
                self._show_status(f"↑  Exported {len(records)} records to CSV.")
            except Exception as err:
                AlertDialog(self, "Export Error", f"Export failed:\n{err}", "error")

    # ======================================================================
    # TABLE INTERACTION
    # ======================================================================

    def _on_table_select(self, rec: HealthRecord) -> None:
        self.selected_record_id = rec.id
        self._selected_record_created_at = rec.created_at
        analysis = BMIService.get_suggestion_and_details(rec.height, rec.weight, rec.age, rec.gender)
        self._update_summary_telemetry(analysis)
        self._refresh_chart(target_name=rec.name)

    def _on_table_double_click(self, rec: HealthRecord) -> None:
        self.selected_record_id = rec.id
        self._selected_record_created_at = rec.created_at
        self._apply_preset(rec.name, rec.height, rec.weight, rec.age, rec.gender)
        self.name_val.set(rec.name)
        self.name_entry.is_placeholder_active = False
        self.name_entry.config(fg=styles.COLOR_TEXT)
        if self._form_card_frame:
            styles.highlight_card(self._form_card_frame)
        self._refresh_chart(target_name=rec.name)
        self._show_status(f"Loaded '{rec.name}' — edit and click Update.")

    def _on_search_change(self, *_args) -> None:
        if not hasattr(self, "record_table"):
            return
        query = self._get_field(self.search_entry, self.search_var)
        if query:
            records = self.db.search_records_by_name(query)
            self.record_table.populate(records, is_search_filter=True)
        else:
            self.record_table.populate(self.db.get_all_records())

    # ======================================================================
    # CLOCK & STATUS
    # ======================================================================

    def _update_clock(self) -> None:
        now = datetime.now()
        try:
            self.date_lbl.config(text=now.strftime("%A, %B %d, %Y"))
            self.time_lbl.config(text=now.strftime("%I:%M:%S %p"))
            self.status_time_lbl.config(text=now.strftime("%H:%M:%S"))
        except Exception:
            return
        self.after(1000, self._update_clock)

    def _show_status(self, text: str, is_error: bool = False) -> None:
        color = styles.COLOR_DANGER if is_error else styles.AURORA_TEAL
        try:
            self.status_msg_lbl.config(text=text, fg=color)
        except Exception:
            return
        if self._status_timer_id:
            try:
                self.after_cancel(self._status_timer_id)
            except Exception:
                pass
        self._status_timer_id = self.after(4500, self._reset_status)

    def _reset_status(self) -> None:
        try:
            self.status_msg_lbl.config(text="● System Nominal",
                                        fg=styles.AURORA_TEAL if styles.CURRENT_THEME == "dark" else "#059669")
        except Exception:
            pass
        self._status_timer_id = None

    # ======================================================================
    # ANIMATIONS
    # ======================================================================

    def _animate_count(self, widget: tk.Label, target: float,
                       is_float: bool = True, steps: int = 15) -> None:
        try:
            current = float(widget.cget("text"))
        except (ValueError, tk.TclError):
            current = 0.0

        def _step(n: int) -> None:
            if n >= steps:
                try:
                    widget.config(text=f"{target:.2f}" if is_float else str(int(target)))
                except Exception:
                    pass
                return
            ratio = n / steps
            val   = current + (target - current) * ratio
            try:
                widget.config(text=f"{val:.2f}" if is_float else str(int(val)))
                widget.after(18, lambda: _step(n + 1))
            except Exception:
                pass

        _step(0)

    def _pulse_badge(self, color: str, cycles: int = 2) -> None:
        if cycles <= 0:
            try:
                self.badge_frame.config(bg=color)
                self.badge_lbl.config(bg=color)
            except Exception:
                pass
            return
        styles.animate_color(self.badge_frame, color, "#FFFFFF", duration_ms=100, step_ms=14)
        styles.animate_color(self.badge_lbl,   color, "#FFFFFF", duration_ms=100, step_ms=14)
        self.badge_frame.after(
            110,
            lambda: styles.animate_color(self.badge_frame, "#FFFFFF", color, duration_ms=100, step_ms=14),
        )
        self.badge_lbl.after(
            110,
            lambda: styles.animate_color(self.badge_lbl,   "#FFFFFF", color, duration_ms=100, step_ms=14),
        )
        self.badge_frame.after(230, lambda: self._pulse_badge(color, cycles - 1))

    # ======================================================================
    # NAV BUTTON HANDLERS
    # ======================================================================

    def _on_settings(self) -> None:
        SettingsDialog(self, db_path=str(self.db.db_path), on_theme_change=self.apply_theme)

    def _on_about(self) -> None:
        AlertDialog(
            self,
            "About FitTrack Orbital Station",
            (
                "FitTrack  v3.0.0-ORBITAL\n\n"
                "Author  :  vasiharan\n"
                "License :  MIT\n"
                "Engine  :  Python 3 · Tkinter · Matplotlib · SQLite\n\n"
                "Glassmorphism Space Station biometric health tracker\n"
                "with animated orbital sphere, aurora glass panels,\n"
                "and animated star-field background."
            ),
            "info",
        )
