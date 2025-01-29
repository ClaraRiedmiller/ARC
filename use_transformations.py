import arckit
import csv
import numpy as np

from dsl.transformation import apply_transformation, convert_grid_format, remove_bg, add_bg
from dsl.dsl import *
from dsl.hodel_hardness import upper_bound_hardness
from dsl.dsl_dictionary import get_dsl_dict
from arckit_handler.arckit_handler import getGrid, get_problem
from dsl.test_grids import grid1


# # apply the transformation move_left to an example grid. We could extend this to take a specific grid as an input as well
# apply_transformation(move_left)

# # print all problems whose hardness (under hodel) is upper bounded by the paramter specified
# print(upper_bound_hardness(3)) 

# # get problem from arckit handler
# get_problem('68b16354')

def test_grid_level():

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






def test_object_level():


    # for this, we make an example first:
    grid = np.array([[None,None,None,None,None, None, None], [None,3,2,3,None, None, None], [None,3,None,3,None, None, None], [None,3,3,4,None, None, None], [None,None,None,None,None, None, None]]).astype(object)
    # , [None,None,None,None,None, None, None], [None,None,None,None,None, None, None]

    grid_name = 'test_object_transformation'

    function = 'color_object_max'

    # apply_transformation(grid, grid_name, function)

    
    # this gets me all the dsl functions (by default excluding the auxiliary ones). In this case, we want to only have ones that work on the object level
    dsl_functions = get_dsl_dict(excludeObjectOnly=True)

    print(dsl_functions)

    # for now, exclude operations that resize the grid (as far as I can tell, main issue with reconverting the grid rn. But at the latest when it comes to search, we need to figure out how to adjust the meta paramters (grid dimensions) after applying a transformation)
    dsl_functions = {key: value for key, value in dsl_functions.items() if value.get('grid_size_change') == '0'}

    # apply all the dsl functions to our object
    for function, type in dsl_functions.items():
        print('\n', function)
        apply_transformation(grid, grid_name, function)







def test_object_level_dimensions():

    # this test the dsl functions that manipulate and object but also affect the grid size. I think I need to modify the dsl in a way that changes its own parameters (width and height)


    # for this, we make an example first:
    grid = grid1
    print(grid1)

    grid_name = 'test_object_transformation'


    # this gets me all the dsl functions (by default excluding the auxiliary ones). In this case, we want to only have ones that work on the object level
    dsl_functions = get_dsl_dict()
        

    function = 'flip_object_around_own_xax'

    apply_transformation(grid, grid_name, function)

    

    # #@Lorenz these all rely on the neighborhood functions. there is a type issue that i marked in the dsl
    # forbidden_functions = ['add_border_around_object', 'add_corners_around_object', 'add_star_around_object', 'change_color_pixel_out', 'change_color_pixel_in']

    # # filter out the forbidden functions (Lorenz needs to look over them)
    # dsl_functions = {key: value for key, value in dsl_functions.items() if key not in forbidden_functions}
    

    # # apply all the dsl functions to our object
    # for function, type in dsl_functions.items():
    #     print('\n', function)
    #     apply_transformation(grid, grid_name, function)


test_object_level_dimensions()

# test_grid_level()


