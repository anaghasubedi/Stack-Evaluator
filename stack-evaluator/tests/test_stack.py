"""
Unit tests for Stack data structure
Author: Your Name
Date: 2025-01-13
"""

import pytest
from src.core.stack import Stack


def test_stack_initialization():
    """Test that a new stack is empty."""
    stack = Stack()
    assert stack.is_empty() is True
    assert stack.size() == 0


def test_push_single_item():
    """Test pushing a single item onto the stack."""
    stack = Stack()
    stack.push(5)
    assert stack.is_empty() is False
    assert stack.size() == 1
    assert stack.peek() == 5


def test_push_multiple_items():
    """Test pushing multiple items onto the stack."""
    stack = Stack()
    stack.push(1)
    stack.push(2)
    stack.push(3)
    assert stack.size() == 3
    assert stack.peek() == 3


def test_pop_single_item():
    """Test popping a single item from the stack."""
    stack = Stack()
    stack.push(10)
    item = stack.pop()
    assert item == 10
    assert stack.is_empty() is True


def test_pop_multiple_items():
    """Test popping multiple items maintains LIFO order."""
    stack = Stack()
    stack.push(1)
    stack.push(2)
    stack.push(3)
    
    assert stack.pop() == 3
    assert stack.pop() == 2
    assert stack.pop() == 1
    assert stack.is_empty() is True


def test_pop_empty_stack():
    """Test that popping from empty stack raises IndexError."""
    stack = Stack()
    with pytest.raises(IndexError):
        stack.pop()


def test_peek():
    """Test peeking at the top item without removing it."""
    stack = Stack()
    stack.push(7)
    stack.push(8)
    
    assert stack.peek() == 8
    assert stack.size() == 2  # Size should not change


def test_peek_empty_stack():
    """Test that peeking at empty stack raises IndexError."""
    stack = Stack()
    with pytest.raises(IndexError):
        stack.peek()


def test_clear():
    """Test clearing the stack."""
    stack = Stack()
    stack.push(1)
    stack.push(2)
    stack.push(3)
    
    stack.clear()
    assert stack.is_empty() is True
    assert stack.size() == 0


def test_get_items():
    """Test getting a copy of stack items."""
    stack = Stack()
    stack.push(1)
    stack.push(2)
    stack.push(3)
    
    items = stack.get_items()
    assert items == [1, 2, 3]
    
    # Modify the copy - should not affect the original
    items.append(4)
    assert stack.size() == 3


def test_len():
    """Test __len__ method."""
    stack = Stack()
    assert len(stack) == 0
    
    stack.push(1)
    stack.push(2)
    assert len(stack) == 2


def test_str_representation():
    """Test string representation of stack."""
    stack = Stack()
    stack.push(1)
    stack.push(2)
    
    assert str(stack) == "Stack([1, 2])"


def test_mixed_data_types():
    """Test that stack can hold different data types."""
    stack = Stack()
    stack.push(1)
    stack.push("hello")
    stack.push(3.14)
    stack.push([1, 2, 3])
    
    assert stack.pop() == [1, 2, 3]
    assert stack.pop() == 3.14
    assert stack.pop() == "hello"
    assert stack.pop() == 1