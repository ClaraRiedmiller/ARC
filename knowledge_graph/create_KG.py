from arckit import Task

import numpy as np
import torch
import networkx as nx
from dgl import to_networkx

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

from knowledge_graph.create_obj import label_by_color, get_unique_labels, extract_object_shapes
from create_obj_Rel import get_object_adjacency_scipy, is_same_shape
from create_obj_groups import *

from kuzu_db_manager import KuzuDBManager

def extract_objects(gird):
    """
    Extracts object-level nodes from a grid.
    """
    pass

def extract_groups(grid):
    """
    Extracts group-level nodes from a grid.
    """
    pass

def extract_contains_relations(grid):
    """
    Extracts contains relations between groups and objects.
    """
    pass

def create_knowledge_graph(task: Task):
    knowledge_graph = KuzuDBManager()
    knowledge_graph.create_schema()

    for input, output in task.train:
        # Extract object-level nodes
        input_objects = extract_objects(input)
        output_objects = extract_objects(output)

        # Extract group-level nodes
        input_groups = extract_groups(input)
        output_groups = extract_groups(output)

        # Extract contains relations between groups and objects
        input_contains = extract_contains_relations(input)
        output_contains = extract_contains_relations(output)

    # Insert the data into the database
    knowledge_graph.insert_input_objects(input_objects)
    knowledge_graph.insert_output_objects(output_objects)
    knowledge_graph.insert_input_groups(input_groups)
    knowledge_graph.insert_output_groups(output_groups) 
    knowledge_graph.relationships(input_contains + output_contains)   

    # TODO: Extend to add task.test to the knowledge graph so we can make predictions
    return knowledge_graph

