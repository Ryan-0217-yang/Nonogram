"""
Dependency tracking for search optimization.
Corresponds to Dependency.h in the C++ version.
"""

from typing import List
from config import P_SIZE
from bit import LineMask


class DependencyTable:
    """
    Tracks dependencies between cells for optimization.
    Used to determine which cells need to be re-evaluated after changes.
    """
    
    def __init__(self):
        # Track which lines are affected by each point
        self.point_tables: List[List[LineMask]] = [[0] * P_SIZE for _ in range(P_SIZE)]
        
        # Overall update tracking
        self.update_table: LineMask = 0
        self.temp_update_table: LineMask = 0
        self.this_update_table: LineMask = 0
        self.this_temp_table: LineMask = 0


# Global dependency table instance
db_table = DependencyTable()
