"""
Stack Evaluator — Expression Evaluator & Converter
Run: python src/main.py
"""

import sys
import tkinter as tk
from tkinter import ttk

sys.path.insert(0, "src")

from core.stack import Stack
from core.postfix_evaluator import PostfixEvaluator
from core.prefix_evaluator import PrefixEvaluator
from core.infix_converter import InfixConverter
from core.postfix_converter import PostfixConverter
from core.expression_validator import ExpressionValidator
from utils.animations import StepAnimator

from gui.stack_visualizer import StackVisualizer
from gui.output_visualizer import OutputVisualizer
from gui.history_panel import HistoryPanel
import gui.styles as S


# ─────────────────────────────────────────────────────────────────────────────
# Controller  — all business logic, zero tk widgets
# ─────────────────────────────────────────────────────────────────────────────

class Controller:
    """
    Bridges the UI and the core algorithms.
    Builds a flat list of animation steps for any (input_type, operation) pair,
    then hands them to a StepAnimator.
    """

    # (input_type, operation) → method
    _DISPATCH = {
        ("infix",   "evaluate"):    "_infix_evaluate",
        ("infix",   "to_postfix"):  "_infix_to_postfix",
        ("infix",   "to_prefix"):   "_infix_to_prefix",
        ("infix",   "to_infix"):    "_infix_to_infix",

        ("postfix", "evaluate"):    "_postfix_evaluate",
        ("postfix", "to_infix"):    "_postfix_to_infix",
        ("postfix", "to_prefix"):   "_postfix_to_prefix",
        ("postfix", "to_postfix"):  "_postfix_to_postfix",

        ("prefix",  "evaluate"):    "_prefix_evaluate",
        ("prefix",  "to_postfix"):  "_prefix_to_postfix",
        ("prefix",  "to_infix"):    "_prefix_to_infix",
        ("prefix",  "to_prefix"):   "_prefix_to_prefix",
    }

    def run(self, input_type: str, operation: str, expression: str):
        """
        Execute the requested operation.

        Returns
        -------
        dict with keys:
            steps   : list[dict]   — animation steps
            result  : str          — final result string
            mode    : str          — 'evaluate' | 'convert'
        """
        key = (input_type, operation)
        method_name = self._DISPATCH.get(key)
        if not method_name:
            raise ValueError(f"Unsupported combination: {input_type} → {operation}")
        return getattr(self, method_name)(expression)

    # ── Infix ─────────────────────────────────────────────────────────────────

    def _infix_evaluate(self, expr):
        converter = InfixConverter()
        postfix   = converter.convert(expr)
        evaluator = PostfixEvaluator()
        steps     = list(evaluator.evaluate_step_by_step(postfix))
        result    = _fmt(steps[-1]["result"])
        return _pack(steps, result, "evaluate",
                     preamble=f"Infix → Postfix: {postfix}")

    def _infix_to_postfix(self, expr):
        converter = InfixConverter()
        steps     = list(converter.convert_step_by_step(expr))
        result    = steps[-1].get("postfix", "")
        return _pack(steps, result, "convert")

    def _infix_to_prefix(self, expr):
        # infix → postfix → prefix
        converter = InfixConverter()
        postfix   = converter.convert(expr)
        pc        = PostfixConverter()
        prefix    = pc.to_prefix(postfix)
        # Reuse postfix conversion steps for visualisation, override label
        steps     = list(converter.convert_step_by_step(expr))
        return _pack(steps, prefix, "convert",
                     preamble=f"Infix → Postfix → Prefix: {prefix}")

    def _infix_to_infix(self, expr):
        # normalise (re-tokenise round-trip)
        converter = InfixConverter()
        postfix   = converter.convert(expr)
        pc        = PostfixConverter()
        infix_out = pc.to_infix(postfix)
        steps     = list(converter.convert_step_by_step(expr))
        return _pack(steps, infix_out, "convert",
                     preamble="Already infix — normalised form shown")

    # ── Postfix ───────────────────────────────────────────────────────────────

    def _postfix_evaluate(self, expr):
        evaluator = PostfixEvaluator()
        steps     = list(evaluator.evaluate_step_by_step(expr))
        result    = _fmt(steps[-1]["result"])
        return _pack(steps, result, "evaluate")

    def _postfix_to_infix(self, expr):
        pc     = PostfixConverter()
        result = pc.to_infix(expr)
        # Build synthetic steps for log
        steps = _synthetic_steps(expr, result, "to_infix")
        return _pack(steps, result, "convert")

    def _postfix_to_prefix(self, expr):
        pc     = PostfixConverter()
        result = pc.to_prefix(expr)
        steps  = _synthetic_steps(expr, result, "to_prefix")
        return _pack(steps, result, "convert")

    def _postfix_to_postfix(self, expr):
        steps = _synthetic_steps(expr, expr, "to_postfix")
        return _pack(steps, expr, "convert",
                     preamble="Already in postfix notation")

    # ── Prefix ────────────────────────────────────────────────────────────────

    def _prefix_evaluate(self, expr):
        evaluator = PrefixEvaluator()
        steps     = list(evaluator.evaluate_step_by_step(expr))
        result    = _fmt(steps[-1]["result"])
        return _pack(steps, result, "evaluate")

    def _prefix_to_postfix(self, expr):
        evaluator = PrefixEvaluator()
        result    = evaluator.to_postfix(expr)
        steps     = _synthetic_steps(expr, result, "to_postfix")
        return _pack(steps, result, "convert")

    def _prefix_to_infix(self, expr):
        evaluator = PrefixEvaluator()
        result    = evaluator.to_infix(expr)
        steps     = _synthetic_steps(expr, result, "to_infix")
        return _pack(steps, result, "convert")

    def _prefix_to_prefix(self, expr):
        steps = _synthetic_steps(expr, expr, "to_prefix")
        return _pack(steps, expr, "convert",
                     preamble="Already in prefix notation")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _fmt(value) -> str:
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def _pack(steps, result, mode, preamble=""):
    return {"steps": steps, "result": result, "mode": mode, "preamble": preamble}


