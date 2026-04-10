"""
MainWindow — the top-level Tk window for the Stack Evaluator.

main.py becomes:
    from gui.main_window import MainWindow
    MainWindow().mainloop()
"""

import tkinter as tk

from core.postfix_evaluator import PostfixEvaluator
from core.prefix_evaluator  import PrefixEvaluator
from core.infix_converter   import InfixConverter
from core.prefix_converter  import PrefixConverter
from core.postfix_converter import PostfixConverter
from utils.animations       import StepAnimator

from gui.stack_visualizer  import StackVisualizer
from gui.output_visualizer import OutputVisualizer
from gui.history_panel     import HistoryPanel
import gui.styles as S


# ─────────────────────────────────────────────────────────────────────────────
# Controller  (pure logic, no widgets)
# ─────────────────────────────────────────────────────────────────────────────

class _Controller:
    """
    Maps every (input_type, operation) pair to a list of animation steps
    plus a final result string and a mode tag ('evaluate' | 'convert').
    """

    def run(self, input_type: str, operation: str, expression: str) -> dict:
        method = f"_{input_type}_{operation}"
        fn = getattr(self, method, None)
        if fn is None:
            raise ValueError(f"Unsupported: {input_type} → {operation}")
        return fn(expression)

    # ── infix ─────────────────────────────────────────────────────────────────

    def _infix_evaluate(self, expr):
        ic      = InfixConverter()
        postfix = ic.convert(expr)
        ev      = PostfixEvaluator()
        steps   = list(ev.evaluate_step_by_step(postfix))
        return _pack(steps, _fmt(steps[-1]["result"]), "evaluate",
                     preamble=f"Infix → Postfix: {postfix}")

    def _infix_to_postfix(self, expr):
        ic    = InfixConverter()
        steps = list(ic.convert_step_by_step(expr))
        return _pack(steps, steps[-1].get("postfix", ""), "convert")

    def _infix_to_prefix(self, expr):
        pc    = PrefixConverter()
        steps = list(pc.from_infix_step_by_step(expr))
        return _pack(steps, steps[-1].get("prefix", ""), "convert")

    def _infix_to_infix(self, expr):
        # normalise via round-trip
        ic      = InfixConverter()
        postfix = ic.convert(expr)
        result  = PostfixConverter().to_infix(postfix)
        steps   = list(ic.convert_step_by_step(expr))
        return _pack(steps, result, "convert",
                     preamble="Normalised infix shown")

    # ── postfix ───────────────────────────────────────────────────────────────

    def _postfix_evaluate(self, expr):
        ev    = PostfixEvaluator()
        steps = list(ev.evaluate_step_by_step(expr))
        return _pack(steps, _fmt(steps[-1]["result"]), "evaluate")

    def _postfix_to_infix(self, expr):
        result = PostfixConverter().to_infix(expr)
        return _pack(_synthetic(expr, result, "to_infix"), result, "convert")

    def _postfix_to_prefix(self, expr):
        result = PrefixConverter().from_postfix(expr)
        return _pack(_synthetic(expr, result, "to_prefix"), result, "convert")

    def _postfix_to_postfix(self, expr):
        return _pack(_synthetic(expr, expr, "to_postfix"), expr, "convert",
                     preamble="Already postfix")

    # ── prefix ────────────────────────────────────────────────────────────────

    def _prefix_evaluate(self, expr):
        ev    = PrefixEvaluator()
        steps = list(ev.evaluate_step_by_step(expr))
        return _fmt_prefix_eval(steps)

    def _prefix_to_postfix(self, expr):
        result = PrefixEvaluator().to_postfix(expr)
        return _pack(_synthetic(expr, result, "to_postfix"), result, "convert")

    def _prefix_to_infix(self, expr):
        result = PrefixEvaluator().to_infix(expr)
        return _pack(_synthetic(expr, result, "to_infix"), result, "convert")

    def _prefix_to_prefix(self, expr):
        return _pack(_synthetic(expr, expr, "to_prefix"), expr, "convert",
                     preamble="Already prefix")


# ── module-level helpers ──────────────────────────────────────────────────────

def _fmt(value) -> str:
    return f"{value:g}" if isinstance(value, float) else str(value)


def _pack(steps, result, mode, preamble="") -> dict:
    return {"steps": steps, "result": result, "mode": mode, "preamble": preamble}


def _fmt_prefix_eval(steps) -> dict:
    last   = steps[-1]
    result = _fmt(last["result"])
    return _pack(steps, result, "evaluate")


