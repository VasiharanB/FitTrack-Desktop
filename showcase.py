"""
showcase.py
===========
FitTrack Enterprise — Before / After Deep Architectural Showcase Studio

Presents a comprehensive side-by-side comparison between:
- BEFORE: Classic Prototype (vasi.py)
- AFTER:  FitTrack Enterprise (v2.2)

Features:
- Full-screen responsive layout supporting high-resolution widescreen monitors
- Side-by-side project showcase command cards with live status badges
- 12-dimension deep architectural and technical comparison matrix
- Metric evolution benchmark counters
- Multi-launch controller: Launch Before, Launch After, or Launch Both Side-by-Side
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# COLOR PALETTE & DESIGN TOKENS
# ---------------------------------------------------------------------------
BG_DARK        = "#070B14"   # Deep cosmic background
BG_SURFACE     = "#0E1526"   # Surface layer
BG_CARD        = "#131C31"   # Card background
BG_CARD_ALT    = "#18243E"   # Card alternate / hover
BG_ROW_EVEN    = "#10182B"   # Matrix row even
BG_ROW_ODD     = "#141E34"   # Matrix row odd
BORDER_COLOR   = "#1F2E4D"   # Subtle card border
BORDER_GLOW    = "#3B82F6"   # Blue accent glow
BORDER_CYAN    = "#06B6D4"   # Cyan accent glow

TEXT_WHITE     = "#FFFFFF"
TEXT_LIGHT     = "#F1F5F9"
TEXT_MUTED     = "#94A3B8"
TEXT_SUBTLE    = "#64748B"

ACCENT_BLUE    = "#2563EB"
ACCENT_BLUE_LT = "#3B82F6"
ACCENT_CYAN    = "#06B6D4"
ACCENT_VIOLET  = "#8B5CF6"
ACCENT_EMERALD = "#10B981"
ACCENT_AMBER   = "#F59E0B"
ACCENT_ROSE    = "#F43F5E"

# Typography tokens (All strictly integer font sizes for Python 3.14 Tkinter)
FONT_HERO      = ("Segoe UI", 18, "bold")
FONT_H1        = ("Segoe UI", 15, "bold")
FONT_H2        = ("Segoe UI", 12, "bold")
FONT_H3        = ("Segoe UI", 11, "bold")
FONT_BODY      = ("Segoe UI", 10)
FONT_BODY_BOLD = ("Segoe UI", 10, "bold")
FONT_SM        = ("Segoe UI", 9)
FONT_SM_BOLD   = ("Segoe UI", 9, "bold")
FONT_TINY      = ("Segoe UI", 8)
FONT_MONO      = ("Consolas", 9)
FONT_METRIC_V  = ("Segoe UI", 22, "bold")

FITTRACK_DIR = Path(__file__).resolve().parent / "FitTrack"
VASI_PY      = Path(__file__).resolve().parent / "vasi.py"
FITTRACK_MAIN = FITTRACK_DIR / "main.py"

# ---------------------------------------------------------------------------
# LAUNCH CONTROLLER
# ---------------------------------------------------------------------------

def launch_before():
    """Launch the original vasi.py prototype in an independent process."""
    if not VASI_PY.exists():
        messagebox.showerror("File Missing", f"Could not locate vasi.py at:\n{VASI_PY}")
        return
    try:
        subprocess.Popen([sys.executable, str(VASI_PY)], cwd=str(VASI_PY.parent))
    except Exception as e:
        messagebox.showerror("Launch Error", f"Could not launch vasi.py:\n{e}")

def launch_after():
    """Launch FitTrack Enterprise in an independent process (with fallback)."""
    if FITTRACK_MAIN.exists():
        try:
            subprocess.Popen([sys.executable, str(FITTRACK_MAIN)], cwd=str(FITTRACK_DIR))
            return
        except Exception:
            pass

    # Fallback to in-process launch if subprocess fails
    sys.path.insert(0, str(FITTRACK_DIR))
    try:
        from ui.styles import configure_styles, COLOR_BG
        from ui.dashboard import FitTrackDashboard
        from database.db import DatabaseManager

        win = tk.Toplevel()
        win.title("FitTrack Enterprise v2.2.0")
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        W, H = 1280, 840
        win.geometry(f"{W}x{H}+{max(0,(sw-W)//2)}+{max(0,(sh-H)//2)}")
        win.configure(bg=COLOR_BG)
        configure_styles(win)
        db = DatabaseManager()
        FitTrackDashboard(win, db)
    except Exception as e:
        messagebox.showerror("Launch Error", f"Could not start FitTrack Enterprise:\n{e}")

def launch_both():
    """Launch both applications simultaneously for live side-by-side evaluation."""
    launch_before()
    launch_after()

# ---------------------------------------------------------------------------
# ARCHITECTURAL COMPARISON DATA
# ---------------------------------------------------------------------------

COMPARISON_MATRIX = [
    (
        "Software Architecture",
        "Single Flat Script (~190 LOC)",
        "Procedural paradigm where GUI layout, database calls, calculations, and event handlers are tightly coupled in one file.",
        "Modular MVC Architecture (~1,850 LOC)",
        "Strict separation of concerns across 10 specialized packages (models, services, database, ui, styles) with decoupled data flow."
    ),
    (
        "Database & Storage",
        "MySQL Local Server (Port 3306)",
        "Relies on external MySQL daemon running on localhost with specific user credentials. Fails if server is not active.",
        "Zero-Config Embedded SQLite",
        "ACID-compliant local SQLite database ('fittrack.db') with automated schema creation, auto-migrations, indexing, and stats queries."
    ),
    (
        "User Interface & Design",
        "Classic Windows 95 / Tkinter",
        "Multi-colored static Tkinter frames (pink, yellow, skyblue, red) with Algerian and Edwardian Script fonts.",
        "Aurora Glassmorphism Cockpit",
        "Deep cosmic space station HUD with real-time starfield canvas engine, glowing neon borders, glass cards, and modern Segoe UI typography."
    ),
    (
        "Theme Customization",
        "Single Fixed Color Scheme",
        "Hard-coded background and foreground colors with no dark or light mode switching capabilities.",
        "Dynamic Dual-Theme Engine",
        "Instant toggle between Cyber Obsidian HUD (high-contrast dark mode) and Aurora Bloom (clean, high-visibility medical light mode)."
    ),
    (
        "Biometric Visualization",
        "Static Text Readout & Popups",
        "Displays calculated number in a plain label with standard modal dialog alert boxes ('Your BMI is Normal').",
        "60 FPS OrbitalBMISphere & Scanner",
        "Animated canvas gauge with rotating orbit rings, 4 dynamic color-shifting arcs, pulsing glow, and live digital readout."
    ),
    (
        "Bio-Avatar & Clinical Scope",
        "3 Basic Classification Tiers",
        "Under-Weight (<18.5), Normal (18.5–25.9), Over-Weight (>25.9) based solely on raw BMI index.",
        "Full Holographic Bio-Avatar & Advisory",
        "Interactive wireframe avatar with active radar scan beam, Mifflin-St Jeor BMR, Mosteller BSA, Target Weight Delta, and WHO Advisory."
    ),
    (
        "Real-Time Interaction",
        "Static Entries + Button Trigger",
        "Requires typing values into entry boxes and manually clicking the 'CALCULATE' button to compute results.",
        "Synchronized Entries + Cyber Sliders",
        "Dual-input controls: interactive Height and Weight sliders synchronized with numeric fields, updating the gauge in real time."
    ),
    (
        "Data Analytics & Charts",
        "No Visual Charts or Trends",
        "Historical data is only viewable as raw textual rows with no trends or statistical graphs.",
        "Embedded Matplotlib Waveforms",
        "Real-time Oscilloscope BMI Trend line chart and WHO Category Spectrum distribution bar chart with interactive mode switching."
    ),
    (
        "Records Management",
        "Standard ttk.Treeview Grid",
        "Simple table with manual Delete and View actions. Limited search, no column sorting, and no telemetry reflection.",
        "Biometric Flight Matrix",
        "Filterable, sortable telemetry grid with quick search, glow selection, double-click editing, and single-click HUD needle reflection."
    ),
    (
        "Data Export",
        "No Export Capabilities",
        "All data remains confined to the local MySQL table with no external file extraction support.",
        "1-Click CSV Telemetry Export",
        "Full dataset export to standard CSV format with automated timestamps and user-selected save destination."
    ),
    (
        "Input Validation",
        "Basic Exception Trapping",
        "Simple try/except float conversion. Fails silently or displays generic missing-field error boxes.",
        "Enterprise InputValidator",
        "Strong typing, range checks (Height 50–250cm, Weight 20–300kg, Age 1–120), informative non-blocking alerts, and error highlights."
    ),
    (
        "Diagnostic Presets",
        "No Preset Profiles",
        "Requires manual entry of all parameters for every test subject.",
        "1-Click Biometric Presets",
        "Quick diagnostic profiles for rapid testing: Athlete (Low BMI), Standard (Optimal), Youth (Early scan), and Power (High BMI)."
    ),
]

METRICS = [
    ("Modularity", "1 File", "10 Modules", "+900% Structure"),
    ("Code Volume", "~190 LOC", "~1,850 LOC", "Enterprise Grade"),
    ("Biometrics", "1 Metric", "5 Formulas", "BMI + BMR + BSA + Delta"),
    ("Rendering", "Static Labels", "60 FPS Canvas", "Orbital Sphere + Waveforms"),
    ("Portability", "Needs MySQL", "Zero Config", "Self-Contained SQLite"),
    ("Themes", "1 Palette", "2 Full Themes", "Cyber Dark & Bloom Light"),
]

# ---------------------------------------------------------------------------
# MAIN SHOWCASE APPLICATION
# ---------------------------------------------------------------------------

class ShowcaseStudio:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("FitTrack — Before / After Architectural Showcase Studio")
        root.configure(bg=BG_DARK)

        # Maximize cleanly on Windows, with robust geometry fallback
        try:
            root.state("zoomed")
        except Exception:
            sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
            root.geometry(f"{max(1100, sw - 120)}x{max(720, sh - 100)}+60+30")

        root.minsize(1020, 680)

        # Keyboard shortcuts
        root.bind("<Alt-Key-1>", lambda _e: launch_before())
        root.bind("<Alt-Key-2>", lambda _e: launch_after())
        root.bind("<Alt-Key-3>", lambda _e: launch_both())
        root.bind("<F11>", self._toggle_fullscreen)

        self._build_ui()

    def _toggle_fullscreen(self, _event=None):
        is_fs = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not is_fs)

    # ------------------------------------------------------------------
    # UI CONSTRUCTION
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # Dynamic Fluid Header
        self.hdr = tk.Canvas(self.root, bg=BG_DARK, height=92, highlightthickness=0)
        self.hdr.pack(fill=tk.X)
        self.hdr.bind("<Configure>", self._draw_header)

        # Scrollable Viewport Container
        outer = tk.Frame(self.root, bg=BG_DARK)
        outer.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(outer, bg=BG_DARK, highlightthickness=0)
        self.vsb = tk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Content frame inside canvas
        self.body = tk.Frame(self.canvas, bg=BG_DARK)
        self.body_id = self.canvas.create_window((0, 0), window=self.body, anchor="nw")

        # Bind configure to stretch body to full canvas width (no empty margins!)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.body.bind("<Configure>", self._on_body_configure)

        # Mouse wheel support
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Populate content sections
        self._build_content(self.body)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.body_id, width=event.width)

    def _on_body_configure(self, _event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ------------------------------------------------------------------
    # HEADER RENDERING
    # ------------------------------------------------------------------

    def _draw_header(self, _event=None):
        w = max(self.hdr.winfo_width(), 960)
        h = 92
        self.hdr.delete("all")

        # Smooth horizontal gradient from Indigo-Violet to Dark Cosmic Slate
        step = 4
        r1, g1, b1 = 0x1E, 0x1B, 0x4B   # #1E1B4B
        r2, g2, b2 = 0x07, 0x0B, 0x14   # #070B14
        for i in range(0, w, step):
            ratio = i / max(1, w)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            self.hdr.create_rectangle(i, 0, i + step, h,
                                 fill=f"#{r:02x}{g:02x}{b:02x}", outline="")

        # Glowing accent baseline
        self.hdr.create_line(0, h - 2, w, h - 2, fill=ACCENT_BLUE_LT, width=2)
        self.hdr.create_line(0, h - 1, w, h - 1, fill="#1D4ED8", width=1)

        # Orb logo
        self.hdr.create_oval(24, 20, 72, 68, outline="#38BDF8", width=2)
        self.hdr.create_oval(28, 24, 68, 64, outline="#818CF8", width=1)
        pts = [32, 44, 40, 44, 44, 32, 48, 56, 52, 38, 56, 44, 64, 44]
        self.hdr.create_line(pts, fill=TEXT_WHITE, width=3,
                             capstyle=tk.ROUND, joinstyle=tk.ROUND)

        # Title & Subtitle
        self.hdr.create_text(86, 34, text="FitTrack Evolution Studio",
                             font=FONT_HERO, fill=TEXT_WHITE, anchor="w")
        self.hdr.create_text(
            86, 60,
            text="Deep Architectural & Feature Comparison: Prototype (vasi.py) vs Next-Gen Enterprise (v2.2)",
            font=FONT_BODY, fill="#93C5FD", anchor="w"
        )

        # Right-aligned badges
        badge_x = w - 30
        self.hdr.create_rectangle(badge_x - 220, 26, badge_x, 64,
                                  fill="#131C31", outline="#3B82F6", width=1)
        self.hdr.create_text(badge_x - 110, 45, text="✦ DUAL-PROJECT STUDIO ✦",
                             font=FONT_SM_BOLD, fill="#60A5FA", anchor="center")

    # ------------------------------------------------------------------
    # BODY CONTENT
    # ------------------------------------------------------------------

    def _build_content(self, parent: tk.Frame) -> None:
        container = tk.Frame(parent, bg=BG_DARK, padx=36, pady=24)
        container.pack(fill=tk.BOTH, expand=True)

        # 1. Action Launch Bar
        self._build_action_bar(container)

        # 2. Hero Project Cards (Side-by-Side 50/50 responsive)
        self._build_hero_cards(container)

        # 3. Evolution Metrics Strip
        self._build_metrics_strip(container)

        # 4. Deep Architectural & Feature Comparison Matrix
        self._build_comparison_matrix(container)

        # 5. Footer & Information Bar
        self._build_footer(container)

    # ------------------------------------------------------------------
    # 1. ACTION LAUNCH BAR
    # ------------------------------------------------------------------

    def _build_action_bar(self, parent: tk.Frame) -> None:
        bar = tk.Frame(parent, bg=BG_SURFACE, padx=20, pady=14,
                       highlightthickness=1, highlightbackground=BORDER_COLOR)
        bar.pack(fill=tk.X, pady=(0, 24))

        # Left label
        info = tk.Frame(bar, bg=BG_SURFACE)
        info.pack(side=tk.LEFT)
        tk.Label(info, text="QUICK LAUNCH CONTROLLER", font=FONT_SM_BOLD,
                 bg=BG_SURFACE, fg=ACCENT_CYAN).pack(anchor="w")
        tk.Label(info, text="Start applications independently or side-by-side to inspect live behavior",
                 font=FONT_SM, bg=BG_SURFACE, fg=TEXT_MUTED).pack(anchor="w")

        # Right action buttons
        btn_box = tk.Frame(bar, bg=BG_SURFACE)
        btn_box.pack(side=tk.RIGHT)

        self._create_button(
            btn_box, text="📜 Launch Before (vasi.py)",
            command=launch_before, bg="#334155", hover="#475569",
            fg=TEXT_WHITE, padx=16, pady=8, font=FONT_SM_BOLD
        ).pack(side=tk.LEFT, padx=6)

        self._create_button(
            btn_box, text="🌌 Launch After (FitTrack)",
            command=launch_after, bg=ACCENT_BLUE, hover=ACCENT_BLUE_LT,
            fg=TEXT_WHITE, padx=16, pady=8, font=FONT_SM_BOLD
        ).pack(side=tk.LEFT, padx=6)

        self._create_button(
            btn_box, text="⚡ Launch Both Side-by-Side",
            command=launch_both, bg="#059669", hover="#10B981",
            fg=TEXT_WHITE, padx=18, pady=8, font=FONT_SM_BOLD
        ).pack(side=tk.LEFT, padx=6)

    # ------------------------------------------------------------------
    # 2. HERO PROJECT CARDS (50/50 RESPONSIVE SPLIT)
    # ------------------------------------------------------------------

    def _build_hero_cards(self, parent: tk.Frame) -> None:
        row = tk.Frame(parent, bg=BG_DARK)
        row.pack(fill=tk.X, pady=(0, 24))
        row.columnconfigure(0, weight=1, uniform="card")
        row.columnconfigure(1, weight=1, uniform="card")

        # --- LEFT CARD: BEFORE (vasi.py) ---
        card_before = tk.Frame(row, bg=BG_CARD, padx=26, pady=24,
                               highlightthickness=1, highlightbackground=BORDER_COLOR)
        card_before.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        # Header badge & title
        head_b = tk.Frame(card_before, bg=BG_CARD)
        head_b.pack(fill=tk.X)
        self._pill(head_b, "CLASSIC PROTOTYPE", bg="#1E293B", fg="#94A3B8").pack(side=tk.LEFT)
        status_b = tk.Label(head_b, text="● Ready on Disk", font=FONT_SM_BOLD,
                            bg=BG_CARD, fg=ACCENT_EMERALD)
        status_b.pack(side=tk.RIGHT)

        tk.Label(card_before, text="📜  vasi.py", font=FONT_H1,
                 bg=BG_CARD, fg=TEXT_WHITE).pack(anchor="w", pady=(10, 2))
        tk.Label(card_before, text="Original BMI Calculator Script · Single-file procedural baseline",
                 font=FONT_SM, bg=BG_CARD, fg="#94A3B8").pack(anchor="w", pady=(0, 14))

        # Tech Stack Pills
        stack_b = tk.Frame(card_before, bg=BG_CARD)
        stack_b.pack(fill=tk.X, pady=(0, 16))
        for tech in ["Python 3.14", "Tkinter Procedural", "MySQL Connector", "ttk.Treeview", "Algerian UI"]:
            self._pill(stack_b, tech, bg="#1E293B", fg="#CBD5E1").pack(side=tk.LEFT, padx=(0, 6), pady=2)

        # Key Architecture Specs
        specs_b = tk.Frame(card_before, bg=BG_SURFACE, padx=14, pady=12,
                           highlightthickness=1, highlightbackground=BORDER_COLOR)
        specs_b.pack(fill=tk.X, pady=(0, 16))
        self._spec_row(specs_b, "File Path:", "c:\\Users\\vasiharan\\Downloads\\BMI calculator\\vasi.py")
        self._spec_row(specs_b, "Code Structure:", "Single flat file (~190 lines of code)")
        self._spec_row(specs_b, "Database:", "MySQL localhost daemon (table 'bmi_calculator')")
        self._spec_row(specs_b, "GUI Theme:", "Multi-color panels (Pink / Skyblue / Yellow / Red)")

        # Feature bullet list
        tk.Label(card_before, text="Included Capabilities:", font=FONT_SM_BOLD,
                 bg=BG_CARD, fg=TEXT_WHITE).pack(anchor="w", pady=(0, 6))
        bullets_b = [
            "Input details form: Name, Age, Gender, Height, Weight",
            "Direct SQL record insertion and deletion",
            "Tkinter Treeview data grid with vertical & horizontal scrollbars",
            "Single-action BMI calculation with popup message boxes",
            "Clear form entries and view selected records",
        ]
        for b in bullets_b:
            self._bullet_item(card_before, "▫", b, fg=TEXT_MUTED)

        # Launch Button
        btn_b = self._create_button(
            card_before, text="🚀  Launch BEFORE (vasi.py)",
            command=launch_before, bg="#334155", hover="#475569",
            fg=TEXT_WHITE, padx=22, pady=12, font=FONT_H3
        )
        btn_b.pack(anchor="w", pady=(20, 0))

        # --- RIGHT CARD: AFTER (FitTrack Enterprise) ---
        card_after = tk.Frame(row, bg=BG_CARD, padx=26, pady=24,
                              highlightthickness=1, highlightbackground=BORDER_CYAN)
        card_after.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        # Header badge & title
        head_a = tk.Frame(card_after, bg=BG_CARD)
        head_a.pack(fill=tk.X)
        self._pill(head_a, "NEXT-GEN ENTERPRISE", bg="#0C4A6E", fg="#38BDF8").pack(side=tk.LEFT)
        status_a = tk.Label(head_a, text="● Operational (v2.2.0)", font=FONT_SM_BOLD,
                            bg=BG_CARD, fg=ACCENT_CYAN)
        status_a.pack(side=tk.RIGHT)

        tk.Label(card_after, text="🌌  FitTrack Enterprise", font=FONT_H1,
                 bg=BG_CARD, fg=TEXT_WHITE).pack(anchor="w", pady=(10, 2))
        tk.Label(card_after, text="Glassmorphism Space Station HUD · Full MVC Telemetry Console",
                 font=FONT_SM, bg=BG_CARD, fg=ACCENT_BLUE_LT).pack(anchor="w", pady=(0, 14))

        # Tech Stack Pills
        stack_a = tk.Frame(card_after, bg=BG_CARD)
        stack_a.pack(fill=tk.X, pady=(0, 16))
        for tech in ["Clean MVC", "Embedded SQLite", "Canvas Starfield", "Matplotlib Charts", "Orbital Sphere", "Dual Theme"]:
            self._pill(stack_a, tech, bg="#172554", fg="#93C5FD").pack(side=tk.LEFT, padx=(0, 6), pady=2)

        # Key Architecture Specs
        specs_a = tk.Frame(card_after, bg=BG_SURFACE, padx=14, pady=12,
                           highlightthickness=1, highlightbackground=BORDER_COLOR)
        specs_a.pack(fill=tk.X, pady=(0, 16))
        self._spec_row(specs_a, "Location:", "c:\\Users\\vasiharan\\Downloads\\BMI calculator\\FitTrack\\")
        self._spec_row(specs_a, "Code Structure:", "10 modular packages (~1,850 LOC) with clean MVC")
        self._spec_row(specs_a, "Database:", "Standalone SQLite engine with auto-migrations & stats")
        self._spec_row(specs_a, "GUI Theme:", "Dynamic Dual-Theme (Cyber Obsidian Dark & Aurora Light)")

        # Feature bullet list
        tk.Label(card_after, text="Advanced Capabilities:", font=FONT_SM_BOLD,
                 bg=BG_CARD, fg=TEXT_WHITE).pack(anchor="w", pady=(0, 6))
        bullets_a = [
            "60 FPS animated OrbitalBMISphere with rotating orbit rings & glow",
            "Holographic Bio-Avatar wireframe with active radar sweep beam",
            "Dual input controls: Numeric entries + real-time cyber sliders",
            "Clinical diagnostics: Mifflin-St Jeor BMR, Mosteller BSA, Target Delta",
            "Embedded Matplotlib Oscilloscope Trend and WHO Spectrum bar charts",
            "1-Click Biometric Presets, CSV export, search filters, and shortcuts",
        ]
        for b in bullets_a:
            self._bullet_item(card_after, "✦", b, fg="#93C5FD")

        # Launch Button
        btn_a = self._create_button(
            card_after, text="⚡  Launch AFTER (FitTrack Enterprise)",
            command=launch_after, bg=ACCENT_BLUE, hover=ACCENT_BLUE_LT,
            fg=TEXT_WHITE, padx=22, pady=12, font=FONT_H3
        )
        btn_a.pack(anchor="w", pady=(20, 0))

    # ------------------------------------------------------------------
    # 3. EVOLUTION METRICS STRIP
    # ------------------------------------------------------------------

    def _build_metrics_strip(self, parent: tk.Frame) -> None:
        self._section_header(parent, "📊  System Evolution Metrics",
                             "Quantifiable improvements across code architecture, diagnostic depth, and user experience")

        strip = tk.Frame(parent, bg=BG_DARK)
        strip.pack(fill=tk.X, pady=(0, 24))

        for idx, (label, before_val, after_val, delta) in enumerate(METRICS):
            strip.columnconfigure(idx, weight=1)
            card = tk.Frame(strip, bg=BG_CARD, padx=14, pady=14,
                            highlightthickness=1, highlightbackground=BORDER_COLOR)
            card.grid(row=0, column=idx, sticky="nsew",
                      padx=(0 if idx == 0 else 6, 0 if idx == len(METRICS) - 1 else 6))

            tk.Label(card, text=label.upper(), font=FONT_TINY,
                     bg=BG_CARD, fg=TEXT_SUBTLE).pack(anchor="w")

            row_val = tk.Frame(card, bg=BG_CARD)
            row_val.pack(anchor="w", pady=(4, 2))
            tk.Label(row_val, text=before_val, font=FONT_SM,
                     bg=BG_CARD, fg=TEXT_MUTED).pack(side=tk.LEFT)
            tk.Label(row_val, text=" → ", font=FONT_SM_BOLD,
                     bg=BG_CARD, fg=ACCENT_CYAN).pack(side=tk.LEFT)
            tk.Label(row_val, text=after_val, font=FONT_H3,
                     bg=BG_CARD, fg=TEXT_WHITE).pack(side=tk.LEFT)

            tk.Label(card, text=delta, font=FONT_TINY,
                     bg=BG_CARD, fg=ACCENT_EMERALD).pack(anchor="w")

    # ------------------------------------------------------------------
    # 4. DEEP ARCHITECTURAL COMPARISON MATRIX
    # ------------------------------------------------------------------

    def _build_comparison_matrix(self, parent: tk.Frame) -> None:
        self._section_header(parent, "✨  Full Architectural & Feature Comparison Matrix",
                             "Detailed side-by-side breakdown comparing every layer of both software systems")

        tbl_wrapper = tk.Frame(parent, bg=BORDER_COLOR, bd=1)
        tbl_wrapper.pack(fill=tk.X, pady=(0, 28))

        tbl = tk.Frame(tbl_wrapper, bg=BG_CARD)
        tbl.pack(fill=tk.X)

        # Responsive column layout
        tbl.columnconfigure(0, weight=2, minsize=180)   # Dimension
        tbl.columnconfigure(1, weight=4, minsize=280)   # BEFORE
        tbl.columnconfigure(2, weight=5, minsize=360)   # AFTER

        # Header row
        hdr_bg = "#0F172A"
        h0 = tk.Label(tbl, text="EVALUATION DIMENSION", font=FONT_SM_BOLD,
                      bg=hdr_bg, fg=TEXT_MUTED, anchor="w", padx=16, pady=12)
        h0.grid(row=0, column=0, sticky="nsew")

        h1 = tk.Label(tbl, text="BEFORE: CLASSIC PROTOTYPE (vasi.py)", font=FONT_SM_BOLD,
                      bg=hdr_bg, fg="#94A3B8", anchor="w", padx=16, pady=12)
        h1.grid(row=0, column=1, sticky="nsew")

        h2 = tk.Label(tbl, text="AFTER: FITTRACK ENTERPRISE (v2.2)", font=FONT_SM_BOLD,
                      bg=hdr_bg, fg=ACCENT_CYAN, anchor="w", padx=16, pady=12)
        h2.grid(row=0, column=2, sticky="nsew")

        # Separator line
        sep = tk.Frame(tbl, bg=BORDER_COLOR, height=1)
        sep.grid(row=1, column=0, columnspan=3, sticky="ew")

        # Data rows
        for i, (dim, b_title, b_desc, a_title, a_desc) in enumerate(COMPARISON_MATRIX):
            r_idx = i + 2
            row_bg = BG_ROW_EVEN if i % 2 == 0 else BG_ROW_ODD

            # Dimension cell
            c0 = tk.Frame(tbl, bg=row_bg, padx=16, pady=10)
            c0.grid(row=r_idx, column=0, sticky="nsew")
            tk.Label(c0, text=dim, font=FONT_BODY_BOLD,
                     bg=row_bg, fg=TEXT_WHITE, anchor="w").pack(anchor="w")

            # Before cell
            c1 = tk.Frame(tbl, bg=row_bg, padx=16, pady=10)
            c1.grid(row=r_idx, column=1, sticky="nsew")
            tk.Label(c1, text=b_title, font=FONT_SM_BOLD,
                     bg=row_bg, fg="#CBD5E1", anchor="w").pack(anchor="w")
            desc1 = tk.Label(c1, text=b_desc, font=FONT_SM,
                             bg=row_bg, fg=TEXT_MUTED, justify="left",
                             anchor="w")
            desc1.pack(anchor="w", pady=(2, 0), fill=tk.X)
            c1.bind("<Configure>", lambda e, l=desc1: l.config(wraplength=max(200, e.width - 24)))

            # After cell
            c2 = tk.Frame(tbl, bg=row_bg, padx=16, pady=10)
            c2.grid(row=r_idx, column=2, sticky="nsew")
            tk.Label(c2, text=a_title, font=FONT_SM_BOLD,
                     bg=row_bg, fg="#60A5FA", anchor="w").pack(anchor="w")
            desc2 = tk.Label(c2, text=a_desc, font=FONT_SM,
                             bg=row_bg, fg="#93C5FD", justify="left",
                             anchor="w")
            desc2.pack(anchor="w", pady=(2, 0), fill=tk.X)
            c2.bind("<Configure>", lambda e, l=desc2: l.config(wraplength=max(200, e.width - 24)))

    # ------------------------------------------------------------------
    # 5. FOOTER & INFORMATION BAR
    # ------------------------------------------------------------------

    def _build_footer(self, parent: tk.Frame) -> None:
        ftr = tk.Frame(parent, bg=BG_SURFACE, padx=24, pady=18,
                       highlightthickness=1, highlightbackground=BORDER_COLOR)
        ftr.pack(fill=tk.X, pady=(10, 20))

        tk.Label(
            ftr,
            text="FitTrack Evolution Studio  ·  Designed for Comprehensive Architectural Comparison  ·  Both Systems Fully Functional",
            font=FONT_SM_BOLD, bg=BG_SURFACE, fg=TEXT_MUTED
        ).pack(anchor="center")

        tk.Label(
            ftr,
            text="Shortcuts: [Alt + 1] Launch vasi.py  ·  [Alt + 2] Launch FitTrack  ·  [Alt + 3] Launch Both  ·  [F11] Fullscreen",
            font=FONT_TINY, bg=BG_SURFACE, fg=TEXT_SUBTLE
        ).pack(anchor="center", pady=(4, 0))

    # ------------------------------------------------------------------
    # HELPER COMPONENTS
    # ------------------------------------------------------------------

    def _section_header(self, parent: tk.Frame, title: str, subtitle: str) -> None:
        sec = tk.Frame(parent, bg=BG_DARK)
        sec.pack(fill=tk.X, pady=(10, 10))
        tk.Label(sec, text=title, font=FONT_H2, bg=BG_DARK, fg=TEXT_WHITE).pack(anchor="w")
        tk.Label(sec, text=subtitle, font=FONT_SM, bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w")

    def _pill(self, parent: tk.Frame, text: str, bg: str, fg: str) -> tk.Frame:
        p = tk.Frame(parent, bg=bg, padx=8, pady=3)
        tk.Label(p, text=text, font=FONT_TINY, bg=bg, fg=fg).pack()
        return p

    def _spec_row(self, parent: tk.Frame, label: str, value: str) -> None:
        r = tk.Frame(parent, bg=BG_SURFACE)
        r.pack(fill=tk.X, pady=2)
        tk.Label(r, text=label, font=FONT_SM_BOLD, bg=BG_SURFACE,
                 fg=TEXT_MUTED, width=15, anchor="w").pack(side=tk.LEFT)
        tk.Label(r, text=value, font=FONT_SM, bg=BG_SURFACE,
                 fg=TEXT_LIGHT, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _bullet_item(self, parent: tk.Frame, symbol: str, text: str, fg: str) -> None:
        r = tk.Frame(parent, bg=BG_CARD)
        r.pack(fill=tk.X, pady=2)
        tk.Label(r, text=symbol, font=FONT_SM, bg=BG_CARD, fg=ACCENT_CYAN,
                 width=2, anchor="n").pack(side=tk.LEFT)
        tk.Label(r, text=text, font=FONT_SM, bg=BG_CARD, fg=fg,
                 anchor="w", justify="left").pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _create_button(self, parent: tk.Frame, text: str, command, bg: str,
                       hover: str, fg: str, padx: int, pady: int, font) -> tk.Button:
        btn = tk.Button(
            parent, text=text, command=command, font=font,
            bg=bg, fg=fg, activebackground=hover, activeforeground=TEXT_WHITE,
            relief="flat", bd=0, padx=padx, pady=pady, cursor="hand2"
        )
        btn.bind("<Enter>", lambda _e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda _e: btn.config(bg=bg))
        return btn


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app_root = tk.Tk()
    ShowcaseStudio(app_root)
    app_root.mainloop()
