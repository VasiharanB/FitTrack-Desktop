"""
main.py
=======
FitTrack Orbital Station — application entry point.

Responsibilities
----------------
1. Create and configure the root Tk window
2. Generate a logo PNG asset if missing (requires Pillow)
3. Show an animated Glassmorphism Space Station splash while the DB initialises
4. Hand off to FitTrackDashboard once everything is ready
"""

import math
import tkinter as tk
from pathlib import Path

from database.db import DatabaseManager
from ui.styles import configure_styles, COLOR_BG
from ui.dashboard import FitTrackDashboard


# ---------------------------------------------------------------------------
# ASSET GENERATION
# ---------------------------------------------------------------------------

def _generate_logo(path: Path) -> None:
    """Programmatically generate a 64×64 orbital logo PNG using Pillow if available."""
    try:
        from PIL import Image, ImageDraw
        path.parent.mkdir(parents=True, exist_ok=True)
        img  = Image.new("RGBA", (64, 64), (5, 8, 17, 255))
        draw = ImageDraw.Draw(img)
        # Outer orbit ring
        draw.ellipse([(3, 3), (60, 60)], outline=(167, 139, 250, 255), width=2)
        # Inner glow orb
        draw.ellipse([(20, 20), (44, 44)], fill=(45, 212, 191, 200))
        # Diagonal orbit
        draw.ellipse([(8, 18), (56, 46)], outline=(167, 139, 250, 180), width=1)
        img.save(path, "PNG")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# WINDOW UTILITIES
# ---------------------------------------------------------------------------

