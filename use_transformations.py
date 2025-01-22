from typing import TypeAlias, Tuple, Set

from dsl.transformation import apply_transformation
from dsl.dsl import *
from dsl.hodel_hardness import upper_bound_hardness
from arckit_handler.arckit_handler import get_problem
from dsl.dsl_features import get_dsl_functions


# # apply the transformation move_left to an example grid. We could extend this to take a specific grid as an input as well
# apply_transformation(move_left)

# # print all problems whose hardness (under hodel) is upper bounded by the paramter specified
# print(upper_bound_hardness(2)) 

# # get problem from arckit handler
# get_problem('68b16354')





# get the dsl funcitons and their names
dsl_functions = get_dsl_functions()


filtered_dict = {key: value for key, value in dsl_functions.items() if value['inputs'] == ['object', 'gridsize']}
print(filtered_dict)

forbidden_functions = ['holes', 'isolate', 'pixel_in', 'pixel_out', 'pixel_out_with_uncovered_neighbors' ,'pixel_out_with_uncovered_neighbors_only_diagonal_neighborhood', 'pixel_out_with_uncovered_neighbors_with_diagonal', 'project_bigger', 'project_smaller']
broken_functions = ['move_down', 'move_down_edge', 'move_left_edge', 'move_right', 'move_right_edge', 'move_up', 'move_up_edge', 'neighborhood', 'rotate_horizontal', 'rotate_vertical']
working_functions = ['color_object_max', 'color_object_min', 'move_left', 'color_object_max', 'color_object_min', 'move_left', 'color_object_max', 'color_object_min', 'move_left', 'color_object_max', 'color_object_min', 'move_left', 'neighborhood_with_diagonals', 'only_diagonal_neighborhood']


# I sorted the functions we have right now into three buckets (see above). Should be self-explanatory, otherwise ask me, Lorenz :)
for function, type in filtered_dict.items():
    print('\n', function)
    if function in broken_functions:
        apply_transformation(function, image_visualize=False)
    elif function in forbidden_functions:
        print('forbidden function!')
    else:
        print('last working function:', working_functions)
        working_functions.append(function)
        apply_transformation(function)


