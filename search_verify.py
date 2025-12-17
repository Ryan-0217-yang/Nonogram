"""
Multi-solution verification for puzzle generation.
Corresponds to Search.Verify.cpp in the C++ version.
"""

import copy
import math
from typing import List
from config import P_SIZE, S_SIZE, SOLVED, UNSOLVED, CONFLICT, MANY_SOLUTION
from puzzle import (Puzzle, Board, get_square, set_and_flag, NodeQueue,
                    SQUARE_UNKNOWN, SQUARE_BLOCK, SQUARE_SPACE)
from bit import count64
from line_solver import line_solver


# Static storage for guessed boards (separate from search_solver)
if_guess_black_board: List[List[Board]] = [[Board() for _ in range(P_SIZE)] for _ in range(P_SIZE)]
if_guess_white_board: List[List[Board]] = [[Board() for _ in range(P_SIZE)] for _ in range(P_SIZE)]


class SquareToGo:
    """Represents the two possible branches in DFS search."""
    
    def __init__(self):
        self.first_go: Board = Board()
        self.second_go: Board = Board()


def solve_one_two_sat_verify(problem: Puzzle, correct_board: Board,
                             one_solution: Board, is_find_solution: List[bool],
                             if_guess_black: Board, if_guess_white: Board,
                             x: int, y: int) -> int:
    """
    2-SAT solver for verification (checks for multiple solutions).
    
    Args:
        problem: The puzzle
        correct_board: Current board state (modified in place)
        one_solution: Previously found solution
        is_find_solution: List with boolean indicating if solution found
        if_guess_black: Board after guessing black
        if_guess_white: Board after guessing white
        x: Column index
        y: Row index
    
    Returns:
        SOLVED, UNSOLVED, CONFLICT, or MANY_SOLUTION
    """
    resume_board = copy.deepcopy(correct_board)
    
    # Try white/space
    set_and_flag(x, y, correct_board, SQUARE_SPACE)
    state1 = line_solver(problem, correct_board)
    if_guess_white.__dict__.update(correct_board.__dict__)
    
    # Try black
    correct_board.__dict__.update(resume_board.__dict__)
    set_and_flag(x, y, correct_board, SQUARE_BLOCK)
    state2 = line_solver(problem, correct_board)
    if_guess_black.__dict__.update(correct_board.__dict__)
    
    correct_board.__dict__.update(resume_board.__dict__)
    
    # Check if both lead to solutions (multiple solutions exist)
    if state1 == SOLVED and state2 == SOLVED:
        one_solution.__dict__.update(if_guess_black.__dict__)
        correct_board.__dict__.update(if_guess_white.__dict__)
        return MANY_SOLUTION
    
    # Both unsolved or conflict
    elif state1 != SOLVED and state2 != SOLVED:
        if state1 == CONFLICT and state2 == CONFLICT:
            return CONFLICT
        elif state1 == CONFLICT:
            correct_board.__dict__.update(if_guess_black.__dict__)
        elif state2 == CONFLICT:
            correct_board.__dict__.update(if_guess_white.__dict__)
        elif state1 == UNSOLVED and state2 == UNSOLVED:
            # Try to merge
            is_update = False
            for i in range(P_SIZE):
                one_row = if_guess_black.row_string[i] | if_guess_white.row_string[i]
                if one_row != correct_board.row_string[i]:
                    is_update = True
                    correct_board.num_of_square_on_board += count64(
                        correct_board.row_string[i] ^ one_row)
                    correct_board.row_string[i] &= one_row
                    NodeQueue.myQ.push_q(i + P_SIZE)
                
                one_col = if_guess_black.col_string[i] | if_guess_white.col_string[i]
                if one_col != correct_board.col_string[i]:
                    is_update = True
                    correct_board.col_string[i] &= one_col
                    NodeQueue.myQ.push_q(i)
            
            if is_update:
                state = line_solver(problem, correct_board)
                if state == SOLVED:
                    return SOLVED
                elif state == CONFLICT:
                    return CONFLICT
    
    # One solved, one not
    elif state1 == SOLVED or state2 == SOLVED:
        if state1 == CONFLICT:
            correct_board.__dict__.update(if_guess_black.__dict__)
            return SOLVED
        elif state2 == CONFLICT:
            correct_board.__dict__.update(if_guess_white.__dict__)
            return SOLVED
        else:
            # One is solved, one is unsolved
            if state1 == SOLVED:
                resume_board.__dict__.update(if_guess_white.__dict__)
            else:
                resume_board.__dict__.update(if_guess_black.__dict__)
            
            if not is_find_solution[0]:
                is_find_solution[0] = True
                one_solution.__dict__.update(resume_board.__dict__)
                return UNSOLVED
            else:
                # Check if it's a different solution
                if resume_board.row_string != one_solution.row_string:
                    correct_board.__dict__.update(resume_board.__dict__)
                    return MANY_SOLUTION
                else:
                    return UNSOLVED
    
    return UNSOLVED


