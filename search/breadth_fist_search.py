from collections import deque
from typing import Any, Callable, List, Tuple
from dsl.dsl import Constraints

class BreadthFirstSearch:
    def __init__(
        self,
        problem: List[Tuple[Any, Any, Constraints]],
        goal_test: Callable[[Any], bool],
        operators: List [Callable],
        max_depth: int
    ):
        """
        Initialize the Best-First Search class.

        Args:
            initial_state: The starting point of the search (e.g., empty program).
            goal_test: A function to check if a given state satisfies the synthesis goal.
            heuristic: A function to compute the estimated cost to the goal from a given state.
            expand: A function to generate successor states and their associated costs.
        """
        self.problem = problem
        self.goal_test = goal_test
        self.operators = operators
        self.max_depth = max_depth

    def search(self) -> Any:
        """
        Perform Best-First Search for program synthesis.

        Returns:
            The synthesized program if a solution is found, or None if no solution exists.
        """
        queue = deque([([])])  # Start with an empty program

        while queue:
            current_program = queue.popleft()
        
            # Check if the current program solves the synthesis problem
            if self.goal_test(self.problem, current_program):
                return current_program

              # Expand search if within depth limit
            if len(current_program) < self.max_depth:
                for op in self.operators:
                    new_program = current_program + [op]
                    queue.append(new_program)
    
        # Return None if no solution is found
        return None