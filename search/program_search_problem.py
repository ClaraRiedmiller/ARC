def example_goal_test(program):
    # Define when the program satisfies the synthesis goal
    return program == "desired_program"

def example_heuristic(program):
    # Estimate how far the program is from the goal (lower is better)
    return len(program)  # Example: shorter programs are better

def example_expand(program):
    # Generate possible expansions of the current program
    # Each expansion is a tuple (new_program, cost_of_expansion)
    candidates = [(program + "A", 1), (program + "B", 2)]
    return candidates
