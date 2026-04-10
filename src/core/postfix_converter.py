from core.stack import Stack
from utils.operators import is_operator, is_number
from core.expression_validator import ExpressionValidator


class PostfixConverter:
    """
    Converts postfix (RPN) expressions to infix or prefix notation.
    """

    def to_infix(self, expression: str) -> str:
        """Convert postfix to fully-parenthesised infix."""
        is_valid, err = ExpressionValidator.validate_postfix(expression)
        if not is_valid:
            raise ValueError(err)

        stack = Stack()
        for token in expression.split():
            if is_number(token):
                stack.push(token)
            elif is_operator(token):
                if stack.size() < 2:
                    raise ValueError(f"Insufficient operands for '{token}'")
                right = stack.pop()
                left = stack.pop()
                stack.push(f"( {left} {token} {right} )")
        if stack.size() != 1:
            raise ValueError("Invalid postfix expression")
        return stack.pop()

    def to_prefix(self, expression: str) -> str:
        """Convert postfix to prefix."""
        is_valid, err = ExpressionValidator.validate_postfix(expression)
        if not is_valid:
            raise ValueError(err)

        stack = Stack()
        for token in expression.split():
            if is_number(token):
                stack.push(token)
            elif is_operator(token):
                if stack.size() < 2:
                    raise ValueError(f"Insufficient operands for '{token}'")
                right = stack.pop()
                left = stack.pop()
                stack.push(f"{token} {left} {right}")
        if stack.size() != 1:
            raise ValueError("Invalid postfix expression")
        return stack.pop()