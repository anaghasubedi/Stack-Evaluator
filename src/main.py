"""
Universal Expression Evaluator & Converter
Supports: Prefix, Infix, Postfix
Operations: Evaluate, Convert between notations
With Step-by-Step Visualization

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
        self.root.title("Expression Evaluator & Converter")
        self.root.geometry("1100x850")
        self.root.configure(bg="#ecf0f1")
        
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
        """Setup the complete user interface"""
        
        # ===== HEADER =====
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=90)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="🧮 Expression Evaluator & Converter",
            font=("Arial", 26, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title.pack(pady=25)
        
        # ===== MAIN CONTROL PANEL =====
        control_panel = tk.Frame(self.root, bg="#ecf0f1")
        control_panel.pack(pady=20, padx=30, fill=tk.X)
        
        # LEFT SIDE: Input Expression
        left_panel = tk.Frame(control_panel, bg="#ecf0f1")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            left_panel,
            text="📝 Enter Expression:",
            font=("Arial", 13, "bold"),
            bg="#ecf0f1"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.expression_entry = tk.Entry(
            left_panel,
            font=("Arial", 16),
            width=40,
            relief=tk.SOLID,
            bd=2
        )
        self.expression_entry.pack(fill=tk.X, pady=5)
        self.expression_entry.insert(0, "(5 + 3) * 2")
        self.expression_entry.bind('<Return>', lambda e: self.execute())
        
        # Examples
        examples_frame = tk.Frame(left_panel, bg="#ecf0f1")
        examples_frame.pack(anchor=tk.W, pady=5)
        
        tk.Label(
            examples_frame,
            text="Examples:",
            font=("Arial", 9, "bold"),
            bg="#ecf0f1",
            fg="#34495e"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            examples_frame,
            text="Infix: (3+5)*2",
            font=("Arial", 9),
            bg="#ecf0f1",
            fg="#7f8c8d"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            examples_frame,
            text="Postfix: 3 5 + 2 *",
            font=("Arial", 9),
            bg="#ecf0f1",
            fg="#7f8c8d"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            examples_frame,
            text="Prefix: * + 3 5 2",
            font=("Arial", 9),
            bg="#ecf0f1",
            fg="#7f8c8d"
        ).pack(side=tk.LEFT, padx=5)
        
        # RIGHT SIDE: Configuration
        right_panel = tk.LabelFrame(
            control_panel,
            text="⚙️ Configuration",
            font=("Arial", 11, "bold"),
            bg="#ffffff",
            padx=20,
            pady=15
        )
        right_panel.pack(side=tk.RIGHT, padx=(20, 0))
        
        # Input Type Selection
        tk.Label(
            right_panel,
            text="Input Type:",
            font=("Arial", 10, "bold"),
            bg="#ffffff"
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        input_types = [
            ("Infix (3 + 5)", "infix"),
            ("Postfix (3 5 +)", "postfix"),
            ("Prefix (+ 3 5)", "prefix")
        ]
        
        for i, (text, value) in enumerate(input_types):
            tk.Radiobutton(
                right_panel,
                text=text,
                variable=self.input_type,
                value=value,
                font=("Arial", 9),
                bg="#ffffff",
                cursor="hand2"
            ).grid(row=i+1, column=0, sticky=tk.W, padx=10)
        
        # Operation Selection
        tk.Label(
            right_panel,
            text="Operation:",
            font=("Arial", 10, "bold"),
            bg="#ffffff"
        ).grid(row=4, column=0, sticky=tk.W, pady=(15, 5))
        
        operations = [
            ("Evaluate", "evaluate"),
            ("Convert to Infix", "to_infix"),
            ("Convert to Postfix", "to_postfix"),
            ("Convert to Prefix", "to_prefix")
        ]
        
        for i, (text, value) in enumerate(operations):
            tk.Radiobutton(
                right_panel,
                text=text,
                variable=self.operation,
                value=value,
                font=("Arial", 9),
                bg="#ffffff",
                cursor="hand2"
            ).grid(row=i+5, column=0, sticky=tk.W, padx=10)
        
        # ===== ACTION BUTTONS =====
        button_frame = tk.Frame(self.root, bg="#ecf0f1")
        button_frame.pack(pady=15)
        
        tk.Button(
            button_frame,
            text="▶ Execute",
            command=self.execute,
            font=("Arial", 13, "bold"),
            bg="#27ae60",
            fg="white",
            padx=40,
            pady=12,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3
        ).pack(side=tk.LEFT, padx=8)
        
        self.step_btn = tk.Button(
            button_frame,
            text="⏭ Next Step",
            command=self.next_step,
            font=("Arial", 13, "bold"),
            bg="#3498db",
            fg="white",
            padx=40,
            pady=12,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3,
            state=tk.DISABLED
        )
        self.step_btn.pack(side=tk.LEFT, padx=8)
        
        tk.Button(
            button_frame,
            text="🔄 Clear All",
            command=self.clear_all,
            font=("Arial", 13, "bold"),
            bg="#e74c3c",
            fg="white",
            padx=40,
            pady=12,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3
        ).pack(side=tk.LEFT, padx=8)
        
        # ===== SPEED CONTROL =====
        speed_frame = tk.Frame(self.root, bg="#ecf0f1")
        speed_frame.pack(pady=5)
        
        tk.Label(
            speed_frame,
            text="⚡ Animation Speed:",
            font=("Arial", 10),
            bg="#ecf0f1"
        ).pack(side=tk.LEFT, padx=5)
        
        self.speed_var = tk.DoubleVar(value=0.8)
        tk.Scale(
            speed_frame,
            from_=0.2,
            to=2.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            length=250,
            bg="#ecf0f1",
            command=lambda v: setattr(self, 'animation_speed', float(v))
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            speed_frame,
            text="Fast ← → Slow",
            font=("Arial", 8, "italic"),
            bg="#ecf0f1",
            fg="#7f8c8d"
        ).pack(side=tk.LEFT, padx=5)
        
        # ===== VISUALIZATION AREA =====
        viz_container = tk.Frame(self.root, bg="#ecf0f1")
        viz_container.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)
        
        # Left: Stack Visualization
        stack_frame = tk.LabelFrame(
            viz_container,
            text="📚 Stack Visualization",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            padx=15,
            pady=15
        )
        stack_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.stack_canvas = tk.Canvas(
            stack_frame,
            bg="#f8f9fa",
            height=250,
            highlightthickness=2,
            highlightbackground="#bdc3c7"
        )
        self.stack_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Right: Output Visualization
        output_frame = tk.LabelFrame(
            viz_container,
            text="📋 Output Queue",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            padx=15,
            pady=15
        )
        output_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.output_canvas = tk.Canvas(
            output_frame,
            bg="#f8f9fa",
            height=250,
            highlightthickness=2,
            highlightbackground="#bdc3c7"
        )
        self.output_canvas.pack(fill=tk.BOTH, expand=True)
        
        # ===== STEP-BY-STEP LOG =====
        log_frame = tk.LabelFrame(
            self.root,
            text="📝 Step-by-Step Process",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            padx=10,
            pady=10
        )
        log_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scroll = tk.Scrollbar(log_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(
            log_frame,
            height=10,
            font=("Courier New", 10),
            bg="#fdfefe",
            state=tk.DISABLED,
            yscrollcommand=scroll.set,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.log_text.yview)
        
        # Configure text tags
        self.log_text.tag_configure("header", foreground="#2c3e50", font=("Courier New", 11, "bold"))
        self.log_text.tag_configure("step", foreground="#3498db", font=("Courier New", 10, "bold"))
        self.log_text.tag_configure("operation", foreground="#e67e22", font=("Courier New", 10))
        self.log_text.tag_configure("result", foreground="#27ae60", font=("Courier New", 11, "bold"))
        self.log_text.tag_configure("error", foreground="#e74c3c", font=("Courier New", 10, "bold"))
        
        # ===== RESULT DISPLAY =====
        self.result_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 18, "bold"),
            bg="#ecf0f1",
            fg="#27ae60",
            pady=10
        )
        self.result_label.pack()
        
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
            elif operation == "to_infix":
                self.convert_to_infix(expression, input_type)
            elif operation == "to_postfix":
                self.convert_to_postfix(expression, input_type)
            elif operation == "to_prefix":
                self.convert_to_prefix(expression, input_type)
        
        except Exception as e:
            self.add_log(f"\n❌ Error: {str(e)}\n", "error")
            messagebox.showerror("Error", str(e))
            self.result_label.config(text=f"❌ Error", fg="#e74c3c")
    
    def evaluate_expression(self, expression, input_type):
        """Evaluate expression based on input type"""
        self.add_log("="*60 + "\n", "header")
        self.add_log(f"EVALUATING {input_type.upper()} EXPRESSION\n", "header")
        self.add_log("="*60 + "\n\n", "header")
        self.add_log(f"Input: {expression}\n", "operation")
        self.add_log(f"Type: {input_type.upper()}\n\n", "operation")
        
        # Convert to postfix if needed
        if input_type == "infix":
            self.add_log("Step 1: Converting Infix to Postfix...\n", "step")
            converter = InfixConverter()
            postfix = converter.convert(expression)
            self.add_log(f"Postfix: {postfix}\n\n", "operation")
            expression = postfix
        elif input_type == "prefix":
            self.add_log("⚠️ Prefix evaluation not yet implemented\n", "error")
            self.add_log("Converting Prefix to Postfix first...\n\n", "operation")
            # TODO: Implement prefix to postfix conversion
            messagebox.showinfo("Info", "Prefix evaluation coming soon! Please use Infix or Postfix.")
            return
        
        # Evaluate postfix
        self.add_log("Step 2: Evaluating Postfix Expression...\n\n", "step")
        
        evaluator = PostfixEvaluator()
        self.steps = list(evaluator.evaluate_step_by_step(expression))
        self.current_step = 0
        
        self.step_btn.config(state=tk.NORMAL)
        self.animate_evaluation()
    
    def convert_to_postfix(self, expression, input_type):
        """Convert expression to postfix"""
        self.add_log("="*60 + "\n", "header")
        self.add_log(f"CONVERTING TO POSTFIX\n", "header")
        self.add_log("="*60 + "\n\n", "header")
        self.add_log(f"Input: {expression}\n", "operation")
        self.add_log(f"Type: {input_type.upper()}\n\n", "operation")
        
        if input_type == "postfix":
            self.add_log("ℹ️ Expression is already in postfix notation!\n", "operation")
            self.result_label.config(text=f"Result: {expression}", fg="#3498db")
            return
        
        if input_type == "infix":
            converter = InfixConverter()
            self.steps = list(converter.convert_step_by_step(expression))
            self.current_step = 0
            
            self.step_btn.config(state=tk.NORMAL)
            self.animate_conversion()
        
        elif input_type == "prefix":
            messagebox.showinfo("Info", "Prefix to Postfix conversion coming soon!")
    
    def convert_to_infix(self, expression, input_type):
        """Convert expression to infix"""
        self.add_log("="*60 + "\n", "header")
        self.add_log(f"CONVERTING TO INFIX\n", "header")
        self.add_log("="*60 + "\n\n", "header")
        
        if input_type == "infix":
            self.add_log("ℹ️ Expression is already in infix notation!\n", "operation")
            self.result_label.config(text=f"Result: {expression}", fg="#3498db")
            return
        
        messagebox.showinfo("Info", "Postfix/Prefix to Infix conversion coming soon!")
    
    def convert_to_prefix(self, expression, input_type):
        """Convert expression to prefix"""
        self.add_log("="*60 + "\n", "header")
        self.add_log(f"CONVERTING TO PREFIX\n", "header")
        self.add_log("="*60 + "\n\n", "header")
        
        if input_type == "prefix":
            self.add_log("ℹ️ Expression is already in prefix notation!\n", "operation")
            self.result_label.config(text=f"Result: {expression}", fg="#3498db")
            return
        
        messagebox.showinfo("Info", "Infix/Postfix to Prefix conversion coming soon!")
    
    def animate_evaluation(self):
        """Animate evaluation steps"""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            
            # Update stack
            if 'stack_after' in step:
                self.stack = step['stack_after']
                self.draw_stack()
            
            # Log step
            self.add_log(f"Step {step['step_number']}: {step['description']}\n", "step")
            
            self.current_step += 1
            self.root.after(int(self.animation_speed * 1000), self.animate_evaluation)
        else:
            # Complete
            if self.steps and 'result' in self.steps[-1]:
                result = self.steps[-1]['result']
                self.add_log(f"\n{'='*60}\n", "header")
                self.add_log(f"✅ FINAL RESULT: {result}\n", "result")
                self.add_log(f"{'='*60}\n", "header")
                self.result_label.config(text=f"✅ Result: {result}", fg="#27ae60")
            self.step_btn.config(state=tk.DISABLED)
    
    def animate_conversion(self):
        """Animate conversion steps"""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            
            # Update visualizations
            if 'operator_stack_after' in step:
                self.stack = step['operator_stack_after']
                self.draw_stack()
            
            if 'output_queue_after' in step:
                self.output_queue = step['output_queue_after']
                self.draw_output()
            
            # Log step
            self.add_log(f"Step {step['step_number']}: {step['description']}\n", "step")
            
            self.current_step += 1
            self.root.after(int(self.animation_speed * 1000), self.animate_conversion)
        else:
            # Complete
            if self.steps and 'postfix' in self.steps[-1]:
                result = self.steps[-1]['postfix']
                self.add_log(f"\n{'='*60}\n", "header")
                self.add_log(f"✅ POSTFIX RESULT: {result}\n", "result")
                self.add_log(f"{'='*60}\n", "header")
                self.result_label.config(text=f"✅ Postfix: {result}", fg="#27ae60")
            self.step_btn.config(state=tk.DISABLED)
    
    def next_step(self):
        """Execute next step manually"""
        if self.operation.get() == "evaluate":
            if self.current_step < len(self.steps):
                step = self.steps[self.current_step]
                
                if 'stack_after' in step:
                    self.stack = step['stack_after']
                    self.draw_stack()
                
                self.add_log(f"Step {step['step_number']}: {step['description']}\n", "step")
                self.current_step += 1
                
                if self.current_step >= len(self.steps):
                    if 'result' in self.steps[-1]:
                        result = self.steps[-1]['result']
                        self.add_log(f"\n✅ FINAL RESULT: {result}\n", "result")
                        self.result_label.config(text=f"✅ Result: {result}", fg="#27ae60")
                    self.step_btn.config(state=tk.DISABLED)
        
        else:  # Conversion
            if self.current_step < len(self.steps):
                step = self.steps[self.current_step]
                
                if 'operator_stack_after' in step:
                    self.stack = step['operator_stack_after']
                    self.draw_stack()
                
                if 'output_queue_after' in step:
                    self.output_queue = step['output_queue_after']
                    self.draw_output()
                
                self.add_log(f"Step {step['step_number']}: {step['description']}\n", "step")
                self.current_step += 1
                
                if self.current_step >= len(self.steps):
                    if 'postfix' in self.steps[-1]:
                        result = self.steps[-1]['postfix']
                        self.add_log(f"\n✅ POSTFIX RESULT: {result}\n", "result")
                        self.result_label.config(text=f"✅ Postfix: {result}", fg="#27ae60")
                    self.step_btn.config(state=tk.DISABLED)
    
    def draw_stack(self):
        """Draw stack visualization"""
        self.stack_canvas.delete("all")
        
        width = self.stack_canvas.winfo_width()
        height = self.stack_canvas.winfo_height()
        
        if not self.stack:
            self.stack_canvas.create_text(
                width // 2, height // 2,
                text="Stack Empty",
                font=("Arial", 14, "italic"),
                fill="#95a5a6"
            )
            return
        
        # Draw as vertical stack
        box_width = 120
        box_height = 50
        spacing = 10
        start_x = (width - box_width) // 2
        
        for i, value in enumerate(self.stack):
            y = height - 50 - (i * (box_height + spacing))
            
            # Color
            if i == len(self.stack) - 1:
                color = "#f39c12"  # Top
            else:
                color = "#3498db"
            
            # Box
            self.stack_canvas.create_rectangle(
                start_x, y,
                start_x + box_width, y + box_height,
                fill=color, outline="#2c3e50", width=3
            )
            
            # Value
            self.stack_canvas.create_text(
                start_x + box_width // 2, y + box_height // 2,
                text=str(value),
                font=("Arial", 16, "bold"),
                fill="white"
            )
            
            # Top label
            if i == len(self.stack) - 1:
                self.stack_canvas.create_text(
                    start_x + box_width + 30, y + box_height // 2,
                    text="← TOP",
                    font=("Arial", 11, "bold"),
                    fill="#f39c12"
                )
    
    def draw_output(self):
        """Draw output queue"""
        self.output_canvas.delete("all")
        
        width = self.output_canvas.winfo_width()
        height = self.output_canvas.winfo_height()
        
        if not self.output_queue:
            self.output_canvas.create_text(
                width // 2, height // 2,
                text="Output Empty",
                font=("Arial", 14, "italic"),
                fill="#95a5a6"
            )
            return
        
        # Draw horizontally
        box_width = 70
        box_height = 50
        spacing = 10
        total_width = len(self.output_queue) * (box_width + spacing)
        start_x = max(20, (width - total_width) // 2)
        start_y = (height - box_height) // 2
        
        for i, value in enumerate(self.output_queue):
            x = start_x + i * (box_width + spacing)
            
            self.output_canvas.create_rectangle(
                x, start_y,
                x + box_width, start_y + box_height,
                fill="#9b59b6", outline="#2c3e50", width=3
            )
            
            self.output_canvas.create_text(
                x + box_width // 2, start_y + box_height // 2,
                text=str(value),
                font=("Arial", 14, "bold"),
                fill="white"
            )
    
    def add_log(self, message, tag="normal"):
        """Add message to log"""
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
    """Main entry point"""
    root = tk.Tk()
    app = ExpressionEvaluator(root)
    root.mainloop()


if __name__ == "__main__":
    main()