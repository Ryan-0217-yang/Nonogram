"""
Line solver using dynamic programming.
Corresponds to lineSolver.cpp and LineSolver.h in the C++ version.
"""

from typing import List
from config import P_SIZE, S_SIZE, SOLVED, UNSOLVED, CONFLICT
from puzzle import (Puzzle, Board, LineNumbers, set_square, NodeQueue,
                    SQUARE_BLOCK, SQUARE_SPACE, SQUARE_UNKNOWN, SQUARE)
from bit import LineMask, shift_l, shift_r, count64
from hash_table import find_hash, insert_hash
from dependency import db_table


# DP table for line solving
# Dimensions: [P_SIZE+1][(P_SIZE+1)//2]
dp_table: List[List[int]] = [[UNSOLVED] * ((P_SIZE + 1) // 2) for _ in range(P_SIZE + 1)]


# Pre-computed block masks for different lengths
block_mask = [
    0, 0x1, 0x5, 0x15, 0x55, 0x155, 0x555, 0x1555, 0x5555,
    0x15555, 0x55555, 0x155555, 0x555555, 0x1555555, 0x5555555,
    0x15555555, 0x55555555, 0x155555555, 0x555555555, 0x1555555555,
    0x5555555555, 0x15555555555, 0x55555555555, 0x155555555555,
    0x555555555555, 0x1555555555555
]

new_block_mask = [
    0x2, 0x6, 0x16, 0x56, 0x156, 0x556, 0x1556, 0x5556,
    0x15556, 0x55556, 0x155556, 0x555556, 0x1555556, 0x5555556,
    0x15555556, 0x55555556, 0x155555556, 0x555555556, 0x1555555556,
    0x5555555556, 0x15555555556, 0x55555555556, 0x155555555556,
    0x555555555556, 0x1555555555556, 0x5555555555556, 0x15555555555556,
    0x55555555555556
]


def sprint_settle(des: LineNumbers, in_string: LineMask, i: int, j: int,
                  settle_string: List[LineMask]) -> bool:
    global dp_table

    # Base cases
    if (i == -1 or i == 0) and j == 0:
        return True

    if i < 0:
        return False

    # 新增：當 i = 0 但 j != 0 時，表示位置不夠放剩餘的方塊
    if i == 0:
        dp_table[i][j] = CONFLICT
        return False

    if dp_table[i][j] == CONFLICT:
        return False

    if dp_table[i][j] == SOLVED:
        return True

    # Get current square state (現在 i >= 1，所以 i-1 >= 0)
    now_square = int(shift_r(in_string, i - 1) & SQUARE)
    
    is_valid = False
    
    # Try placing a block (only if j > 0, i.e., there are blocks remaining)
    if j > 0:
        # Check if we can place a block here
        position_of_block = i - des.m_numbers[j]
        if position_of_block < 0:
            dp_table[i][j] = CONFLICT
            return False
        
        # Create mask for this block
        this_block_mask = shift_l(block_mask[des.m_numbers[j]], position_of_block)
        this_block_mask |= shift_l(SQUARE_SPACE, position_of_block - 1)
        
        # Check if block placement is valid
        should_try_block = True
        if this_block_mask & (~in_string):
            should_try_block = False
        
        # Try placing the block
        if now_square != SQUARE_SPACE and should_try_block:
            if sprint_settle(des, in_string, position_of_block - 1, j - 1, settle_string):
                settle_string[0] |= this_block_mask
                is_valid = True
    
    # Try placing a space
    if now_square != SQUARE_BLOCK and i > des.m_sum[j]:
        if sprint_settle(des, in_string, i - 1, j, settle_string):
            settle_string[0] |= shift_l(SQUARE_SPACE, i - 1)
            is_valid = True
    
    dp_table[i][j] = SOLVED if is_valid else CONFLICT
    return is_valid


def line_solver(prob: Puzzle, sol: Board) -> int:
    """
    Main line solver function. Processes lines until no more changes occur.
    
    Args:
        prob: The puzzle with clues
        sol: The current board state (modified in place)
    
    Returns:
        SOLVED, UNSOLVED, or CONFLICT
    """
    global dp_table
    
    state = UNSOLVED
    
    while not NodeQueue.myQ.is_empty():
        i = NodeQueue.myQ.pop_and_front()
        
        # Track this line in dependency table
        db_table.this_temp_table |= (1 << i)
        
        # Get the appropriate string (column or row)
        if i < P_SIZE:
            current_string = sol.col_string[i]
        else:
            current_string = sol.row_string[i - P_SIZE]
        
        # Try to find cached result
        found, settle = find_hash(prob.m_lines[i], current_string)
        
        if not found:
            # Reset DP table
            for row in range(P_SIZE + 1):
                for col in range((P_SIZE + 1) // 2):
                    dp_table[row][col] = UNSOLVED
            
            # Solve this line
            settle_list = [0]
            success = sprint_settle(prob.m_lines[i], current_string,
                                   P_SIZE, prob.m_lines[i].m_count, settle_list)
            settle = settle_list[0]
            
            if not success:
                NodeQueue.myQ.clear()
                return CONFLICT
            
            # Cache the result
            insert_hash(prob.m_lines[i], current_string, settle)
        
        # Apply changes
        if i < P_SIZE:
            change = sol.col_string[i] ^ settle
        else:
            change = sol.row_string[i - P_SIZE] ^ settle
        
        j = 0
        
        while change != 0 and j < P_SIZE:
            temp = change & 3
            if temp:
                sol.num_of_square_on_board += 1
                
                if i < P_SIZE:
                    # Column line
                    set_square(i, j, sol, temp)
                    NodeQueue.myQ.push_q(j + P_SIZE)
                else:
                    # Row line
                    set_square(j, i - P_SIZE, sol, temp)
                    NodeQueue.myQ.push_q(j)
            
            change >>= 2
            j += 1
    
    # Check if solved
    if sol.num_of_square_on_board == S_SIZE:
        return SOLVED
    else:
        return UNSOLVED
