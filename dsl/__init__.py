from dsl import (
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

DSL_OBJECT_SHAPE_MUTATION_INSIDE_METHODS = [
    fill_pixel,
    fill_pixel_down,
    fill_pixel_right
]

DSL_OBJECT_SHAPE_MUTATION_OUTSIDE_METHODS = [
     add_border_around_object,
    add_corners_around_object,
    add_star_around_object
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
    flip_xax,

]

DSL_OBJECT_MOVE_UP_METHODS = [
    move_up,
    move_up_edge,
    flip_xax,
]

DSL_OBJECT_MOVE_LEFT_METHODS = [
    move_left,
    move_left_edge,
    flip_yax,

]

DSL_OBJECT_MOVE_RIGHT_METHODS = [
    move_right,
    move_right_edge,
    flip_yax,
]

DSL_IGNORE = [
    isolate,
]
