"""
Stack Visualizer — draws the stack as vertical boxes, bottom-to-top.
"""
import tkinter as tk
from gui.styles import (
    BG_SURFACE, BORDER, TEXT_PRIMARY, TEXT_MUTED,
    STACK_COLORS, STACK_TOP_COLOR, AMBER,
    FONT_MONO_LG, FONT_UI_SM, FONT_LABEL,
)


class StackVisualizer(tk.Canvas):
    """
    A Canvas widget that renders a stack as stacked rectangles.
    Top of stack is highlighted in amber; rest fade through a blue gradient.
    """

    BOX_H    = 52
    BOX_W    = 130
    GAP      = 6
    MARGIN_X = 20
    MARGIN_Y = 16

    def __init__(self, parent, **kwargs):
        opts = dict(bg=BG_SURFACE, highlightthickness=1,
                    highlightbackground=BORDER)
        opts.update(kwargs)
        super().__init__(parent, **opts)
        self._items = []
        self.bind("<Configure>", lambda _: self.render())

    # ── Public API ────────────────────────────────────────────────────────────

    def set_items(self, items: list):
        """Update the stack contents and redraw."""
        self._items = list(items)
        self.render()

    def clear(self):
        self._items = []
        self.render()

    # ── Rendering ────────────────────────────────────────────────────────────

    def render(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1 or h <= 1:
            return

        items = self._items
        if not items:
            self._draw_empty(w, h)
            return

        bw = min(self.BOX_W, w - self.MARGIN_X * 2)
        bh = self.BOX_H
        gap = self.GAP
        x0 = (w - bw) // 2

        # Draw from bottom (index 0) to top (index -1)
        for i, value in enumerate(items):
            y_bottom = h - self.MARGIN_Y - (i) * (bh + gap)
            y_top    = y_bottom - bh

            if y_top < self.MARGIN_Y:
                # Stack overflows canvas — draw a "…" indicator and stop
                self.create_text(
                    w // 2, self.MARGIN_Y + 10,
                    text="↑  more  ↑",
                    font=FONT_LABEL,
                    fill=TEXT_MUTED,
                )
                break

            is_top = (i == len(items) - 1)
            fill   = STACK_TOP_COLOR if is_top else STACK_COLORS[i % len(STACK_COLORS)]
            text_c = "#000000" if is_top else TEXT_PRIMARY

            # Shadow
            self.create_rectangle(
                x0 + 3, y_top + 3, x0 + bw + 3, y_bottom + 3,
                fill="#000000", outline="", stipple="gray25",
            )
            # Box
            self.create_rectangle(
                x0, y_top, x0 + bw, y_bottom,
                fill=fill, outline=BORDER, width=1,
            )
            # Value
            label = self._fmt(value)
            self.create_text(
                x0 + bw // 2, (y_top + y_bottom) // 2,
                text=label,
                font=FONT_MONO_LG,
                fill=text_c,
            )

            # "TOP" badge
            if is_top:
                self.create_text(
                    x0 - 6, (y_top + y_bottom) // 2,
                    text="▶",
                    font=FONT_LABEL,
                    fill=AMBER,
                    anchor="e",
                )

        # Axis line
        self.create_line(
            x0 - 12, h - self.MARGIN_Y,
            x0 - 12, self.MARGIN_Y,
            fill=BORDER, width=1, dash=(4, 4),
        )

    def _draw_empty(self, w, h):
        self.create_text(
            w // 2, h // 2,
            text="[ empty ]",
            font=FONT_UI_SM,
            fill=TEXT_MUTED,
        )

    @staticmethod
    def _fmt(value) -> str:
        if isinstance(value, float):
            return f"{value:g}"
        return str(value)