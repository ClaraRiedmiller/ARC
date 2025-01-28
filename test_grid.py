# this is how you can retreive the test examples for a specific task (bc this is training, we have the input and output but ultimately, we will need to be able to use only the input)

import arckit
from arckit_handler.arckit_handler import getGrid, get_problem


# get example grid so we can test our transformations
train_set, eval_set = arckit.load_data() 

# specify which problem we want
task_id = '68b16354'

# get the test input grid from that problem
is_training = False # this is where you specify whether you get the example from the training or test part of the problem
which_example = 0 # there is only one training example, so we get the first index 
is_in = True # this specifies whether you want the input (if false, it gives you the output)
grid_name = str(task_id) + '_' + str(int(is_training)) + '_' + str(which_example) + '_' + str(is_in)

# get specific grid
grid = getGrid(train_set[task_id], is_training, which_example, is_in)
print(grid)

# this is how you can look at the entire problem
get_problem(task_id)