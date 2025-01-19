import numpy as np
import torch
import dgl
import networkx as nx
from dgl import to_networkx

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

from create_Obj import label_by_color, get_unique_labels, extract_object_shapes
from create_obj_Rel import get_object_adjacency_scipy, is_same_shape


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
    adjacency = get_object_adjacency_scipy(labeled_array, mode="diagonal")

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
    # ----------------------------------------------------------------------
    same_shape_src = []
    same_shape_dst = []

    for i, lbl_i in enumerate(unique_labels):
        arr_i = object_shapes[lbl_i]  # shape array for object i
        for j, lbl_j in enumerate(unique_labels):
            if j <= i:
                continue  # skip lower triangle and self (don't comparre in bothe directions)
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
        arr = object_shapes.get(lbl, np.zeros((0, 0), dtype=np.uint8))
        if arr is None:
            arr = np.zeros((0, 0), dtype=np.uint8)
        shape_arrays.append(arr)

    # Padding is questionable: blows up and we loose the shape correspondence;
    # Seems to be necessary for a lot of GNN applications. 
    # Finding shape correspondence could be done earlier and IDd by Integers.We still have the original shapes
    # Maybe just 


    max_dim = 1
    if shape_arrays:
        max_dim = max((max(a.shape) if a.size > 0 else 1) for a in shape_arrays)


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
        # For demonstration, we’ll store a dummy 1D feature for each group node.
        group_feat = torch.zeros(num_group_nodes, 4)  # shape [num_group_nodes, 4]
        g.nodes["group"].data["group_feat"] = group_feat

    return g


def visualize_heterograph(
    g, 
    node_attrs=None, 
    edge_attrs=None, 
    edge_color_map=None, 
    colormap='viridis',
    plot_name=None
):
    """
    Parameters:
        g (dgl.DGLGraph): The heterograph to visualize.
        node_attrs (list): List of node attributes to include in visualization (e.g., ['color', 'shape']).
        edge_attrs (list): List of edge attributes to include (e.g., ['etype']).
        edge_color_map (dict): Mapping of edge relation types to colors.
        colormap (str): Colormap name for numeric node attributes.
        output_file (str): Filepath to save the plot. If None, the plot is not saved.
    """
    # Default edge color map if none is provided
    if edge_color_map is None:
        edge_color_map = {
            ('group', 'contains', 'object'): 'green',
            ('object', 'adjacent_to', 'object'): 'blue',
            ('object', 'same_shape_as', 'object'): 'red',
            'unknown': 'black',  # Fallback for unknown relations
        }

    # Convert the DGL graph to a NetworkX graph
    nx_g = to_networkx(
    g, 
    node_attrs=node_attrs, 
    edge_attrs=edge_attrs, 
    etype_attr='relation_type'  # Use a different name for edge type
)

    # Initialize colormap
    cmap = plt.cm.get_cmap(colormap)
    norm = plt.Normalize(vmin=0, vmax=10)

    # Process node attributes
    node_colors = []
    for n, d in nx_g.nodes(data=True):
        if 'color' in d:
            if isinstance(d['color'], torch.Tensor):
                value = d['color'].item() if d['color'].ndim == 0 else 0
            elif isinstance(d['color'], (int, float)):
                value = d['color']
            else:
                value = 0
            node_colors.append(cmap(norm(value)))
        else:
            node_colors.append('gray')  # Default color if no attribute exists

    edge_colors = []
    for u, v, data in nx_g.edges(data=True):
        rel_type = data.get('relation_type', 'unknown')  # Use 'relation_type' instead of 'etype'
        edge_colors.append(edge_color_map.get(rel_type, 'black'))
    # Draw the graph
    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(nx_g)  # Generate positions using a spring layout
    nx.draw(
        nx_g, pos,
        node_color=node_colors,
        edge_color=edge_colors,
        with_labels=True,
        node_size=800,
        font_size=10
    )

    # Add legend for edge types
    for label, color in edge_color_map.items():
        plt.plot([], [], color=color, label=label, linewidth=2)
    plt.legend(title="Edge Types")

    plt.title("Heterograph Visualization")

    # Save or show the plot
    if plot_name:
        plt.savefig(plot_name, dpi=300, bbox_inches='tight')
    plt.show()