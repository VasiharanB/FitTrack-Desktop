"""
ui/dialogs.py
=============
Reusable modal dialog classes for FitTrack Enterprise.
Supports dynamic Light and Dark mode styling.

AlertDialog      — info / success / warning / error message box
ConfirmDialog    — yes/no confirmation with keyboard support
SettingsDialog   — settings panel with theme switcher and system info
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from ui import styles


# ---------------------------------------------------------------------------
# BASE
# ---------------------------------------------------------------------------

class _BaseDialog(tk.Toplevel):
    """
    Shared base for all FitTrack modal dialogs.
    Handles centering, modality, focus grab and escape binding.
    """

    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        width: int = 420,
        height: int = 220,
    ) -> None:
        super().__init__(parent)
        self.title(title)
        self.configure(bg=styles.COLOR_BG)
        self.resizable(False, False)
        self.withdraw()

        # Center over parent
        self.update_idletasks()
        try:
            px = parent.winfo_rootx() if hasattr(parent, "winfo_rootx") else 0
            py = parent.winfo_rooty() if hasattr(parent, "winfo_rooty") else 0
            pw = parent.winfo_width() if hasattr(parent, "winfo_width") else 800
            ph = parent.winfo_height() if hasattr(parent, "winfo_height") else 600
        except Exception:
            px, py, pw, ph = 0, 0, 800, 600

        x = max(0, px + (pw - width) // 2)
        y = max(0, py + (ph - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.deiconify()
        self.lift()
        try:
            self.transient(parent)
            self.grab_set()
        except Exception:
            pass
        self.focus_force()

    def _close(self) -> None:
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()


# ---------------------------------------------------------------------------
# ALERT
# ---------------------------------------------------------------------------

class AlertDialog(_BaseDialog):
    """Styled replacement for messagebox — supports info / success / warning / error."""

    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        message: str,
        alert_type: str = "info",
    ) -> None:
        super().__init__(parent, title, width=420, height=200)

        theme = styles.get_theme_dict()
        themes_map = {
            "info":    (styles.COLOR_PRIMARY, "ⓘ"),
            "success": (styles.COLOR_SUCCESS, "✅"),
            "warning": (styles.COLOR_WARNING, "⚠"),
            "error":   (styles.COLOR_DANGER,  "✖"),
        }
        color, icon = themes_map.get(alert_type, themes_map["info"])

        # Accent top stripe
        stripe = tk.Frame(self, bg=color, height=4)
        stripe.pack(fill=tk.X, side=tk.TOP)

        body = tk.Frame(self, bg=styles.COLOR_BG, padx=22, pady=18)
        body.pack(fill=tk.BOTH, expand=True)

        # Icon column
        tk.Label(body, text=icon, fg=color, bg=styles.COLOR_BG,
                 font=styles.get_font(26, "bold")).pack(side=tk.LEFT, anchor=tk.N, padx=(0, 16))

        # Content column
        right = tk.Frame(body, bg=styles.COLOR_BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(right, text=message, fg=styles.COLOR_TEXT, bg=styles.COLOR_BG,
                 font=styles.get_font(10), justify=tk.LEFT,
                 wraplength=290).pack(anchor=tk.W, pady=(0, 16), fill=tk.X)

        btn_type = "danger" if alert_type == "error" else "primary"
        btn = styles.make_modern_button(right, "OK", btn_type, self._close, width=10)
        btn.pack(anchor=tk.E)
        btn.focus_set()

        self.bind("<Return>", lambda _e: self._close())
        self.bind("<Escape>", lambda _e: self._close())
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.wait_window()


# ---------------------------------------------------------------------------
# CONFIRM
# ---------------------------------------------------------------------------

class ConfirmDialog(_BaseDialog):
    """Yes / Cancel confirmation dialog. Check `.result` after construction."""

    def __init__(self, parent: tk.Widget, title: str, message: str) -> None:
        super().__init__(parent, title, width=430, height=200)
        self.result: bool = False

        # Accent stripe
        tk.Frame(self, bg=styles.COLOR_DANGER, height=4).pack(fill=tk.X, side=tk.TOP)

        body = tk.Frame(self, bg=styles.COLOR_BG, padx=22, pady=18)
        body.pack(fill=tk.BOTH, expand=True)

        tk.Label(body, text="⚠", fg=styles.COLOR_DANGER, bg=styles.COLOR_BG,
                 font=styles.get_font(26, "bold")).pack(side=tk.LEFT, anchor=tk.N, padx=(0, 16))

        right = tk.Frame(body, bg=styles.COLOR_BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(right, text=message, fg=styles.COLOR_TEXT, bg=styles.COLOR_BG,
                 font=styles.get_font(10), justify=tk.LEFT,
                 wraplength=300).pack(anchor=tk.W, pady=(0, 16), fill=tk.X)

        btns = tk.Frame(right, bg=styles.COLOR_BG)
        btns.pack(fill=tk.X, anchor=tk.E)

        styles.make_modern_button(btns, "Cancel",  "secondary", self._no,  width=10).pack(side=tk.RIGHT, padx=(6, 0))
        confirm_btn = styles.make_modern_button(btns, "Confirm", "danger", self._yes, width=10)
        confirm_btn.pack(side=tk.RIGHT)
        confirm_btn.focus_set()

        self.bind("<Return>", lambda _e: self._yes())
        self.bind("<Escape>", lambda _e: self._no())
        self.protocol("WM_DELETE_WINDOW", self._no)
        self.wait_window()

    def _yes(self) -> None:
        self.result = True
        self._close()

    def _no(self) -> None:
        self.result = False
        self._close()


# ---------------------------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------------------------

class SettingsDialog(_BaseDialog):
    """
    Settings panel with:
    - Theme switcher (Light / Dark Mode)
    - Application info (version, author, license)
    - Database path display
    - Keyboard shortcuts reference
    """

    def __init__(
        self,
        parent: tk.Widget,
        db_path: str = "",
        on_theme_change: Optional[Callable[[str], None]] = None,
    ) -> None:
        super().__init__(parent, "⚙  Settings — FitTrack Enterprise", width=540, height=460)
        self.on_theme_change = on_theme_change

        theme = styles.get_theme_dict()

        # Accent stripe
        self.stripe = tk.Frame(self, bg=styles.COLOR_PRIMARY, height=4)
        self.stripe.pack(fill=tk.X, side=tk.TOP)

        # Tab bar
        self.tab_bar = tk.Frame(self, bg=theme["tab_bar_bg"], height=38)
        self.tab_bar.pack(fill=tk.X)
        self.tab_bar.pack_propagate(False)

        self._tab_frames: dict = {}
        self._tab_buttons: dict = {}
        self._active_tab: str = ""

        self.content_area = tk.Frame(self, bg=styles.COLOR_BG)
        self.content_area.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        # Build tabs
        for label in ("General", "Keyboard", "About"):
            key = label.lower()
            frame = tk.Frame(self.content_area, bg=styles.COLOR_BG)
            self._tab_frames[key] = frame

            btn = tk.Button(
                self.tab_bar, text=label,
                font=styles.get_font(10, "bold"),
                bg=theme["tab_btn_bg"], fg=styles.COLOR_TEXT_MUTED,
                relief="flat", bd=0, padx=20, pady=8,
                cursor="hand2",
                command=lambda k=key: self._switch_tab(k),
            )
            btn.pack(side=tk.LEFT)
            self._tab_buttons[key] = btn

        # Populate tab content
        self._build_general(self._tab_frames["general"], db_path)
        self._build_keyboard(self._tab_frames["keyboard"])
        self._build_about(self._tab_frames["about"])

        # Footer
        self.footer = tk.Frame(self, bg=theme["table_heading_bg"], height=48)
        self.footer.pack(fill=tk.X, side=tk.BOTTOM)
        self.footer.pack_propagate(False)
        self.close_btn = styles.make_modern_button(
            self.footer, "Close", "primary", self._close, width=10
        )
        self.close_btn.pack(side=tk.RIGHT, padx=16, pady=8)

        self._switch_tab("general")

        self.bind("<Escape>", lambda _e: self._close())
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _switch_tab(self, key: str) -> None:
        if self._active_tab == key:
            return
        self._active_tab = key
        theme = styles.get_theme_dict()
        is_dark = (styles.CURRENT_THEME == "dark")
        active_fg = "#0A0A0C" if is_dark else "#FFFFFF"
        for k, frame in self._tab_frames.items():
            frame.pack_forget()
        self._tab_frames[key].pack(fill=tk.BOTH, expand=True)
        for k, btn in self._tab_buttons.items():
            if k == key:
                btn.config(bg=styles.COLOR_PRIMARY, fg=active_fg)
            else:
                btn.config(bg=theme["tab_btn_bg"], fg=styles.COLOR_TEXT_MUTED)

    def _section(self, parent: tk.Frame, title: str) -> tk.Frame:
        tk.Label(parent, text=title, bg=styles.COLOR_BG,
                 fg=styles.COLOR_TEXT, font=styles.get_font(11, "bold")).pack(anchor=tk.W, pady=(8, 4))
        line = tk.Frame(parent, bg=styles.COLOR_BORDER, height=1)
        line.pack(fill=tk.X, pady=(0, 6))
        return parent

    def _row(self, parent: tk.Frame, label: str, value: str) -> None:
        row = tk.Frame(parent, bg=styles.COLOR_BG)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=label, bg=styles.COLOR_BG, fg=styles.COLOR_TEXT_MUTED,
                 font=styles.get_font(9), width=22, anchor=tk.W).pack(side=tk.LEFT)
        tk.Label(row, text=value, bg=styles.COLOR_BG, fg=styles.COLOR_TEXT,
                 font=styles.get_font(9, "bold"), anchor=tk.W).pack(side=tk.LEFT)

    def _build_general(self, frame: tk.Frame, db_path: str) -> None:
        self._section(frame, "Appearance & Theme")

        theme_row = tk.Frame(frame, bg=styles.COLOR_BG)
        theme_row.pack(fill=tk.X, pady=4)
        tk.Label(theme_row, text="Color Theme", bg=styles.COLOR_BG,
                 fg=styles.COLOR_TEXT_MUTED, font=styles.get_font(9),
                 width=22, anchor=tk.W).pack(side=tk.LEFT)

        theme_btns_frame = tk.Frame(theme_row, bg=styles.COLOR_BG)
        theme_btns_frame.pack(side=tk.LEFT)

        is_dark = (styles.CURRENT_THEME == "dark")
        self.light_btn = tk.Button(
            theme_btns_frame, text="☀️ Light Mode (Maroon & Gold)",
            font=styles.get_font(9, "bold"),
            bg=styles.COLOR_PRIMARY if not is_dark else styles.COLOR_BORDER,
            fg="#FFFFFF" if not is_dark else styles.COLOR_TEXT,
            relief="flat", bd=0, padx=12, pady=5, cursor="hand2",
            command=lambda: self._select_theme("light")
        )
        self.light_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.dark_btn = tk.Button(
            theme_btns_frame, text="🌙 Dark Mode (Black & Gold)",
            font=styles.get_font(9, "bold"),
            bg=styles.COLOR_PRIMARY if is_dark else styles.COLOR_BORDER,
            fg="#0A0A0C" if is_dark else styles.COLOR_TEXT,
            relief="flat", bd=0, padx=12, pady=5, cursor="hand2",
            command=lambda: self._select_theme("dark")
        )
        self.dark_btn.pack(side=tk.LEFT)

        self._section(frame, "Application")
        self._row(frame, "Application Name",  "FitTrack Enterprise")
        self._row(frame, "Version",           "2.1.0")
        self._row(frame, "Platform",          "Windows Desktop (Tkinter)")

        self._section(frame, "Database")
        db_display = db_path if len(db_path) <= 55 else "..." + db_path[-52:]
        self._row(frame, "Database Engine",  "SQLite 3")
        self._row(frame, "Database Path",    db_display or "fittrack.db")

    def _select_theme(self, theme_name: str) -> None:
        if self.on_theme_change:
            self.on_theme_change(theme_name)
        # Update settings dialog's own theme
        self.configure(bg=styles.COLOR_BG)
        self.content_area.configure(bg=styles.COLOR_BG)
        theme = styles.get_theme_dict()
        is_dark = (theme_name == "dark")
        self.tab_bar.configure(bg=theme["tab_bar_bg"])
        self.footer.configure(bg=theme["table_heading_bg"])
        self.stripe.configure(bg=styles.COLOR_PRIMARY)
        styles.retheme_button(self.close_btn)
        for frame in self._tab_frames.values():
            frame.configure(bg=styles.COLOR_BG)
            for child in frame.winfo_children():
                try:
                    child.configure(bg=styles.COLOR_BG)
                except Exception:
                    pass

        self.light_btn.config(
            bg=styles.COLOR_PRIMARY if not is_dark else styles.COLOR_BORDER,
            fg="#FFFFFF" if not is_dark else styles.COLOR_TEXT
        )
        self.dark_btn.config(
            bg=styles.COLOR_PRIMARY if is_dark else styles.COLOR_BORDER,
            fg="#0A0A0C" if is_dark else styles.COLOR_TEXT
        )
        self._switch_tab(self._active_tab or "general")

    def _build_keyboard(self, frame: tk.Frame) -> None:
        self._section(frame, "Keyboard Shortcuts")
        shortcuts = [
            ("Ctrl + S",  "Calculate BMI and Save record"),
            ("Ctrl + N",  "Clear form and deselect record"),
            ("Delete",    "Delete selected record"),
            ("Return",    "Submit form (when inside a field)"),
            ("Tab",       "Move focus to next field"),
            ("Shift+Tab", "Move focus to previous field"),
            ("Escape",    "Close any open dialog"),
        ]
        for keys, desc in shortcuts:
            row = tk.Frame(frame, bg=styles.COLOR_BG)
            row.pack(fill=tk.X, pady=3)
            key_lbl = tk.Label(row, text=keys,
                               bg=styles.COLOR_BORDER, fg=styles.COLOR_TEXT,
                               font=styles.get_font(9, "bold"),
                               padx=8, pady=2, relief="flat")
            key_lbl.pack(side=tk.LEFT)
            tk.Label(row, text=f"  {desc}", bg=styles.COLOR_BG, fg=styles.COLOR_TEXT,
                     font=styles.get_font(9)).pack(side=tk.LEFT)

    def _build_about(self, frame: tk.Frame) -> None:
        self._section(frame, "About FitTrack Enterprise")
        about_rows = [
            ("Author",    "vasiharan"),
            ("License",   "MIT License"),
            ("Copyright", "© 2026 vasiharan"),
            ("Language",  "Python 3 + Tkinter + Matplotlib"),
            ("GitHub",    "github.com/vasiharan/fittrack"),
        ]
        for label, value in about_rows:
            self._row(frame, label, value)

        tk.Label(
            frame,
            text=(
                "\nFitTrack Enterprise is a health record management desktop\n"
                "application for tracking BMI history across multiple users.\n"
                "Built with a fully modular MVC architecture."
            ),
            bg=styles.COLOR_BG, fg=styles.COLOR_TEXT_MUTED,
            font=styles.get_font(9), justify=tk.LEFT,
            wraplength=460,
        ).pack(anchor=tk.W, pady=(8, 0))
