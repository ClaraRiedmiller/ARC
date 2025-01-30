from typing import List, Callable
from dsl import DSL_METHODS

def _goal_test(initial_state, goal_state, constraints, program) -> bool:
    outcome = initial_state
    for step in program:
        outcome = step(constraints, outcome)
    return outcome == goal_state

def goal_test(problem, program):
    initial_goal_state_pairs = problem
    for initial_state, goal_state, constraints in initial_goal_state_pairs:
        if not _goal_test(initial_state, goal_state, constraints, program):
            return False 
    return True

def heuristic(program):
    # Estimate how far the program is from the goal (lower is better)
    return len(program)  # Example: shorter programs are better

def expand(program: List[Callable]):
    # Generate possible expansions of the current program
    # Each expansion is a tuple (new_program, cost_of_expansion)
    candidates = [program.copy().append() for func in DSL_METHODS]
    return candidates
