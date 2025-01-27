import arckit
import csv

from dsl.transformation import apply_transformation
from dsl.dsl import *
from dsl.hodel_hardness import upper_bound_hardness
from dsl.dsl_dictionary import get_dsl_dict
from arckit_handler.arckit_handler import getGrid, get_problem


# # apply the transformation move_left to an example grid. We could extend this to take a specific grid as an input as well
# apply_transformation(move_left)

# # print all problems whose hardness (under hodel) is upper bounded by the paramter specified
# print(upper_bound_hardness(2)) 

# # get problem from arckit handler
# get_problem('68b16354')


# get example grid so we can test our transformations
train_set, eval_set = arckit.load_data() 

# specify which grid we want. This is just an example one for now that helps to visualize the transformations.
task_id = '68b16354'
is_training = True
which_example = 0
is_in = True
grid_name = str(task_id) + '_' + str(int(is_training)) + '_' + str(which_example) + '_' + str(is_in)

# get specific grid
grid = getGrid(train_set[task_id], True, 0, True)




# this gets me all the dsl functions (by default excluding the auxiliary ones). In this case, we want to only have ones that work on the grid level, not only the object level so we exclude those functions as well.
dsl_functions = get_dsl_dict(excludeObjectOnly=True)


# apply all the dsl functions to our object
for function, type in dsl_functions.items():
    print('\n', function)
    apply_transformation(grid, grid_name, function)


