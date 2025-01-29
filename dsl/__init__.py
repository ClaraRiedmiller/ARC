from dsl.dsl import (
    add_border_around_object,
    add_corners_around_object,
    add_star_around_object,
    change_color_pixel_out,
    change_color_pixel_in,
    color_object_max,
    color_object_min,
    fill_pixel,
    fill_pixel_down,
    fill_pixel_right,
    flip_xax,
    flip_yax,
    grid_add_down,
    grid_add_left,
    grid_add_left_and_right,
    grid_add_right,
    grid_add_up,
    grid_add_up_and_down,
    grid_duplicate_down,
    grid_duplicate_left,
    grid_duplicate_left_and_right,
    grid_duplicate_right,
    grid_duplicate_up,
    grid_duplicate_up_and_down,
    isolate,
    move_down,
    move_down_edge,
    move_left,
    move_left_edge,
    move_right,
    move_right_edge,
    move_up,
    move_up_edge,
    project_dupliate,
    project_triplicate,
    project_quintuplicate,
    project_half,
    project_third,
    project_fifth
)

DSL_METHODS = [
    add_border_around_object,
    add_corners_around_object,
    add_star_around_object,
    change_color_pixel_out,
    change_color_pixel_in,
    color_object_max,
    color_object_min,
    fill_pixel,
    fill_pixel_down,
    fill_pixel_right,
    flip_xax,
    flip_yax,
    grid_add_down,
    grid_add_left,
    grid_add_left_and_right,
    grid_add_right,
    grid_add_up,
    grid_add_up_and_down,
    grid_duplicate_down,
    grid_duplicate_left,
    grid_duplicate_left_and_right,
    grid_duplicate_right,
    grid_duplicate_up,
    grid_duplicate_up_and_down,
    move_down,
    move_down_edge,
    move_left,
    move_left_edge,
    move_right,
    move_right_edge,
    move_up,
    move_up_edge,
    project_dupliate,
    project_triplicate,
    project_quintuplicate,
    project_half,
    project_third,
    project_fifth
]

#check whether color of a pixel is changed
DSL_COLOR_METHODS = [
    change_color_pixel_out,
    change_color_pixel_in,
    color_object_max,
    color_object_min
]

#somehow check whether the grid its self is an object
DSL_GRID_MUTATION_METHODS = [
    grid_add_down,
    grid_add_left,
    grid_add_left_and_right,
    grid_add_right,
    grid_add_up,
    grid_add_up_and_down,
    grid_duplicate_down,
    grid_duplicate_left,
    grid_duplicate_left_and_right,
    grid_duplicate_right,
    grid_duplicate_up,
    grid_duplicate_up_and_down,
    project_dupliate,
    project_triplicate,
    project_quintuplicate,
    project_half,
    project_third,
    project_fifth
]

# Check if adding a line to the input grid (e.g., increasing its width or height by a fixed amount, such as 1 or 2) will match the dimensions of the output grid.
DSL_GRID_MUTATION_METHODS_ONELINE =[
    grid_add_down,
    grid_add_left,
    grid_add_left_and_right,
    grid_add_right,
    grid_add_up,
    grid_add_up_and_down,
    grid_duplicate_down,
    grid_duplicate_left,
    grid_duplicate_left_and_right,
    grid_duplicate_right,
    grid_duplicate_up,
    grid_duplicate_up_and_down,
]

# Check if adding a line to the input grid height (e.g., increasing by a fixed amount, such as 1 or 2) will match the dimensions of the output grid height.
DSL_GRID_MUTATION_METHODS_ONELINE_HEIGHT =[
    grid_add_down,
    grid_add_up,
    grid_add_up_and_down,
    grid_duplicate_down,
    grid_duplicate_up,
    grid_duplicate_up_and_down
]

# Check if the the added line is uniformly colored
DSL_GRID_MUTATION_METHODS_ONELINE_HEIGHT_UNIFROM =[
    grid_add_down,
    grid_add_up,
    grid_add_up_and_down
]

# Check if the the added line is uniformly colored
DSL_GRID_MUTATION_METHODS_ONELINE_HEIGHT_NONUNIFORM =[
    grid_duplicate_down,
    grid_duplicate_up,
    grid_duplicate_up_and_down
]

