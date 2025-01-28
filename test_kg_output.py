from knowledge_graph.create_kg import create_knowledge_graph, visualize_knowledge_graph
from knowledge_graph.kuzu_db_manager import *
from knowledge_graph.get_similarity import *
from knowledge_graph.create_output import *
import arckit


train_set, eval_set = arckit.load_data()
task = train_set[4]
task.show()
db_manager = create_knowledge_graph(task)

# Get shared properties for a specific example_id
shared_properties = db_manager.get_shared_properties(example_id=1, batch_size=50)

best_pairs = get_highest_similarity_pairs(shared_properties)

similarity_matrix, input_ids, output_ids = create_similarity_matrix(shared_properties)

optimal_pairs = optimal_one_to_one_assignment_with_valid_dummies(shared_properties)
possibly_matches = one_to_many_matches_dict(shared_properties)

print(possibly_matches)


# Print the results
# for pair in optimal_pairs:
#     print(pair)

# print(possibly_matches)

unshared_matched = get_unshared_properties_for_matched_pairs(
    shared_properties, 
    optimal_pairs,
    considered_properties=None
)


top_5 = get_top_n_matches(possibly_matches, n=5)

print("Top 5 matches by similarity:")
for in_id, out_id, sim in top_5:
    print(f"Input {in_id} => Output {out_id} (similarity: {sim})")

top_5_dict = get_top_n_matches_dict(possibly_matches)



possibly_matches = one_to_many_matches_dict(shared_properties, similarity_threshold=0.1)

# 2) Fetch the top 5 properties for matched pairs

print(possibly_matches)
print(optimal_pairs)
print(top_5_dict)

#######Make the outputs uniform; transform the top_5 function; Extract features for possibly_matches 


# For instance, create 20x20 input grids and 25x25 output grids:
all_pairs = create_input_output_grid_pairs((20, 20), (25, 25), get_properties_for_top_n_matches(db_manager, possibly_matches))
print(all_pairs)
# print(all_pairs)

