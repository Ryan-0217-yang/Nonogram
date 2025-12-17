"""
Search solver using 2-SAT and DFS.
Corresponds to Search.Solver.cpp and SearchSolver.h in the C++ version.
"""

import copy
import math
from typing import List
from config import P_SIZE, SOLVED, UNSOLVED, CONFLICT, NUM_OF_QUESTIONS, OUTPUT_FILE
from puzzle import (Puzzle, Board, get_square, set_and_flag, print_board_taai,
                    SQUARE_UNKNOWN, SQUARE_BLOCK, SQUARE_SPACE, NodeQueue)
from bit import count64
from line_solver import line_solver
from dependency import db_table


# Static storage for guessed boards
if_guess_black_board: List[List[Board]] = [[Board() for _ in range(P_SIZE)] for _ in range(P_SIZE)]
if_guess_white_board: List[List[Board]] = [[Board() for _ in range(P_SIZE)] for _ in range(P_SIZE)]


class SquareToGo:
    """Represents the two possible branches in DFS search."""
    
    def __init__(self):
        self.first_go: Board = Board()
        self.second_go: Board = Board()


def solve_one_two_sat(problem: Puzzle, correct_board: Board,
                      if_guess_black: Board, if_guess_white: Board,
                      x: int, y: int) -> int:
    """
    Solve using 2-SAT by trying both values for a cell.
    
    Args:
        problem: The puzzle
        correct_board: Current board state (modified in place)
        if_guess_black: Board after guessing black
        if_guess_white: Board after guessing white
        x: Column index
        y: Row index
    
    Returns:
        SOLVED, UNSOLVED, or CONFLICT
    """
    resume_board = copy.deepcopy(correct_board)
    
    # Try guessing white/space
    set_and_flag(x, y, correct_board, SQUARE_SPACE)
    db_table.this_temp_table = 0
    state = line_solver(problem, correct_board)
    space_table = db_table.this_temp_table
    db_table.this_update_table |= space_table
    
    if state == SOLVED:
        return SOLVED
    elif state == CONFLICT:
        # White is conflict, try black
        correct_board.__dict__.update(resume_board.__dict__)
        set_and_flag(x, y, correct_board, SQUARE_BLOCK)
        db_table.this_temp_table = 0
        state = line_solver(problem, correct_board)
        db_table.temp_update_table |= db_table.this_temp_table
        
        if state == SOLVED:
            return SOLVED
        elif state == CONFLICT:
            return CONFLICT
    else:
        # White is unsolved, save it and try black
        if_guess_white.__dict__.update(correct_board.__dict__)
        correct_board.__dict__.update(resume_board.__dict__)
        
        set_and_flag(x, y, correct_board, SQUARE_BLOCK)
        db_table.this_temp_table = 0
        state = line_solver(problem, correct_board)
        db_table.this_update_table |= db_table.this_temp_table
        
        if state == SOLVED:
            return SOLVED
        elif state == CONFLICT:
            # Black is conflict, use white
            correct_board.__dict__.update(if_guess_white.__dict__)
            db_table.temp_update_table |= space_table
        else:
            # Both are unsolved, try to merge
            if_guess_black.__dict__.update(correct_board.__dict__)
            correct_board.__dict__.update(resume_board.__dict__)
            
            is_update = False
            for i in range(P_SIZE):
                # Merge rows
                one_row = if_guess_black.row_string[i] | if_guess_white.row_string[i]
                if one_row != correct_board.row_string[i]:
                    is_update = True
                    correct_board.num_of_square_on_board += count64(
                        correct_board.row_string[i] ^ one_row)
                    correct_board.row_string[i] &= one_row
                    NodeQueue.myQ.push_q(i + P_SIZE)
                
                # Merge columns
                one_col = if_guess_black.col_string[i] | if_guess_white.col_string[i]
                if one_col != correct_board.col_string[i]:
                    is_update = True
                    correct_board.col_string[i] &= one_col
                    NodeQueue.myQ.push_q(i)
            
            if is_update:
                db_table.this_temp_table = 0
                state = line_solver(problem, correct_board)
                db_table.temp_update_table |= db_table.this_temp_table
                
                if state == SOLVED:
                    return SOLVED
                elif state == CONFLICT:
                    return CONFLICT
    
    return UNSOLVED


