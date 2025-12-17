"""
Configuration constants for Nonogram solver.
Corresponds to config.h in the C++ version.
"""

# Puzzle size constants
P_SIZE = 25
S_SIZE = P_SIZE * P_SIZE

# Stack depth for search
STACK_MAX_DEPTH = 626

# Search return values
SOLVED = 0
UNSOLVED = 1
CONFLICT = 2
TIMEOUT = 3
MANY_SOLUTION = 4

# Configuration for batch processing
NUM_OF_QUESTIONS = 1000
MODE = 1  # 0 for scheduled solver, 1 for direct solving

# File paths
INPUT_FILE = "input.txt"
OUTPUT_FILE = "solution.txt"
LOG_FILE = "log.txt"

# Node limits for search
LIGHT_NODE_LIMITED = 15000
HEAVY_NODE_LIMITED = 60000

# Schedule configuration
SCHEDULE_NUM_QUESTIONS = 10
