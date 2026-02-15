"""
Operator Utilities
Author: Your Name
Date: 2025-01-13

Defines operator precedence, associativity, and operations.
"""

# Operator precedence (higher number = higher precedence)
PRECEDENCE = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
    '%': 2,
    '^': 3
}

# Operator associativity
# 'L' = Left associative, 'R' = Right associative
ASSOCIATIVITY = {
    '+': 'L',
    '-': 'L',
    '*': 'L',
    '/': 'L',
    '%': 'L',
    '^': 'R'  # Exponentiation is right associative
}


def is_operator(char):
    """
    Check if a character is an operator.
    
    Args:
        char (str): Character to check
    
    Returns:
        bool: True if char is an operator, False otherwise
    """
    return char in PRECEDENCE


def get_precedence(operator):
    """
    Get the precedence level of an operator.
    
    Args:
        operator (str): The operator
    
    Returns:
        int: Precedence level, or -1 if not an operator
    """
    return PRECEDENCE.get(operator, -1)


def get_associativity(operator):
    """
    Get the associativity of an operator.
    
    Args:
        operator (str): The operator
    
    Returns:
        str: 'L' for left, 'R' for right, or None if not an operator
    """
    return ASSOCIATIVITY.get(operator, None)


def compare_precedence(op1, op2):
    """
    Compare precedence of two operators.
    
    Args:
        op1 (str): First operator
        op2 (str): Second operator
    
    Returns:
        int: Positive if op1 > op2, negative if op1 < op2, 0 if equal
    """
    return get_precedence(op1) - get_precedence(op2)


def apply_operator(operator, operand2, operand1):
    """
    Apply an operator to two operands.
    Note: operand1 is applied first (left operand)
    
    Args:
        operator (str): The operator to apply
        operand2 (float): Right operand (second pop from stack)
        operand1 (float): Left operand (first pop from stack)
    
    Returns:
        float: Result of the operation
    
    Raises:
        ValueError: If operator is invalid or division by zero
    """
    try:
        operand1 = float(operand1)
        operand2 = float(operand2)
        
        if operator == '+':
            return operand1 + operand2
        elif operator == '-':
            return operand1 - operand2
        elif operator == '*':
            return operand1 * operand2
        elif operator == '/':
            if operand2 == 0:
                raise ValueError("Division by zero")
            return operand1 / operand2
        elif operator == '%':
            if operand2 == 0:
                raise ValueError("Modulo by zero")
            return operand1 % operand2
        elif operator == '^':
            return operand1 ** operand2
        else:
            raise ValueError(f"Invalid operator: {operator}")
    except (ValueError, TypeError) as e:
        raise ValueError(f"Error applying operator '{operator}': {str(e)}")


def is_number(token):
    """
    Check if a token is a valid number.
    
    Args:
        token (str): Token to check
    
    Returns:
        bool: True if token is a number, False otherwise
    """
    try:
        float(token)
        return True
    except ValueError:
        return False