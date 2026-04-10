"""
Output Visualizer — renders the output queue as horizontal token boxes.
"""
import tkinter as tk
from gui.styles import (
    BG_SURFACE, BORDER, TEXT_PRIMARY, TEXT_MUTED,
    QUEUE_COLOR, QUEUE_LAST_COLOR,
    FONT_MONO_LG, FONT_UI_SM, FONT_LABEL,
)


class OutputVisualizer(tk.Canvas):
    """
    A Canvas widget that renders a list of tokens as a horizontal queue.
    The most-recently-added token is highlighted in teal.
    """

    BOX_SIZE = 58
    GAP      = 8
    MARGIN_Y = 14

    def __init__(self, parent, **kwargs):
        opts = dict(bg=BG_SURFACE, highlightthickness=1,
                    highlightbackground=BORDER)
        opts.update(kwargs)
        super().__init__(parent, **opts)
        self._items = []
        self.bind("<Configure>", lambda _: self.render())

    # ── Public API ────────────────────────────────────────────────────────────

    def set_items(self, items: list):
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

        bs  = self.BOX_SIZE
        gap = self.GAP
        total_w = len(items) * (bs + gap) - gap
        start_x = max(self.GAP, (w - total_w) // 2)
        y0 = (h - bs) // 2

        for i, token in enumerate(items):
            x0 = start_x + i * (bs + gap)
            is_last = (i == len(items) - 1)
            fill = QUEUE_LAST_COLOR if is_last else QUEUE_COLOR

            # Shadow
            self.create_rectangle(
                x0 + 3, y0 + 3, x0 + bs + 3, y0 + bs + 3,
                fill="#000000", outline="", stipple="gray25",
            )
            # Box
            self.create_rectangle(
                x0, y0, x0 + bs, y0 + bs,
                fill=fill, outline=BORDER, width=1,
            )
            # Token text
            self.create_text(
                x0 + bs // 2, y0 + bs // 2,
                text=str(token),
                font=FONT_MONO_LG,
                fill="#000000" if is_last else TEXT_PRIMARY,
            )

            # Index label beneath
            self.create_text(
                x0 + bs // 2, y0 + bs + 10,
                text=str(i),
                font=FONT_LABEL,
                fill=TEXT_MUTED,
            )

            # Arrow between boxes
            if i < len(items) - 1:
                ax = x0 + bs + gap // 2
                self.create_text(
                    ax, y0 + bs // 2,
                    text="→",
                    font=FONT_LABEL,
                    fill=TEXT_MUTED,
                )

    def _draw_empty(self, w, h):
        self.create_text(
            w // 2, h // 2,
            text="[ empty ]",
            font=FONT_UI_SM,
            fill=TEXT_MUTED,
        )