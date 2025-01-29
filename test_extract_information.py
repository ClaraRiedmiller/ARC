from knowledge_graph.create_kg import KnowledgeGraphBuilder
from knowledge_graph.kuzu_db_manager import KuzuDBManager
from knowledge_graph.get_similarity import *
from knowledge_graph.utils import remove_folder_if_exists

import arckit



# Load data
train_set, eval_set = arckit.load_data()
similarity_matrices = {}

# Loop over the first 20 training sets
for i in range(min(20, len(train_set))):

    task = train_set[i]
    print(f"Processing training set {i + 1}")
    
    db_folder = "kuzudb"
    remove_folder_if_exists(db_folder)
    
    # Use context manager to create knowledge graph
    with KuzuDBManager(db_folder) as db_manager:
        db_manager.create_schema()
        kg_builder = KnowledgeGraphBuilder(db_manager)
        kg_builder.build_knowledge_graph(task)


        # Get shared properties for the specific example_id
        shared_properties = db_manager.get_shared_properties(example_id=1, batch_size=50)

        # Sort the shared properties by normalized similarity
        sorted_properties = sorted(shared_properties, key=lambda x: x['normalized_similarity'], reverse=True)

        # Print sorted matches
        for match in sorted_properties:
            print(match)

        # Get the highest similarity pairs
        best_pairs = get_highest_similarity_pairs(shared_properties)
        for input_id, best_match in best_pairs.items():
            print(f"Input Object {input_id} best matches with Output Object {best_match['output_id']} with similarity {best_match['normalized_similarity']:.2f}")

        # Create the similarity matrix
        similarity_matrix, input_ids, output_ids = create_similarity_matrix(shared_properties)

        # Store the similarity matrix for this task
        similarity_matrices[f"Task_{i + 1}"] = {
            "similarity_matrix": similarity_matrix,
            "input_ids": input_ids,
            "output_ids": output_ids
        }

        # Print the optimal pairs
        optimal_pairs = optimal_one_to_one_assignment_with_valid_dummies(shared_properties)
        for pair in optimal_pairs:
            print(pair)

        # Get unshared matched properties
        unshared_matched = get_unshared_properties_for_matched_pairs(
            shared_properties, 
            optimal_pairs,
            considered_properties=None
        )

        # Print unshared matched properties
        for row in unshared_matched:
            print(row)

        # Print properties for matched pairs
        print(get_properties_for_matched_pairs(db_manager, optimal_pairs))

        

# The similarity_matrices dictionary contains the matrices for the first 20 training sets
