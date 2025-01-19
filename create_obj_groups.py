# We need intra-grid and inter-grid groups 
# I.e. we will need the intra-grid groups to define the inter-grid groups
# But also the inter-grid groups to refine the intra-grid groups 
# Do we want a proper group type?
# We want to restrict attention to objects with |number of elements|>2
# We want group features like same_color on adjacency group
# Maybe wrap the group production into one function to not 
# unncessarily compute the objects over and over again.


def create_color_group(obj_color_dict):
    return True

def create_shape_group(obj_shape_dict):
    return True

def create_djacency_group(obj_adjacency_dict):
    return True

def create_rotations_group(obj_shape_dict):
    return True

def create_shape_color_group(obj_shape_dict, obj_color_dict):
    return True

def create_groups(grid):
    return True