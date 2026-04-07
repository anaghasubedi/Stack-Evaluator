"""
Stack Evaluator - Main Application
Complete GUI with Infix & Postfix support and visualization

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


class StackEvaluatorApp:
    """Main application window for Stack Evaluator"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Stack Expression Evaluator")
        self.root.geometry("1000x800")
        self.root.configure(bg="#ecf0f1")
        
        # Application state
        self.mode = tk.StringVar(value="postfix")
        self.stack = []
        self.output_queue = []
        self.steps = []
        self.current_step = 0
        self.is_animating = False
        self.animation_speed = 0.5
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the complete user interface"""
        
        # ===== HEADER =====
        header_frame = tk.Frame(self.root, bg="#34495e", height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="📚 Stack Expression Evaluator",
            font=("Arial", 24, "bold"),
            bg="#34495e",
            fg="white"
        )
        title.pack(pady=20)
        
        # ===== MODE SELECTION =====
        mode_frame = tk.LabelFrame(
            self.root,
            text="Expression Type",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1",
            padx=20,
            pady=15
        )
        mode_frame.pack(pady=15, padx=20, fill=tk.X)
        
        postfix_radio = tk.Radiobutton(
            mode_frame,
            text="📝 Postfix (RPN)",
            variable=self.mode,
            value="postfix",
            font=("Arial", 11),
            bg="#ecf0f1",
            command=self.on_mode_change,
            cursor="hand2"
        )
        postfix_radio.pack(side=tk.LEFT, padx=20)
        
        infix_radio = tk.Radiobutton(
            mode_frame,
            text="🔢 Infix (Standard)",
            variable=self.mode,
            value="infix",
            font=("Arial", 11),
            bg="#ecf0f1",
            command=self.on_mode_change,
            cursor="hand2"
        )
        infix_radio.pack(side=tk.LEFT, padx=20)
        
        # ===== INPUT SECTION =====
        input_frame = tk.Frame(self.root, bg="#ecf0f1")
        input_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.input_label = tk.Label(
            input_frame,
            text="Enter Postfix Expression:",
            font=("Arial", 12, "bold"),
            bg="#ecf0f1"
        )
        self.input_label.pack(anchor=tk.W, padx=5)
        
        self.expression_entry = tk.Entry(
            input_frame,
            font=("Arial", 14),
            width=50,
            relief=tk.SOLID,
            bd=2
        )
        self.expression_entry.pack(fill=tk.X, padx=5, pady=5)
        self.expression_entry.insert(0, "5 3 + 2 *")
        self.expression_entry.bind('<Return>', lambda e: self.evaluate())
        
        # Example label
        self.example_label = tk.Label(
            input_frame,
            text="Example: 5 3 + 2 *  (Result: 16)",
            font=("Arial", 9, "italic"),
            bg="#ecf0f1",
            fg="#7f8c8d"
        )
        self.example_label.pack(anchor=tk.W, padx=5)
        
        # ===== CONTROL BUTTONS =====
        button_frame = tk.Frame(self.root, bg="#ecf0f1")
        button_frame.pack(pady=15)
        
        self.eval_btn = tk.Button(
            button_frame,
            text="▶ Evaluate",
            command=self.evaluate,
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=30,
            pady=10,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3
        )
        self.eval_btn.pack(side=tk.LEFT, padx=5)
        
        self.step_btn = tk.Button(
            button_frame,
            text="⏭ Next Step",
            command=self.next_step,
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            padx=30,
            pady=10,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3,
            state=tk.DISABLED
        )
        self.step_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(
            button_frame,
            text="🔄 Clear",
            command=self.clear_all,
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            padx=30,
            pady=10,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # ===== SPEED CONTROL =====
        speed_frame = tk.Frame(self.root, bg="#ecf0f1")
        speed_frame.pack(pady=5)
        
        tk.Label(
            speed_frame,
            text="⚡ Animation Speed:",
            font=("Arial", 10),
            bg="#ecf0f1"
        ).pack(side=tk.LEFT, padx=5)
        
        self.speed_var = tk.DoubleVar(value=0.5)
        speed_scale = tk.Scale(
            speed_frame,
            from_=0.1,
            to=2.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            length=250,
            bg="#ecf0f1",
            command=self.update_speed
        )
        speed_scale.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            speed_frame,
            text="(slower ← → faster)",
            font=("Arial", 8, "italic"),
            bg="#ecf0f1",
            fg="#7f8c8d"
        ).pack(side=tk.LEFT, padx=5)
        
        # ===== VISUALIZATION AREA =====
        viz_container = tk.Frame(self.root, bg="#ecf0f1")
        viz_container.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Left: Stack Visualization
        stack_frame = tk.LabelFrame(
            viz_container,
            text="📦 Stack Visualization",
            font=("Arial", 11, "bold"),
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
        
        # Right: Output/Result
        output_frame = tk.LabelFrame(
            viz_container,
            text="📝 Output / Result",
            font=("Arial", 11, "bold"),
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
        
        # ===== HISTORY/STEPS PANEL =====
        history_frame = tk.LabelFrame(
            self.root,
            text="📋 Evaluation Steps",
            font=("Arial", 11, "bold"),
            bg="#ffffff",
            padx=10,
            pady=10
        )
        history_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scroll = tk.Scrollbar(history_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_text = tk.Text(
            history_frame,
            height=10,
            font=("Courier", 10),
            bg="#fdfefe",
            state=tk.DISABLED,
            yscrollcommand=scroll.set,
            wrap=tk.WORD
        )
        self.history_text.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.history_text.yview)
        
        # Configure text tags
        self.history_text.tag_configure("step", foreground="#3498db", font=("Courier", 10, "bold"))
        self.history_text.tag_configure("operation", foreground="#e67e22", font=("Courier", 10, "bold"))
        self.history_text.tag_configure("result", foreground="#27ae60", font=("Courier", 10, "bold"))
        self.history_text.tag_configure("error", foreground="#e74c3c", font=("Courier", 10, "bold"))
        
        # ===== RESULT LABEL =====
        self.result_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 16, "bold"),
            bg="#ecf0f1",
            fg="#27ae60"
        )
        self.result_label.pack(pady=10)
        
        # Draw initial empty state
        self.draw_stack()
        self.draw_output()
    
    def on_mode_change(self):
        """Handle mode change between postfix and infix"""
        mode = self.mode.get()
        
        if mode == "postfix":
            self.input_label.config(text="Enter Postfix Expression:")
            self.expression_entry.delete(0, tk.END)
            self.expression_entry.insert(0, "5 3 + 2 *")
            self.example_label.config(text="Example: 5 3 + 2 *  (Result: 16)")
        else:  # infix
            self.input_label.config(text="Enter Infix Expression:")
            self.expression_entry.delete(0, tk.END)
            self.expression_entry.insert(0, "(5 + 3) * 2")
            self.example_label.config(text="Example: (5 + 3) * 2  (Result: 16)")
        
        self.clear_all()
    
    def update_speed(self, value):
        """Update animation speed"""
        self.animation_speed = float(value)
    
    def evaluate(self):
        """Start evaluation process"""
        expression = self.expression_entry.get().strip()
        
        if not expression:
            messagebox.showwarning("Empty Expression", "Please enter an expression!")
            return
        
        # Clear previous results
        self.clear_all()
        
        try:
            mode = self.mode.get()
            
            if mode == "postfix":
                self.evaluate_postfix(expression)
            else:  # infix
                self.evaluate_infix(expression)
                
        except Exception as e:
            self.add_history(f"❌ Error: {str(e)}", "error")
            messagebox.showerror("Evaluation Error", str(e))
            self.result_label.config(text=f"❌ Error: {str(e)}", fg="#e74c3c")
    
    def evaluate_postfix(self, expression):
        """Evaluate postfix expression with animation"""
        evaluator = PostfixEvaluator()
        
        try:
            # Get all steps
            self.steps = list(evaluator.evaluate_step_by_step(expression))
            self.current_step = 0
            
            # Enable step button
            self.step_btn.config(state=tk.NORMAL)
            
            # Start animation
            self.animate_steps()
            
        except Exception as e:
            raise e
    
    def evaluate_infix(self, expression):
        """Convert infix to postfix and evaluate"""
        converter = InfixConverter()
        
        try:
            # Convert to postfix
            postfix = converter.convert(expression)
            self.add_history(f"🔄 Converting: {expression}", "step")
            self.add_history(f"📝 Postfix: {postfix}", "operation")
            
            # Show postfix in output canvas
            self.output_queue = postfix.split()
            self.draw_output()
            
            self.root.update()
            time.sleep(self.animation_speed)
            
            # Now evaluate the postfix
            self.add_history("\n--- Evaluating Postfix ---\n", "step")
            self.evaluate_postfix(postfix)
            
        except Exception as e:
            raise e
    
    def animate_steps(self):
        """Animate through evaluation steps"""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            
            # Update visualizations
            if 'stack_after' in step:
                self.stack = step['stack_after']
            
            self.draw_stack()
            
            # Add to history
            self.add_history(f"Step {step['step_number']}: {step['description']}", "step")
            
            self.current_step += 1
            
            # Continue animation
            self.root.after(int(self.animation_speed * 1000), self.animate_steps)
        else:
            # Animation complete
            if self.steps and 'result' in self.steps[-1]:
                result = self.steps[-1]['result']
                self.result_label.config(
                    text=f"✅ Final Result: {result}",
                    fg="#27ae60"
                )
                self.add_history(f"\n✅ Final Result: {result}", "result")
            
            self.step_btn.config(state=tk.DISABLED)
    
    def next_step(self):
        """Execute next step manually"""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            
            # Update visualizations
            if 'stack_after' in step:
                self.stack = step['stack_after']
            
            self.draw_stack()
            
            # Add to history
            self.add_history(f"Step {step['step_number']}: {step['description']}", "step")
            
            self.current_step += 1
            
            # Check if done
            if self.current_step >= len(self.steps):
                if self.steps and 'result' in self.steps[-1]:
                    result = self.steps[-1]['result']
                    self.result_label.config(
                        text=f"✅ Final Result: {result}",
                        fg="#27ae60"
                    )
                    self.add_history(f"\n✅ Final Result: {result}", "result")
                
                self.step_btn.config(state=tk.DISABLED)
    
    def draw_stack(self):
        """Draw the stack visualization"""
        self.stack_canvas.delete("all")
        
        width = self.stack_canvas.winfo_width()
        height = self.stack_canvas.winfo_height()
        
        if not self.stack:
            self.stack_canvas.create_text(
                width // 2,
                height // 2,
                text="Stack is Empty",
                font=("Arial", 14, "italic"),
                fill="#95a5a6"
            )
            return
        
        # Draw stack elements
        box_width = 100
        box_height = 50
        spacing = 10
        start_x = 50
        
        # Calculate starting y to center vertically
        total_height = len(self.stack) * (box_height + spacing)
        start_y = max(50, (height - total_height) // 2)
        
        for i, value in enumerate(self.stack):
            y = start_y + i * (box_height + spacing)
            
            # Highlight top element
            if i == len(self.stack) - 1:
                fill_color = "#f39c12"  # Orange for top
            else:
                fill_color = "#3498db"  # Blue for others
            
            # Draw box
            self.stack_canvas.create_rectangle(
                start_x, y,
                start_x + box_width, y + box_height,
                fill=fill_color,
                outline="#2c3e50",
                width=2
            )
            
            # Draw value
            self.stack_canvas.create_text(
                start_x + box_width // 2,
                y + box_height // 2,
                text=str(value),
                font=("Arial", 16, "bold"),
                fill="white"
            )
            
            # Draw index label
            if i == len(self.stack) - 1:
                self.stack_canvas.create_text(
                    start_x + box_width + 20,
                    y + box_height // 2,
                    text="← TOP",
                    font=("Arial", 10, "bold"),
                    fill="#f39c12"
                )
    
    def draw_output(self):
        """Draw the output queue/result"""
        self.output_canvas.delete("all")
        
        width = self.output_canvas.winfo_width()
        height = self.output_canvas.winfo_height()
        
        if not self.output_queue:
            self.output_canvas.create_text(
                width // 2,
                height // 2,
                text="Output Queue Empty",
                font=("Arial", 14, "italic"),
                fill="#95a5a6"
            )
            return
        
        # Draw output queue elements
        box_width = 80
        box_height = 50
        spacing = 10
        start_x = 30
        start_y = height // 2 - box_height // 2
        
        for i, value in enumerate(self.output_queue):
            x = start_x + i * (box_width + spacing)
            
            # Draw box
            self.output_canvas.create_rectangle(
                x, start_y,
                x + box_width, start_y + box_height,
                fill="#9b59b6",
                outline="#2c3e50",
                width=2
            )
            
            # Draw value
            self.output_canvas.create_text(
                x + box_width // 2,
                start_y + box_height // 2,
                text=str(value),
                font=("Arial", 14, "bold"),
                fill="white"
            )
    
    def add_history(self, message, tag="normal"):
        """Add message to history panel"""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, message + "\n", tag)
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)
    
    def clear_all(self):
        """Clear all data and reset UI"""
        self.stack = []
        self.output_queue = []
        self.steps = []
        self.current_step = 0
        
        self.draw_stack()
        self.draw_output()
        
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state=tk.DISABLED)
        
        self.result_label.config(text="")
        self.step_btn.config(state=tk.DISABLED)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = StackEvaluatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()