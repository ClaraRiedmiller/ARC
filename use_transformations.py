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





forbidden_functions = ['holes', 'isolate', 'pixel_in', 'pixel_out', 'pixel_out_with_uncovered_neighbors' ,'pixel_out_with_uncovered_neighbors_only_diagonal_neighborhood', 'pixel_out_with_uncovered_neighbors_with_diagonal', 'project_bigger', 'grid_duplicate_down']
broken_functions = ['move_down', 'move_down_edge', 'move_left_edge', 'move_right', 'move_right_edge', 'move_up', 'move_up_edge', 'neighborhood', 'flip_xax', 'flip_yax']
working_functions = ['color_object_max', 'color_object_min', 'move_left', 'color_object_max', 'color_object_min', 'move_left', 'color_object_max', 'color_object_min', 'move_left', 'color_object_max', 'color_object_min', 'move_left', 'neighborhood_with_diagonals', 'only_diagonal_neighborhood']

testing_functions = ['project_smaller']


# apply_transformation(grid, grid_name, 'color_object_max', show=False)


# # for function in testing_functions:
# #     apply_transformation(grid, grid_name, function, show=False)


# I sorted the functions we have right now into three buckets (see above). Should be self-explanatory, otherwise ask me, Lorenz :)
for function, type in dsl_functions.items():
    print('\n', function)
    if function in forbidden_functions or function in testing_functions:
        print('forbidden function or testing')
    # elif function in forbidden_functions:
    #     print('forbidden function!')
    else:
        # print('last working function:', working_functions)
        # working_functions.append(function)
        apply_transformation(grid, grid_name, function)


