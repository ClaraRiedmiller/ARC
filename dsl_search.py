# This is a first attempt at searching through the dsl. I will write out the steps in pseudocode first and then add whatever we have

# From the knowledge graph, we would get (for now) what kind of object correspondences we are reasoning about (highest level of sufficient correlation). 

# While the correlation is informed by all training examples of a task, we will ask the dsl to find a program for the first task first, then use it as a hypothesis for the following (this could be an opportunity to query the knowledge graph again at a later point if the dsl fails to reason at the level we thought would work. We could thus theoretically go back to the kg depending on success in the reasoning).

# In the dsl, this means we take the input grid of the first training example and generate a search tree (for each object). The subtrees of this further depends on some 'meta-parameters' (meaning in our case parameters that determine the subtree like color info, grid size info, or more generally what kind of functions are intuitively deemed most appropriate). 

# If we manage to find a program for the first example, we test it on the other ones as well and maybe refine it (if there are more objects,...).


# ----------

import arckit
import numpy as np

from arckit_handler.arckit_handler import getGrid, terminalVis
from dsl.transformation import apply_transformation, convert_grid_format, remove_bg
from dsl.test_problems import *
from test_kg_output import print_kg_output

from dsl.dsl import Constraints
from dsl import flip_xax

from search.breadth_fist_search import BreadthFirstSearch
from search.best_first_search import BestFirstSearch
from search.program_search_problem import goal_test, heuristic, expand


def get_arc_problem(task_id):

    # get example grid so we can test our transformations
    train_set, eval_set = arckit.load_data() 

    problem = train_set[task_id]

    return(problem)



def search_for_program(problem):

    # get the training examples and learn a program from them
    training_examples = [(convert_grid_format(remove_bg(input_img)), convert_grid_format(remove_bg(output_img))) for input_img, output_img in problem.train]
    # p = convert_grid_format(remove_bg(problem.train[0][0]))
    # training_examples = [(p,p)]
    
    grid = problem.train[0][1]
    grid_height, grid_width = np.shape(grid)
    constraints = Constraints(color = 1, grid_width = grid_width, grid_height = grid_height)

    fmt_problem = (training_examples, constraints)

    # Try search for programs only on the grid level
    bfs = BreadthFirstSearch(
        problem=fmt_problem,
        goal_test=goal_test,
        operators= [flip_xax],
        max_depth=1
    )

    search_result = bfs.search()

    if search_result:
        program = search_result

        # get the test example and see whether the program above produces a correct prediction
        test = problem.test
        test_input = test[0][0]
        test_output = test[0][1]
        output_guess = apply_transformation(test_input, 'test_input', program, show=False, image_visualize=False, terminal_visualize=False)

        # print(f'Testing program{program}: ...\n')


        # see whether our prediction is correct
        success = np.array_equal(test_output, output_guess)

        if success:
            print('\nSuccess! I learned working program!')
        else: 
            print('\nI was not able to generaliza a correct program :(')


    else:
        print('\nI was not able to find a candidate program for the training examples :(')


def main():

    # # specify how you want to get the problem:

    # # from arc by task_id
    # task_id = '68b16354'
    # problem = get_arc_problem(task_id)

    # from our test problems

    problem = get_problem_1()
    terminalVis(problem)
    print(problem)

    search_for_program(problem)



main()