def _synthetic_steps(expr: str, result: str, op: str) -> list:
    """One-shot step list for operations that don't have sub-steps."""
    return [
        {
            "step_number": 1,
            "token": expr,
            "action": op,
            "description": f"{expr}  →  {result}",
            "stack_before": [],
            "stack_after": [],
            "operator_stack_before": [],
            "operator_stack_after": [],
            "output_queue_before": [],
            "output_queue_after": result.split(),
        },
        {
            "step_number": 2,
            "token": "END",
            "action": "complete",
            "description": f"Done. Result: {result}",
            "stack_before": [],
            "stack_after": [],
            "operator_stack_before": [],
            "operator_stack_after": [],
            "output_queue_before": result.split(),
            "output_queue_after": result.split(),
            "postfix": result,
            "result": result,
        },
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Application Window
# ─────────────────────────────────────────────────────────────────────────────

class App(tk.Tk):

    # Speed slider: maps 0–100 → ms delay
    SPEED_MIN_MS = 100
    SPEED_MAX_MS = 2000

    def __init__(self):
        super().__init__()
        self.title("Stack Evaluator")
        self.geometry("1100x720")
        self.minsize(900, 620)
        self.configure(bg=S.BG_DARK)

        self._controller = Controller()
        self._animator: StepAnimator | None = None
        self._result_data = None

        # State variables
        self._input_type = tk.StringVar(value="infix")
        self._operation  = tk.StringVar(value="evaluate")
        self._speed_var  = tk.IntVar(value=65)    # 0–100 slider position

        self._build_ui()
    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_body()

    def _build_header(self):
        bar = tk.Frame(self, bg=S.BG_PANEL, height=52)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        # Left: title
        tk.Label(
            bar,
            text="⚙  STACK EVALUATOR",
            font=("Segoe UI", 13, "bold"),
            bg=S.BG_PANEL, fg=S.AMBER,
            padx=20,
        ).pack(side=tk.LEFT, pady=14)

        # Right: subtitle
        tk.Label(
            bar,
            text="expression evaluator & converter",
            font=("Segoe UI", 9),
            bg=S.BG_PANEL, fg=S.TEXT_MUTED,
            padx=16,
        ).pack(side=tk.RIGHT, pady=14)

        # Separator
        tk.Frame(self, bg=S.AMBER, height=2).pack(fill=tk.X)

    def _build_body(self):
        # Outer: left content + right history sidebar
        outer = tk.Frame(self, bg=S.BG_DARK)
        outer.pack(fill=tk.BOTH, expand=True)

        # ── Left column ──
        left = tk.Frame(outer, bg=S.BG_DARK)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(14, 6), pady=12)

        self._build_input_row(left)
        self._build_controls_row(left)
        self._build_viz_row(left)
        self._build_log_row(left)
        self._build_result_row(left)

        # ── Right sidebar ──
        right = tk.Frame(outer, bg=S.BG_PANEL, width=210)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 0), pady=0)
        right.pack_propagate(False)

        self._history = HistoryPanel(
            right,
            on_select=lambda expr: (
                self._expression_var.set(expr),
                self._expr_entry.icursor(tk.END),
            ),
        )
        self._history.pack(fill=tk.BOTH, expand=True)

    def _build_input_row(self, parent):
        row = tk.Frame(parent, bg=S.BG_DARK)
        row.pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            row, text="EXPRESSION",
            font=("Segoe UI", 7, "bold"),
            bg=S.BG_DARK, fg=S.TEXT_MUTED,
        ).pack(anchor=tk.W)

        # Entry with coloured border frame trick
        border = tk.Frame(row, bg=S.AMBER, padx=1, pady=1)
        border.pack(fill=tk.X, pady=(2, 0))

        self._expression_var = tk.StringVar()
        self._expr_entry = tk.Entry(
            border,
            textvariable=self._expression_var,
            **S.ENTRY_OPTS,
            highlightthickness=0,
        )
        self._expr_entry.pack(fill=tk.X, ipady=6, padx=2, pady=1)
        self._expr_entry.bind("<Return>", lambda _: self._on_execute())
        self._expr_entry.focus_set()

    def _build_controls_row(self, parent):
        row = tk.Frame(parent, bg=S.BG_DARK)
        row.pack(fill=tk.X, pady=(0, 10))

        # ── Input type ──
        self._build_radio_group(
            row, "INPUT TYPE",
            [("Infix", "infix"), ("Postfix", "postfix"), ("Prefix", "prefix")],
            self._input_type,
        ).pack(side=tk.LEFT, padx=(0, 10))

        # ── Operation ──
        self._build_radio_group(
            row, "OPERATION",
            [("Evaluate", "evaluate"), ("→ Infix", "to_infix"),
             ("→ Postfix", "to_postfix"), ("→ Prefix", "to_prefix")],
            self._operation,
        ).pack(side=tk.LEFT, padx=(0, 10))

        # ── Buttons + speed ──
        btn_col = tk.Frame(row, bg=S.BG_DARK)
        btn_col.pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            btn_col, text="▶  Execute",
            command=self._on_execute, **S.BTN_PRIMARY,
        ).pack(fill=tk.X, pady=(0, 4))

        self._step_btn = tk.Button(
            btn_col, text="⏭  Next Step",
            command=self._on_next_step,
            state=tk.DISABLED, **S.BTN_SECONDARY,
        )
        self._step_btn.pack(fill=tk.X, pady=(0, 4))

        self._pause_btn = tk.Button(
            btn_col, text="⏸  Pause",
            command=self._on_pause_resume,
            state=tk.DISABLED, **S.BTN_SECONDARY,
        )
        self._pause_btn.pack(fill=tk.X, pady=(0, 4))

        tk.Button(
            btn_col, text="✕  Clear",
            command=self._on_clear, **S.BTN_DANGER,
        ).pack(fill=tk.X)

        # Speed slider
        spd_col = tk.Frame(row, bg=S.BG_DARK)
        spd_col.pack(side=tk.LEFT)

        tk.Label(
            spd_col, text="SPEED",
            font=("Segoe UI", 7, "bold"),
            bg=S.BG_DARK, fg=S.TEXT_MUTED,
        ).pack(anchor=tk.W)

        speed_slider = tk.Scale(
            spd_col,
            from_=0, to=100,
            orient=tk.HORIZONTAL,
            variable=self._speed_var,
            command=self._on_speed_change,
            showvalue=False,
            length=100,
            bg=S.BG_DARK, fg=S.AMBER,
            troughcolor=S.BG_SURFACE,
            highlightthickness=0,
            relief="flat",
        )
        speed_slider.pack()

        tk.Label(
            spd_col, textvariable=self._speed_label_var(),
            font=("Segoe UI", 7),
            bg=S.BG_DARK, fg=S.TEXT_MUTED,
        ).pack()

    def _build_viz_row(self, parent):
        row = tk.Frame(parent, bg=S.BG_DARK)
        row.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        # Stack panel
        sp = self._panel(row, "STACK")
        sp.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        self._stack_viz = StackVisualizer(sp, height=210)
        self._stack_viz.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Output queue panel
        op = self._panel(row, "OUTPUT QUEUE")
        op.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._output_viz = OutputVisualizer(op, height=210)
        self._output_viz.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def _build_log_row(self, parent):
        lp = self._panel(parent, "STEP LOG")
        lp.pack(fill=tk.X, pady=(0, 6))

        scroll = tk.Scrollbar(lp, bg=S.BG_PANEL)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._log = tk.Text(
            lp, height=7, state=tk.DISABLED,
            yscrollcommand=scroll.set,
            **S.LOG_OPTS,
        )
        self._log.pack(fill=tk.X, padx=6, pady=6)
        scroll.config(command=self._log.yview)

        for tag, cfg in S.LOG_TAGS.items():
            self._log.tag_configure(tag, **cfg)

    def _build_result_row(self, parent):
        row = tk.Frame(parent, bg=S.BG_DARK)
        row.pack(fill=tk.X)

        self._result_var = tk.StringVar()
        tk.Label(
            row,
            textvariable=self._result_var,
            font=("Cascadia Code", 15, "bold"),
            bg=S.BG_DARK, fg=S.GREEN,
            anchor="w",
        ).pack(side=tk.LEFT)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _panel(self, parent, title: str) -> tk.Frame:
        """Returns a styled LabelFrame-like panel."""
        outer = tk.Frame(parent, bg=S.BG_PANEL, padx=1, pady=1)
        tk.Label(
            outer, text=title,
            font=("Segoe UI", 7, "bold"),
            bg=S.BG_PANEL, fg=S.TEXT_MUTED,
            anchor="w", padx=6,
        ).pack(fill=tk.X)
        tk.Frame(outer, bg=S.BORDER, height=1).pack(fill=tk.X)
        return outer

    def _build_radio_group(self, parent, title, options, variable) -> tk.Frame:
        frame = tk.Frame(parent, bg=S.BG_DARK)
        tk.Label(
            frame, text=title,
            font=("Segoe UI", 7, "bold"),
            bg=S.BG_DARK, fg=S.TEXT_MUTED,
        ).pack(anchor=tk.W)
        for text, val in options:
            tk.Radiobutton(
                frame, text=text, variable=variable, value=val,
                **S.RADIO_OPTS,
            ).pack(anchor=tk.W)
        return frame

    def _speed_label_var(self):
        var = tk.StringVar(value="0.65 s")
        self._speed_str_var = var
        return var

    def _speed_ms(self) -> int:
        """Convert slider 0–100 to ms (inverted: higher slider = faster)."""
        pct = self._speed_var.get() / 100.0
        ms  = int(self.SPEED_MAX_MS - pct * (self.SPEED_MAX_MS - self.SPEED_MIN_MS))
        return ms

    # ── Event Handlers ────────────────────────────────────────────────────────

    def _on_speed_change(self, _=None):
        ms = self._speed_ms()
        secs = ms / 1000
        self._speed_str_var.set(f"{secs:.2f} s")
        if self._animator:
            self._animator.set_speed(ms)

    def _on_execute(self):
        expr = self._expression_var.get().strip()
        if not expr:
            self._log_write("Please enter an expression.\n", "error")
            return

        self._clear_visuals()

        input_type = self._input_type.get()
        operation  = self._operation.get()

        try:
            data = self._controller.run(input_type, operation, expr)
        except ValueError as e:
            self._log_write(f"Error: {e}\n", "error")
            self._history.add(input_type, operation, expr, str(e), ok=False)
            return

        self._result_data = data

        if data["preamble"]:
            self._log_write(data["preamble"] + "\n", "header")

        # Wire up the animator
        self._animator = StepAnimator(
            root=self,
            steps=data["steps"],
            on_step=self._on_step,
            on_done=self._on_done,
            speed_ms=self._speed_ms(),
            auto_play=True,
        )

        self._step_btn.config(state=tk.NORMAL)
        self._pause_btn.config(state=tk.NORMAL, text="⏸  Pause")
        self._result_var.set("")

        self._animator.start()

    def _on_step(self, step: dict, index: int):
        """Called by StepAnimator for each step."""
        mode = self._result_data["mode"] if self._result_data else "evaluate"

        # Update stack visualiser
        if "stack_after" in step and step["stack_after"] is not None:
            self._stack_viz.set_items(step["stack_after"])
        elif "operator_stack_after" in step and step["operator_stack_after"] is not None:
            self._stack_viz.set_items(step["operator_stack_after"])

        # Update output queue visualiser
        if "output_queue_after" in step and step["output_queue_after"] is not None:
            self._output_viz.set_items(step["output_queue_after"])

        # Log
        desc = step.get("description", "")
        if desc:
            action = step.get("action", "")
            tag = "push" if action == "push" else "pop" if action == "operate" else "step"
            step_num = step.get("step_number", index + 1)
            self._log_write(f"[{step_num:02d}] {desc}\n", tag)

    def _on_done(self):
        """Called when all steps are exhausted."""
        data = self._result_data
        if not data:
            return

        result = data["result"]
        mode   = data["mode"]

        if mode == "evaluate":
            self._result_var.set(f"  =  {result}")
            self._log_write(f"\n  Result: {result}\n", "result")
        else:
            label = {
                "to_infix":   "Infix",
                "to_postfix": "Postfix",
                "to_prefix":  "Prefix",
            }.get(self._operation.get(), "Output")
            self._result_var.set(f"  {label}: {result}")
            self._log_write(f"\n  {label}: {result}\n", "result")

        # History
        self._history.add(
            self._input_type.get(),
            self._operation.get(),
            self._expression_var.get().strip(),
            result,
            ok=True,
        )

        self._step_btn.config(state=tk.DISABLED)
        self._pause_btn.config(state=tk.DISABLED)

    def _on_next_step(self):
        if self._animator:
            self._animator.pause()
            self._animator.next_step()

    def _on_pause_resume(self):
        if not self._animator:
            return
        if self._animator._running:
            self._animator.pause()
            self._pause_btn.config(text="▶  Resume")
        else:
            self._animator.resume()
            self._pause_btn.config(text="⏸  Pause")

    def _on_clear(self):
        if self._animator:
            self._animator.pause()
            self._animator = None
        self._clear_visuals()
        self._result_var.set("")
        self._expression_var.set("")
        self._step_btn.config(state=tk.DISABLED)
        self._pause_btn.config(state=tk.DISABLED, text="⏸  Pause")

    def _clear_visuals(self):
        self._stack_viz.clear()
        self._output_viz.clear()
        self._log.config(state=tk.NORMAL)
        self._log.delete("1.0", tk.END)
        self._log.config(state=tk.DISABLED)
        self._result_var.set("")

    def _log_write(self, text: str, tag: str = "step"):
        self._log.config(state=tk.NORMAL)
        self._log.insert(tk.END, text, tag)
        self._log.see(tk.END)
        self._log.config(state=tk.DISABLED)

def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()