# Check if adding a line to the input grid width (e.g., increasing by a fixed amount, such as 1 or 2) will match the dimensions of the output grid width.
DSL_GRID_MUTATION_METHODS_ONELINE_WIDTH =[
    grid_add_left,
    grid_add_left_and_right,
    grid_add_right,
    grid_duplicate_left,
    grid_duplicate_left_and_right,
    grid_duplicate_right,
]


# Check if the INPUT grid height and width, when multiplied by 2, 3,4, or 5, matches the dimensions of the OUTPUT grid height and width.
DSL_GRID_MUTATION_MULTIPLICATION = [ 
    project_dupliate,
    project_triplicate,
    project_quintuplicate
]

# Check if the OUTPUT grid height and width, when multiplied by 2, 3,4, or 5, matches the dimensions of the INPUT grid height and width.
DSL_GRID_MUTATION_DIVISION = [
    project_half,
    project_third,
    project_fifth
]

# check whether shape is not the same
DSL_OBJECT_SHAPE_MUTATION_METHODS = [
    project_dupliate,
    project_triplicate,
    project_quintuplicate,
    project_half,
    project_third,
    project_fifth,
    add_border_around_object,
    add_corners_around_object,
    add_star_around_object,
    fill_pixel,
    fill_pixel_down,
    fill_pixel_right
]

# Check if bbox/bboy does NOT stay the same and the amount of pixels increase
DSL_OBJECT_SHAPE_MUTATION_METHODS_ADD = [
    add_border_around_object,
    add_corners_around_object,
    add_star_around_object
]

# Check if bbox/bboy stays the same and the amount of pixels increase
DSL_OBJECT_SHAPE_MUTATION_METHODS_FILL = [
    fill_pixel,
    fill_pixel_down,
    fill_pixel_right
]

#Check whether the coordinates of the object change
DSL_OBJECT_MOVE_METHODS = [
    move_down,
    move_down_edge,
    move_left,
    move_left_edge,
    move_right,
    move_right_edge,
    move_up,
    move_up_edge,
    flip_xax,                   
    flip_yax,
]

# decrease of y values
DSL_OBJECT_MOVE_DOWN_METHODS = [
    move_down,
    move_down_edge,
    flip_xax 
]

# increase of y values
DSL_OBJECT_MOVE_UP_METHODS = [
    move_up,
    move_up_edge,
    flip_xax
]

# increase of x values
DSL_OBJECT_MOVE_RIGHT_METHODS =[
    move_right_edge,
    move_up,
    flip_yax
]

# decrease of x values
DSL_OBJECT_MOVE_LEFT_METHODS =[
    move_left_edge,
    move_left,
    flip_yax
]


DSL_IGNORE = [
    isolate,
]


DSL_METHODS_BY_CATEGORY = {
    'colour': DSL_COLOR_METHODS,
    'grid': DSL_GRID_MUTATION_METHODS,
    'grid_division': DSL_GRID_MUTATION_DIVISION,
    'grid_multiplication': DSL_GRID_MUTATION_MULTIPLICATION,
    'grid_one_line': DSL_GRID_MUTATION_METHODS_ONELINE,
    'grid_one_line_height': DSL_GRID_MUTATION_METHODS_ONELINE_HEIGHT,
    'grid_one_line_height_uniform': DSL_GRID_MUTATION_METHODS_ONELINE_HEIGHT_UNIFROM,
    'grid_one_line_height_none_uniform': DSL_GRID_MUTATION_METHODS_ONELINE_HEIGHT_NONUNIFORM,
    'grid_one_line_width':DSL_GRID_MUTATION_METHODS_ONELINE_WIDTH,
    'object_move':DSL_OBJECT_MOVE_METHODS,
    'object_move_down':DSL_OBJECT_MOVE_DOWN_METHODS,
    'object_move_up':DSL_OBJECT_MOVE_UP_METHODS,
    'object_move_left':DSL_OBJECT_MOVE_LEFT_METHODS,
    'object_move_right':DSL_OBJECT_MOVE_RIGHT_METHODS,
    'object_mutation':DSL_OBJECT_SHAPE_MUTATION_METHODS,
    'object_mutation_add':DSL_OBJECT_SHAPE_MUTATION_METHODS_ADD,
    'object_mutation_fill': DSL_OBJECT_SHAPE_MUTATION_METHODS_FILL
}