import pytest
import sys
sys.path.insert(0, 'src')

from core.infix_converter import InfixConverter


def test_simple_addition():
    """Test simple addition: 3 + 5 → 3 5 +"""
    converter = InfixConverter()
    result = converter.convert("3 + 5")
    assert result == "3 5 +"


def test_simple_subtraction():
    """Test simple subtraction: 10 - 3 → 10 3 -"""
    converter = InfixConverter()
    result = converter.convert("10 - 3")
    assert result == "10 3 -"


def test_simple_multiplication():
    """Test simple multiplication: 4 * 5 → 4 5 *"""
    converter = InfixConverter()
    result = converter.convert("4 * 5")
    assert result == "4 5 *"


def test_simple_division():
    """Test simple division: 10 / 2 → 10 2 /"""
    converter = InfixConverter()
    result = converter.convert("10 / 2")
    assert result == "10 2 /"


def test_precedence_multiply_add():
    """Test precedence: 3 + 4 * 2 → 3 4 2 * +"""
    converter = InfixConverter()
    result = converter.convert("3 + 4 * 2")
    assert result == "3 4 2 * +"


def test_precedence_add_multiply():
    """Test precedence: 3 * 4 + 2 → 3 4 * 2 +"""
    converter = InfixConverter()
    result = converter.convert("3 * 4 + 2")
    assert result == "3 4 * 2 +"


def test_parentheses_simple():
    """Test parentheses: (3 + 5) * 2 → 3 5 + 2 *"""
    converter = InfixConverter()
    result = converter.convert("(3 + 5) * 2")
    assert result == "3 5 + 2 *"


def test_parentheses_complex():
    """Test complex parentheses: ((3 + 5) * 2) - 4 → 3 5 + 2 * 4 -"""
    converter = InfixConverter()
    result = converter.convert("((3 + 5) * 2) - 4")
    assert result == "3 5 + 2 * 4 -"


def test_nested_parentheses():
    """Test nested parentheses: (3 + (4 * 5)) → 3 4 5 * +"""
    converter = InfixConverter()
    result = converter.convert("(3 + (4 * 5))")
    assert result == "3 4 5 * +"


def test_exponentiation():
    """Test exponentiation: 2 ^ 3 → 2 3 ^"""
    converter = InfixConverter()
    result = converter.convert("2 ^ 3")
    assert result == "2 3 ^"


def test_exponentiation_right_associative():
    """Test right associativity: 2 ^ 3 ^ 2 → 2 3 2 ^ ^"""
    converter = InfixConverter()
    result = converter.convert("2 ^ 3 ^ 2")
    assert result == "2 3 2 ^ ^"


def test_multiple_operators():
    """Test multiple operators: 3 + 4 * 2 - 5 → 3 4 2 * + 5 -"""
    converter = InfixConverter()
    result = converter.convert("3 + 4 * 2 - 5")
    assert result == "3 4 2 * + 5 -"


def test_division_and_subtraction():
    """Test division and subtraction: 10 / 2 - 3 → 10 2 / 3 -"""
    converter = InfixConverter()
    result = converter.convert("10 / 2 - 3")
    assert result == "10 2 / 3 -"


def test_complex_expression():
    """Test complex expression: (3 + 4) * (5 - 2) → 3 4 + 5 2 - *"""
    converter = InfixConverter()
    result = converter.convert("(3 + 4) * (5 - 2)")
    assert result == "3 4 + 5 2 - *"


def test_floating_point():
    """Test floating point numbers: 3.5 + 2.5 → 3.5 2.5 +"""
    converter = InfixConverter()
    result = converter.convert("3.5 + 2.5")
    assert result == "3.5 2.5 +"


def test_negative_numbers():
    """Test negative numbers: -5 + 3 → -5 3 +"""
    converter = InfixConverter()
    result = converter.convert("-5 + 3")
    assert result == "-5 3 +"


def test_spaces_handling():
    """Test expression with various spacing: 3+5*2 → 3 5 2 * +"""
    converter = InfixConverter()
    result = converter.convert("3+5*2")
    assert result == "3 5 2 * +"


def test_no_spaces():
    """Test expression without spaces: (3+5)*2 → 3 5 + 2 *"""
    converter = InfixConverter()
    result = converter.convert("(3+5)*2")
    assert result == "3 5 + 2 *"


def test_mismatched_parentheses_extra_close():
    """Test mismatched parentheses with extra closing."""
    converter = InfixConverter()
    with pytest.raises(ValueError, match="Mismatched parentheses"):
        converter.convert("3 + 5)")


def test_mismatched_parentheses_extra_open():
    """Test mismatched parentheses with extra opening."""
    converter = InfixConverter()
    with pytest.raises(ValueError, match="Mismatched parentheses"):
        converter.convert("(3 + 5")


def test_empty_expression():
    """Test empty expression."""
    converter = InfixConverter()
    with pytest.raises(ValueError):
        converter.convert("")


def test_invalid_character():
    """Test invalid character in expression."""
    converter = InfixConverter()
    with pytest.raises(ValueError):
        converter.convert("3 + a")


def test_steps_tracking():
    """Test that conversion steps are tracked correctly."""
    converter = InfixConverter()
    converter.convert("3 + 5 * 2")
    steps = converter.get_steps()
    
    # Should have steps for: 3, +, 5, *, 2, and final
    assert len(steps) >= 5
    assert steps[0]['action'] == 'output_number'
    assert steps[1]['action'] == 'process_operator'


def test_convert_and_evaluate():
    """Test combined conversion and evaluation."""
    converter = InfixConverter()
    postfix, result = converter.convert_and_evaluate("(3 + 5) * 2")
    
    assert postfix == "3 5 + 2 *"
    assert result == 16


def test_modulo_operator():
    """Test modulo operator: 10 % 3 → 10 3 %"""
    converter = InfixConverter()
    result = converter.convert("10 % 3")
    assert result == "10 3 %"


def test_all_operators():
    """Test expression with all operators: 2 + 3 * 4 - 5 / 2 ^ 2 → 2 3 4 * + 5 2 2 ^ / -"""
    converter = InfixConverter()
    result = converter.convert("2 + 3 * 4 - 5 / 2 ^ 2")
    assert result == "2 3 4 * + 5 2 2 ^ / -"


def test_step_by_step_generator():
    """Test step-by-step generator."""
    converter = InfixConverter()
    steps = list(converter.convert_step_by_step("3 + 5"))
    
    assert len(steps) > 0
    assert steps[-1]['action'] == 'complete'
    assert 'postfix' in steps[-1]