def _synthetic(expr: str, result: str, op: str) -> list:
    """One-shot two-step list for operations with no sub-steps."""
    tokens = result.split()
    return [
        {
            "step_number": 1, "token": expr, "action": op,
            "description": f"{expr}  →  {result}",
            "stack_before": [], "stack_after": [],
            "operator_stack_before": [], "operator_stack_after": [],
            "output_queue_before": [], "output_queue_after": tokens,
        },
        {
            "step_number": 2, "token": "END", "action": "complete",
            "description": f"Done — result: {result}",
            "stack_before": [], "stack_after": [],
            "operator_stack_before": [], "operator_stack_after": [],
            "output_queue_before": tokens, "output_queue_after": tokens,
            "postfix": result, "prefix": result, "result": result,
        },
    ]


# ─────────────────────────────────────────────────────────────────────────────
# MainWindow
# ─────────────────────────────────────────────────────────────────────────────

class MainWindow(tk.Tk):
    """
    Top-level application window.
    Instantiate and call .mainloop() — that's all main.py needs to do.
    """

    _SPEED_MIN_MS = 100
    _SPEED_MAX_MS = 2000

    def __init__(self):
        super().__init__()
        self.title("Stack Evaluator")
        self.geometry("1150x740")
        self.minsize(900, 640)
        self.configure(bg=S.BG_DARK)

        self._ctrl:       _Controller       = _Controller()
        self._animator:   StepAnimator|None = None
        self._run_data:   dict|None         = None
        self._paused:     bool              = False

        # Tk variables
        self._input_type = tk.StringVar(value="infix")
        self._operation  = tk.StringVar(value="evaluate")
        self._expr_var   = tk.StringVar()
        self._speed_var  = tk.IntVar(value=65)
        self._speed_lbl  = tk.StringVar(value="0.65 s")
        self._result_var = tk.StringVar()

        self._build()

    # ─────────────────────────────────────────────────────────────────────────
    # UI construction
    # ─────────────────────────────────────────────────────────────────────────

    def _build(self):
        self._build_header()
        self._build_body()

    def _build_header(self):
        bar = tk.Frame(self, bg=S.BG_PANEL, height=52)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        tk.Label(bar, text="⚙  STACK EVALUATOR",
                 font=("Segoe UI", 13, "bold"),
                 bg=S.BG_PANEL, fg=S.AMBER, padx=20).pack(side=tk.LEFT, pady=14)

        tk.Label(bar, text="expression evaluator & converter",
                 font=("Segoe UI", 9),
                 bg=S.BG_PANEL, fg=S.TEXT_MUTED, padx=16).pack(side=tk.RIGHT, pady=14)

        tk.Frame(self, bg=S.AMBER, height=2).pack(fill=tk.X)

    def _build_body(self):
        outer = tk.Frame(self, bg=S.BG_DARK)
        outer.pack(fill=tk.BOTH, expand=True)

        # Left: main content
        left = tk.Frame(outer, bg=S.BG_DARK)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(14, 6), pady=12)

        self._build_input(left)
        self._build_controls(left)
        self._build_viz(left)
        self._build_log(left)
        self._build_result_bar(left)

        # Right: history sidebar
        right = tk.Frame(outer, bg=S.BG_PANEL, width=215)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)

        self._history = HistoryPanel(
            right,
            on_select=lambda expr: (
                self._expr_var.set(expr),
                self._entry.icursor(tk.END),
            ),
        )
        self._history.pack(fill=tk.BOTH, expand=True)

    def _build_input(self, parent):
        row = tk.Frame(parent, bg=S.BG_DARK)
        row.pack(fill=tk.X, pady=(0, 8))

        tk.Label(row, text="EXPRESSION",
                 font=("Segoe UI", 7, "bold"),
                 bg=S.BG_DARK, fg=S.TEXT_MUTED).pack(anchor=tk.W)

        border = tk.Frame(row, bg=S.AMBER, padx=1, pady=1)
        border.pack(fill=tk.X, pady=(2, 0))

        self._entry = tk.Entry(border, textvariable=self._expr_var,
                               **S.ENTRY_OPTS, highlightthickness=0)
        self._entry.pack(fill=tk.X, ipady=6, padx=2, pady=1)
        self._entry.bind("<Return>", lambda _: self._execute())
        self._entry.focus_set()

    def _build_controls(self, parent):
        row = tk.Frame(parent, bg=S.BG_DARK)
        row.pack(fill=tk.X, pady=(0, 10))

        self._radio_group(
            row, "INPUT TYPE",
            [("Infix", "infix"), ("Postfix", "postfix"), ("Prefix", "prefix")],
            self._input_type,
        ).pack(side=tk.LEFT, padx=(0, 10))

        self._radio_group(
            row, "OPERATION",
            [("Evaluate", "evaluate"), ("→ Infix", "to_infix"),
             ("→ Postfix", "to_postfix"), ("→ Prefix", "to_prefix")],
            self._operation,
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Buttons
        btn_col = tk.Frame(row, bg=S.BG_DARK)
        btn_col.pack(side=tk.LEFT, padx=(0, 14))

        tk.Button(btn_col, text="▶  Execute",
                  command=self._execute, **S.BTN_PRIMARY).pack(fill=tk.X, pady=(0, 4))

        self._step_btn = tk.Button(btn_col, text="⏭  Next Step",
                                   command=self._next_step,
                                   state=tk.DISABLED, **S.BTN_SECONDARY)
        self._step_btn.pack(fill=tk.X, pady=(0, 4))

        self._pause_btn = tk.Button(btn_col, text="⏸  Pause",
                                    command=self._toggle_pause,
                                    state=tk.DISABLED, **S.BTN_SECONDARY)
        self._pause_btn.pack(fill=tk.X, pady=(0, 4))

        tk.Button(btn_col, text="✕  Clear",
                  command=self._clear, **S.BTN_DANGER).pack(fill=tk.X)

        # Speed
        spd = tk.Frame(row, bg=S.BG_DARK)
        spd.pack(side=tk.LEFT)

        tk.Label(spd, text="SPEED", font=("Segoe UI", 7, "bold"),
                 bg=S.BG_DARK, fg=S.TEXT_MUTED).pack(anchor=tk.W)

        tk.Scale(spd, from_=0, to=100, orient=tk.HORIZONTAL,
                 variable=self._speed_var, command=self._on_speed,
                 showvalue=False, length=110,
                 bg=S.BG_DARK, fg=S.AMBER, troughcolor=S.BG_SURFACE,
                 highlightthickness=0, relief="flat").pack()

        tk.Label(spd, textvariable=self._speed_lbl,
                 font=("Segoe UI", 7),
                 bg=S.BG_DARK, fg=S.TEXT_MUTED).pack()

    def _build_viz(self, parent):
        row = tk.Frame(parent, bg=S.BG_DARK)
        row.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        sp = self._panel(row, "STACK")
        sp.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        self._stack_viz = StackVisualizer(sp, height=210)
        self._stack_viz.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        qp = self._panel(row, "OUTPUT QUEUE")
        qp.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._queue_viz = OutputVisualizer(qp, height=210)
        self._queue_viz.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def _build_log(self, parent):
        lp = self._panel(parent, "STEP LOG")
        lp.pack(fill=tk.X, pady=(0, 6))

        scroll = tk.Scrollbar(lp, bg=S.BG_PANEL)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._log = tk.Text(lp, height=7, state=tk.DISABLED,
                            yscrollcommand=scroll.set, **S.LOG_OPTS)
        self._log.pack(fill=tk.X, padx=6, pady=6)
        scroll.config(command=self._log.yview)

        for tag, cfg in S.LOG_TAGS.items():
            self._log.tag_configure(tag, **cfg)

    def _build_result_bar(self, parent):
        bar = tk.Frame(parent, bg=S.BG_DARK)
        bar.pack(fill=tk.X)
        tk.Label(bar, textvariable=self._result_var,
                 font=("Cascadia Code", 15, "bold"),
                 bg=S.BG_DARK, fg=S.GREEN, anchor="w").pack(side=tk.LEFT)

    # ─────────────────────────────────────────────────────────────────────────
    # Widget helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _panel(self, parent, title: str) -> tk.Frame:
        outer = tk.Frame(parent, bg=S.BG_PANEL, padx=1, pady=1)
        tk.Label(outer, text=title, font=("Segoe UI", 7, "bold"),
                 bg=S.BG_PANEL, fg=S.TEXT_MUTED,
                 anchor="w", padx=6).pack(fill=tk.X)
        tk.Frame(outer, bg=S.BORDER, height=1).pack(fill=tk.X)
        return outer

    def _radio_group(self, parent, title, options, variable) -> tk.Frame:
        frame = tk.Frame(parent, bg=S.BG_DARK)
        tk.Label(frame, text=title, font=("Segoe UI", 7, "bold"),
                 bg=S.BG_DARK, fg=S.TEXT_MUTED).pack(anchor=tk.W)
        for text, val in options:
            tk.Radiobutton(frame, text=text, variable=variable,
                           value=val, **S.RADIO_OPTS).pack(anchor=tk.W)
        return frame

    # ─────────────────────────────────────────────────────────────────────────
    # Speed
    # ─────────────────────────────────────────────────────────────────────────

    def _speed_ms(self) -> int:
        pct = self._speed_var.get() / 100.0
        return int(self._SPEED_MAX_MS
                   - pct * (self._SPEED_MAX_MS - self._SPEED_MIN_MS))

    def _on_speed(self, _=None):
        ms = self._speed_ms()
        self._speed_lbl.set(f"{ms/1000:.2f} s")
        if self._animator:
            self._animator.set_speed(ms)

    # ─────────────────────────────────────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────────────────────────────────────

    def _execute(self):
        expr = self._expr_var.get().strip()
        if not expr:
            self._log_write("Please enter an expression.\n", "error")
            return

        self._reset_visuals()

        input_type = self._input_type.get()
        operation  = self._operation.get()

        try:
            data = self._ctrl.run(input_type, operation, expr)
        except ValueError as e:
            self._log_write(f"Error: {e}\n", "error")
            self._history.add(input_type, operation, expr, str(e), ok=False)
            return

        self._run_data = data

        if data["preamble"]:
            self._log_write(data["preamble"] + "\n", "header")

        self._animator = StepAnimator(
            root=self,
            steps=data["steps"],
            on_step=self._on_step,
            on_done=self._on_done,
            speed_ms=self._speed_ms(),
        )
        self._paused = False
        self._step_btn.config(state=tk.NORMAL)
        self._pause_btn.config(state=tk.NORMAL, text="⏸  Pause")
        self._result_var.set("")
        self._animator.start()

    def _on_step(self, step: dict, _index: int):
        # Stack
        for key in ("stack_after", "operator_stack_after"):
            val = step.get(key)
            if val is not None:
                self._stack_viz.set_items(val)
                break

        # Queue
        val = step.get("output_queue_after")
        if val is not None:
            self._queue_viz.set_items(val)

        # Log
        desc   = step.get("description", "")
        action = step.get("action", "")
        tag    = ("push" if action == "push"
                  else "pop" if action == "operate"
                  else "token" if action in ("output_number",)
                  else "step")
        n = step.get("step_number", "?")
        if desc:
            self._log_write(f"[{n:02}] {desc}\n", tag)

    def _on_done(self):
        data = self._run_data
        if not data:
            return

        result    = data["result"]
        mode      = data["mode"]
        operation = self._operation.get()

        if mode == "evaluate":
            self._result_var.set(f"  =  {result}")
            self._log_write(f"\n  Result: {result}\n", "result")
        else:
            label = {"to_infix": "Infix", "to_postfix": "Postfix",
                     "to_prefix": "Prefix"}.get(operation, "Output")
            self._result_var.set(f"  {label}: {result}")
            self._log_write(f"\n  {label}: {result}\n", "result")

        self._history.add(
            self._input_type.get(), operation,
            self._expr_var.get().strip(), result, ok=True,
        )
        self._step_btn.config(state=tk.DISABLED)
        self._pause_btn.config(state=tk.DISABLED)

    def _next_step(self):
        if self._animator:
            self._animator.pause()
            self._paused = True
            self._pause_btn.config(text="▶  Resume")
            self._animator.next_step()

    def _toggle_pause(self):
        if not self._animator:
            return
        if not self._paused:
            self._animator.pause()
            self._paused = True
            self._pause_btn.config(text="▶  Resume")
        else:
            self._paused = False
            self._pause_btn.config(text="⏸  Pause")
            self._animator.resume()

    def _clear(self):
        if self._animator:
            self._animator.pause()
            self._animator = None
        self._reset_visuals()
        self._expr_var.set("")
        self._result_var.set("")
        self._step_btn.config(state=tk.DISABLED)
        self._pause_btn.config(state=tk.DISABLED, text="⏸  Pause")
        self._paused = False

    def _reset_visuals(self):
        self._stack_viz.clear()
        self._queue_viz.clear()
        self._log.config(state=tk.NORMAL)
        self._log.delete("1.0", tk.END)
        self._log.config(state=tk.DISABLED)
        self._result_var.set("")

    def _log_write(self, text: str, tag: str = "step"):
        self._log.config(state=tk.NORMAL)
        self._log.insert(tk.END, text, tag)
        self._log.see(tk.END)
        self._log.config(state=tk.DISABLED)