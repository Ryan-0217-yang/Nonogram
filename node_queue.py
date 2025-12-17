"""
Queue implementation for tracking nodes to process.
Corresponds to MyQueue struct in Puzzle.h.
"""

from typing import List
from config import P_SIZE


class MyQueue:
    """
    A specialized queue for tracking which lines need to be processed.
    Uses a circular buffer with tracking of which items are in the queue.
    """
    
    def __init__(self):
        """Initialize an empty queue."""
        self.in_q: List[bool] = [False] * (P_SIZE * 2)
        self.data_q: List[int] = [0] * (P_SIZE * 2 + 1)
        self.f_pos: int = 0  # Front position
        self.r_pos: int = 0  # Rear position
        self.max_size: int = P_SIZE * 2 + 1
    
    def initial(self) -> None:
        """Reset the queue to initial state."""
        self.in_q = [False] * (P_SIZE * 2)
        self.f_pos = 0
        self.r_pos = 0
        self.max_size = P_SIZE * 2 + 1
    
    def is_in_q(self, index: int) -> bool:
        """
        Check if an index is currently in the queue.
        
        Args:
            index: The index to check
        
        Returns:
            True if index is in queue, False otherwise
        """
        return self.in_q[index]
    
    def set_in_q(self, index: int, value: bool) -> None:
        """
        Set whether an index is in the queue.
        
        Args:
            index: The index to set
            value: True if in queue, False otherwise
        """
        self.in_q[index] = value
    
    def push_q(self, index: int) -> None:
        """
        Add an index to the queue if not already present.
        
        Args:
            index: The index to add
        """
        if self.in_q[index]:
            return
        
        self.data_q[self.r_pos] = index
        self.r_pos = (self.r_pos + 1) % self.max_size
        self.set_in_q(index, True)
    
    def pop_and_front(self) -> int:
        """
        Remove and return the front element from the queue.
        
        Returns:
            The front element's index
        """
        u_front = self.data_q[self.f_pos]
        self.f_pos = (self.f_pos + 1) % self.max_size
        self.set_in_q(u_front, False)
        return u_front
    
    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        Returns:
            True if queue is empty, False otherwise
        """
        return self.r_pos == self.f_pos
    
    def clear(self) -> None:
        """Clear all elements from the queue."""
        self.in_q = [False] * (P_SIZE * 2)
        self.f_pos = 0
        self.r_pos = 0


class NodeQueue:
    """
    Global node queue singleton.
    Corresponds to NodeQueue class in C++ with static myQ member.
    """
    myQ = MyQueue()
