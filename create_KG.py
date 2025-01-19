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
    """
    # ----------------------------------------------------------------------
    # 1. Identify object-level data
    # ----------------------------------------------------------------------
    labeled_array = label_by_color(grid, mode="direct")
    unique_labels = get_unique_labels(labeled_array, exclude_zero=True)
    object_shapes = extract_object_shapes(labeled_array)

    # Create adjacency using diagonal connectivity
    adjacency = get_object_adjacency_scipy(labeled_array, mode="diagonal")

    # Map each label to an integer ID (for 'object' nodes)
    label2id = {lbl: i for i, lbl in enumerate(unique_labels)}
    num_object_nodes = len(unique_labels)

    # ----------------------------------------------------------------------
    # 2. Build adjacency edges (object -> object)
    # ----------------------------------------------------------------------
    adjacency_src, adjacency_dst = [], []
    for lbl in unique_labels:
        i = label2id[lbl]
        neighbors = adjacency.get(lbl, set())
        for neigh in neighbors:
            adjacency_src.append(i)
            adjacency_dst.append(label2id[neigh])

    # ----------------------------------------------------------------------
    # 3. Build same-shape edges (object -> object)
    # ----------------------------------------------------------------------
    same_shape_src, same_shape_dst = [], []
    for i, lbl_i in enumerate(unique_labels):
        arr_i = object_shapes[lbl_i]
        for j, lbl_j in enumerate(unique_labels):
            if j <= i:
                continue
            arr_j = object_shapes[lbl_j]
            if is_same_shape(arr_i, arr_j):
                # Add edges in both directions
                same_shape_src.extend([i, j])
                same_shape_dst.extend([j, i])

    # ----------------------------------------------------------------------
    # 4. (Optional) Build group nodes & edges
    # ----------------------------------------------------------------------
    group_src, group_dst = [], []
    num_group_nodes = 0
    if include_groups:
        # Single 'group' node that contains all objects (demo)
        num_group_nodes = 1
        for i in range(num_object_nodes):
            group_src.append(0)  # group node index
            group_dst.append(i)  # object node index

    # ----------------------------------------------------------------------
    # 5. Construct data dictionary for the heterograph
    # ----------------------------------------------------------------------
    data_dict = {
        ("object", "adjacent_to", "object"): (
            torch.tensor(adjacency_src, dtype=torch.int64),
            torch.tensor(adjacency_dst, dtype=torch.int64),
        ),
        ("object", "same_shape_as", "object"): (
            torch.tensor(same_shape_src, dtype=torch.int64),
            torch.tensor(same_shape_dst, dtype=torch.int64),
        ),
    }
    if include_groups:
        data_dict[("group", "contains", "object")] = (
            torch.tensor(group_src, dtype=torch.int64),
            torch.tensor(group_dst, dtype=torch.int64),
        )

    # ----------------------------------------------------------------------
    # 6. Define number of nodes for each type
    # ----------------------------------------------------------------------
    num_nodes_dict = {"object": num_object_nodes}
    if include_groups:
        num_nodes_dict["group"] = num_group_nodes

    # ----------------------------------------------------------------------
    # 7. Create the heterograph
    # ----------------------------------------------------------------------
    g = dgl.heterograph(data_dict, num_nodes_dict=num_nodes_dict)

    # ----------------------------------------------------------------------
    # 8. Add node features for 'object' nodes (color & shape)
    # ----------------------------------------------------------------------
    colors = np.array([lbl // 100 for lbl in unique_labels], dtype=np.float32)
    g.nodes["object"].data["color"] = torch.from_numpy(colors)

    # Prepare shape features (padded 2D arrays flattened)
    shape_arrays = [object_shapes.get(lbl, np.zeros((0, 0), dtype=np.uint8)) for lbl in unique_labels]
    max_dim = 1
    if shape_arrays:
        max_dim = max((max(a.shape) if a.size > 0 else 1) for a in shape_arrays)

    padded_shapes = []
    for arr in shape_arrays:
        h, w = arr.shape if arr.size > 0 else (0, 0)
        pad_h, pad_w = max_dim - h, max_dim - w
        arr_padded = np.pad(arr, ((0, pad_h), (0, pad_w)), mode="constant")
        padded_shapes.append(arr_padded.flatten())
    shape_features = np.stack(padded_shapes, axis=0).astype(np.float32)
    g.nodes["object"].data["shape"] = torch.from_numpy(shape_features)

    # (Optional) group node features
    if include_groups:
        group_feat = torch.zeros(num_group_nodes, 4)  # shape [num_group_nodes, 4]
        g.nodes["group"].data["group_feat"] = group_feat

    return g

###############################################################################
# 2. Visualize a Single Heterograph (Node & Edge Colors)
###############################################################################
def visualize_heterograph(
    g,
    node_attrs=None,
    edge_attrs=None,
    edge_color_map=None,
    colormap="viridis",
    plot_name=None,
    ax=None
):
    """
    Visualize a single heterograph with nodes and edges colored by attributes.

    Parameters:
        g (dgl.DGLGraph): The heterograph to visualize.
        node_attrs (list): Node attributes to include (e.g., ['color', 'shape']).
        edge_attrs (list): Edge attributes to include (e.g., []).
        edge_color_map (dict): Mapping of edge types to colors (e.g. 'adjacent_to' -> 'blue').
        colormap (str): Colormap name for numeric node attributes.
        plot_name (str): Filepath to save the plot. If None, the plot is not saved.
        ax (plt.Axes): If provided, draw on this subplot axis. Otherwise, create a new figure.
    """
    # 1. Default Edge Color Map
    if edge_color_map is None:
        edge_color_map = {
            "adjacent_to": "blue",
            "same_shape_as": "red",
            "contains": "green",
            "unknown": "black",
        }

    # 2. Convert the DGL graph to a NetworkX graph
    #    - Do NOT use 'etype' in edge_attrs or it conflicts with DGL's internal usage
    nx_g = to_networkx(
        g,
        node_attrs=node_attrs,
        edge_attrs=edge_attrs,  # Typically []
        etype_attr="relation_type"  # Name for edge type attribute
    )

    # 3. Colormap & Normalization for Node Colors
    cmap = plt.cm.get_cmap(colormap)
    norm = plt.Normalize(vmin=0, vmax=10)  # Adjust as needed

    # 4. Map Node Colors
    node_colors = []
    for _, data_dict in nx_g.nodes(data=True):
        if "color" in data_dict:
            val = data_dict["color"]
            # Handle torch.Tensor or scalar
            if isinstance(val, torch.Tensor):
                val = val.item()
            node_colors.append(cmap(norm(val)))
        else:
            node_colors.append("gray")

    # 5. Map Edge Colors Based on 'relation_type'
    edge_colors = []
    for _, _, data_dict in nx_g.edges(data=True):
        rel_type = data_dict.get("relation_type", "unknown")
        edge_colors.append(edge_color_map.get(rel_type, "black"))

    # 6. Draw the Graph
    if ax is None:
        plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(nx_g)
    nx.draw(
        nx_g, pos,
        ax=ax,
        with_labels=True,
        node_color=node_colors,
        edge_color=edge_colors,
        node_size=800,
        font_size=10
    )

    # 7. Legend & (Optional) Save
    if ax is None:
        for label, color in edge_color_map.items():
            plt.plot([], [], color=color, label=label, linewidth=2)
        plt.legend(title="Edge Types")
        plt.title("Heterograph Visualization")

        if plot_name:
            plt.savefig(plot_name, dpi=300, bbox_inches="tight")
        plt.show()

###############################################################################
# 3. Visualize Multiple Heterographs in a 2x2 Grid
###############################################################################
def visualize_multiple_heterographs(task, create_graph_func, plot_name=None):
    """
    Visualize multiple heterographs in a 2x2 grid layout using grids from a task.

    Parameters:
        task: Task object containing the grids (train/test) for a task.
        create_graph_func: Function to create a heterograph from a grid.
        plot_name (str): If provided, saves the combined plot to this path.
    """
    # Define the grids to process and plot (4 subplots)
    grids = [
        (task.train[0][0], "train[0][0]"),
        (task.train[0][1], "train[0][1]"),
        (task.train[1][0], "train[1][0]"),
        (task.train[1][1], "train[1][1]"),
    ]
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))

    for idx, (grid, title_str) in enumerate(grids):
        ax = axes[idx // 2, idx % 2]
        
        # Create the heterograph
        g = create_graph_func(grid, include_groups=True)

        # Reuse single-graph visualization for each subplot
        visualize_heterograph(
            g,
            node_attrs=["color", "shape"], 
            edge_attrs=[],  # Typically no conflict with 'etype'
            edge_color_map={
                "adjacent_to": "blue",
                "same_shape_as": "red",
                "contains": "green",
                "unknown": "black",
            },
            ax=ax
        )
        ax.set_title(title_str, fontsize=14)

    plt.tight_layout()
    if plot_name:
        plt.savefig(plot_name, dpi=300, bbox_inches="tight")
    plt.show()