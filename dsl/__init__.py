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

DSL_COLOR_METHODS = [
    change_color_pixel_out,
    change_color_pixel_in,
    color_object_max,
    color_object_min
]


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

DSL_OBJECT_MOVE_DOWN_METHODS = [
    move_down,
    move_down_edge,
    
]

DSL_OBJECT_MOVE_UP_METHODS = [
    move_up,
    move_up_edge,
]

DSL_IGNORE = [
    isolate,
]