def create_heterograph_with_relations_and_groups(grid):
    """
    Create a DGL heterograph that includes:
      - 'object' node type for each labeled object
      - 'group' node type for each group (color, shape, adjacency, rotations, shape_color)
      - edges among objects ('adjacent_to', 'same_shape_as')
      - edges from group -> object ('contains')
    with added features for both objects and groups.
    """

    # ----------------------------------------------------------------------
    # (A) OBJECT-LEVEL PREPARATION
    # ----------------------------------------------------------------------
    labeled_array = label_by_color(grid, mode="direct")
    unique_labels = get_unique_labels(labeled_array, exclude_zero=True)
    object_shapes = extract_object_shapes(labeled_array)
    adjacency = get_object_adjacency_scipy(labeled_array, mode="diagonal")

    # Map each label -> integer ID for 'object' nodes
    label2obj_id = {lbl: i for i, lbl in enumerate(unique_labels)}
    num_object_nodes = len(unique_labels)

    # Build adjacency edges (object <-> object)
    adjacency_src, adjacency_dst = [], []
    for lbl in unique_labels:
        i = label2obj_id[lbl]
        neighbors = adjacency.get(lbl, set())
        for neigh in neighbors:
            adjacency_src.append(i)
            adjacency_dst.append(label2obj_id[neigh])

    # Build same-shape edges (object <-> object)
    same_shape_src, same_shape_dst = [], []
    for i, lbl_i in enumerate(unique_labels):
        arr_i = object_shapes[lbl_i]
        for j, lbl_j in enumerate(unique_labels):
            if j <= i:
                continue
            arr_j = object_shapes[lbl_j]
            if is_same_shape(arr_i, arr_j):
                same_shape_src.extend([i, j])
                same_shape_dst.extend([j, i])

    # ----------------------------------------------------------------------
    # (B) EXTRACT OBJECT FEATURES
    # ----------------------------------------------------------------------
    # 1) Color
    object_colors = np.array([lbl // 100 for lbl in unique_labels], dtype=np.float32)

    # 2) Shape (flattened/padded)
    shape_arrays = [object_shapes.get(lbl, np.zeros((0, 0), dtype=np.uint8))
                    for lbl in unique_labels]
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

    # 3) Bounding box (height, width)
    #    We'll just store (height, width) for each object
    object_bboxes = []
    for lbl in unique_labels:
        arr = object_shapes[lbl]
        if arr.size == 0:
            object_bboxes.append((0, 0))
        else:
            h, w = arr.shape
            object_bboxes.append((h, w))
    object_bboxes = np.array(object_bboxes, dtype=np.float32)  # shape [N, 2]

    # ----------------------------------------------------------------------
    # (C) CREATE GROUPS
    # ----------------------------------------------------------------------
    groups_dict = create_groups(grid)
    # e.g., "color_groups", "shape_groups", "adjacency_groups", "rotations_groups", "shape_color_groups"

    # We'll unify them all in a single node type = "group"
    # We'll track each group as (group_label_set, group_type_str)
    group_entries = []

    # Provide an integer code for each group type (for group_type feature)
    # This is just one example mapping:
    group_type_map = {
        "color_group": 1,
        "shape_group": 2,
        "adjacency_group": 3,
        "rotation_group": 4,
        "shape_color_group": 5
    }

    # (i) color_groups: dict[color_val] = set(labels)
    color_groups = groups_dict["color_groups"]
    for color_val, lbl_set in color_groups.items():
        group_entries.append((lbl_set, "color_group"))

    # (ii) shape_groups: dict[shape_key] = set(labels)
    shape_groups = groups_dict["shape_groups"]
    for shape_key, lbl_set in shape_groups.items():
        group_entries.append((lbl_set, "shape_group"))

    # (iii) adjacency_groups: list of sets
    adjacency_groups = groups_dict["adjacency_groups"]
    for lbl_set in adjacency_groups:
        group_entries.append((lbl_set, "adjacency_group"))

    # (iv) rotations_groups: list of sets
    rotations_groups = groups_dict["rotations_groups"]
    for lbl_set in rotations_groups:
        group_entries.append((lbl_set, "rotation_group"))

    # (v) shape_color_groups: dict[(shape_key, color_val)] = set(labels)
    shape_color_groups = groups_dict["shape_color_groups"]
    for sc_key, lbl_set in shape_color_groups.items():
        group_entries.append((lbl_set, "shape_color_group"))

    # Assign each group node an ID
    group_node_entries = []  # will store (group_id, lbl_set, group_type_str)
    gid = 0
    for (lbl_set, gtype_str) in group_entries:
        if len(lbl_set) == 0:
            continue
        group_node_entries.append((gid, lbl_set, gtype_str))
        gid += 1
    num_group_nodes = gid

    # Edges from group->object
    group_src, group_dst = [], []
    for (gid, lbl_set, gtype_str) in group_node_entries:
        for lbl in lbl_set:
            if lbl in label2obj_id:
                obj_id = label2obj_id[lbl]
                group_src.append(gid)
                group_dst.append(obj_id)

    # ----------------------------------------------------------------------
    # (D) BUILD THE HETEROGRAPH
    # ----------------------------------------------------------------------
    
    return 


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
                ("object", "adjacent_to", "object"): "blue",
                ("object", "same_shape_as", "object"): "red",
                ("group", "contains", "object"): "green",
                "unknown": "black"
            } # Before fix: "adjacent_to", no tuples. 

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
def visualize_all_train_heterographs(task, create_graph_func, plot_name=None):
    """
    Visualize all heterographs in task.train where task.train is of shape (i, 1).

    Parameters:
        task: Task object containing the grids (train/test) for a task.
        create_graph_func: Function to create a heterograph from a grid.
        plot_name (str): If provided, saves the combined plot to this path.
    """
    num_train = len(task.train)  # Number of training examples

    # Create subplots dynamically based on the number of training examples
    num_cols = 2  # Each training example has an Input/Output pair
    num_rows = num_train  # One row per training example
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(12, 6 * num_rows))

    for row_idx, (input_output_pair) in enumerate(task.train):
        input_grid, output_grid = input_output_pair[0], input_output_pair[1]
        
        # Create and visualize the input grid
        ax_input = axes[row_idx, 0] if num_train > 1 else axes[0]
        g_input = create_graph_func(input_grid)
        visualize_heterograph(
            g_input,
            node_attrs=["color", "shape"],
            edge_attrs=[],
            edge_color_map={
                ("object", "adjacent_to", "object"): "blue",
                ("object", "same_shape_as", "object"): "red",
                ("group", "contains", "object"): "green",
                "unknown": "black"
            },
            ax=ax_input
        )
        ax_input.set_title(f"Train {row_idx + 1}: Input", fontsize=14)

        # Create and visualize the output grid
        ax_output = axes[row_idx, 1] if num_train > 1 else axes[1]
        g_output = create_graph_func(output_grid)
        visualize_heterograph(
            g_output,
            node_attrs=["color", "shape"],
            edge_attrs=[],
            edge_color_map={
                ("object", "adjacent_to", "object"): "blue",
                ("object", "same_shape_as", "object"): "red",
                ("group", "contains", "object"): "green",
                "unknown": "black"
            },                          #different relation naming: not just adjacent to
            ax=ax_output
        )
        ax_output.set_title(f"Train {row_idx + 1}: Output", fontsize=14)

    plt.tight_layout()
    if plot_name:
        plt.savefig(plot_name, dpi=300, bbox_inches="tight")
    plt.show()