"""
History Panel — keeps a scrollable record of past operations.
"""
import tkinter as tk
from gui.styles import (
    BG_PANEL, BG_SURFACE, BORDER, TEXT_PRIMARY, TEXT_MUTED,
    AMBER, GREEN, RED, TEAL,
    FONT_MONO_SM, FONT_UI_SM, FONT_LABEL,
)


class HistoryPanel(tk.Frame):
    """
    Scrollable history list.  Each entry shows:
      [input type]  expression  →  result
    Clicking an entry fires an optional callback with the expression string.
    """

    MAX_ENTRIES = 50

    def __init__(self, parent, on_select=None, **kwargs):
        opts = dict(bg=BG_PANEL)
        opts.update(kwargs)
        super().__init__(parent, **opts)

        self._on_select = on_select
        self._entries   = []        # list of dicts

        self._build()

    # ── Public API ────────────────────────────────────────────────────────────

    def add(self, input_type: str, operation: str, expression: str, result: str, ok: bool = True):
        """Prepend a new history entry."""
        entry = dict(
            input_type=input_type,
            operation=operation,
            expression=expression,
            result=result,
            ok=ok,
        )
        self._entries.insert(0, entry)
        if len(self._entries) > self.MAX_ENTRIES:
            self._entries.pop()
        self._refresh()

    def clear(self):
        self._entries.clear()
        self._refresh()

    # ── Internal ─────────────────────────────────────────────────────────────

    def _build(self):
        header = tk.Label(
            self, text="HISTORY",
            font=("Segoe UI", 8, "bold"),
            bg=BG_PANEL, fg=TEXT_MUTED,
            anchor="w", padx=8, pady=4,
        )
        header.pack(fill=tk.X)

        # Scrollable inner area
        container = tk.Frame(self, bg=BG_PANEL)
        container.pack(fill=tk.BOTH, expand=True)

        self._canvas = tk.Canvas(container, bg=BG_PANEL,
                                 highlightthickness=0, bd=0)
        self._scrollbar = tk.Scrollbar(container, orient="vertical",
                                       command=self._canvas.yview)
        self._inner = tk.Frame(self._canvas, bg=BG_PANEL)

        self._inner.bind(
            "<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")
            )
        )

        self._canvas.create_window((0, 0), window=self._inner, anchor="nw")
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Mouse-wheel scrolling
        self._canvas.bind_all("<MouseWheel>",
                              lambda e: self._canvas.yview_scroll(
                                  int(-1 * e.delta / 120), "units"))

    def _refresh(self):
        for widget in self._inner.winfo_children():
            widget.destroy()

        for entry in self._entries:
            self._make_row(entry)

        if not self._entries:
            tk.Label(
                self._inner,
                text="No history yet",
                font=FONT_UI_SM,
                bg=BG_PANEL, fg=TEXT_MUTED,
                pady=16,
            ).pack(fill=tk.X)

    def _make_row(self, entry: dict):
        row = tk.Frame(self._inner, bg=BG_SURFACE, cursor="hand2")
        row.pack(fill=tk.X, padx=6, pady=2)

        badge_color = AMBER if entry['ok'] else RED
        badge = tk.Label(
            row,
            text=f" {entry['input_type'].upper()} ",
            font=FONT_LABEL,
            bg=badge_color, fg="#000000",
            padx=2,
        )
        badge.pack(side=tk.LEFT, padx=(6, 4), pady=6)

        op_label = tk.Label(
            row,
            text=entry['operation'].replace('_', '→'),
            font=FONT_LABEL,
            bg=BG_SURFACE, fg=TEAL,
        )
        op_label.pack(side=tk.LEFT, padx=(0, 6))

        expr_label = tk.Label(
            row,
            text=entry['expression'],
            font=FONT_MONO_SM,
            bg=BG_SURFACE, fg=TEXT_PRIMARY,
            anchor="w",
        )
        expr_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        result_color = GREEN if entry['ok'] else RED
        res_label = tk.Label(
            row,
            text=f"= {entry['result']}" if entry['ok'] else entry['result'],
            font=FONT_MONO_SM,
            bg=BG_SURFACE, fg=result_color,
            padx=8,
        )
        res_label.pack(side=tk.RIGHT)

        # Click to re-use expression
        for widget in (row, badge, expr_label, res_label, op_label):
            widget.bind("<Button-1>", lambda e, ex=entry['expression']: self._click(ex))

    def _click(self, expression: str):
        if self._on_select:
            self._on_select(expression)