from typing import Any

class Node:
    def __init__(self, program: Any, cost: float):
        self.program = program
        self.cost = cost

    def __lt__(self, other: 'Node') -> bool:
        return self.cost < other.cost
    
    def __gt__(self, other: 'Node') -> bool:
        return self.cost > other.cost
    