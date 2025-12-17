"""
Core puzzle data structures for Nonogram solver.
Corresponds to Puzzle.h and puzzle.cpp in the C++ version.
"""

from typing import List
from config import P_SIZE, S_SIZE
from bit import LineMask, shift_r, shift_l
from node_queue import NodeQueue


# Square state constants
SQUARE_BLOCK = 1    # Black square
SQUARE_SPACE = 2    # White/empty square
SQUARE_UNKNOWN = 3  # Unknown state
SQUARE = 3          # Mask for square state


class LineNumbers:
    """
    Represents the clue numbers for a single line (row or column).
    Corresponds to LineNumbers struct in C++.
    """
    
    def __init__(self):
        self.m_count: int = 0  # Number of clue numbers
        self.m_numbers: List[int] = [0] * (P_SIZE + 2)  # The clue numbers
        self.m_sum: List[int] = [0] * (P_SIZE + 2)  # Cumulative sums
        self.hash_key: LineMask = 0  # Zobrist hash for this line


class Puzzle:
    """
    Represents a Nonogram puzzle with all its clues.
    Corresponds to Puzzle struct in C++.
    """
    
    def __init__(self, path: str = None):
        """
        Initialize a puzzle, optionally loading from a file.
        
        Args:
            path: Optional path to puzzle file
        """
        self.m_lines: List[LineNumbers] = [LineNumbers() for _ in range(2 * P_SIZE)]
        
        if path is not None:
            read_buffer(self, path)


class Board:
    """
    Represents the current state of the puzzle board.
    Corresponds to Board struct in C++.
    """
    
    def __init__(self):
        self.num_of_square_on_board: int = 0
        # Each element stores the state of P_SIZE cells (2 bits per cell)
        self.col_string: List[LineMask] = [0] * P_SIZE
        self.row_string: List[LineMask] = [0] * P_SIZE


def set_square(x: int, y: int, sol: Board, i_set: LineMask) -> None:
    """
    Set a square on the board to a specific state.
    
    Args:
        x: Column index
        y: Row index
        sol: The board to modify
        i_set: The state to set (SQUARE_BLOCK or SQUARE_SPACE)
    """
    sol.col_string[x] &= ~shift_l(i_set, y)
    sol.row_string[y] &= ~shift_l(i_set, x)


def get_square(x: int, y: int, sol: Board) -> int:
    """
    Get the state of a square on the board.
    
    Args:
        x: Column index
        y: Row index
        sol: The board to query
    
    Returns:
        Square state (SQUARE_BLOCK, SQUARE_SPACE, or SQUARE_UNKNOWN)
    """
    return int(shift_r(sol.row_string[y], x) & SQUARE)


def init_board(sol: Board) -> None:
    """
    Initialize a board to all unknown squares.
    
    Args:
        sol: The board to initialize
    """
    # Set all bits to 1 (SQUARE_UNKNOWN = 3 = 0b11)
    sol.num_of_square_on_board = 0
    for i in range(P_SIZE):
        sol.col_string[i] = (1 << (P_SIZE * 2)) - 1
        sol.row_string[i] = (1 << (P_SIZE * 2)) - 1
    
    NodeQueue.myQ.initial()
    
    # Add all lines to the queue initially
    for i in range(P_SIZE * 2):
        NodeQueue.myQ.push_q(i)


def set_and_flag(i: int, j: int, sol: Board, to_set: int) -> None:
    """
    Set a square and flag the affected lines for processing.
    
    Args:
        i: Column index
        j: Row index
        sol: The board to modify
        to_set: The state to set (SQUARE_BLOCK or SQUARE_SPACE)
    """
    set_square(i, j, sol, to_set)
    sol.num_of_square_on_board += 1
    NodeQueue.myQ.push_q(i)
    NodeQueue.myQ.push_q(j + P_SIZE)


def print_board_taai(sol: Board) -> None:
    """
    Print the board in TAAI format (tab-separated 0s and 1s).
    
    Args:
        sol: The board to print
    """
    for i in range(P_SIZE):
        for j in range(P_SIZE):
            state = get_square(j, i, sol)
            if state == SQUARE_BLOCK:
                print("1", end="")
            elif state == SQUARE_SPACE:
                print("0", end="")
            elif state == SQUARE_UNKNOWN:
                print("-1", end="")
            else:
                print("-2", end="")
            
            if j != P_SIZE - 1:
                print("\t", end="")
            else:
                print()


def read_buffer(quest: Puzzle, s_input: str) -> None:
    """
    Read puzzle data from a buffer string.
    
    Args:
        quest: The puzzle to populate
        s_input: Buffer containing puzzle data
    """
    import hash_table
    
    # Initialize all lines
    for i in range(P_SIZE * 2):
        quest.m_lines[i].m_count = 0
    
    # Parse the buffer - split by 'z' delimiter
    tokens = s_input.split('z')
    
    for count, token in enumerate(tokens):
        if count >= P_SIZE * 2 or not token:
            break
        
        quest.m_lines[count].m_count = len(token)
        quest.m_lines[count].m_numbers[0] = 0
        quest.m_lines[count].m_sum[0] = 0
        quest.m_lines[count].hash_key = 0
        
        tmp_index = 0
        total_sum = 0
        
        for i, char in enumerate(token, 1):
            num = ord(char) - ord('a') + 1
            quest.m_lines[count].m_numbers[i] = num
            total_sum += num
            quest.m_lines[count].m_sum[i] = total_sum
            
            if num > 0:
                quest.m_lines[count].hash_key ^= hash_table.z_hash_key_table[tmp_index][num]
                tmp_index += 1


def print_puzzle(quest: Puzzle, sol: Board) -> None:
    """
    Print the puzzle with current board state (for debugging).
    
    Args:
        quest: The puzzle with clues
        sol: The current board state
    """
    for i in range(P_SIZE):
        for j in range(P_SIZE):
            state = get_square(j, i, sol)
            if state == SQUARE_BLOCK:
                print("■", end="")
            elif state == SQUARE_SPACE:
                print("□", end="")
            elif state == SQUARE_UNKNOWN:
                print("?", end="")
            else:
                print("X", end="")
        
        # Print row clues
        for j in range(quest.m_lines[i + P_SIZE].m_count):
            if quest.m_lines[i + P_SIZE].m_numbers[j] != 0:
                print(f" {quest.m_lines[i + P_SIZE].m_numbers[j]:2}", end="")
        print()
    
    # Print column clues
    for i in range(1, P_SIZE, 2):
        for j in range(P_SIZE):
            if i >= quest.m_lines[j].m_count:
                print("  ", end="")
                continue
            print(f"{quest.m_lines[j].m_numbers[i]:2}", end="")
        print()
