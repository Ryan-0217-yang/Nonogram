"""
Main entry point for Nonogram solver.
Corresponds to main.cpp in the C++ version.

Supports two modes:
1. SOLVE - Solve a single puzzle
2. GENERATE - Generate/verify a puzzle has unique solution
3. Batch mode - Solve multiple puzzles from input file
"""

import sys
import time
from typing import List
from config import (P_SIZE, NUM_OF_QUESTIONS, MODE, INPUT_FILE, OUTPUT_FILE,
                   LOG_FILE, SOLVED, CONFLICT, MANY_SOLUTION)
from puzzle import Puzzle, Board, init_board, print_board_taai
from parsers import parse_taai, parse_one
from hash_table import initial_hash
from search_solver import search_one_solution
from search_verify import search_two_solutions
from search_scheduling import scheduled_solver


def main():
    """Main entry point for the Nonogram solver."""
    # Initialize hash table
    initial_hash()
    
    if len(sys.argv) > 2:
        # Single puzzle mode with SOLVE or GENERATE command
        command = sys.argv[1]
        puzzle_file = sys.argv[2]
        
        puzzle = Puzzle()
        parse_one(puzzle_file, puzzle)
        
        board = Board()
        init_board(board)
        
        if command == "SOLVE":
            # Solve mode - find one solution
            node_count = [0]
            start_time = time.time()
            
            state = search_one_solution(puzzle, board, node_count)
            
            elapsed = time.time() - start_time
            print(f"{node_count[0]}\t{elapsed:.3f}")
            print_board_taai(board)
            sys.stdout.flush()
        
        elif command == "GENERATE":
            # Generate mode - verify unique solution
            node_count = [0]
            is_find_solution = [False]
            one_board = Board()
            init_board(one_board)
            
            state = search_two_solutions(is_find_solution, puzzle, board,
                                        one_board, node_count)
            
            if state == SOLVED:
                print(node_count[0])
            elif state == CONFLICT:
                print(-1)
            elif state == MANY_SOLUTION:
                print(-2)
            
            sys.stdout.flush()
    
    else:
        # Batch mode - solve multiple puzzles
        quests = [Puzzle() for _ in range(NUM_OF_QUESTIONS)]
        parse_taai(INPUT_FILE, quests)
        
        if MODE == 0:
            # Scheduled solver mode
            scheduled_solver(quests, 0)
        else:
            # Direct solving mode
            boards = [Board() for _ in range(NUM_OF_QUESTIONS)]
            
            with open(OUTPUT_FILE, 'w') as output:
                with open(LOG_FILE, 'w') as log:
                    begin_time = time.time()
                    
                    for i in range(NUM_OF_QUESTIONS):
                        node_count = [0]
                        start_time = time.time()
                        
                        if MODE == 1:
                            # Solve for one solution
                            init_board(boards[i])
                            state = search_one_solution(quests[i], boards[i],
                                                       node_count)
                            
                            print(f"#{i + 1} solved!!!", file=sys.stderr)
                            
                            output.write(f"${i + 1}\n")
                            
                            # Redirect stdout to capture print_board_taai
                            old_stdout = sys.stdout
                            sys.stdout = output
                            print_board_taai(boards[i])
                            sys.stdout = old_stdout
                        
                        elif MODE == 2:
                            # Verify unique solution
                            one_board = Board()
                            init_board(one_board)
                            init_board(boards[i])
                            is_find_solution = [False]
                            
                            state = search_two_solutions(is_find_solution,
                                                        quests[i], boards[i],
                                                        one_board, node_count)
                            
                            print(f"#{i + 1} solved!!!", file=sys.stderr)
                            
                            output.write(f"${i + 1}\n")
                            
                            # Print first solution
                            old_stdout = sys.stdout
                            sys.stdout = output
                            print_board_taai(one_board)
                            sys.stdout = old_stdout
                            
                            # If multiple solutions, print second one too
                            if state == MANY_SOLUTION:
                                old_stdout = sys.stdout
                                sys.stdout = output
                                print_board_taai(boards[i])
                                sys.stdout = old_stdout
                        
                        elapsed = time.time() - start_time
                        log.write(f"#{i + 1}\t{elapsed:.6f}\n")
                        output.flush()
                        log.flush()
                    
                    total_time = time.time() - begin_time
                    log.write(f"total time: {total_time:.6f}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
