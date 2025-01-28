from best_first_search import BestFirstSearch
from program_search_problem import goal_test, heuristic, expand
from dsl.dsl import Constraints

import arckit

train_set, eval_set = arckit.load_data()
task = train_set[4]

constraints = Constraints()
initial_goal_state_pairs = [(None, None)]
problem = (initial_goal_state_pairs,constraints)
bfs = BestFirstSearch(
    problem,
    goal_test,
    heuristic,
    expand
)
result = bfs.search()
print("Synthesized Program:", result)