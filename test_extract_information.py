from knowledge_graph.create_kg import create_knowledge_graph, visualize_knowledge_graph

import numpy as np
from scipy.optimize import linear_sum_assignment
import arckit

def get_highest_similarity_pairs(shared_properties):
    # Create a dictionary to store the best match for each input_id
    best_pairs = {}

    for match in shared_properties:
        input_id = match['input_id']
        # Check if this input_id is already in the dictionary
        if input_id not in best_pairs:
            best_pairs[input_id] = match
        else:
            # Compare similarities and keep the highest
            if match['normalized_similarity'] > best_pairs[input_id]['normalized_similarity']:
                best_pairs[input_id] = match

    return best_pairs

def create_similarity_matrix(shared_properties):
    # Extract unique input and output IDs
    input_ids = sorted(set(match['input_id'] for match in shared_properties))
    output_ids = sorted(set(match['output_id'] for match in shared_properties))
    
    # Create mappings for row (input_id) and column (output_id) indices
    input_index = {id_: idx for idx, id_ in enumerate(input_ids)}
    output_index = {id_: idx for idx, id_ in enumerate(output_ids)}

    # Initialize the similarity matrix with zeros
    similarity_matrix = np.zeros((len(input_ids), len(output_ids)))

    # Populate the similarity matrix with similarity scores
    for match in shared_properties:
        row = input_index[match['input_id']]
        col = output_index[match['output_id']]
        similarity_matrix[row, col] = match['normalized_similarity']

    return similarity_matrix, input_ids, output_ids


def optimal_one_to_one_assignment_with_valid_dummies(shared_properties, similarity_threshold=0.2):
    # Create the similarity matrix and extract input/output IDs
    similarity_matrix, input_ids, output_ids = create_similarity_matrix(shared_properties)

    # Determine the size of the larger dimension (input or output) for padding
    max_size = max(len(input_ids), len(output_ids))

    # Pad the similarity matrix with zeros (no similarity for dummy pairs)
    padded_matrix = np.zeros((max_size, max_size))
    padded_matrix[:len(input_ids), :len(output_ids)] = similarity_matrix

    # Convert the padded similarity matrix to a cost matrix (negative similarity for maximization)
    cost_matrix = -padded_matrix

    # Solve the assignment problem using the Hungarian algorithm
    row_indices, col_indices = linear_sum_assignment(cost_matrix)

    # Extract matched pairs and identify unmatched outputs
    matched_outputs = set()  # Tracks outputs that are properly matched
    unmatched_outputs = set(range(len(output_ids)))  # Initially, all outputs are unmatched

    results = []

    for i, j in zip(row_indices, col_indices):
        if i < len(input_ids) and j < len(output_ids):  # Real input-output match
            similarity = similarity_matrix[i, j]
            if similarity >= similarity_threshold:
                results.append({
                    "input_id": input_ids[i],
                    "output_id": output_ids[j],
                    "similarity": similarity,
                    "marker": "matched"
                })
                matched_outputs.add(j)  # Mark this output as matched
                unmatched_outputs.discard(j)  # Remove from unmatched
            else:
                unmatched_outputs.add(j)  # Below threshold, treat as unmatched
        elif j < len(output_ids):  # Dummy input-output match
            unmatched_outputs.add(j)

    # Add unmatched outputs with dummy input assignments
    for unmatched_index in unmatched_outputs:
        if unmatched_index not in matched_outputs:  # Ensure no duplicate dummies for matched outputs
            results.append({
                "input_id": None,  # Dummy input
                "output_id": output_ids[unmatched_index],
                "similarity": 0.0,
                "marker": "unmatched"
            })

    return results




train_set, eval_set = arckit.load_data()
task = train_set[4]
task.show()
db_manager = create_knowledge_graph(task)

# Get shared properties for a specific example_id
shared_properties = db_manager.get_shared_properties(example_id=1, batch_size=5)

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