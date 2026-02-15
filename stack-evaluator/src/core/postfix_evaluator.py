"""
Postfix Expression Evaluator
Author: Your Name
Date: 2025-01-13

Evaluates postfix (Reverse Polish Notation) expressions.
"""

from src.core.stack import Stack
from src.utils.operators import is_operator, apply_operator, is_number
from src.core.expression_validator import ExpressionValidator


class PostfixEvaluator:
    """
    Evaluates postfix expressions with step-by-step tracking.
    """
    
    def __init__(self, callback=None):
        """
        Initialize the postfix evaluator.
        
        Args:
            callback (function, optional): Callback function to call after each step
                                          Signature: callback(step_info: dict)
        """
        self.stack = Stack()
        self.callback = callback
        self.steps = []
    
    def evaluate(self, expression):
        """
        Evaluate a postfix expression.
        
        Args:
            expression (str): The postfix expression to evaluate
        
        Returns:
            float: The result of the evaluation
        
        Raises:
            ValueError: If the expression is invalid
        """
        # Validate expression
        is_valid, error_msg = ExpressionValidator.validate_postfix(expression)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Reset state
        self.stack.clear()
        self.steps = []
        
        tokens = expression.split()
        
        for i, token in enumerate(tokens):
            step_info = {
                'step_number': i + 1,
                'token': token,
                'action': '',
                'stack_before': self.stack.get_items().copy(),
                'stack_after': [],
                'description': ''
            }
            
            if is_number(token):
                # Push operand onto stack
                self.stack.push(float(token))
                step_info['action'] = 'push'
                step_info['stack_after'] = self.stack.get_items().copy()
                step_info['description'] = f"Push {token} onto stack"
                
            elif is_operator(token):
                # Pop two operands and apply operator
                if self.stack.size() < 2:
                    raise ValueError(f"Insufficient operands for operator '{token}'")
                
                operand2 = self.stack.pop()
                operand1 = self.stack.pop()
                
                result = apply_operator(token, operand2, operand1)
                self.stack.push(result)
                
                step_info['action'] = 'operate'
                step_info['operand1'] = operand1
                step_info['operand2'] = operand2
                step_info['operator'] = token
                step_info['result'] = result
                step_info['stack_after'] = self.stack.get_items().copy()
                step_info['description'] = f"Pop {operand2}, Pop {operand1}, Calculate {operand1} {token} {operand2} = {result}, Push {result}"
            
            self.steps.append(step_info)
            
            # Call callback if provided
            if self.callback:
                self.callback(step_info)
        
        # Final result should be the only item left in stack
        if self.stack.size() != 1:
            raise ValueError("Invalid expression: stack should have exactly one element")
        
        return self.stack.pop()
    
    def get_steps(self):
        """
        Get all evaluation steps.
        
        Returns:
            list: List of step information dictionaries
        """
        return self.steps
    
    def evaluate_step_by_step(self, expression):
        """
        Generator that yields each step of evaluation.
        
        Args:
            expression (str): The postfix expression to evaluate
        
        Yields:
            dict: Step information for each evaluation step
        
        Raises:
            ValueError: If the expression is invalid
        """
        # Validate expression
        is_valid, error_msg = ExpressionValidator.validate_postfix(expression)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Reset state
        self.stack.clear()
        self.steps = []
        
        tokens = expression.split()
        
        for i, token in enumerate(tokens):
            step_info = {
                'step_number': i + 1,
                'token': token,
                'action': '',
                'stack_before': self.stack.get_items().copy(),
                'stack_after': [],
                'description': ''
            }
            
            if is_number(token):
                self.stack.push(float(token))
                step_info['action'] = 'push'
                step_info['stack_after'] = self.stack.get_items().copy()
                step_info['description'] = f"Push {token} onto stack"
                
            elif is_operator(token):
                if self.stack.size() < 2:
                    raise ValueError(f"Insufficient operands for operator '{token}'")
                
                operand2 = self.stack.pop()
                operand1 = self.stack.pop()
                
                result = apply_operator(token, operand2, operand1)
                self.stack.push(result)
                
                step_info['action'] = 'operate'
                step_info['operand1'] = operand1
                step_info['operand2'] = operand2
                step_info['operator'] = token
                step_info['result'] = result
                step_info['stack_after'] = self.stack.get_items().copy()
                step_info['description'] = f"Pop {operand2}, Pop {operand1}, Calculate {operand1} {token} {operand2} = {result}, Push {result}"
            
            self.steps.append(step_info)
            yield step_info
        
        # Yield final result
        if self.stack.size() != 1:
            raise ValueError("Invalid expression: stack should have exactly one element")
        
        final_result = self.stack.peek()
        yield {
            'step_number': len(tokens) + 1,
            'token': 'FINAL',
            'action': 'complete',
            'stack_before': [final_result],
            'stack_after': [final_result],
            'result': final_result,
            'description': f"Evaluation complete. Result: {final_result}"
        }