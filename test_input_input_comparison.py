import arckit
import numpy as np
import json

# Imports from knowledge_graph
from knowledge_graph.create_kg import *
from knowledge_graph.kuzu_db_manager import KuzuDBManager
from knowledge_graph.get_similarity import *
from knowledge_graph.create_output import *


train_set, eval_set = arckit.load_data()
task = train_set[102]
print(len(task.train))

def get_best_input_correspondence(task):
    """
    Finds the training input grid that best corresponds to the test input grid
    based on the highest overall similarity.

    Parameters:
    - task: A Task object containing training and test data.

    Returns:
    - best_matched_pairs: A list of matched object pairs between the best training input grid and the test input grid.
    - best_train_grid_id: The index of the training input grid with the highest similarity.
    """

    # Step 1: Build the knowledge graph
    db_manager = create_knowledge_graph(task)

    highest_similarity = float('-inf')
    best_train_grid_id = None
    best_matched_pairs = []

    # Step 2: Loop through all training input grids and compare with test input grid
    for train_grid_id in range(len(task.train)):  # Loop over training grids
        # Extract shared properties between training input `train_grid_id` and test input
        shared_properties = db_manager.shared_properties_across_input(train_grid_id, 9)

        # Perform optimal one-to-one assignment
        one_to_one_results = optimal_one_to_one_assignment_with_valid_dummies(
            shared_properties,
            similarity_threshold=0  # Consider all potential matches
        )

        # Extract matched object pairs
        matched_pairs = [row for row in one_to_one_results if row['marker'] == 'matched']
        matched_pairs = sorted(matched_pairs, key=lambda x: x['similarity'], reverse=True)[:5]


        # Compute overall similarity score for this training grid
        total_similarity = sum(pair['similarity'] for pair in matched_pairs)

        # Step 3: Update best match if this grid has the highest similarity
        if total_similarity > highest_similarity:
            highest_similarity = total_similarity
            best_train_grid_id = train_grid_id
            best_matched_pairs = matched_pairs

    return best_matched_pairs, best_train_grid_id


print(get_best_input_correspondence(task))