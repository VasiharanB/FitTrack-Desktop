"""
ui/gauge.py
===========
Glassmorphism Space Station — Biometric Orbital Components.

OrbitalBMISphere  : Glowing central orb with rotating orbit rings, pulsing
                    aurora glow, and a large BMI digital readout at center.
BiometricAvatar   : Holographic human silhouette with aurora scan beam.
"""

import math
import tkinter as tk
from typing import Optional
from ui import styles


class OrbitalBMISphere(tk.Canvas):
    """
    Glassmorphism Orbital BMI Sphere.

    Features:
    - Central glowing sphere with aurora color zones:
        Violet/Teal  (<18.5)  : Underweight
        Teal/Emerald (18.5-25): Normal / Optimal
        Amber        (25-30)  : Overweight
        Rose/Crimson (30+)    : Obese
    - 3 concentric elliptical orbit rings rotating at different velocities
    - Soft pulsing glow that breathes in/out using sine modulation
    - Large BMI value + status label drawn at center
    - Smooth ease-out BMI value animation
    """

    MIN_BMI = 12.0
    MAX_BMI = 42.0

    def __init__(
        self,
        parent: tk.Widget,
        width: int = 340,
        height: int = 240,
        initial_bmi: Optional[float] = None,
        **kwargs
    ) -> None:
        theme = styles.get_theme_dict()
        bg_color = kwargs.pop("bg", theme.get("card", "#0C1428"))
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=bg_color,
            highlightthickness=0,
            **kwargs
        )
        self.width  = width
        self.height = height

        self._current_bmi  = 22.0 if initial_bmi is None else float(initial_bmi)
        self._target_bmi   = self._current_bmi
        self._status_text  = "NORMAL"
        self._status_color = styles.AURORA_TEAL

        self._anim_job: Optional[str] = None
        self._orbit_job: Optional[str] = None
        self._pulse_job: Optional[str] = None

        # Orbital ring angles (each ring rotates at a different speed)
        self._ring_angles = [0.0, 120.0, 240.0]   # initial offset in degrees
        self._ring_speeds = [0.9, -0.6, 0.45]      # deg/frame (negative = reverse)

        # Pulse glow state
        self._pulse_t    = 0.0
        self._pulse_step = 0.06   # radians per frame

        self.bind("<Configure>", self._on_resize)
        self.after(60, self._start_animation)

    # ------------------------------------------------------------------
    # RESIZE
    # ------------------------------------------------------------------

    def _on_resize(self, event: tk.Event) -> None:
        if event.width > 20 and event.height > 20:
            self.width  = event.width
            self.height = event.height
            self._render()

    # ------------------------------------------------------------------
    # PUBLIC API — matches the old BiometricRadialGauge interface
    # ------------------------------------------------------------------

    def set_bmi(self, bmi_val: float, status: str = "", animate: bool = True) -> None:
        """Sets target BMI value and smoothly animates to it."""
        val = max(self.MIN_BMI, min(self.MAX_BMI, float(bmi_val)))
        self._target_bmi   = val
        self._status_text  = status.upper() if status else self._compute_status_text(val)
        self._status_color = self._get_color_for_bmi(val)

        if not animate:
            self._current_bmi = self._target_bmi
            self._render()
            return

        if self._anim_job:
            try:
                self.after_cancel(self._anim_job)
            except Exception:
                pass
            self._anim_job = None
        self._animate_value_step()

    def _get_color_for_bmi(self, bmi: float) -> str:
        """Returns aurora accent color for the given BMI category."""
        theme = styles.get_theme_dict()
        is_dark = (styles.CURRENT_THEME == "dark")
        if bmi < 18.5:
            return theme.get("hud_cyan", styles.AURORA_TEAL)
        elif bmi < 25.0:
            return theme.get("hud_green", styles.AURORA_TEAL)
        elif bmi < 30.0:
            return theme.get("hud_amber", styles.AURORA_AMBER)
        else:
            return theme.get("hud_crimson", "#F87171")

    def _compute_status_text(self, bmi: float) -> str:
        if bmi < 18.5:
            return "UNDERWEIGHT"
        elif bmi < 25.0:
            return "NORMAL"
        elif bmi < 30.0:
            return "OVERWEIGHT"
        else:
            return "OBESE"

    # ------------------------------------------------------------------
    # VALUE ANIMATION (ease-out)
    # ------------------------------------------------------------------

    def _animate_value_step(self) -> None:
        diff = self._target_bmi - self._current_bmi
        if abs(diff) < 0.06:
            self._current_bmi = self._target_bmi
            self._render()
            self._anim_job = None
            return

        step = diff * 0.18
        if abs(step) < 0.03:
            step = 0.03 if diff > 0 else -0.03

        self._current_bmi += step
        self._render()
        self._anim_job = self.after(16, self._animate_value_step)

    # ------------------------------------------------------------------
    # ORBITAL RING ANIMATION
    # ------------------------------------------------------------------

    def _start_animation(self) -> None:
        """Starts the continuous orbital ring + pulse animation loops."""
        self._orbit_tick()
        self._pulse_tick()

    def _orbit_tick(self) -> None:
        """Rotate orbit rings one step and re-render."""
        for i in range(len(self._ring_angles)):
            self._ring_angles[i] = (self._ring_angles[i] + self._ring_speeds[i]) % 360.0
        self._render()
        try:
            self._orbit_job = self.after(30, self._orbit_tick)
        except Exception:
            pass

    def _pulse_tick(self) -> None:
        """Advance the pulse phase one step (render is driven by orbit_tick)."""
        self._pulse_t += self._pulse_step
        try:
            self._pulse_job = self.after(30, self._pulse_tick)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # RENDER
    # ------------------------------------------------------------------

    def _render(self) -> None:
        """Full redraw of the orbital sphere."""
        self.delete("all")
        theme = styles.get_theme_dict()
        is_dark = (styles.CURRENT_THEME == "dark")

        w = self.width
        h = self.height
        cx = w / 2
        cy = h / 2 + 8

        # Base radius of the central orb
        base_r = min(w * 0.28, h * 0.40)

        # Pulse modulation: glow expands/contracts softly
        pulse_factor = 1.0 + 0.06 * math.sin(self._pulse_t)
        glow_r = base_r * pulse_factor

        # Active category color
        active_col = self._status_color

        # --- Background gradient rings (soft glow layers behind orb) ---
        for layer, alpha_mult in [(3.2, 0.07), (2.5, 0.12), (2.0, 0.18), (1.55, 0.28)]:
            rr = int(glow_r * layer)
            glow_color = self._blend_with_bg(active_col, alpha_mult, theme.get("card", "#0C1428"))
            self.create_oval(
                cx - rr, cy - rr, cx + rr, cy + rr,
                fill=glow_color, outline=""
            )

        # --- Orbit ring ellipses (3 rings, different tilt/speed) ---
        ring_configs = [
            # (rx_scale, ry_scale, color, width, dash)
            (glow_r * 1.82, glow_r * 0.55,  active_col, 1, (6, 5)),
            (glow_r * 1.50, glow_r * 0.42,  styles.AURORA_VIOLET if is_dark else "#7C3AED", 1, (4, 6)),
            (glow_r * 1.22, glow_r * 0.32,  styles.AURORA_TEAL   if is_dark else "#0891B2", 1, (3, 7)),
        ]
        for idx, (rx, ry, col, lw, dash) in enumerate(ring_configs):
            self._draw_orbit_ring(cx, cy, rx, ry, self._ring_angles[idx], col, lw, dash)

        # --- Central orb fill (multi-stop radial gradient simulation) ---
        # Outermost layer (full orb, slightly desaturated)
        orb_shadow = self._blend_with_bg(active_col, 0.40, theme.get("card", "#0C1428"))
        self.create_oval(
            cx - base_r, cy - base_r, cx + base_r, cy + base_r,
            fill=orb_shadow, outline=active_col, width=2
        )

        # Mid layer
        mid_r = base_r * 0.72
        orb_mid = self._blend_with_bg(active_col, 0.65, theme.get("card", "#0C1428"))
        self.create_oval(
            cx - mid_r, cy - mid_r, cx + mid_r, cy + mid_r,
            fill=orb_mid, outline=""
        )

        # Core highlight (bright spot — simulates glass refraction)
        core_r = base_r * 0.38
        core_color = active_col
        self.create_oval(
            cx - core_r, cy - core_r, cx + core_r, cy + core_r,
            fill=core_color, outline=""
        )

        # Specular highlight dot (glass lens effect)
        spec_x = cx - base_r * 0.28
        spec_y = cy - base_r * 0.30
        spec_r = base_r * 0.12
        self.create_oval(
            spec_x - spec_r, spec_y - spec_r, spec_x + spec_r, spec_y + spec_r,
            fill="#FFFFFF", outline=""
        )

        # --- BMI Value at center ---
        bmi_font_size = max(18, int(base_r * 0.55))
        self.create_text(
            cx, cy - 5,
            text=f"{self._current_bmi:.1f}",
            font=(styles.FONT_FAMILY, bmi_font_size, "bold"),
            fill="#FFFFFF"
        )

        # --- Status label below orb ---
        status_y = cy + base_r + 16
        self.create_text(
            cx, status_y,
            text=f"● {self._status_text}",
            font=(styles.FONT_FAMILY, 9, "bold"),
            fill=active_col
        )

        # --- Top label ---
        label_col = styles.COLOR_TEXT_MUTED
        self.create_text(
            cx, cy - base_r - 14,
            text="BODY MASS INDEX",
            font=(styles.FONT_FAMILY, 8, "bold"),
            fill=label_col
        )

        # --- Glass corner brackets ---
        b_len = 10
        bracket_col = theme.get("glass_border", styles.COLOR_BORDER)
        self.create_line(4, 4 + b_len, 4, 4, 4 + b_len, 4,         fill=bracket_col, width=1)
        self.create_line(w - 4 - b_len, 4, w - 4, 4, w - 4, 4 + b_len,    fill=bracket_col, width=1)
        self.create_line(4, h - 4 - b_len, 4, h - 4, 4 + b_len, h - 4,    fill=bracket_col, width=1)
        self.create_line(w - 4 - b_len, h - 4, w - 4, h - 4, w - 4, h - 4 - b_len, fill=bracket_col, width=1)

        # Update canvas bg
        self.configure(bg=theme.get("card", "#0C1428"))

    def _draw_orbit_ring(
        self, cx: float, cy: float,
        rx: float, ry: float,
        angle_deg: float,
        color: str, width: int, dash: tuple
    ) -> None:
        """
        Draw an ellipse rotated by angle_deg around (cx,cy).
        Approximated using a polygon of 64 points.
        """
        points = []
        angle_rad = math.radians(angle_deg)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        steps = 64
        for i in range(steps):
            theta = 2 * math.pi * i / steps
            x0 = rx * math.cos(theta)
            y0 = ry * math.sin(theta)
            # Rotate
            x_rot = x0 * cos_a - y0 * sin_a
            y_rot = x0 * sin_a + y0 * cos_a
            points.extend([cx + x_rot, cy + y_rot])

        if len(points) >= 4:
            self.create_polygon(
                points,
                outline=color,
                fill="",
                width=width,
                smooth=True,
                dash=dash
            )

    @staticmethod
    def _blend_with_bg(hex_color: str, alpha: float, bg_hex: str) -> str:
        """Blend a hex color with a background at given alpha (0–1)."""
        try:
            fr, fg_c, fb = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
            br, bg_c, bb = int(bg_hex[1:3], 16),    int(bg_hex[3:5], 16),    int(bg_hex[5:7], 16)
            r = int(br + (fr - br) * alpha)
            g = int(bg_c + (fg_c - bg_c) * alpha)
            b = int(bb + (fb - bb) * alpha)
            r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return bg_hex


