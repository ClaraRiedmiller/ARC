import arckit
import kuzu

from create_Obj import *
from create_KG import create_knowledge_graph
from create_obj_Rel import *
from create_obj_groups import *



if __name__ == "__main__":
    # Load the data
    train_set, _ = arckit.load_data()

    for task in train_set:
        # Create a task centric knowledge graph
        knowledge_graph = create_knowledge_graph(task)


    # Or for multiple subplots (task with 4 known grids):
    visualize_all_train_heterographs(
        task,
        create_graph_func=create_heterograph_with_relations_and_groups,
        plot_name="images/kg_plots/Graphs_Multiple.png"
    )