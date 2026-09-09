"""
ui/table.py
===========
HealthRecordTable — a ttk.Treeview with scrollbars, column sorting,
alternating rows, and canvas-based empty states.
Theme-aware with dynamic theme updates.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional

from models.person import HealthRecord
from ui import styles


class HealthRecordTable(ttk.Frame):
    """
    Full-featured data table for HealthRecord objects.

    Features
    --------
    - Sortable columns (click header to toggle asc/desc)
    - Alternating row colours that survive sorting
    - Animated canvas empty states for 'no records' and 'no search results'
    - Single-select with select and double-click callbacks
    - Theme-aware styling for Light and Dark modes
    """

    COLUMNS = ("id", "name", "age", "gender", "height", "weight", "bmi", "status", "created_at")
    HEADERS = ("ID", "Name", "Age", "Gender", "Height (cm)", "Weight (kg)", "BMI", "Status", "Created")
    WIDTHS  = {"id": 45, "name": 150, "age": 55, "gender": 75,
               "height": 90, "weight": 90, "bmi": 75, "status": 105, "created_at": 145}

    def __init__(
        self,
        parent,
        on_select_callback: Optional[Callable[[HealthRecord], None]] = None,
        on_double_click_callback: Optional[Callable[[HealthRecord], None]] = None,
    ) -> None:
        super().__init__(parent)
        self.on_select = on_select_callback
        self.on_double_click = on_double_click_callback
        self._records_map: dict = {}       # item_id → HealthRecord
        self._current_state: str = ""
        self._empty_canvas: Optional[tk.Canvas] = None
        self._setup_ui()

    # ------------------------------------------------------------------
    # CONSTRUCTION
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            self,
            columns=self.COLUMNS,
            show="headings",
            selectmode="browse",
            height=8,
        )

        for col, header in zip(self.COLUMNS, self.HEADERS):
            self.tree.heading(
                col, text=header, anchor=tk.CENTER,
                command=lambda c=col: self._sort_column(c, False),
            )
            self.tree.column(
                col,
                width=self.WIDTHS.get(col, 100),
                minwidth=self.WIDTHS.get(col, 50),
                anchor=tk.W if col == "name" else tk.CENTER,
            )

        self.vsb = ttk.Scrollbar(self, orient="vertical",   command=self.tree.yview, style="Vertical.TScrollbar")
        self.hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview, style="Horizontal.TScrollbar")
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")

        # Alternating row tags
        self.apply_theme()

        self.tree.bind("<<TreeviewSelect>>", self._handle_select)
        self.tree.bind("<Double-1>",         self._handle_double_click)

    def apply_theme(self) -> None:
        """Update row colors and empty canvas to reflect current theme."""
        self.tree.tag_configure("even", background=styles.COLOR_TABLE_ALT, foreground=styles.COLOR_TEXT)
        self.tree.tag_configure("odd",  background=styles.COLOR_CARD,      foreground=styles.COLOR_TEXT)
        if self._empty_canvas:
            self._empty_canvas.configure(bg=styles.COLOR_CARD)
            self._redraw_empty(self._current_state)

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def populate(self, records: List[HealthRecord], is_search_filter: bool = False) -> None:
        """Clear and re-populate the table with new records."""
        self.tree.delete(*self.tree.get_children())
        self._records_map.clear()

        if not records:
            state = "no_search" if is_search_filter else "no_records"
            self._show_empty_state(state)
            return

        self._hide_empty_state()

        for idx, rec in enumerate(records):
            tag = "even" if idx % 2 == 0 else "odd"
            date_str = rec.created_at.split(".")[0].replace("T", " ") if rec.created_at else ""
            item_id = self.tree.insert(
                "", tk.END,
                values=(
                    rec.id,
                    rec.name,
                    rec.age,
                    rec.gender,
                    f"{rec.height:.1f}",
                    f"{rec.weight:.1f}",
                    f"{rec.bmi:.2f}",
                    rec.status,
                    date_str,
                ),
                tags=(tag,),
            )
            self._records_map[item_id] = rec

    def get_selected_record(self) -> Optional[HealthRecord]:
        """Return the HealthRecord for the currently highlighted row, or None."""
        sel = self.tree.selection()
        return self._records_map.get(sel[0]) if sel else None

    def select_record_by_id(self, record_id: int) -> None:
        """Highlight and scroll to the row matching record_id."""
        for item_id, rec in self._records_map.items():
            if rec.id == record_id:
                self.tree.selection_set(item_id)
                self.tree.see(item_id)
                break

    def clear_selection(self) -> None:
        """Remove any row highlight."""
        sel = self.tree.selection()
        if sel:
            self.tree.selection_remove(sel[0])

    # ------------------------------------------------------------------
    # SORTING
    # ------------------------------------------------------------------

    def _sort_column(self, col: str, reverse: bool) -> None:
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        try:
            items.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            items.sort(key=lambda t: t[0].lower(), reverse=reverse)
        for index, (_, k) in enumerate(items):
            self.tree.move(k, "", index)
        self.tree.heading(col, command=lambda: self._sort_column(col, not reverse))
        self._recolor_rows()

    def _recolor_rows(self) -> None:
        for idx, k in enumerate(self.tree.get_children("")):
            self.tree.item(k, tags=("even" if idx % 2 == 0 else "odd",))

    # ------------------------------------------------------------------
    # EVENT HANDLERS
    # ------------------------------------------------------------------

    def _handle_select(self, _event) -> None:
        if self.on_select:
            rec = self.get_selected_record()
            if rec:
                self.on_select(rec)

    def _handle_double_click(self, _event) -> None:
        if self.on_double_click:
            rec = self.get_selected_record()
            if rec:
                self.on_double_click(rec)

    # ------------------------------------------------------------------
    # EMPTY STATES
    # ------------------------------------------------------------------

    def _ensure_canvas(self) -> tk.Canvas:
        if self._empty_canvas is None:
            self._empty_canvas = tk.Canvas(
                self, bg=styles.COLOR_CARD, highlightthickness=0
            )
            self._empty_canvas.bind(
                "<Configure>",
                lambda _e: self._redraw_empty(self._current_state),
            )
        return self._empty_canvas

    def _show_empty_state(self, state: str) -> None:
        self._current_state = state
        self.tree.grid_remove()
        self.vsb.grid_remove()
        self.hsb.grid_remove()
        canvas = self._ensure_canvas()
        canvas.configure(bg=styles.COLOR_CARD)
        canvas.grid(row=0, column=0, columnspan=2, rowspan=2, sticky="nsew")
        self._redraw_empty(state)

    def _hide_empty_state(self) -> None:
        if self._empty_canvas:
            self._empty_canvas.grid_remove()
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")

    def _redraw_empty(self, state: str) -> None:
        canvas = self._ensure_canvas()
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 10 or h < 10:
            return
        cx, cy = w // 2, h // 2

        if state == "no_records":
            self._draw_clipboard(canvas, cx, cy)
        else:
            self._draw_magnifier(canvas, cx, cy)

    def _draw_clipboard(self, canvas: tk.Canvas, cx: int, cy: int) -> None:
        """Vector clipboard illustration for the 'no records' state."""
        is_dark = (styles.CURRENT_THEME == "dark")
        body_bg = "#1F1F26" if is_dark else "#F7F2EA"
        border_c = styles.COLOR_PRIMARY if is_dark else "#C59B27"
        line_c = styles.COLOR_BORDER

        canvas.create_rectangle(cx - 30, cy - 38, cx + 30, cy + 30,
                                 fill=body_bg, outline=border_c, width=2)
        canvas.create_rectangle(cx - 12, cy - 45, cx + 12, cy - 36,
                                 fill=border_c, outline=border_c, width=1)
        for offset in (-12, 0, 12):
            canvas.create_line(cx - 16, cy + offset, cx + 16, cy + offset,
                                fill=line_c, width=2)
        canvas.create_text(cx, cy - 58, text="📋", font=styles.get_font(20))
        canvas.create_text(cx, cy + 46,
                            text="No Health Records Yet",
                            font=styles.get_font(11, "bold"),
                            fill=styles.COLOR_TEXT)
        canvas.create_text(cx, cy + 66,
                            text="Create your first health record using the form on the left.",
                            font=styles.get_font(9),
                            fill=styles.COLOR_TEXT_MUTED)

    def _draw_magnifier(self, canvas: tk.Canvas, cx: int, cy: int) -> None:
        """Vector magnifier illustration for the 'no search results' state."""
        handle_c = styles.COLOR_PRIMARY
        canvas.create_oval(cx - 24, cy - 40, cx + 8, cy - 8,
                            outline=styles.COLOR_BORDER_FOCUS, width=3)
        canvas.create_line(cx + 6, cy - 10, cx + 22, cy + 6,
                            fill=handle_c, width=5, capstyle=tk.ROUND)
        canvas.create_text(cx + 20, cy - 42, text="🔍", font=styles.get_font(18))
        canvas.create_text(cx, cy + 28,
                            text="No matching records found",
                            font=styles.get_font(11, "bold"),
                            fill=styles.COLOR_TEXT)
        canvas.create_text(cx, cy + 48,
                            text="Check spelling or clear search filter to see all records.",
                            font=styles.get_font(9),
                            fill=styles.COLOR_TEXT_MUTED)
