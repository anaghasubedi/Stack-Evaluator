from utils.operators import is_operator, is_number


class ExpressionValidator:
    """Validates mathematical expressions in infix, postfix, and prefix notations."""

    @staticmethod
    def validate_postfix(expression: str):
        """
        Validate a postfix expression.

        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        if not expression or not expression.strip():
            return False, "Expression cannot be empty"

        tokens = expression.split()
        if not tokens:
            return False, "Expression cannot be empty"

        operand_count = 0
        for token in tokens:
            if is_number(token):
                operand_count += 1
            elif is_operator(token):
                if operand_count < 2:
                    return False, f"Insufficient operands for operator '{token}'"
                operand_count -= 1  # pop 2, push 1 → net -1
            else:
                return False, f"Invalid token: '{token}'"

        if operand_count != 1:
            return False, "Invalid expression: too many operands"

        return True, "Valid expression"

    @staticmethod
    def validate_infix(expression: str):
        """
        Validate an infix expression.

        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        if not expression or not expression.strip():
            return False, "Expression cannot be empty"

        # Balanced parentheses check
        depth = 0
        for char in expression:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
                if depth < 0:
                    return False, "Mismatched parentheses"
        if depth != 0:
            return False, "Mismatched parentheses"

        # Allowed characters
        valid_chars = set('0123456789.+-*/^%() ')
        for char in expression:
            if char not in valid_chars:
                return False, f"Invalid character: '{char}'"

        return True, "Valid expression"

    @staticmethod
    def validate_prefix(expression: str):
        """
        Validate a prefix expression.

        A prefix expression is valid when reading left-to-right the running
        tally of (operators - operands) never drops below −(n_operands - 1)
        and ends at exactly 0.  Equivalently: simulate a right-to-left stack
        scan — operand_count must reach exactly 1 at the end.

        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        if not expression or not expression.strip():
            return False, "Expression cannot be empty"

        tokens = expression.split()
        if not tokens:
            return False, "Expression cannot be empty"

        # Allowed characters (same set as infix, no parens needed)
        valid_chars = set('0123456789.+-*/^% ')
        for char in expression:
            if char not in valid_chars:
                return False, f"Invalid character: '{char}'"

        # Simulate right-to-left evaluation
        operand_count = 0
        for token in reversed(tokens):
            if is_number(token):
                operand_count += 1
            elif is_operator(token):
                if operand_count < 2:
                    return False, f"Insufficient operands for operator '{token}'"
                operand_count -= 1  # consume 2, produce 1 → net -1
            else:
                return False, f"Invalid token: '{token}'"

        if operand_count != 1:
            return False, "Invalid expression: too many operands"

        return True, "Valid expression"