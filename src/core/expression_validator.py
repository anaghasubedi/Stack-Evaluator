
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
        
        # Check parentheses balance
        paren_count = 0
        for char in expression:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
                if paren_count < 0:
                    return False, "Mismatched parentheses"
        
        if paren_count != 0:
            return False, "Mismatched parentheses"
        
        # Check for valid characters
        valid_chars = set('0123456789.+-*/^%() ')
        for char in expression:
            if char not in valid_chars:
                return False, f"Invalid character: '{char}'"
        
        # Basic validation passed
        return True, "Valid expression"