def _center_window(window: tk.Tk, width: int = 1280, height: int = 800) -> None:
    """Place the window in the centre of the primary screen."""
    window.update_idletasks()
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()
    x  = max(0, (sw - width)  // 2)
    y  = max(0, (sh - height) // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


# ---------------------------------------------------------------------------
# SPLASH SCREEN — Glassmorphism Space Station
# ---------------------------------------------------------------------------

def _show_splash(root: tk.Tk, on_done) -> None:
    """
    Display a Glassmorphism Space Station animated splash screen.
    Deep void background with animated star particles, orbital logo, and
    aurora-tinted progress bar.
    Calls `on_done` once the animation completes.
    """
    root.withdraw()

    W, H = 600, 360
    splash = tk.Toplevel(root)
    splash.overrideredirect(True)

    sw = splash.winfo_screenwidth()
    sh = splash.winfo_screenheight()
    splash.geometry(f"{W}x{H}+{(sw - W) // 2}+{(sh - H) // 2}")
    splash.configure(bg="#050811")

    canvas = tk.Canvas(splash, bg="#050811", highlightthickness=1,
                        highlightbackground="#A78BFA")
    canvas.pack(fill=tk.BOTH, expand=True)

    # Deep space gradient background
    for row in range(0, H, 2):
        ratio = row / H
        r = int(0x05 + 0x05 * ratio)
        g = int(0x08 + 0x08 * ratio)
        b = int(0x11 + 0x12 * ratio)
        canvas.create_rectangle(0, row, W, row + 2, fill=f"#{r:02x}{g:02x}{b:02x}", outline="")

    # Aurora wash band (violet glow at top)
    for row in range(0, 100, 3):
        alpha = math.sin(math.pi * row / 100) * 0.25
        r = int(0x7C * alpha); g = int(0x3A * alpha); b = int(0xED * alpha)
        r = max(0, min(255, r)); g = max(0, min(255, g)); b = max(0, min(255, b))
        canvas.create_rectangle(0, row, W, row + 3,
                                  fill=f"#{r:02x}{g:02x}{b:02x}", outline="")

    # Star particles
    import random
    rng = random.Random(42)
    for _ in range(120):
        sx = rng.randint(0, W)
        sy = rng.randint(0, H)
        sz = rng.choice([1, 1, 1, 2, 2])
        col = rng.choice(["#FFFFFF", "#A78BFA", "#2DD4BF", "#C4B5FD", "#F9A8D4"])
        canvas.create_oval(sx - sz, sy - sz, sx + sz, sy + sz, fill=col, outline="")

    # Corner aurora brackets
    b_len = 18
    bdr_col = "#A78BFA"
    canvas.create_line(8, 8 + b_len, 8, 8, 8 + b_len, 8, fill=bdr_col, width=2)
    canvas.create_line(W - 8 - b_len, 8, W - 8, 8, W - 8, 8 + b_len, fill=bdr_col, width=2)
    canvas.create_line(8, H - 8 - b_len, 8, H - 8, 8 + b_len, H - 8, fill=bdr_col, width=2)
    canvas.create_line(W - 8 - b_len, H - 8, W - 8, H - 8, W - 8, H - 8 - b_len, fill=bdr_col, width=2)

    # Orbital logo at center
    CX, CY, OR = W // 2, 130, 38
    # Outer ring
    canvas.create_oval(CX - OR, CY - OR, CX + OR, CY + OR,
                        outline="#A78BFA", width=2)
    # Diagonal orbit ellipse
    canvas.create_oval(CX - OR, CY - int(OR * 0.45), CX + OR, CY + int(OR * 0.45),
                        outline="#A78BFA", width=1, dash=(4, 4))
    # Center orb glow rings
    for gr, ga_col in [(22, "#2DD4BF"), (16, "#5EEAD4"), (10, "#A7F3D0")]:
        canvas.create_oval(CX - gr, CY - gr, CX + gr, CY + gr, fill=ga_col, outline="")
    # Orb core
    canvas.create_oval(CX - 7, CY - 7, CX + 7, CY + 7, fill="#FFFFFF", outline="")
    # Specular dot
    canvas.create_oval(CX - 10, CY - 12, CX - 4, CY - 6, fill="#FFFFFF", outline="")

    # Title text
    canvas.create_text(W // 2, 192,
                        text="FitTrack  //  ORBITAL STATION",
                        font=("Segoe UI", 22, "bold"), fill="#FFFFFF")
    canvas.create_text(W // 2, 220,
                        text="v3.0.0  ·  Glassmorphism Space Station  ·  Biometric Orbital Core",
                        font=("Segoe UI", 10, "bold"), fill="#A78BFA")

    # Copyright
    canvas.create_text(W // 2, 338,
                        text="© 2026 vasiharan  —  MIT License  ✦  Aurora Space Station Edition",
                        font=("Segoe UI", 8), fill="#4A5568")

    # Aurora progress bar track
    BAR_L, BAR_R, BAR_Y1, BAR_Y2 = 70, W - 70, 260, 267
    canvas.create_rectangle(BAR_L, BAR_Y1, BAR_R, BAR_Y2,
                             fill="#0C1428", outline="#1E2A45")
    bar = canvas.create_rectangle(BAR_L, BAR_Y1, BAR_L, BAR_Y2,
                                   fill="#A78BFA", outline="")

    status = canvas.create_text(W // 2, 284,
                                  text="Initializing orbital systems…",
                                  font=("Segoe UI", 9), fill="#8892B0")

    bar_width = BAR_R - BAR_L
    messages = {
        15: "Calibrating aurora bio-scanner…",
        35: "Spinning up orbital BMI sphere…",
        55: "Connecting biometric database…",
        75: "Rendering glass station panels…",
        92: "Animating star-field and orbit rings…",
        100: "✦  Orbital Station Online.",
    }

    def _tick(pct: int) -> None:
        if pct > 100:
            splash.destroy()
            root.deiconify()
            on_done()
            return
        # Animate bar color from violet to teal as it fills
        ratio = pct / 100.0
        r = int(0xA7 + (0x2D - 0xA7) * ratio)
        g = int(0x8B + (0xD4 - 0x8B) * ratio)
        b = int(0xFA + (0xBF - 0xFA) * ratio)
        r = max(0, min(255, r)); g = max(0, min(255, g)); b = max(0, min(255, b))
        bar_col = f"#{r:02x}{g:02x}{b:02x}"
        canvas.itemconfig(bar, fill=bar_col)
        canvas.coords(bar, BAR_L, BAR_Y1, BAR_L + int(bar_width * pct / 100), BAR_Y2)
        if pct in messages:
            canvas.itemconfig(status, text=messages[pct])
        splash.after(14, lambda: _tick(pct + 2))

    splash.after(60, lambda: _tick(0))


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

def main() -> None:
    """Bootstrap FitTrack Orbital Station."""
    root = tk.Tk()
    root.title("FitTrack  ·  Orbital Station  ·  v3.0.0")
    root.configure(bg=COLOR_BG)
    _center_window(root, width=1280, height=800)
    root.minsize(1100, 700)

    # Application icon
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    if not logo_path.exists():
        _generate_logo(logo_path)
    if logo_path.exists():
        try:
            root.iconphoto(True, tk.PhotoImage(file=str(logo_path)))
        except Exception:
            pass

    # Database — initialises schema on first run
    db = DatabaseManager()

    # ttk style system
    configure_styles(root)

    def _launch() -> None:
        FitTrackDashboard(root, db)

    _show_splash(root, _launch)
    root.mainloop()


if __name__ == "__main__":
    main()
