from knowledge_graph.create_kg import create_knowledge_graph, visualize_knowledge_graph
from knowledge_graph.kuzu_db_manager import *
from knowledge_graph.get_similarity import *
import arckit


train_set, eval_set = arckit.load_data()
task = train_set[4]
task.show()
db_manager = create_knowledge_graph(task)

# Get shared properties for a specific example_id
shared_properties = db_manager.get_shared_properties(example_id=1, batch_size=50)

sorted_properties = sorted(shared_properties, key=lambda x: x['normalized_similarity'], reverse=True)

for match in sorted_properties:
    print(match)

best_pairs = get_highest_similarity_pairs(shared_properties)
for input_id, best_match in best_pairs.items():
    print(f"Input Object {input_id} best matches with Output Object {best_match['output_id']} with similarity {best_match['normalized_similarity']:.2f}")

similarity_matrix, input_ids, output_ids = create_similarity_matrix(shared_properties)

# print("Similarity Matrix:")
# print(similarity_matrix)


optimal_pairs = optimal_one_to_one_assignment_with_valid_dummies(shared_properties)
# possibly_matches = one_to_many_matches_dict(shared_properties)

# print(possibly_matches)


# Print the results
for pair in optimal_pairs:
    print(pair)

unshared_matched = get_unshared_properties_for_matched_pairs(
    shared_properties, 
    optimal_pairs,
    considered_properties=None
)

for row in unshared_matched:
    print(row)

print(get_properties_for_matched_pairs(db_manager, optimal_pairs))
