"""
Expression Evaluator & Converter
Clean, modern design with proper visualization

Run: python src/main.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time

import sys
sys.path.insert(0, 'src')

from core.stack import Stack
from core.postfix_evaluator import PostfixEvaluator
from core.infix_converter import InfixConverter


class ExpressionEvaluator:
    """Main application for expression evaluation and conversion"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Expression Evaluator")
        self.root.geometry("900x700")
        self.root.configure(bg="#f5f5f5")
        
        # Application state
        self.stack = []
        self.output_queue = []
        self.steps = []
        self.current_step = 0
        self.animation_speed = 0.8
        
        # Variables
        self.input_type = tk.StringVar(value="infix")
        self.operation = tk.StringVar(value="evaluate")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # ===== HEADER (Smaller) =====
        header = tk.Frame(self.root, bg="#2c3e50", height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="Expression Evaluator",
            font=("Segoe UI", 16, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=12)
        
        # ===== INPUT SECTION =====
        input_section = tk.Frame(self.root, bg="#f5f5f5")
        input_section.pack(pady=15, padx=20, fill=tk.X)
        
        # Expression Entry
        tk.Label(
            input_section,
            text="Expression:",
            font=("Segoe UI", 10),
            bg="#f5f5f5"
        ).pack(anchor=tk.W)
        
        self.expression_entry = tk.Entry(
            input_section,
            font=("Consolas", 13),
            width=50
        )
        self.expression_entry.pack(fill=tk.X, pady=5)
        self.expression_entry.bind('<Return>', lambda e: self.execute())
        
        # ===== CONTROLS (Compact) =====
        controls = tk.Frame(self.root, bg="#f5f5f5")
        controls.pack(pady=10, padx=20, fill=tk.X)
        
        # Left: Input Type
        left = tk.LabelFrame(controls, text="Input Type", font=("Segoe UI", 9), bg="#f5f5f5")
        left.pack(side=tk.LEFT, padx=(0, 10))
        
        for text, val in [("Infix", "infix"), ("Postfix", "postfix"), ("Prefix", "prefix")]:
            tk.Radiobutton(left, text=text, variable=self.input_type, value=val,
                          font=("Segoe UI", 9), bg="#f5f5f5").pack(anchor=tk.W, padx=10, pady=2)
        
        # Middle: Operation
        middle = tk.LabelFrame(controls, text="Operation", font=("Segoe UI", 9), bg="#f5f5f5")
        middle.pack(side=tk.LEFT, padx=10)
        
        for text, val in [("Evaluate", "evaluate"), ("To Infix", "to_infix"), 
                         ("To Postfix", "to_postfix"), ("To Prefix", "to_prefix")]:
            tk.Radiobutton(middle, text=text, variable=self.operation, value=val,
                          font=("Segoe UI", 9), bg="#f5f5f5").pack(anchor=tk.W, padx=10, pady=2)
        
        # Right: Buttons
        right = tk.Frame(controls, bg="#f5f5f5")
        right.pack(side=tk.RIGHT)
        
        tk.Button(right, text="Execute", command=self.execute,
                 font=("Segoe UI", 10, "bold"), bg="#27ae60", fg="white",
                 padx=20, pady=8, cursor="hand2").pack(pady=2)
        
        self.step_btn = tk.Button(right, text="Next Step", command=self.next_step,
                                  font=("Segoe UI", 10), bg="#3498db", fg="white",
                                  padx=20, pady=8, cursor="hand2", state=tk.DISABLED)
        self.step_btn.pack(pady=2)
        
        tk.Button(right, text="Clear", command=self.clear_all,
                 font=("Segoe UI", 10), bg="#e74c3c", fg="white",
                 padx=20, pady=8, cursor="hand2").pack(pady=2)
        
        # ===== VISUALIZATION (Bigger) =====
        viz = tk.Frame(self.root, bg="#f5f5f5")
        viz.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Stack
        stack_frame = tk.LabelFrame(viz, text="Stack", font=("Segoe UI", 10, "bold"), bg="white")
        stack_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.stack_canvas = tk.Canvas(stack_frame, bg="white", highlightthickness=0)
        self.stack_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Output Queue
        output_frame = tk.LabelFrame(viz, text="Output Queue", font=("Segoe UI", 10, "bold"), bg="white")
        output_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.output_canvas = tk.Canvas(output_frame, bg="white", highlightthickness=0)
        self.output_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ===== LOG (Compact) =====
        log_frame = tk.LabelFrame(self.root, text="Steps", font=("Segoe UI", 10, "bold"), bg="white")
        log_frame.pack(pady=(10, 15), padx=20, fill=tk.BOTH)
        
        scroll = tk.Scrollbar(log_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame, height=8, font=("Consolas", 9),
                               bg="white", state=tk.DISABLED, yscrollcommand=scroll.set, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll.config(command=self.log_text.yview)
        
        # Tags
        self.log_text.tag_configure("step", foreground="#3498db")
        self.log_text.tag_configure("result", foreground="#27ae60", font=("Consolas", 9, "bold"))
        self.log_text.tag_configure("error", foreground="#e74c3c", font=("Consolas", 9, "bold"))
        
        # ===== RESULT =====
        self.result_label = tk.Label(self.root, text="", font=("Segoe UI", 14, "bold"),
                                     bg="#f5f5f5", fg="#27ae60")
        self.result_label.pack(pady=(0, 10))
        
        # Initial draw
        self.draw_stack()
        self.draw_output()
    
    def execute(self):
        """Execute the selected operation"""
        expression = self.expression_entry.get().strip()
        
        if not expression:
            messagebox.showwarning("Empty Input", "Please enter an expression!")
            return
        
        self.clear_all()
        
        input_type = self.input_type.get()
        operation = self.operation.get()
        
        try:
            if operation == "evaluate":
                self.evaluate_expression(expression, input_type)
            elif operation == "to_postfix":
                self.convert_to_postfix(expression, input_type)
            else:
                messagebox.showinfo("Coming Soon", f"{operation} is not yet implemented!")
        
        except Exception as e:
            self.add_log(f"Error: {str(e)}\n", "error")
            messagebox.showerror("Error", str(e))
    
    def evaluate_expression(self, expression, input_type):
        """Evaluate expression"""
        self.add_log(f"Evaluating {input_type} expression: {expression}\n", "step")
        
        # Convert to postfix if needed
        if input_type == "infix":
            converter = InfixConverter()
            postfix = converter.convert(expression)
            self.add_log(f"Converted to postfix: {postfix}\n", "step")
            expression = postfix
        elif input_type == "prefix":
            messagebox.showinfo("Info", "Prefix evaluation not yet implemented!")
            return
        
        # Evaluate
        evaluator = PostfixEvaluator()
        self.steps = list(evaluator.evaluate_step_by_step(expression))
        self.current_step = 0
        
        self.step_btn.config(state=tk.NORMAL)
        self.animate_evaluation()
    
    def convert_to_postfix(self, expression, input_type):
        """Convert to postfix"""
        self.add_log(f"Converting {input_type} to postfix: {expression}\n", "step")
        
        if input_type == "postfix":
            self.add_log("Already in postfix notation!\n", "result")
            return
        
        if input_type == "infix":
            converter = InfixConverter()
            self.steps = list(converter.convert_step_by_step(expression))
            self.current_step = 0
            
            self.step_btn.config(state=tk.NORMAL)
            self.animate_conversion()
        else:
            messagebox.showinfo("Info", "Prefix to Postfix not yet implemented!")
    
    def animate_evaluation(self):
        """Animate evaluation"""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            
            if 'stack_after' in step:
                self.stack = step['stack_after']
                self.draw_stack()
            
            self.add_log(f"{step['description']}\n", "step")
            
            self.current_step += 1
            self.root.after(int(self.animation_speed * 1000), self.animate_evaluation)
        else:
            if self.steps and 'result' in self.steps[-1]:
                result = self.steps[-1]['result']
                self.add_log(f"\nFinal Result: {result}\n", "result")
                self.result_label.config(text=f"Result: {result}", fg="#27ae60")
            self.step_btn.config(state=tk.DISABLED)
    
    def animate_conversion(self):
        """Animate conversion"""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            
            if 'operator_stack_after' in step:
                self.stack = step['operator_stack_after']
                self.draw_stack()
            
            if 'output_queue_after' in step:
                self.output_queue = step['output_queue_after']
                self.draw_output()
            
            self.add_log(f"{step['description']}\n", "step")
            
            self.current_step += 1
            self.root.after(int(self.animation_speed * 1000), self.animate_conversion)
        else:
            if self.steps and 'postfix' in self.steps[-1]:
                result = self.steps[-1]['postfix']
                self.add_log(f"\nPostfix Result: {result}\n", "result")
                self.result_label.config(text=f"Postfix: {result}", fg="#27ae60")
            self.step_btn.config(state=tk.DISABLED)
    
    def next_step(self):
        """Execute next step manually"""
        if self.operation.get() == "evaluate":
            if self.current_step < len(self.steps):
                step = self.steps[self.current_step]
                
                if 'stack_after' in step:
                    self.stack = step['stack_after']
                    self.draw_stack()
                
                self.add_log(f"{step['description']}\n", "step")
                self.current_step += 1
                
                if self.current_step >= len(self.steps):
                    if 'result' in self.steps[-1]:
                        result = self.steps[-1]['result']
                        self.add_log(f"\nFinal Result: {result}\n", "result")
                        self.result_label.config(text=f"Result: {result}", fg="#27ae60")
                    self.step_btn.config(state=tk.DISABLED)
        else:
            if self.current_step < len(self.steps):
                step = self.steps[self.current_step]
                
                if 'operator_stack_after' in step:
                    self.stack = step['operator_stack_after']
                    self.draw_stack()
                
                if 'output_queue_after' in step:
                    self.output_queue = step['output_queue_after']
                    self.draw_output()
                
                self.add_log(f"{step['description']}\n", "step")
                self.current_step += 1
                
                if self.current_step >= len(self.steps):
                    if 'postfix' in self.steps[-1]:
                        result = self.steps[-1]['postfix']
                        self.add_log(f"\nPostfix Result: {result}\n", "result")
                        self.result_label.config(text=f"Postfix: {result}", fg="#27ae60")
                    self.step_btn.config(state=tk.DISABLED)
    
    def draw_stack(self):
        """Draw stack visualization - vertical boxes from bottom to top"""
        self.stack_canvas.delete("all")
        
        width = self.stack_canvas.winfo_width()
        height = self.stack_canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        if not self.stack:
            self.stack_canvas.create_text(
                width // 2, height // 2,
                text="Empty",
                font=("Segoe UI", 12),
                fill="#95a5a6"
            )
            return
        
        # Draw stack from bottom to top
        box_width = min(150, width - 40)
        box_height = 60
        spacing = 5
        
        x = (width - box_width) // 2
        
        for i in range(len(self.stack)):
            # Position from bottom up
            y = height - 20 - ((i + 1) * (box_height + spacing))
            
            if y < 0:
                break
            
            value = self.stack[i]
            
            # Color - top element is different
            if i == len(self.stack) - 1:
                color = "#f39c12"
            else:
                color = "#3498db"
            
            # Draw box
            self.stack_canvas.create_rectangle(
                x, y, x + box_width, y + box_height,
                fill=color, outline="#2c3e50", width=2
            )
            
            # Draw value
            self.stack_canvas.create_text(
                x + box_width // 2, y + box_height // 2,
                text=str(value),
                font=("Consolas", 16, "bold"),
                fill="white"
            )
            
            # Label top
            if i == len(self.stack) - 1:
                self.stack_canvas.create_text(
                    x - 35, y + box_height // 2,
                    text="TOP →",
                    font=("Segoe UI", 9, "bold"),
                    fill="#f39c12"
                )
    
    def draw_output(self):
        """Draw output queue - horizontal boxes left to right"""
        self.output_canvas.delete("all")
        
        width = self.output_canvas.winfo_width()
        height = self.output_canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        if not self.output_queue:
            self.output_canvas.create_text(
                width // 2, height // 2,
                text="Empty",
                font=("Segoe UI", 12),
                fill="#95a5a6"
            )
            return
        
        # Draw queue horizontally
        box_size = 60
        spacing = 10
        
        total_width = len(self.output_queue) * (box_size + spacing)
        start_x = max(10, (width - total_width) // 2)
        y = (height - box_size) // 2
        
        for i, value in enumerate(self.output_queue):
            x = start_x + i * (box_size + spacing)
            
            # Draw box
            self.output_canvas.create_rectangle(
                x, y, x + box_size, y + box_size,
                fill="#9b59b6", outline="#2c3e50", width=2
            )
            
            # Draw value
            self.output_canvas.create_text(
                x + box_size // 2, y + box_size // 2,
                text=str(value),
                font=("Consolas", 14, "bold"),
                fill="white"
            )
    
    def add_log(self, message, tag="normal"):
        """Add to log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message, tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear_all(self):
        """Clear everything"""
        self.stack = []
        self.output_queue = []
        self.steps = []
        self.current_step = 0
        
        self.draw_stack()
        self.draw_output()
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.result_label.config(text="")
        self.step_btn.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = ExpressionEvaluator(root)
    root.mainloop()


if __name__ == "__main__":
    main()