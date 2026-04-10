"""
Stack Evaluator — Entry point
Run: python src/main.py
"""
import sys
sys.path.insert(0, "src")

from gui.main_window import MainWindow

if __name__ == "__main__":
    MainWindow().mainloop()