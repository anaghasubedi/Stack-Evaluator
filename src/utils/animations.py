"""
Animation helpers for the Stack Evaluator GUI.
All animations are driven by tkinter's .after() scheduler — no threads.
"""
from __future__ import annotations
from typing import Callable, Optional


class StepAnimator:
    """
    Drives step-by-step animation for evaluation / conversion.

    Usage
    -----
    animator = StepAnimator(root, steps, on_step, on_done, speed_ms=700)
    animator.start()       # begin auto-play
    animator.next_step()   # manual advance (also works mid-play)
    animator.pause()
    animator.resume()
    animator.reset()
    """

    MIN_SPEED_MS = 100
    MAX_SPEED_MS = 2000

    def __init__(
        self,
        root,
        steps: list,
        on_step: Callable[[dict, int], None],
        on_done: Callable[[], None],
        speed_ms: int = 700,
        auto_play: bool = True,
    ):
        self.root       = root
        self.steps      = steps
        self.on_step    = on_step
        self.on_done    = on_done
        self.speed_ms   = speed_ms
        self.auto_play  = auto_play

        self._index:    int           = 0
        self._running:  bool          = False
        self._after_id: Optional[str] = None

    # ── Public ───────────────────────────────────────────────────────────────

    def start(self):
        """Begin (or restart from current index) auto-play."""
        if self._running:
            return
        self._running = True
        self._schedule()

    def pause(self):
        self._running = False
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None

    def resume(self):
        if not self._running and self._index < len(self.steps):
            self.start()

    def reset(self):
        self.pause()
        self._index = 0

    def next_step(self):
        """Manually advance one step (cancels any scheduled auto-step)."""
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        self._execute_step()

    def set_speed(self, speed_ms: int):
        self.speed_ms = max(self.MIN_SPEED_MS,
                            min(self.MAX_SPEED_MS, speed_ms))

    @property
    def is_done(self) -> bool:
        return self._index >= len(self.steps)

    @property
    def current_index(self) -> int:
        return self._index

    # ── Internal ────────────────────────────────────────────────────────────

    def _schedule(self):
        if self._running and not self.is_done:
            self._after_id = self.root.after(self.speed_ms, self._tick)

    def _tick(self):
        self._after_id = None
        self._execute_step()
        if self._running and not self.is_done:
            self._schedule()

    def _execute_step(self):
        if self.is_done:
            self._running = False
            self.on_done()
            return

        step = self.steps[self._index]
        self.on_step(step, self._index)
        self._index += 1

        if self.is_done:
            self._running = False
            self.on_done()


def flash_widget(widget, flash_color: str, original_color: str,
                 duration_ms: int = 300, root=None):
    """
    Briefly change a widget's background colour then restore it.
    Useful for highlighting a canvas element on change.
    """
    widget.configure(bg=flash_color)
    _root = root or widget
    _root.after(duration_ms, lambda: widget.configure(bg=original_color))