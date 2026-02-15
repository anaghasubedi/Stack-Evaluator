"""
Stack Data Structure Implementation
Author: Your Name
Date: 2025-01-13

A basic stack implementation with standard operations.
"""

class Stack:
    """
    A stack data structure that follows LIFO (Last In First Out) principle.
    
    Attributes:
        _items (list): Internal list to store stack elements
    """
    
    def __init__(self):
        """Initialize an empty stack."""
        self._items = []
    
    def push(self, item):
        """
        Add an item to the top of the stack.
        
        Args:
            item: The item to be pushed onto the stack
        
        Returns:
            None
        """
        self._items.append(item)
    
    def pop(self):
        """
        Remove and return the item at the top of the stack.
        
        Returns:
            The item at the top of the stack
        
        Raises:
            IndexError: If the stack is empty
        """
        if self.is_empty():
            raise IndexError("Cannot pop from an empty stack")
        return self._items.pop()
    
    def peek(self):
        """
        Return the item at the top of the stack without removing it.
        
        Returns:
            The item at the top of the stack
        
        Raises:
            IndexError: If the stack is empty
        """
        if self.is_empty():
            raise IndexError("Cannot peek at an empty stack")
        return self._items[-1]
    
    def is_empty(self):
        """
        Check if the stack is empty.
        
        Returns:
            bool: True if stack is empty, False otherwise
        """
        return len(self._items) == 0
    
    def size(self):
        """
        Get the number of items in the stack.
        
        Returns:
            int: The number of items in the stack
        """
        return len(self._items)
    
    def clear(self):
        """Remove all items from the stack."""
        self._items.clear()
    
    def get_items(self):
        """
        Get a copy of all items in the stack.
        
        Returns:
            list: A copy of the stack items
        """
        return self._items.copy()
    
    def __str__(self):
        """
        String representation of the stack.
        
        Returns:
            str: String representation showing stack contents
        """
        return f"Stack({self._items})"
    
    def __repr__(self):
        """
        Official string representation of the stack.
        
        Returns:
            str: String representation for debugging
        """
        return f"Stack({self._items})"
    
    def __len__(self):
        """
        Get the length of the stack.
        
        Returns:
            int: The number of items in the stack
        """
        return len(self._items)