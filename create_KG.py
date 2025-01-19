import numpy as np
import torch
import dgl

from objects import label_by_color, get_unique_labels, extract_object_shapes
from adjacency import get_object_adjacency_scipy

def is_same_shape(arr1, arr2):
    """
    Return True if arr1 and arr2 have the same shape (dimensions)
    and same pattern (values).
    """
    if arr1 is None or arr1.size == 0:
        return arr2 is None or arr2.size == 0
    if arr2 is None or arr2.size == 0:
        return arr1 is None or arr1.size == 0

    return (arr1.shape == arr2.shape) and np.array_equal(arr1, arr2)

def create_heterograph_with_relations(grid, include_groups=False):
    """
    Create a DGL heterograph with:
      - 'object' node type for each labeled object
      - optionally 'group' node type (placeholder)
      - edge type 'adjacent_to' for adjacency among objects
      - edge type 'same_shape_as' for objects that share the same shape

    Args:
        grid: 2D array representing the puzzle/scene
        include_groups (bool): If True, also create 'group' nodes (placeholder).
                               In a real scenario, you'd pass in data about these groups.

    Returns:
        dgl.DGLHeteroGraph
    """
    # ----------------------------------------------------------------------
    # 1. Identify object-level data
    # ----------------------------------------------------------------------
    labeled_array = label_by_color(grid, mode="direct")
    unique_labels = get_unique_labels(labeled_array, exclude_zero=True)
    object_shapes = extract_object_shapes(labeled_array)

    # Create adjacency using 8-way connectivity
    adjacency = get_object_adjacency_scipy(labeled_array, mode="8-way")

    # We’ll map each label to an integer ID (for 'object' nodes)
    label2id = {lbl: i for i, lbl in enumerate(unique_labels)}
    num_object_nodes = len(unique_labels)

    # ----------------------------------------------------------------------
    # 2. Build adjacency edges
    #    Edge type: ('object', 'adjacent_to', 'object')
    # ----------------------------------------------------------------------
    adjacency_src = []
    adjacency_dst = []
    for lbl in unique_labels:
        i = label2id[lbl]
        neighbors = adjacency.get(lbl, set())
        for neigh in neighbors:
            adjacency_src.append(i)
            adjacency_dst.append(label2id[neigh])

    # ----------------------------------------------------------------------
    # 3. Build same-shape edges
    #    Edge type: ('object', 'same_shape_as', 'object')
    #    - Undirected, but in DGL we add both directions (i->j, j->i)
    # ----------------------------------------------------------------------
    same_shape_src = []
    same_shape_dst = []

    for i, lbl_i in enumerate(unique_labels):
        arr_i = object_shapes[lbl_i]  # get the shape array for object i
        for j, lbl_j in enumerate(unique_labels):
            if j <= i:
                continue  # skip lower triangle and self
            arr_j = object_shapes[lbl_j]  # get the shape array for object j
            
            if is_same_shape(arr_i, arr_j):
                # Add edges in both directions
                same_shape_src.append(i)
                same_shape_dst.append(j)
                same_shape_src.append(j)
                same_shape_dst.append(i)

    # ----------------------------------------------------------------------
    # 4. (Optional) Build group nodes & edges
    #    - In a real scenario, you might define group membership edges, e.g.:
    #      ('group', 'contains', 'object') or ('object', 'member_of', 'group')
    # ----------------------------------------------------------------------
    group_src = []
    group_dst = []
    num_group_nodes = 0
    if include_groups:
        # For demonstration, let's pretend we create a single "group" node that contains all objects
        # or do something more elaborate if you have real group data.
        num_group_nodes = 1
        # The single group node ID will be 0 within the 'group' node space
        # We can connect that node to all object nodes
        for i in range(num_object_nodes):
            group_src.append(0)  # group node index
            group_dst.append(i)  # object node index
        # Edges: ('group', 'contains', 'object')

    # ----------------------------------------------------------------------
    # 5. Construct data dictionary for a heterograph
    #    Each key is a 3-tuple (src_type, edge_type, dst_type),
    #    and each value is (src_list, dst_list).
    # ----------------------------------------------------------------------
    data_dict = {
        # object -> object (adjacent_to)
        ("object", "adjacent_to", "object"): (
            torch.tensor(adjacency_src, dtype=torch.int64),
            torch.tensor(adjacency_dst, dtype=torch.int64),
        ),
        # object -> object (same_shape_as)
        ("object", "same_shape_as", "object"): (
            torch.tensor(same_shape_src, dtype=torch.int64),
            torch.tensor(same_shape_dst, dtype=torch.int64),
        ),
    }

    if include_groups:
        # Add the group->object edges
        data_dict[("group", "contains", "object")] = (
            torch.tensor(group_src, dtype=torch.int64),
            torch.tensor(group_dst, dtype=torch.int64),
        )
        # If you also want the reverse edges, you might do
        # ("object", "in_group", "group"): (...)

    # ----------------------------------------------------------------------
    # 6. Define how many nodes each type has
    # ----------------------------------------------------------------------
    num_nodes_dict = {
        "object": num_object_nodes,
    }
    if include_groups:
        num_nodes_dict["group"] = num_group_nodes

    # ----------------------------------------------------------------------
    # 7. Create the heterograph
    # ----------------------------------------------------------------------
    g = dgl.heterograph(data_dict, num_nodes_dict=num_nodes_dict)

    # ----------------------------------------------------------------------
    # 8. Add node features for 'object' nodes
    #    color: e.g. (lbl // 100)
    #    shape: padded 2D mask
    # ----------------------------------------------------------------------
    # color
    colors = np.array([lbl // 100 for lbl in unique_labels], dtype=np.float32)
    g.nodes["object"].data["color"] = torch.from_numpy(colors)

    shape_arrays = []
    for lbl in unique_labels:
        # Safely retrieve the array if it exists; otherwise use a 0×0 array
        arr = object_shapes.get(lbl, np.zeros((0, 0), dtype=np.uint8))
        
        # Optionally check if arr is None (in case object_shapes can store None)
        # if arr is None:
        #     arr = np.zeros((0, 0), dtype=np.uint8)
        
        shape_arrays.append(arr)

    # Find the largest dimension among the shape arrays
    max_dim = 1
    if shape_arrays:
        max_dim = max((max(a.shape) if a.size > 0 else 1) for a in shape_arrays)

    # Now you can proceed to pad each array to (max_dim x max_dim) and flatten
    padded_shapes = []
    for arr in shape_arrays:
        h, w = arr.shape if arr.size > 0 else (0, 0)
        pad_h = max_dim - h
        pad_w = max_dim - w
        arr_padded = np.pad(arr, ((0, pad_h), (0, pad_w)), mode="constant")
        padded_shapes.append(arr_padded.flatten())

    shape_features = np.stack(padded_shapes, axis=0).astype(np.float32)
    g.nodes["object"].data["shape"] = torch.from_numpy(shape_features)


    # Pad each mask to (max_dim x max_dim), then flatten
    padded_shapes = []
    for arr in shape_arrays:
        h, w = arr.shape if arr.size > 0 else (0, 0)
        pad_h = max_dim - h
        pad_w = max_dim - w
        arr_padded = np.pad(arr, ((0, pad_h), (0, pad_w)), mode="constant")
        padded_shapes.append(arr_padded.flatten())
    shape_features = np.stack(padded_shapes, axis=0).astype(np.float32)

    g.nodes["object"].data["shape"] = torch.from_numpy(shape_features)

    # ----------------------------------------------------------------------
    # 9. (Optionally) add node features for 'group' nodes
    # ----------------------------------------------------------------------
    if include_groups:
        # In a real scenario, you'd have group-level features. 
        # For demonstration, we’ll store a dummy 1D feature for each group node.
        group_feat = torch.zeros(num_group_nodes, 4)  # shape [num_group_nodes, 4]
        g.nodes["group"].data["group_feat"] = group_feat

    return g