# Alias for backward compatibility with existing dashboard references
BiometricRadialGauge = OrbitalBMISphere


class BiometricAvatar(tk.Canvas):
    """
    Holographic Human Silhouette with Aurora Radar Scan Beam.
    Wireframe body with vital sensor beacons that change color
    to match the current BMI category.
    """

    def __init__(
        self,
        parent: tk.Widget,
        width: int = 120,
        height: int = 160,
        **kwargs
    ) -> None:
        theme = styles.get_theme_dict()
        bg_color = kwargs.pop("bg", theme.get("card", "#0C1428"))
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=bg_color,
            highlightthickness=0,
            **kwargs
        )
        self.width   = width
        self.height  = height
        self._scan_y = 20.0
        self._scan_dir = 2.2
        self._status_color = styles.AURORA_TEAL
        self._scan_job: Optional[str] = None

        self.bind("<Configure>", self._on_resize)
        self.after(60, self._start_scan)

    def _on_resize(self, event: tk.Event) -> None:
        if event.width > 10 and event.height > 10:
            self.width  = event.width
            self.height = event.height

    def set_status_color(self, color: str) -> None:
        self._status_color = color
        self._draw_frame()

    def _start_scan(self) -> None:
        self._scan_tick()

    def _scan_tick(self) -> None:
        self._scan_y += self._scan_dir
        h = self.height
        if self._scan_y > h - 20:
            self._scan_dir = -2.2
        elif self._scan_y < 20:
            self._scan_dir = 2.2
        self._draw_frame()
        try:
            self._scan_job = self.after(28, self._scan_tick)
        except Exception:
            pass

    def _draw_frame(self) -> None:
        """Redraw the holographic avatar for the current scan position."""
        self.delete("all")
        theme = styles.get_theme_dict()
        is_dark = (styles.CURRENT_THEME == "dark")
        w = self.width
        h = self.height
        cx = w / 2

        bg = theme.get("card", "#0C1428")
        self.configure(bg=bg)

        # Body color (dim wireframe)
        body_col = theme.get("glass_border", "#2A3A5E")
        active_col = self._status_color

        # Scale factors
        sy = h / 160.0
        sx = w / 120.0

        # Head circle
        hx, hy, hr = cx, 20 * sy, 13 * min(sx, sy)
        self.create_oval(hx - hr, hy - hr, hx + hr, hy + hr,
                         outline=body_col, fill="", width=1)

        # Body (torso trapezoid)
        torso_pts = [
            cx - 16*sx, 36*sy,
            cx + 16*sx, 36*sy,
            cx + 13*sx, 80*sy,
            cx - 13*sx, 80*sy,
        ]
        self.create_polygon(torso_pts, outline=body_col, fill="", width=1)

        # Arms
        self.create_line(cx - 16*sx, 36*sy, cx - 28*sx, 60*sy, fill=body_col, width=1)
        self.create_line(cx - 28*sx, 60*sy, cx - 22*sx, 80*sy, fill=body_col, width=1)
        self.create_line(cx + 16*sx, 36*sy, cx + 28*sx, 60*sy, fill=body_col, width=1)
        self.create_line(cx + 28*sx, 60*sy, cx + 22*sx, 80*sy, fill=body_col, width=1)

        # Legs
        self.create_line(cx - 6*sx, 80*sy, cx - 10*sx, 120*sy, fill=body_col, width=1)
        self.create_line(cx - 10*sx, 120*sy, cx - 8*sx, 148*sy, fill=body_col, width=1)
        self.create_line(cx + 6*sx, 80*sy, cx + 10*sx, 120*sy, fill=body_col, width=1)
        self.create_line(cx + 10*sx, 120*sy, cx + 8*sx, 148*sy, fill=body_col, width=1)

        # Vital sensor beacons
        beacons = [
            (cx, 36*sy),   # Chest
            (cx, 58*sy),   # Abdomen
            (cx, 76*sy),   # Pelvis
        ]
        for bx, by in beacons:
            br = 3 * min(sx, sy)
            self.create_oval(bx - br, by - br, bx + br, by + br,
                             fill=active_col, outline=active_col, width=1)

        # Aurora scan beam (horizontal line)
        scan_y_pos = max(15, min(h - 15, self._scan_y))
        scan_alpha_col = self._alpha_blend(active_col, bg, 0.55)
        self.create_line(4, scan_y_pos, w - 4, scan_y_pos,
                         fill=scan_alpha_col, width=1)

        # Scan label
        self.create_text(cx, h - 9,
                         text="BIO-SCAN // ACTIVE",
                         font=(styles.FONT_FAMILY, 7, "bold"),
                         fill=body_col)

        # Corner micro-brackets
        b = 6
        self.create_line(2, 2 + b, 2, 2, 2 + b, 2, fill=body_col, width=1)
        self.create_line(w - 2 - b, 2, w - 2, 2, w - 2, 2 + b, fill=body_col, width=1)
        self.create_line(2, h - 2 - b, 2, h - 2, 2 + b, h - 2, fill=body_col, width=1)
        self.create_line(w - 2 - b, h - 2, w - 2, h - 2, w - 2, h - 2 - b, fill=body_col, width=1)

    @staticmethod
    def _alpha_blend(hex_color: str, bg_hex: str, alpha: float) -> str:
        try:
            fr, fg_c, fb = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
            br, bg_c, bb = int(bg_hex[1:3], 16),    int(bg_hex[3:5], 16),    int(bg_hex[5:7], 16)
            r = int(br + (fr - br) * alpha)
            g = int(bg_c + (fg_c - bg_c) * alpha)
            b = int(bb + (fb - bb) * alpha)
            r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color
