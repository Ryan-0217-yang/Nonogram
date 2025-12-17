"""
Input file parsing functions for Nonogram puzzles.
Corresponds to Parsers.h and Parsers.cpp in the C++ version.
"""

from typing import List
from config import P_SIZE, NUM_OF_QUESTIONS
from puzzle import Puzzle, read_buffer


def parse_taai(path: str, quests: List[Puzzle]) -> None:
    """
    Parse multiple puzzles from a TAAI format file.
    
    Args:
        path: Path to the input file
        quests: List to populate with parsed puzzles
    """
    with open(path, 'r') as fp:
        puz_buf = []
        
        for i in range(NUM_OF_QUESTIONS):
            # Read puzzle number line (starts with $)
            line = fp.readline()
            
            # Read P_SIZE * 2 lines (column clues + row clues)
            for j in range(P_SIZE * 2):
                line = fp.readline().strip()
                
                if not line:
                    # Empty line
                    puz_buf.append(chr(ord('a') - 1))
                else:
                    # Parse tab or space separated numbers
                    tokens = line.replace('\t', ' ').split()
                    for token in tokens:
                        try:
                            num = int(token)
                            puz_buf.append(chr(num + ord('a') - 1))
                        except ValueError:
                            pass
                
                puz_buf.append('z')  # Delimiter between lines
            
            # Convert buffer to string and parse
            puz_str = ''.join(puz_buf)
            read_buffer(quests[i], puz_str)
            puz_buf.clear()


def parse_one(path: str, quest: Puzzle) -> None:
    """
    Parse a single puzzle from a file.
    
    Args:
        path: Path to the input file
        quest: Puzzle object to populate
    """
    with open(path, 'r') as fp:
        puz_buf = []
        
        # Read P_SIZE * 2 lines (column clues + row clues)
        for j in range(P_SIZE * 2):
            line = fp.readline().strip()
            
            if not line:
                # Empty line
                puz_buf.append(chr(ord('a') - 1))
            else:
                # Parse tab or space separated numbers
                tokens = line.replace('\t', ' ').split()
                for token in tokens:
                    try:
                        num = int(token)
                        puz_buf.append(chr(num + ord('a') - 1))
                    except ValueError:
                        pass
            
            puz_buf.append('z')  # Delimiter between lines
        
        # Convert buffer to string and parse
        puz_str = ''.join(puz_buf)
        read_buffer(quest, puz_str)
