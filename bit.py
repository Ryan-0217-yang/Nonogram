"""
Bit manipulation utilities for Nonogram solver.
Corresponds to bit.h in the C++ version.

In Python, we use int for LineMask (Python's arbitrary precision integers).
"""

from config import P_SIZE

# Type alias for line mask (in Python, just use int)
LineMask = int

# Bit mask constants
MASK50 = 1125899906842623  # 0x3FFFFFFFFFFFF in hex


def shift_r(a: LineMask, s: int) -> LineMask:
    """
    Shift right by s positions (each position is 2 bits).
    Equivalent to C++ SHIFT_R macro.
    
    Args:
        a: The bit mask to shift
        s: Number of positions to shift (each position = 2 bits)
    
    Returns:
        Shifted bit mask
    """
    return (a >> (s * 2)) & ((1 << (P_SIZE * 2)) - 1)


def shift_l(a: LineMask, s: int) -> LineMask:
    """
    Shift left by s positions (each position is 2 bits).
    Equivalent to C++ SHIFT_L macro.
    
    Args:
        a: The bit mask to shift
        s: Number of positions to shift (each position = 2 bits)
    
    Returns:
        Shifted bit mask
    """
    return (a << (s * 2)) & ((1 << (P_SIZE * 2)) - 1)


def count64(block: LineMask) -> int:
    """
    Count the number of set bits in a 64-bit integer.
    Equivalent to C++ count64 inline function.
    
    This uses a fast bit counting algorithm.
    
    Args:
        block: The bit mask to count
    
    Returns:
        Number of set bits
    """
    block = block & 0xFFFFFFFFFFFFFFFF  # Ensure 64-bit
    block -= ((block >> 1) & 0x5555555555555555)
    block = ((block >> 2) & 0x3333333333333333) + (block & 0x3333333333333333)
    return (((block + (block >> 4)) & 0x0F0F0F0F0F0F0F0F) * 0x0101010101010101) >> 56


def COUNT64(x: LineMask) -> int:
    """
    Count bits in x masked with MASK50.
    Equivalent to C++ COUNT64 macro.
    
    Args:
        x: The bit mask to count
    
    Returns:
        Number of set bits in masked value
    """
    return count64(x & MASK50)
