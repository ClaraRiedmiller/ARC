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
    task = train_set[20]
    drawProblem(task, "ForGraphTest")

    grid = task.train[0][0]
    g = create_heterograph_with_relations(grid, include_groups=True)

    # Print summary for debugging
    print(g)

    # Generalized visualization
    visualize_heterograph(
        g,
        node_attrs=['color', 'shape'], 
        edge_attrs=['etype'], 
        plot_name="./kg_plots/Graph_Task_20_00.png"
    )