
from src.utils.operators import is_operator, is_number


class ExpressionValidator:
    """Validates mathematical expressions."""
    
    @staticmethod
    def validate_postfix(expression):
        """
        Validate a postfix expression.
        
        Args:
            expression (str): The postfix expression to validate
        
        Returns:
            tuple: (is_valid (bool), error_message (str))
        """
        if not expression or expression.strip() == "":
            return False, "Expression cannot be empty"
        
        tokens = expression.split()
        
        if len(tokens) == 0:
            return False, "Expression cannot be empty"
        
        # Count operands and operators
        operand_count = 0
        
        for token in tokens:
            if is_number(token):
                operand_count += 1
            elif is_operator(token):
                if operand_count < 2:
                    return False, f"Insufficient operands for operator '{token}'"
                operand_count -= 1  # Pop 2, push 1 = net -1
            else:
                return False, f"Invalid token: '{token}'"
        
        # Should have exactly one operand left (the result)
        if operand_count != 1:
            return False, "Invalid expression: too many operands"
        
        return True, "Valid expression"
    
    @staticmethod
    def validate_infix(expression):
        """
        Validate an infix expression.
        
        Args:
            expression (str): The infix expression to validate
        
        Returns:
            tuple: (is_valid (bool), error_message (str))
        """
        if not expression or expression.strip() == "":
            return False, "Expression cannot be empty"
        
        # Remove spaces for easier validation
        expr = expression.replace(" ", "")
        
        if len(expr) == 0:
            return False, "Expression cannot be empty"
        
        # Check parentheses balance
        paren_count = 0
        for char in expr:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
                if paren_count < 0:
                    return False, "Unbalanced parentheses: too many closing parentheses"
        
        if paren_count != 0:
            return False, "Unbalanced parentheses: missing closing parentheses"
        
        # Check for valid characters
        valid_chars = set('0123456789.+-*/^%() ')
        for char in expression:
            if char not in valid_chars:
                return False, f"Invalid character: '{char}'"
        
        # Check for consecutive operators
        tokens = expression.split()
        prev_was_operator = False
        prev_was_open_paren = False
        
        for i, token in enumerate(tokens):
            # Skip parentheses for this check
            if token == '(':
                prev_was_open_paren = True
                prev_was_operator = False
                continue
            elif token == ')':
                prev_was_open_paren = False
                prev_was_operator = False
                continue
            
            if is_operator(token):
                if prev_was_operator:
                    return False, f"Consecutive operators found at position {i}"
                if prev_was_open_paren:
                    return False, f"Operator '{token}' cannot follow opening parenthesis"
                prev_was_operator = True
            elif is_number(token):
                prev_was_operator = False
                prev_was_open_paren = False
            else:
                return False, f"Invalid token: '{token}'"
        
        # Check if expression ends with an operator
        if tokens and is_operator(tokens[-1]):
            return False, "Expression cannot end with an operator"
        
        return True, "Valid expression"