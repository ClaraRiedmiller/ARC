# We have to relate the groups of objects to extract important features
# e.g. we want to relate groups that have the same color, same number of objects, etc.
# Further, establish some causal relations between groups 
# Objects in group are rotations of objects in other group etc.

# For inter-grid comparison we have to take care of the naming!
# Invariance!!
# Match persisting shapes.

def group_same_size():
    return True

def group_same_color():
    return True

def group_sub_group():
    return True

def group_is_scaled():
    return True