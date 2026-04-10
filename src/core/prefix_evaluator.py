from core.stack import Stack
from utils.operators import is_operator, apply_operator, is_number
from core.expression_validator import ExpressionValidator


class PrefixEvaluator:
    """
    Evaluates prefix (Polish notation) expressions and handles conversions.

    Prefix evaluation reads right-to-left:
      - Push numbers onto the stack
      - On operator: pop two operands, apply, push result
    """

    def __init__(self, callback=None):
        self.stack = Stack()
        self.callback = callback
        self.steps = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(self, expression: str) -> float:
        """Evaluate a prefix expression and return the numeric result."""
        is_valid, error_msg = ExpressionValidator.validate_prefix(expression)
        if not is_valid:
            raise ValueError(error_msg)

        self.stack.clear()
        self.steps = []

        tokens = expression.split()
        tokens.reverse()           # right-to-left scan

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

                operand1 = self.stack.pop()   # left operand
                operand2 = self.stack.pop()   # right operand
                result = apply_operator(token, operand2, operand1)
                self.stack.push(result)

                step_info['action'] = 'operate'
                step_info['operand1'] = operand1
                step_info['operand2'] = operand2
                step_info['operator'] = token
                step_info['result'] = result
                step_info['stack_after'] = self.stack.get_items().copy()
                step_info['description'] = (
                    f"Pop {operand1}, Pop {operand2}, "
                    f"Calculate {operand1} {token} {operand2} = {result}, Push {result}"
                )

            self.steps.append(step_info)
            if self.callback:
                self.callback(step_info)

        if self.stack.size() != 1:
            raise ValueError("Invalid expression: stack should have exactly one element")

        return self.stack.pop()

    def evaluate_step_by_step(self, expression: str):
        """Generator yielding each evaluation step."""
        is_valid, error_msg = ExpressionValidator.validate_prefix(expression)
        if not is_valid:
            raise ValueError(error_msg)

        self.stack.clear()
        self.steps = []

        tokens = expression.split()
        tokens.reverse()

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

                operand1 = self.stack.pop()
                operand2 = self.stack.pop()
                result = apply_operator(token, operand2, operand1)
                self.stack.push(result)

                step_info['action'] = 'operate'
                step_info['operand1'] = operand1
                step_info['operand2'] = operand2
                step_info['operator'] = token
                step_info['result'] = result
                step_info['stack_after'] = self.stack.get_items().copy()
                step_info['description'] = (
                    f"Pop {operand1}, Pop {operand2}, "
                    f"Calculate {operand1} {token} {operand2} = {result}, Push {result}"
                )

            self.steps.append(step_info)
            yield step_info

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

    # ------------------------------------------------------------------
    # Conversion helpers
    # ------------------------------------------------------------------

    def to_postfix(self, expression: str) -> str:
        """Convert prefix expression to postfix."""
        is_valid, error_msg = ExpressionValidator.validate_prefix(expression)
        if not is_valid:
            raise ValueError(error_msg)

        tokens = expression.split()
        stack = Stack()

        for token in reversed(tokens):
            if is_number(token):
                stack.push(token)
            elif is_operator(token):
                if stack.size() < 2:
                    raise ValueError(f"Insufficient operands for operator '{token}'")
                op1 = stack.pop()
                op2 = stack.pop()
                stack.push(f"{op1} {op2} {token}")
            else:
                raise ValueError(f"Invalid token: {token}")

        if stack.size() != 1:
            raise ValueError("Invalid prefix expression")

        return stack.pop()

    def to_infix(self, expression: str) -> str:
        """Convert prefix expression to infix (fully parenthesised)."""
        is_valid, error_msg = ExpressionValidator.validate_prefix(expression)
        if not is_valid:
            raise ValueError(error_msg)

        tokens = expression.split()
        stack = Stack()

        for token in reversed(tokens):
            if is_number(token):
                stack.push(token)
            elif is_operator(token):
                if stack.size() < 2:
                    raise ValueError(f"Insufficient operands for operator '{token}'")
                op1 = stack.pop()
                op2 = stack.pop()
                stack.push(f"( {op1} {token} {op2} )")
            else:
                raise ValueError(f"Invalid token: {token}")

        if stack.size() != 1:
            raise ValueError("Invalid prefix expression")

        return stack.pop()

    def get_steps(self):
        return self.steps