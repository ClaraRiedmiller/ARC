# We need intra-grid and inter-grid groups 
# I.e. we will need the intra-grid groups to define the inter-grid groups
# But also the inter-grid groups to refine the intra-grid groups 
# Do we want a proper group type?
# We want to restrict attention to objects with |number of elements|>2?
    # Maybe some kind of loop -> first search meaningful bigger objects
    # Otherwise: We would like to to that from the DGL after constructing the graph.    
# We want group features like same_color on adjacency group
# Maybe wrap the group production into one function to not 
# unncessarily compute the objects over and over again.

# Maybe introduce composed objects, baiscally we have them as adjacency group
import numpy as np
from scipy.ndimage import label, binary_fill_holes
from scipy.ndimage import binary_dilation

from arckit_handler.arckit_handler import drawProblem
import arckit
import arckit.vis as vis

from knowledge_graph.create_obj_Rel import *

def to_hashable_shape(shape_array):
    """
    Convert a 2D NumPy array into a tuple-of-tuples so it can be used as a dictionary key.
    """
    return tuple(tuple(row) for row in shape_array)


# def create_color_group(obj_color_dict, obj_shapes):
#     """
#     Group objects by color, skipping any object whose shape has <= 2 pixels.

#     Parameters
#     ----------
#     obj_color_dict : dict
#         Maps label -> color (integer).
#     obj_shapes : dict
#         Maps label -> 2D NumPy array (the object's binary shape).

#     Returns
#     -------
#     dict
#         color_groups[color] = set of labels that have this color (and size > 2).
#     """
#     color_groups = {}
#     for lbl, color_val in obj_color_dict.items():
#         # Skip objects with <= 2 pixels
#         shape_arr = obj_shapes.get(lbl, None)
#         if shape_arr is None or np.count_nonzero(shape_arr) <= 2:
#             continue
        
#         if color_val not in color_groups:
#             color_groups[color_val] = set()
#         color_groups[color_val].add(lbl)
    
#     return color_groups

# def create_shape_group(obj_shape_dict):
#     """
#     Group objects that share the exact same 2D shape (binary array),
#     skipping shapes with <= 2 pixels.

#     Parameters
#     ----------
#     obj_shape_dict : dict
#         Maps label -> 2D NumPy array (the object's binary shape).

#     Returns
#     -------
#     dict
#         shape_groups[shape_key] = set of labels with that shape.
#     """
#     shape_groups = {}
#     for lbl, shape_arr in obj_shape_dict.items():
#         if np.count_nonzero(shape_arr) <= 2:
#             # Skip small objects
#             continue
        
#         shape_key = to_hashable_shape(shape_arr)
#         if shape_key not in shape_groups:
#             shape_groups[shape_key] = set()
#         shape_groups[shape_key].add(lbl)

#     return shape_groups

# def create_adjacency_group(obj_adjacency_dict, obj_shapes):
#     """
#     Group objects that are connected via adjacency. That is, we find connected
#     components in the adjacency dict. Skip objects with <= 2 pixels.

#     Parameters
#     ----------
#     obj_adjacency_dict : dict
#         Maps label -> set of neighboring labels.
#     obj_shapes : dict
#         Maps label -> 2D NumPy array (the object's binary shape).

#     Returns
#     -------
#     list of sets
#         Each set is a group of mutually connected labels.
#     """
#     # Filter out small objects
#     valid_labels = set(lbl for lbl, shape in obj_shapes.items()
#                        if np.count_nonzero(shape) > 2)

#     visited = set()
#     groups = []

#     def dfs(start_label, component):
#         stack = [start_label]
#         while stack:
#             cur = stack.pop()
#             for neighbor in obj_adjacency_dict.get(cur, []):
#                 if neighbor not in visited and neighbor in valid_labels:
#                     visited.add(neighbor)
#                     component.add(neighbor)
#                     stack.append(neighbor)

#     for lbl in valid_labels:
#         if lbl not in visited:
#             visited.add(lbl)
#             new_group = {lbl}
#             dfs(lbl, new_group)
#             groups.append(new_group)

#     return groups


# def create_shape_color_group(obj_shape_dict, obj_color_dict):
#     """
#     Group objects that share both shape and color, ignoring objects with <= 2 pixels.

#     Returns
#     -------
#     dict
#         shape_color_groups[(shape_key, color)] = set of labels
#     """
#     shape_color_groups = {}
#     for lbl, shape_arr in obj_shape_dict.items():
#         if np.count_nonzero(shape_arr) <= 2:
#             continue
#         color_val = obj_color_dict.get(lbl, None)
#         if color_val is None:
#             continue
        
#         shape_key = to_hashable_shape(shape_arr)
#         group_key = (shape_key, color_val)
#         if group_key not in shape_color_groups:
#             shape_color_groups[group_key] = set()
#         shape_color_groups[group_key].add(lbl)

#     return shape_color_groups

# def create_rotations_group(obj_shape_dict):

#     labels = list(obj_shape_dict.keys())
#     visited = set()
#     rotation_groups = []

#     for i in range(len(labels)):
#         lbl_i = labels[i]
#         shape_i = obj_shape_dict[lbl_i]
#         if lbl_i in visited:
#             continue
#         if np.count_nonzero(shape_i) <= 2:
#             continue

#         # We will group all shapes that rotate into shape_i
#         group_set = {lbl_i}
#         visited.add(lbl_i)

#         for j in range(i + 1, len(labels)):
#             lbl_j = labels[j]
#             shape_j = obj_shape_dict[lbl_j]
#             if lbl_j not in visited and np.count_nonzero(shape_j) > 2:
#                 if is_rotation(shape_i, shape_j):
#                     group_set.add(lbl_j)
#                     visited.add(lbl_j)

#         # Add group only if it has at least 2 objects
#         if len(group_set) >= 2:
#             rotation_groups.append(group_set)

#     return rotation_groups


# def create_groups(grid):

#     labeled_array = label_by_color(grid, mode="direct")
#     unique_labels = get_unique_labels(labeled_array, exclude_zero=True)

#     # 2) Build color dict & shape dict
#     obj_color_dict = {}
#     obj_shape_dict = {}
#     for lbl in unique_labels:
#         color_val = lbl // 100  
#         obj_color_dict[lbl] = color_val
#     obj_shape_dict = extract_object_shapes(labeled_array)

#     # 3) Build adjacency
#     adjacency_dict = get_object_adjacency_scipy(labeled_array, mode="diagonal")

#     # 4) Create groups
#     color_groups = create_color_group(obj_color_dict, obj_shape_dict)
#     shape_groups = create_shape_group(obj_shape_dict)
#     adjacency_groups = create_adjacency_group(adjacency_dict, obj_shape_dict)
#     rotations_groups = create_rotations_group(obj_shape_dict)
#     shape_color_groups = create_shape_color_group(obj_shape_dict, obj_color_dict)

#     return {
#         "color_groups": color_groups,
#         "shape_groups": shape_groups,
#         "adjacency_groups": adjacency_groups,
#         "rotations_groups": rotations_groups,
#         "shape_color_groups": shape_color_groups,
#     }

# if __name__ == "__main__":
#     # Example array with multiple "colors" (values)
#     task = train_set[4]
    
#     drawProblem(task, "Problem4")
#     print(create_groups(task.train[0][0]), "\n")
#     print(create_groups(task.train[0][1]))