def two_sat_solver_verify(problem: Puzzle, correct_board: Board,
                          one_solution: Board, is_find_solution: List[bool],
                          where_can_i_go: SquareToGo) -> int:
    """
    2-SAT solver for verification mode.
    
    Args:
        problem: The puzzle
        correct_board: Current board state (modified in place)
        one_solution: Previously found solution
        is_find_solution: List with boolean indicating if solution found
        where_can_i_go: Output for next search branches
    
    Returns:
        SOLVED, UNSOLVED, CONFLICT, or MANY_SOLUTION
    """
    # Check if already solved
    if correct_board.num_of_square_on_board == S_SIZE:
        if not is_find_solution[0]:
            is_find_solution[0] = True
            one_solution.__dict__.update(correct_board.__dict__)
            return SOLVED
        else:
            # Check if different solution
            if correct_board.row_string != one_solution.row_string:
                return MANY_SOLUTION
            else:
                return SOLVED
    
    while True:
        resume_board = copy.deepcopy(correct_board)
        
        for i in range(P_SIZE):
            for j in range(P_SIZE):
                if get_square(i, j, correct_board) == SQUARE_UNKNOWN:
                    state = solve_one_two_sat_verify(
                        problem, correct_board, one_solution, is_find_solution,
                        if_guess_black_board[i][j], if_guess_white_board[i][j],
                        i, j)
                    
                    if state == SOLVED:
                        if not is_find_solution[0]:
                            is_find_solution[0] = True
                            one_solution.__dict__.update(correct_board.__dict__)
                            return SOLVED
                        else:
                            if correct_board.row_string != one_solution.row_string:
                                return MANY_SOLUTION
                            else:
                                return SOLVED
                    elif state == CONFLICT:
                        return CONFLICT
                    elif state == MANY_SOLUTION:
                        return MANY_SOLUTION
        
        # Check if board changed
        if resume_board.row_string == correct_board.row_string:
            # Need to pick a cell
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


def verified_many_solution(is_find_solution: List[bool], problem: Puzzle,
                           solution: Board, one_solution: Board,
                           node_count: List[int]) -> int:
    """
    Verify if puzzle has multiple solutions.
    
    Args:
        is_find_solution: List with boolean indicating if solution found
        problem: The puzzle
        solution: Current board state (modified in place)
        one_solution: Storage for first solution found
        node_count: List with single element tracking node count
    
    Returns:
        SOLVED, CONFLICT, or MANY_SOLUTION
    """
    node_count[0] += 1
    where_can_i_go = SquareToGo()
    
    state = two_sat_solver_verify(problem, solution, one_solution,
                                  is_find_solution, where_can_i_go)
    
    if state == SOLVED:
        return SOLVED
    elif state == CONFLICT:
        return CONFLICT
    elif state == MANY_SOLUTION:
        return MANY_SOLUTION
    
    # Try first branch
    solution.__dict__.update(where_can_i_go.first_go.__dict__)
    state1 = verified_many_solution(is_find_solution, problem, solution,
                                    one_solution, node_count)
    
    if state1 == MANY_SOLUTION:
        return MANY_SOLUTION
    
    # Try second branch
    solution.__dict__.update(where_can_i_go.second_go.__dict__)
    state2 = verified_many_solution(is_find_solution, problem, solution,
                                    one_solution, node_count)
    
    if state2 == MANY_SOLUTION:
        return MANY_SOLUTION
    
    if state1 == CONFLICT and state2 == CONFLICT:
        return CONFLICT
    elif state1 == SOLVED and state2 == SOLVED:
        return MANY_SOLUTION
    else:
        return SOLVED


def search_two_solutions(is_find_solution: List[bool], problem: Puzzle,
                        solution: Board, one_solution: Board,
                        node_count: List[int]) -> int:
    """
    Search for two different solutions to verify uniqueness.
    
    Args:
        is_find_solution: List with boolean indicating if solution found
        problem: The puzzle
        solution: Board to search from (modified in place)
        one_solution: Storage for first solution found
        node_count: List with single element tracking node count
    
    Returns:
        SOLVED, CONFLICT, or MANY_SOLUTION
    """
    state = line_solver(problem, solution)
    
    if state == SOLVED:
        return SOLVED
    elif state == CONFLICT:
        return CONFLICT
    else:
        return verified_many_solution(is_find_solution, problem, solution,
                                     one_solution, node_count)
