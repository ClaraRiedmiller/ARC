from best_first_search import BestFirstSearch
from program_search_problem import example_goal_test, example_heuristic, example_expand

initial_state = ""
bfs = BestFirstSearch(
    initial_state,
    example_goal_test,
    example_heuristic,
    example_expand
)
result = bfs.search()
print("Synthesized Program:", result)