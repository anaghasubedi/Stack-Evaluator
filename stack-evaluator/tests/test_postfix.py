"""
Unit tests for Postfix Evaluator
Author: Your Name
Date: 2025-01-13
"""

import pytest
from src.core.postfix_evaluator import PostfixEvaluator


def test_simple_addition():
    """Test simple addition: 5 3 + = 8."""
    evaluator = PostfixEvaluator()
    result = evaluator.evaluate("5 3 +")
    assert result == 8


def test_simple_subtraction():
    """Test simple subtraction: 10 3 - = 7."""
    evaluator = PostfixEvaluator()
    result = evaluator.evaluate("10 3 -")
    assert result == 7


def test_simple_multiplication():
    """Test simple multiplication: 4 5 * = 20."""
    evaluator = PostfixEvaluator()
    result = evaluator.evaluate("4 5 *")
    assert result == 20


def test_simple_division():
    """Test simple division: 10 2 / = 5."""
    evaluator = PostfixEvaluator()
    result = evaluator.evaluate("10 2 /")
    assert result == 5


def test_exponentiation():
    """Test exponentiation: 2 3 ^ = 8."""
    evaluator = PostfixEvaluator()
    result = evaluator.evaluate("2 3 ^")
    assert result == 8


def test_modulo():
    """Test modulo: 10 3 % = 1."""
    evaluator = PostfixEvaluator()
    result = evaluator.evaluate("10 3 %")
    assert result == 1


def test_complex_expression():
    """Test complex expression: 5 3 + 2 * = 16."""
    evaluator = PostfixEvaluator()
    result = evaluator.evaluate("5 3 + 2 *")
    assert result == 16


def test_another_complex_expression():
    """Test: 15 7 1 1 + - / 3 * 2 1 1 + + - = 5."""
    evaluator = PostfixEvaluator()
    result = evaluator.evaluate("15 7 1 1 + - / 3 * 2 1 1 + + -")
    assert result == 5


def test_division_by_zero():
    """Test that division by zero raises ValueError."""
    evaluator = PostfixEvaluator()
    with pytest.raises(ValueError, match="Division by zero"):
        evaluator.evaluate("10 0 /")


def test_insufficient_operands():
    """Test that insufficient operands raises ValueError."""
    evaluator = PostfixEvaluator()
    with pytest.raises(ValueError):
        evaluator.evaluate("5 +")


def test_too_many_operands():
    """Test that too many operands raises ValueError."""
    evaluator = PostfixEvaluator()
    with pytest.raises(ValueError):
        evaluator.evaluate("5 3 2 +")


def test_invalid_token():
    """Test that invalid tokens raise ValueError."""
    evaluator = PostfixEvaluator()
    with pytest.raises(ValueError):
        evaluator.evaluate("5 abc +")


def test_empty_expression():
    """Test that empty expression raises ValueError."""
    evaluator = PostfixEvaluator()
    with pytest.raises(ValueError):
        evaluator.evaluate("")


def test_floating_point_numbers():
    """Test with floating point numbers."""
    evaluator = PostfixEvaluator()
    result = evaluator.evaluate("3.5 2.5 +")
    assert result == 6.0


def test_negative_numbers():
    """Test with negative numbers."""
    evaluator = PostfixEvaluator()
    result = evaluator.evaluate("-5 3 +")
    assert result == -2

def test_steps_tracking():
    """Test that steps are tracked correctly."""
    evaluator = PostfixEvaluator()
    evaluator.evaluate("5 3 + 2 *")
    steps = evaluator.get_steps()
    
    assert len(steps) == 5  
    assert steps[0]['action'] == 'push'
    assert steps[1]['action'] == 'push' 
    assert steps[2]['action'] == 'operate' 
    assert steps[3]['action'] == 'push'  
    assert steps[4]['action'] == 'operate' 