"""
Resumable and scheduled solver for batch processing.
Corresponds to Search.Scheduling.cpp in the C++ version.
"""

import pickle
import time
from typing import List, Optional
from config import (P_SIZE, STACK_MAX_DEPTH, SOLVED, UNSOLVED, CONFLICT, TIMEOUT,
                   NUM_OF_QUESTIONS, LIGHT_NODE_LIMITED, HEAVY_NODE_LIMITED,
                   SCHEDULE_NUM_QUESTIONS)
from puzzle import Puzzle, Board, init_board, print_board_taai
from line_solver import line_solver
from search_solver import two_sat_solver, SquareToGo, write_result
from dependency import db_table


class SearchStack:
    """
    State for resumable DFS search.
    Can be saved to disk and resumed later.
    """
    
    def __init__(self):
        self.step: List[int] = [0] * STACK_MAX_DEPTH
        self.state: int = UNSOLVED
        self.depth: int = 0
        self.node_limit: int = 0
        self.node_count: int = 0
        self.solution: Board = Board()
        self.where_can_i_go: List[SquareToGo] = [SquareToGo() for _ in range(STACK_MAX_DEPTH)]
    
    def initial(self) -> None:
        """Initialize the search stack."""
        self.step = [0] * STACK_MAX_DEPTH
        init_board(self.solution)
        self.depth = 0
        self.node_count = 0
        self.state = UNSOLVED
    
    def save(self, filename: str) -> None:
        """
        Save the search state to a file.
        
        Args:
            filename: Path to save file
        """
        with open(filename, 'wb') as fp:
            pickle.dump(self, fp)
    
    def load(self, filename: str) -> bool:
        """
        Load the search state from a file.
        
        Args:
            filename: Path to load file
        
        Returns:
            True if successfully loaded, False if file doesn't exist
        """
        try:
            with open(filename, 'rb') as fp:
                loaded = pickle.load(fp)
                self.__dict__.update(loaded.__dict__)
                return True
        except FileNotFoundError:
            return False


def resumable_dfs(filename: str, problem: Puzzle, stack: SearchStack) -> int:
    """
    Perform one step of resumable DFS.
    
    Args:
        filename: File to save state to if timeout
        problem: The puzzle
        stack: Search state (modified in place)
    
    Returns:
        SOLVED, UNSOLVED, CONFLICT, or TIMEOUT
    """
    step = stack.step[stack.depth]
    
    if step == 0:
        # Initial state - run 2-SAT solver
        stack.state = two_sat_solver(problem, stack.solution,
                                     stack.where_can_i_go[stack.depth])
        stack.node_limit -= 1
        stack.node_count += 1
        
        if stack.state == SOLVED:
            return stack.state
        elif stack.state == CONFLICT:
            stack.step[stack.depth] = 0
            stack.depth -= 1
        else:
            # Go to first branch
            stack.solution.__dict__.update(
                stack.where_can_i_go[stack.depth].first_go.__dict__)
            stack.step[stack.depth] = 1
            stack.depth += 1
        
        if stack.node_limit < 0:
            stack.save(filename)
            return TIMEOUT
    
    elif step == 1:
        # First branch failed, try second
        stack.solution.__dict__.update(
            stack.where_can_i_go[stack.depth].second_go.__dict__)
        stack.step[stack.depth] = 2
        stack.depth += 1
    
    elif step == 2:
        # Both branches failed, backtrack
        stack.step[stack.depth] = 0
        stack.depth -= 1
    
    else:
        # Should not happen
        print(f"Bug appeared at depth {stack.depth}")
        stack.depth -= 1
    
    if stack.depth < 0:
        return CONFLICT
    else:
        return UNSOLVED


def resumable_solver(filename: str, problem: Puzzle, node_limit: int,
                     stack: SearchStack) -> int:
    """
    Run a resumable solver that can be paused and resumed.
    
    Args:
        filename: File to save/load state
        problem: The puzzle
        node_limit: Maximum nodes to explore before timeout
        stack: Search state (modified in place)
    
    Returns:
        SOLVED, TIMEOUT, or CONFLICT
    """
    # Try to load existing state
    if not stack.load(filename):
        # No saved state, start fresh
        stack.initial()
        state = line_solver(problem, stack.solution)
        if state == SOLVED:
            return SOLVED
    
    stack.node_limit = node_limit
    
    # Run DFS steps until done or timeout
    state = UNSOLVED
    while state == UNSOLVED:
        state = resumable_dfs(filename, problem, stack)
    
    return state


class QuestionStruct:
    """Metadata for a question in scheduled solving."""
    
    def __init__(self, number: int):
        self.is_solved: bool = False
        self.number: int = number
        self.score: int = 0


def scheduled_solver(problems: List[Puzzle], node_limit: int) -> None:
    """
    Solve multiple puzzles with scheduling and time management.
    
    Args:
        problems: List of puzzles to solve
        node_limit: Initial node limit per puzzle
    """
    stack = SearchStack()
    
    with open("logS.txt", 'w') as fp_log:
        all_questions = [QuestionStruct(i) for i in range(NUM_OF_QUESTIONS)]
        
        begin = time.time()
        count = 0
        first = True
        
        while count != NUM_OF_QUESTIONS:
            index = 0
            
            for i in range(NUM_OF_QUESTIONS):
                start_time = time.time()
                
                if not all_questions[i].is_solved:
                    index += 1
                    question_id = all_questions[i].number
                    
                    filename = f"{question_id}.dat"
                    result = resumable_solver(filename, problems[question_id],
                                             node_limit, stack)
                    
                    if result == SOLVED:
                        print(f"#{question_id + 1} solved!!!", flush=True)
                        
                        sol_filename = f"sol{question_id + 1}.txt"
                        with open(sol_filename, 'w') as sol_file:
                            import sys
                            old_stdout = sys.stdout
                            sys.stdout = sol_file
                            print_board_taai(stack.solution)
                            sys.stdout = old_stdout
                        
                        all_questions[i].is_solved = True
                        count += 1
                    
                    if node_limit == 0:
                        all_questions[i].score = stack.solution.num_of_square_on_board
                    
                    elapsed = time.time() - start_time
                    fp_log.write(f"#{question_id + 1}\t{elapsed:.3f}\t{result}\n")
                
                if not first and index >= SCHEDULE_NUM_QUESTIONS:
                    break
            
            fp_log.write(f"////// solved: {count}, limited: {node_limit} //////\n")
            fp_log.flush()
            
            if first:
                # Sort by score
                all_questions.sort(key=lambda q: q.score, reverse=True)
                
                if node_limit == LIGHT_NODE_LIMITED:
                    first = False
                    node_limit = HEAVY_NODE_LIMITED
                else:
                    node_limit = LIGHT_NODE_LIMITED
        
        write_result()
        total_time = time.time() - begin
        fp_log.write(f"total time usage = {total_time:.3f}\n")
