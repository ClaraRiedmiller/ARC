from arckit_handler import drawProblem
from objects import *
from create_KG import *
from adjacency import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import networkx as nx
import torch
from dgl import to_networkx

if __name__ == "__main__":
    # Example array with multiple "colors" (values)
    task = train_set[20]
    drawProblem(task, "ForGraphTest")
    
    # for j in range(len(task.train[0])):     
    #     for i in range(2):                  
    #         example_grid = task.train[j][i]
    #         if i == 0:
    #             print("New Task:\n ------Input------:\n")
    #         else:
    #             print("------Output------:\n")
            
    #         labeled_array = label_by_color(example_grid, mode="diagonal")
    #         print("Labeled Object-Grid:\n", labeled_array)
            
    #         print("\n List of Objects: \n", [int(labeled_object) for labeled_object in get_unique_labels(labeled_array)])
            
    #         object_shapes = extract_object_shapes(labeled_array)
    #         converted_shapes_dict = {
    #             int(k): v.astype(int).tolist() 
    #             for k, v in object_shapes.items()
    #         }
    #         print("Shape dictionary:\n ",converted_shapes_dict)                
            
    #         # Convert dictionary keys and values
    #         coordinate_dict = label_coordinates_dict(labeled_array, exclude_zero=True)
    #         converted_coordinate_dict = {int(key): [(int(x), int(y)) for x, y in value] for key, value in coordinate_dict.items()}
    #         print("\n Coordinate Dict:", converted_coordinate_dict)
                
    #         # Direct adjacency dictionary
    #         adj_direct = get_object_adjacency_scipy(labeled_array, mode="direct")
    #         converted_adj_direct = {int(key): [int(n) for n in neighbors] for key, neighbors in adj_direct.items()}
    #         print("\n Direct adjacent objects: \n", converted_adj_direct)
                    
    #         # Diagonal adjacency dictionary
    #         adj_diagonal = get_object_adjacency_scipy(labeled_array, mode="diagonal")
    #         converted_adj_diagonal = {int(key): [int(n) for n in neighbors] for key, neighbors in adj_diagonal.items()}
    #         print("\n Diagonally adjacent objects: \n", converted_adj_diagonal)


    grid = task.train[0][0]

    # Create a heterograph with both object-level nodes and group-level nodes
    g = create_heterograph_with_relations(grid, include_groups=True)

    print(g)  # prints a summary of the heterograph
    # e.g.:
    # Graph(num_nodes={'object': 5, 'group': 1},
    #       num_edges={('group', 'contains', 'object'): 5,
    #                  ('object', 'adjacent_to', 'object'): 8,
    #                  ('object', 'same_shape_as', 'object'): 2},
    #       metagraph=[('group', 'contains', 'object'), 
    #                  ('object', 'adjacent_to', 'object'),
    #                  ('object', 'same_shape_as', 'object')])

    # Inspect node features
    print(g.nodes["object"].data["color"].shape)
    print(g.nodes["object"].data["shape"].shape)

    # If we stored group features:
    if "group" in g.ntypes:
        print(g.nodes["group"].data["group_feat"].shape)


    
    #Convert the DGL graph to a NetworkX graph
    nx_g = to_networkx(g, node_attrs=['color', 'shape'], edge_attrs=['type'])

    # Initialize lists for node attributes
    node_colors = []
    cmap = plt.cm.viridis  # Colormap for numerical values
    norm = plt.Normalize(vmin=0, vmax=10)  # Normalization for node colors

    # Process node attributes
    for n, d in nx_g.nodes(data=True):
        if 'color' in d:  # Check if the color attribute exists
            if isinstance(d['color'], torch.Tensor):
                value = d['color'].item() if d['color'].ndim == 0 else 0
            elif isinstance(d['color'], (int, float)):
                value = d['color']
            else:
                value = 0  # Default value if not a tensor or number
            # Map numeric value to a colormap
            node_colors.append(cmap(norm(value)))
        else:
            node_colors.append('gray')  # Default color if no attribute exists

    # Initialize edge colors
    edge_colors = []
    edge_color_map = {
        ('group', 'contains', 'object'): 'green',
        ('object', 'adjacent_to', 'object'): 'blue',
        ('object', 'same_shape_as', 'object'): 'red',
        'unknown': 'black',  # Fallback for unknown relations
}

    # Process edge attributes
    for u, v, data in nx_g.edges(data=True):
        print(f"Edge from {u} to {v}: {data}")  # Debugging line
        rel_type = data.get('etype', 'unknown')  # Extract 'etype' instead of 'type'
        edge_colors.append(edge_color_map.get(rel_type, 'black'))  # Default to black if unknown

    print("Edge Colors:", edge_colors)  # Debugging line



    # Draw the graph
    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(nx_g)  # Generate positions using a spring layout

    # Draw the nodes and edges with colors
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

    plt.savefig("heterograph_visualization.png", dpi=300, bbox_inches='tight')  # Export as PNG
    plt.show()