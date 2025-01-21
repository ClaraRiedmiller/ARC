from arckit_handler import drawProblem
from create_Obj import *
from create_KG import *
from create_obj_Rel import *

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import networkx as nx
import torch
from dgl import to_networkx

if __name__ == "__main__":
    # Example array with multiple "colors"
    # Example usage
    task = train_set[4]
    drawProblem(task, "ForGraphTest")
        # For a single grid:
    grid = task.train[0][0]
    g = create_heterograph_with_relations(grid, include_groups=True)
    visualize_heterograph(
        g,
        node_attrs=["color", "shape"], 
        edge_attrs=[], 
        plot_name="../images/kg_plots/Graph_Single.png"
    )

    # Or for multiple subplots (task with 4 known grids):
    visualize_multiple_heterographs(
        task,
        create_graph_func=create_heterograph_with_relations,
        plot_name="../images/kg_plots/Graphs_Multiple.png"
    )