from src.core.stack import Stack
from src.utils.operators import (
    is_operator, 
    get_precedence, 
    get_associativity, 
    is_number
)
from src.core.expression_validator import ExpressionValidator


class InfixConverter:
    """
    Converts infix expressions to postfix notation using Shunting Yard algorithm.
    
    The Shunting Yard algorithm uses a stack to reorder operators based on their
    precedence and associativity while maintaining the operand order.
    """
    
    def __init__(self, callback=None):
        """
        Initialize the infix converter.
        
        Args:
            callback (function, optional): Callback function for step-by-step tracking
                                          Signature: callback(step_info: dict)
        """
        self.operator_stack = Stack()
        self.output_queue = []
        self.callback = callback
        self.steps = []
    
    def convert(self, infix_expression):
        """
        Convert infix expression to postfix notation.
        
        Args:
            infix_expression (str): Infix expression (e.g., "3 + 5 * 2")
        
        Returns:
            str: Postfix expression (e.g., "3 5 2 * +")
        
        Raises:
            ValueError: If the expression is invalid
        
        Example:
            >>> converter = InfixConverter()
            >>> result = converter.convert("(3 + 5) * 2")
            >>> print(result)
            3 5 + 2 *
        """
        # Validate expression
        is_valid, error_msg = ExpressionValidator.validate_infix(infix_expression)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Reset state
        self.operator_stack.clear()
        self.output_queue = []
        self.steps = []
        
        # Tokenize the expression
        tokens = self._tokenize(infix_expression)
        
        step_number = 1
        
        for token in tokens:
            step_info = {
                'step_number': step_number,
                'token': token,
                'action': '',
                'operator_stack': self.operator_stack.get_items().copy(),
                'output_queue': self.output_queue.copy(),
                'description': ''
            }
            
            if is_number(token):
                # If token is a number, add to output queue
                self.output_queue.append(token)
                step_info['action'] = 'output_number'
                step_info['description'] = f"Number '{token}' → Output queue"
                
            elif token == '(':
                # Left parenthesis goes to operator stack
                self.operator_stack.push(token)
                step_info['action'] = 'push_left_paren'
                step_info['description'] = f"Left parenthesis '(' → Operator stack"
                
            elif token == ')':
                # Right parenthesis: pop until matching left parenthesis
                step_info['action'] = 'process_right_paren'
                step_info['description'] = f"Right parenthesis ')' → Pop until '('"
                
                # Pop operators until we find the matching left parenthesis
                while not self.operator_stack.is_empty() and self.operator_stack.peek() != '(':
                    op = self.operator_stack.pop()
                    self.output_queue.append(op)
                
                # Pop the left parenthesis (but don't add to output)
                if not self.operator_stack.is_empty():
                    self.operator_stack.pop()
                else:
                    raise ValueError("Mismatched parentheses")
                    
            elif is_operator(token):
                # Operator: pop operators with higher or equal precedence
                step_info['action'] = 'process_operator'
                
                # Pop operators from stack while they have higher or equal precedence
                while (not self.operator_stack.is_empty() and 
                       self.operator_stack.peek() != '(' and
                       self._should_pop_operator(token, self.operator_stack.peek())):
                    op = self.operator_stack.pop()
                    self.output_queue.append(op)
                
                # Push current operator to stack
                self.operator_stack.push(token)
                step_info['description'] = f"Operator '{token}' → Operator stack"
            
            else:
                raise ValueError(f"Invalid token: {token}")
            
            step_info['operator_stack_after'] = self.operator_stack.get_items().copy()
            step_info['output_queue_after'] = self.output_queue.copy()
            
            self.steps.append(step_info)
            step_number += 1
            
            # Call callback if provided
            if self.callback:
                self.callback(step_info)
        
        # Pop remaining operators from stack to output
        while not self.operator_stack.is_empty():
            op = self.operator_stack.pop()
            if op == '(' or op == ')':
                raise ValueError("Mismatched parentheses")
            self.output_queue.append(op)
        
        # Final step
        final_step = {
            'step_number': step_number,
            'token': 'END',
            'action': 'complete',
            'operator_stack': [],
            'output_queue': self.output_queue.copy(),
            'description': 'Conversion complete'
        }
        self.steps.append(final_step)
        
        if self.callback:
            self.callback(final_step)
        
        # Return postfix expression as string
        return ' '.join(self.output_queue)
    
    def _should_pop_operator(self, current_op, stack_op):
        """
        Determine if stack operator should be popped based on precedence.
        
        Args:
            current_op (str): Current operator being processed
            stack_op (str): Operator on top of stack
        
        Returns:
            bool: True if stack operator should be popped
        """
        if not is_operator(stack_op):
            return False
        
        current_prec = get_precedence(current_op)
        stack_prec = get_precedence(stack_op)
        current_assoc = get_associativity(current_op)
        
        # Left associative: pop if stack has higher or equal precedence
        # Right associative: pop only if stack has strictly higher precedence
        if current_assoc == 'L':
            return stack_prec >= current_prec
        else:  # Right associative
            return stack_prec > current_prec
    
    def _tokenize(self, expression):
        """
        Tokenize the infix expression.
        
        Args:
            expression (str): Infix expression
        
        Returns:
            list: List of tokens (numbers, operators, parentheses)
        
        Example:
            >>> converter = InfixConverter()
            >>> tokens = converter._tokenize("3 + 5 * 2")
            >>> print(tokens)
            ['3', '+', '5', '*', '2']
        """
        tokens = []
        current_number = ""
        
        for char in expression:
            if char.isspace():
                # Space: end current number if any
                if current_number:
                    tokens.append(current_number)
                    current_number = ""
            elif char.isdigit() or char == '.' or (char == '-' and not current_number and 
                                                   (not tokens or tokens[-1] in ['(', '+', '-', '*', '/', '^', '%'])):
                # Part of a number (including negative numbers)
                current_number += char
            elif char in '+-*/^%()':
                # Operator or parenthesis
                if current_number:
                    tokens.append(current_number)
                    current_number = ""
                tokens.append(char)
            else:
                raise ValueError(f"Invalid character: {char}")
        
        # Add last number if any
        if current_number:
            tokens.append(current_number)
        
        return tokens
    
    def get_steps(self):
        """
        Get all conversion steps.
        
        Returns:
            list: List of step information dictionaries
        """
        return self.steps
    
    def convert_step_by_step(self, infix_expression):
        """
        Generator that yields each step of conversion.
        
        Args:
            infix_expression (str): Infix expression to convert
        
        Yields:
            dict: Step information for each conversion step
        
        Raises:
            ValueError: If the expression is invalid
        """
        # Validate expression
        is_valid, error_msg = ExpressionValidator.validate_infix(infix_expression)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Reset state
        self.operator_stack.clear()
        self.output_queue = []
        self.steps = []
        
        # Tokenize the expression
        tokens = self._tokenize(infix_expression)
        
        step_number = 1
        
        for token in tokens:
            step_info = {
                'step_number': step_number,
                'token': token,
                'action': '',
                'operator_stack_before': self.operator_stack.get_items().copy(),
                'output_queue_before': self.output_queue.copy(),
                'description': ''
            }
            
            if is_number(token):
                self.output_queue.append(token)
                step_info['action'] = 'output_number'
                step_info['description'] = f"Number '{token}' → Output queue"
                
            elif token == '(':
                self.operator_stack.push(token)
                step_info['action'] = 'push_left_paren'
                step_info['description'] = f"Left parenthesis '(' → Operator stack"
                
            elif token == ')':
                step_info['action'] = 'process_right_paren'
                step_info['description'] = f"Right parenthesis ')' → Pop until '('"
                
                while not self.operator_stack.is_empty() and self.operator_stack.peek() != '(':
                    op = self.operator_stack.pop()
                    self.output_queue.append(op)
                
                if not self.operator_stack.is_empty():
                    self.operator_stack.pop()
                else:
                    raise ValueError("Mismatched parentheses")
                    
            elif is_operator(token):
                step_info['action'] = 'process_operator'
                
                while (not self.operator_stack.is_empty() and 
                       self.operator_stack.peek() != '(' and
                       self._should_pop_operator(token, self.operator_stack.peek())):
                    op = self.operator_stack.pop()
                    self.output_queue.append(op)
                
                self.operator_stack.push(token)
                step_info['description'] = f"Operator '{token}' → Operator stack"
            
            step_info['operator_stack_after'] = self.operator_stack.get_items().copy()
            step_info['output_queue_after'] = self.output_queue.copy()
            
            self.steps.append(step_info)
            step_number += 1
            
            yield step_info
        
        # Pop remaining operators
        while not self.operator_stack.is_empty():
            op = self.operator_stack.pop()
            if op == '(' or op == ')':
                raise ValueError("Mismatched parentheses")
            self.output_queue.append(op)
        
        # Yield final step
        final_step = {
            'step_number': step_number,
            'token': 'END',
            'action': 'complete',
            'operator_stack_before': [],
            'operator_stack_after': [],
            'output_queue_before': self.output_queue.copy(),
            'output_queue_after': self.output_queue.copy(),
            'postfix': ' '.join(self.output_queue),
            'description': 'Conversion complete'
        }
        self.steps.append(final_step)
        yield final_step
    
    def convert_and_evaluate(self, infix_expression):
        """
        Convert infix to postfix and evaluate the result.
        
        Args:
            infix_expression (str): Infix expression
        
        Returns:
            tuple: (postfix_expression, result)
        
        Example:
            >>> converter = InfixConverter()
            >>> postfix, result = converter.convert_and_evaluate("(3 + 5) * 2")
            >>> print(f"Postfix: {postfix}, Result: {result}")
            Postfix: 3 5 + 2 *, Result: 16
        """
        from src.core.postfix_evaluator import PostfixEvaluator
        
        # Convert to postfix
        postfix = self.convert(infix_expression)
        
        # Evaluate postfix
        evaluator = PostfixEvaluator()
        result = evaluator.evaluate(postfix)
        
        return postfix, result