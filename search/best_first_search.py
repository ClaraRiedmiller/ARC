import heapq
from typing import Any, Callable, List, Tuple

from search.node import Node

class BestFirstSearch:
    def __init__(
        self,
        initial_state: Any,
        goal_test: Callable[[Any], bool],
        heuristic: Callable[[Any], float],
        expand: Callable[[Any], List[Tuple[Any, float]]]
    ):
        """
        Initialize the Best-First Search class.

        Args:
            initial_state: The starting point of the search (e.g., empty program).
            goal_test: A function to check if a given state satisfies the synthesis goal.
            heuristic: A function to compute the estimated cost to the goal from a given state.
            expand: A function to generate successor states and their associated costs.
        """
        self.initial_state = initial_state
        self.goal_states = goal_test
        self.heuristic = heuristic
        self.expand = expand

    def search(self) -> Any:
        """
        Perform Best-First Search for program synthesis.

        Returns:
            The synthesized program if a solution is found, or None if no solution exists.
        """
        # Priority queue for managing the frontier
        frontier = []
        heapq.heappush(frontier, Node(self.initial_state, 0, self.heuristic(self.initial_state)))

        # Set for visited states to avoid redundant work
        visited = set()

        while frontier:
            # Get the node with the lowest cost
            current_node = heapq.heappop(frontier)
            current_program = current_node.program

            # Check if the current program solves the synthesis problem
            if self.goal_test(current_program):
                return current_program

            # Mark the current program as visited
            visited.add(current_program)

            # Expand the current node to generate successors
            for successor, generation_cost in self.expand(current_program):
                if successor not in visited:
                    heapq.heappush(frontier, Node(successor, current_node.cost + generation_cost, self.heuristic(successor)))

        # Return None if no solution is found
        return None