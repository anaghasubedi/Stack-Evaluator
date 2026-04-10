from core.stack import Stack
from utils.operators import (
    is_operator,
    get_precedence,
    get_associativity,
    is_number,
)
from core.expression_validator import ExpressionValidator


class PrefixConverter:
    """
    Converts infix or postfix expressions to prefix (Polish) notation.

    Algorithm for infix → prefix:
      1. Reverse the infix expression (swap parentheses too)
      2. Run a modified Shunting Yard (right-associative flip)
      3. Reverse the output queue → prefix result

    Algorithm for postfix → prefix:
      Stack-based: scan left-to-right, operands pushed as strings,
      operators combine top two into "op left right".
    """

    def __init__(self, callback=None):
        self.operator_stack = Stack()
        self.output_queue   = []
        self.callback       = callback
        self.steps          = []

    # ─────────────────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────────────────

    def from_infix(self, infix_expression: str) -> str:
        """
        Convert an infix expression to prefix notation.

        Args:
            infix_expression: e.g. "( 3 + 5 ) * 2"

        Returns:
            Prefix string, e.g. "* + 3 5 2"

        Raises:
            ValueError: on invalid input
        """
        is_valid, err = ExpressionValidator.validate_infix(infix_expression)
        if not is_valid:
            raise ValueError(err)

        self._reset()
        tokens  = self._tokenize(infix_expression)
        rev     = self._reverse_tokens(tokens)       # step 1
        postfix = self._shunting_yard(rev)            # step 2
        prefix  = ' '.join(reversed(postfix.split())) # step 3
        return prefix

    def from_infix_step_by_step(self, infix_expression: str):
        """
        Generator — yields one step dict per token while converting
        infix → prefix.  Steps show the internal reversed-postfix pass
        so the stack/queue visualisation stays meaningful.

        Yields:
            dict with keys:
              step_number, token, action, description,
              operator_stack_before, operator_stack_after,
              output_queue_before,   output_queue_after,
              [prefix]  on the final 'complete' step
        """
        is_valid, err = ExpressionValidator.validate_infix(infix_expression)
        if not is_valid:
            raise ValueError(err)

        self._reset()
        tokens  = self._tokenize(infix_expression)
        rev     = self._reverse_tokens(tokens)

        step_number = 1

        for token in rev:
            step_info = {
                'step_number':          step_number,
                'token':                token,
                'action':               '',
                'operator_stack_before': self.operator_stack.get_items().copy(),
                'output_queue_before':   self.output_queue.copy(),
                'description':          '',
            }

            if is_number(token):
                self.output_queue.append(token)
                step_info['action']      = 'output_number'
                step_info['description'] = f"Number '{token}' → output queue"

            elif token == '(':
                # reversed ')' becomes '(' after _reverse_tokens
                self.operator_stack.push(token)
                step_info['action']      = 'push_left_paren'
                step_info['description'] = "Left paren → operator stack"

            elif token == ')':
                step_info['action']      = 'process_right_paren'
                step_info['description'] = "Right paren → pop until '('"

                while (not self.operator_stack.is_empty()
                       and self.operator_stack.peek() != '('):
                    self.output_queue.append(self.operator_stack.pop())

                if not self.operator_stack.is_empty():
                    self.operator_stack.pop()   # discard '('
                else:
                    raise ValueError("Mismatched parentheses")

            elif is_operator(token):
                step_info['action'] = 'process_operator'

                # Right-associative flip: pop only strictly-greater precedence
                while (not self.operator_stack.is_empty()
                       and self.operator_stack.peek() != '('
                       and self._should_pop(token, self.operator_stack.peek())):
                    self.output_queue.append(self.operator_stack.pop())

                self.operator_stack.push(token)
                step_info['description'] = f"Operator '{token}' → operator stack"

            else:
                raise ValueError(f"Invalid token: '{token}'")

            step_info['operator_stack_after'] = self.operator_stack.get_items().copy()
            step_info['output_queue_after']   = self.output_queue.copy()

            self.steps.append(step_info)
            step_number += 1

            if self.callback:
                self.callback(step_info)

            yield step_info

        # Drain remaining operators
        while not self.operator_stack.is_empty():
            op = self.operator_stack.pop()
            if op in '()':
                raise ValueError("Mismatched parentheses")
            self.output_queue.append(op)

        # Reverse to get prefix
        prefix = ' '.join(reversed(self.output_queue))

        final = {
            'step_number':           step_number,
            'token':                 'END',
            'action':                'complete',
            'operator_stack_before': [],
            'operator_stack_after':  [],
            'output_queue_before':   self.output_queue.copy(),
            'output_queue_after':    list(reversed(self.output_queue)),
            'prefix':                prefix,
            'description':           f"Reverse output → prefix: {prefix}",
        }
        self.steps.append(final)

        if self.callback:
            self.callback(final)

        yield final

    def from_postfix(self, postfix_expression: str) -> str:
        """
        Convert a postfix expression to prefix notation.

        Args:
            postfix_expression: e.g. "3 5 + 2 *"

        Returns:
            Prefix string, e.g. "* + 3 5 2"
        """
        is_valid, err = ExpressionValidator.validate_postfix(postfix_expression)
        if not is_valid:
            raise ValueError(err)

        stack = Stack()
        for token in postfix_expression.split():
            if is_number(token):
                stack.push(token)
            elif is_operator(token):
                if stack.size() < 2:
                    raise ValueError(f"Insufficient operands for '{token}'")
                right = stack.pop()
                left  = stack.pop()
                stack.push(f"{token} {left} {right}")
            else:
                raise ValueError(f"Invalid token: '{token}'")

        if stack.size() != 1:
            raise ValueError("Invalid postfix expression")
        return stack.pop()

    def get_steps(self) -> list:
        return self.steps

    # ─────────────────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _reset(self):
        self.operator_stack.clear()
        self.output_queue = []
        self.steps        = []

    def _shunting_yard(self, tokens: list) -> str:
        """Run the modified (right-associative) shunting yard on a token list."""
        self._reset()
        for token in tokens:
            if is_number(token):
                self.output_queue.append(token)
            elif token == '(':
                self.operator_stack.push(token)
            elif token == ')':
                while (not self.operator_stack.is_empty()
                       and self.operator_stack.peek() != '('):
                    self.output_queue.append(self.operator_stack.pop())
                if not self.operator_stack.is_empty():
                    self.operator_stack.pop()
                else:
                    raise ValueError("Mismatched parentheses")
            elif is_operator(token):
                while (not self.operator_stack.is_empty()
                       and self.operator_stack.peek() != '('
                       and self._should_pop(token, self.operator_stack.peek())):
                    self.output_queue.append(self.operator_stack.pop())
                self.operator_stack.push(token)
            else:
                raise ValueError(f"Invalid token: '{token}'")

        while not self.operator_stack.is_empty():
            op = self.operator_stack.pop()
            if op in '()':
                raise ValueError("Mismatched parentheses")
            self.output_queue.append(op)

        return ' '.join(self.output_queue)

    def _should_pop(self, current_op: str, stack_op: str) -> bool:
        """
        For prefix conversion we flip associativity:
        right-associative treatment for ALL operators so that
        reversing the output yields correct prefix order.
        """
        if not is_operator(stack_op):
            return False
        # strictly greater only (treat everything as right-associative)
        return get_precedence(stack_op) > get_precedence(current_op)

    @staticmethod
    def _reverse_tokens(tokens: list) -> list:
        """
        Reverse a token list and swap '(' ↔ ')'.
        Used as the first step of infix → prefix.
        """
        rev = list(reversed(tokens))
        swap = {'(': ')', ')': '('}
        return [swap.get(t, t) for t in rev]

    @staticmethod
    def _tokenize(expression: str) -> list:
        """
        Tokenize an infix expression into numbers, operators, parentheses.
        Handles multi-digit numbers, decimals, and leading-minus negatives.
        """
        tokens = []
        current = ""

        for char in expression:
            if char.isspace():
                if current:
                    tokens.append(current)
                    current = ""
            elif (char.isdigit() or char == '.'
                  or (char == '-' and not current
                      and (not tokens or tokens[-1] in '(+-*/^%'))):
                current += char
            elif char in '+-*/^%()':
                if current:
                    tokens.append(current)
                    current = ""
                tokens.append(char)
            else:
                raise ValueError(f"Invalid character: '{char}'")

        if current:
            tokens.append(current)

        return tokens