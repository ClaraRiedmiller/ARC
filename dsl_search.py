# This is a first attempt at searching through the dsl. I will write out the steps in pseudocode first and then add whatever we have


# From the knowledge graph, we would get (for now) what kind of object correspondences we are reasoning about (highest level of sufficient correlation). 

# While the correlation is informed by all training examples of a task, we will ask the dsl to find a program for the first task first, then use it as a hypothesis for the following (this could be an opportunity to query the knowledge graph again at a later point if the dsl fails to reason at the level we thought would work. We could thus theoretically go back to the kg depending on success in the reasoning).

# In the dsl, this means we take the input grid of the first training example and generate a search tree (for each object). The subtrees of this further depends on some 'meta-parameters' (meaning in our case parameters that determine the subtree like color info, grid size info, or more generally what kind of functions are intuitively deemed most appropriate). 

# If we manage to find a program for the first example, we test it on the other ones as well and maybe refine it (if there are more objects,...).


# ----------

import arckit
import numpy as np

from arckit_handler.arckit_handler import getGrid
from dsl.transformation import apply_transformation
from dsl.test_problems import *


def get_arc_problem(task_id):

    # get example grid so we can test our transformations
    train_set, eval_set = arckit.load_data() 

    problem = train_set[task_id]

    return(problem)


def learn_example_program(input_grid, output_grid):

    input_grid_name = 'dummy_name'

    # restricted program space: We are only considering very simple functions atm
    dsl_functions = ['flip_xax', 'flip_yax', 'color_object_max', 'color_object_min']

    # generate the candidate solutions respective to the functions listed above. this simulates a search of depth one.
    for function in dsl_functions:
        
        trans_input_grid = apply_transformation(input_grid, input_grid_name, function, show=False, image_visualize=False, terminal_visualize=False)

        # check if any of them are equal to the target output (output_grid) and output that function name. This represents the program we learn. Once we have the correct function, return it.
        if np.array_equal(trans_input_grid, output_grid):
            print(f'function {function} produces the correct output.\n')
            return(function)


    


def learn_from_examples(training_examples):

    # iterate over the trainnig examples and see which program produces the correct output
    for no, ex in enumerate(training_examples):
        print('example number: ', no)
        final_program = learn_example_program(ex[0], ex[1])

    # for now, the final program will just be the one the last training example produces. Later, they should build up on each other (or we learn separate programs for each example and simply see whether they can all agree on one)
    # return program if we find one, otherwise return nothing
        return(final_program)



def search_program(problem):

    # get the training examples and learn a program from them
    training_examples = problem.train
    program = learn_from_examples(training_examples)

    if program:

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
    problem = get_problem_3()


    print(problem)

    search_program(problem)


main()