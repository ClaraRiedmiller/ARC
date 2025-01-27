from knowledge_graph.create_kg import create_knowledge_graph, visualize_knowledge_graph
from knowledge_graph.get_similarity import get_highest_similarity_pairs, create_similarity_matrix, optimal_one_to_one_assignment_with_valid_dummies

import arckit


train_set, eval_set = arckit.load_data()
task = train_set[100]
task.show()
db_manager = create_knowledge_graph(task)

# Get shared properties for a specific example_id
shared_properties = db_manager.get_shared_properties(example_id=2, batch_size=50)

sorted_properties = sorted(shared_properties, key=lambda x: x['normalized_similarity'], reverse=True)

# Print sorted results
for match in sorted_properties:
    print(match)

    best_pairs = get_highest_similarity_pairs(shared_properties)

# Print the result
for input_id, best_match in best_pairs.items():
    print(f"Input Object {input_id} best matches with Output Object {best_match['output_id']} with similarity {best_match['normalized_similarity']:.2f}")

similarity_matrix, input_ids, output_ids = create_similarity_matrix(shared_properties)

print("Similarity Matrix:")
print(similarity_matrix)


optimal_pairs = optimal_one_to_one_assignment_with_valid_dummies(shared_properties)

# Print the results
for pair in optimal_pairs:
    print(pair)