def two_sat_solver(problem: Puzzle, correct_board: Board,
                   where_can_i_go: SquareToGo) -> int:
    """
    Apply 2-SAT solver to all unknown cells.
    
    Args:
        problem: The puzzle
        correct_board: Current board state (modified in place)
        where_can_i_go: Output for next search branches
    
    Returns:
        SOLVED, UNSOLVED, or CONFLICT
    """
    db_table.update_table = 0
    
    while True:
        db_table.temp_update_table = 0
        resume_board = copy.deepcopy(correct_board)
        
        for i in range(P_SIZE):
            for j in range(P_SIZE):
                if (get_square(i, j, correct_board) == SQUARE_UNKNOWN and
                    ((db_table.update_table & db_table.point_tables[i][j]) or
                     db_table.update_table == 0)):
                    
                    db_table.this_update_table = 0
                    state = solve_one_two_sat(problem, correct_board,
                                             if_guess_black_board[i][j],
                                             if_guess_white_board[i][j],
                                             i, j)
                    
                    if state == SOLVED:
                        return SOLVED
                    elif state == CONFLICT:
                        return CONFLICT
                    
                    db_table.point_tables[i][j] = db_table.this_update_table
        
        db_table.update_table |= db_table.temp_update_table
        
        if db_table.temp_update_table == 0:
            # 2-SAT stalled, need to choose a cell
            x, y = 0, 0
            max_score = -1.0
            
            for i in range(P_SIZE):
                for j in range(P_SIZE):
                    if get_square(i, j, correct_board) == SQUARE_UNKNOWN:
                        score = (min(if_guess_black_board[i][j].num_of_square_on_board,
                                   if_guess_white_board[i][j].num_of_square_on_board) +
                                1.85 * math.log(1.0 + abs(
                                    if_guess_black_board[i][j].num_of_square_on_board -
                                    if_guess_white_board[i][j].num_of_square_on_board)))
                        
                        if score > max_score:
                            x, y = i, j
                            max_score = score
            
            where_can_i_go.first_go = copy.deepcopy(if_guess_white_board[x][y])
            where_can_i_go.second_go = copy.deepcopy(if_guess_black_board[x][y])
            
            return UNSOLVED
    
    return UNSOLVED


def search_solver_dfs(problem: Puzzle, solution: Board, node_count: List[int]) -> int:
    """
    Depth-first search for puzzle solution.
    
    Args:
        problem: The puzzle
        solution: Current board state (modified in place)
        node_count: List with single element tracking node count
    
    Returns:
        SOLVED or CONFLICT
    """
    where_can_i_go = SquareToGo()
    
    node_count[0] += 1
    state = two_sat_solver(problem, solution, where_can_i_go)
    
    if state == SOLVED:
        return SOLVED
    elif state == CONFLICT:
        return CONFLICT
    
    # Try first branch
    solution.__dict__.update(where_can_i_go.first_go.__dict__)
    state = search_solver_dfs(problem, solution, node_count)
    
    if state == SOLVED:
        return SOLVED
    else:
        # Try second branch
        solution.__dict__.update(where_can_i_go.second_go.__dict__)
        return search_solver_dfs(problem, solution, node_count)


def search_one_solution(problem: Puzzle, solution: Board, node_count: List[int]) -> int:
    """
    Search for one solution to the puzzle.
    
    Args:
        problem: The puzzle
        solution: Board to populate with solution (modified in place)
        node_count: List with single element tracking node count
    
    Returns:
        SOLVED, UNSOLVED, or CONFLICT
    """
    # Initialize dependency tables
    for i in range(P_SIZE):
        for j in range(P_SIZE):
            db_table.point_tables[i][j] = 0
    
    state = line_solver(problem, solution)
    
    if state == SOLVED:
        return SOLVED
    elif state == CONFLICT:
        return CONFLICT
    else:
        return search_solver_dfs(problem, solution, node_count)


def write_result() -> None:
    """
    Write results from individual solution files to final output.
    Used in scheduled solver mode.
    """
    with open(OUTPUT_FILE, 'w') as output:
        for i in range(NUM_OF_QUESTIONS):
            sol_file = f"sol{i + 1}.txt"
            output.write(f"${i + 1}\n")
            
            try:
                with open(sol_file, 'r') as input_file:
                    output.write(input_file.read())
            except FileNotFoundError:
                # Write empty solution
                for j in range(P_SIZE):
                    for k in range(P_SIZE):
                        if k < P_SIZE - 1:
                            output.write("0\t")
                        else:
                            output.write("0\n")
