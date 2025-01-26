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


# get the grid we want to search a program for (input of first training example of specified task)
train_set, eval_set = arckit.load_data() 

# specify which grid we want. We chose this one, it only needs to pick the majority color
task_id = '5582e5ca'
is_training = True
which_example = 0
input_grid_name = str(task_id) + '_' + str(int(is_training)) + '_' + str(which_example) + '_input'

# get specific grid
input_grid = getGrid(train_set[task_id], is_training, which_example, True)
output_grid = getGrid(train_set[task_id], is_training, which_example, False)



# Let's try this with a real example; what we are trying to get at in the second week.

# From kg: We are reasoning on a grid level


# restricted program space: We are only considering very simple functions atm
functions = ['flip_xax', 'flip_yax', 'color_object_max', 'color_object_min']

# generate the candidate solutions respective to the functions listed above
for function in functions:
    trans_input_grid = apply_transformation(input_grid, input_grid_name, function, show=False, image_visualize=False)

    # check if any of them are equal to the target output (output_grid)
    print(np.array_equal(trans_input_grid, output_grid))


