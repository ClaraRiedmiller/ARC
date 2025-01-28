from typing import Callable, List

class Node:
    def __init__(self, program: List[Callable], cost: float, heuristic_value: float):
        self.program = program 
        self.cost = cost
        self.heuristic_value = heuristic_value
        self.f_value = cost + heuristic_value

    def __lt__(self, other: 'Node') -> bool:
        return self.f_value < other.f_value
    
    def __gt__(self, other: 'Node') -> bool:
        return self.f_value > other.f_value
    