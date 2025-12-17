# Nonogram Solver - Python Implementation

This is a Python conversion of the C++ Nonogram solver from the CGI-LAB. The original C++ version won multiple championships in Computer Olympiad/TAAI/TCGA Nonogram tournaments.

## Files Overview

### Core Modules

1. **config.py** - Configuration constants
   - P_SIZE = 25 (puzzle size)
   - State constants (SOLVED, UNSOLVED, CONFLICT, etc.)
   - File paths and other settings

2. **bit.py** - Bit manipulation utilities
   - LineMask type operations
   - Shift operations (shift_l, shift_r)
   - Bit counting functions

3. **node_queue.py** - Queue implementation
   - MyQueue class for tracking lines to process
   - NodeQueue singleton

4. **puzzle.py** - Core data structures
   - Puzzle class (stores clues)
   - Board class (stores puzzle state)
   - LineNumbers class (stores clues for a line)
   - Board manipulation functions

5. **hash_table.py** - Hash table for caching
   - Zobrist hashing implementation
   - Line solver result caching

6. **parsers.py** - Input file parsing
   - parse_taai() - Parse multiple puzzles
   - parse_one() - Parse single puzzle

7. **dependency.py** - Dependency tracking
   - DependencyTable class for optimization

8. **line_solver.py** - Line solving with DP
   - Dynamic programming algorithm
   - Main line solving logic

### Search Algorithms

9. **search_solver.py** - 2-SAT and DFS search
   - search_one_solution() - Find one solution
   - 2-SAT solver for constraint propagation
   - Depth-first search

10. **search_verify.py** - Multi-solution verification
    - search_two_solutions() - Check for unique solution
    - Used in puzzle generation mode

11. **search_scheduling.py** - Batch processing
    - Resumable solver
    - Scheduled solver for multiple puzzles

12. **main.py** - Main entry point
    - Command-line interface
    - SOLVE and GENERATE modes

## Usage

### Solve a Single Puzzle

```bash
python3 main.py SOLVE puzzle_file.txt
```

Output format:
```
<node_count>    <time_in_seconds>
<25x25 grid of 0s and 1s>
```

### Generate/Verify a Puzzle

```bash
python3 main.py GENERATE puzzle_file.txt
```

Output:
- Positive number: Node count (unique solution found)
- -1: No solution exists (CONFLICT)
- -2: Multiple solutions exist (MANY_SOLUTION)

### Batch Processing

```bash
python3 main.py
```

Reads from `input.txt` and writes solutions to `solution.txt`.

## Input File Format

The input file should contain puzzle descriptions in TAAI format:

```
$1
<column clues: P_SIZE lines>
<row clues: P_SIZE lines>
$2
...
```

Each clue line contains space or tab-separated numbers representing consecutive black squares.

## Algorithm

The solver uses:
1. **Line solving** - Dynamic programming to solve individual rows/columns
2. **2-SAT** - Try both values for uncertain cells and merge results
3. **DFS** - Depth-first search when 2-SAT doesn't fully solve
4. **Zobrist hashing** - Cache line solver results for efficiency

## Python-Specific Notes

- Uses Python's arbitrary precision integers for LineMask (bit operations)
- `copy.deepcopy()` replaces C++ copy constructors
- Lists replace C++ arrays
- Type hints added for better code documentation
- Snake_case naming instead of camelCase

## Compatibility with C++ Version

This Python version implements the same algorithms and data structures as the C++ version, with equivalent functionality:

- Same puzzle size (P_SIZE = 25)
- Same search strategies (line solver, 2-SAT, DFS)
- Same input/output formats
- Same hash table implementation

## References

Based on the algorithm described in:

I-Chen Wu, Der-Johng Sun, Lung-Ping Chen, Kan-Yueh Chen, Ching-Hua Kuo, Hao-Hua Kang, Hung-Hsuan Lin, "An Efficient Approach to Solving Nonograms," IEEE Transactions on Computational Intelligence and AI in Games, vol.5, no.3, pp.251~264, Sept. 2013

## Original C++ Version

See: https://github.com/CGI-LAB/Nonogram
