from knowledge_graph.create_kg import create_knowledge_graph, visualize_knowledge_graph

import numpy as np
from scipy.optimize import linear_sum_assignment
import arckit

def get_highest_similarity_pairs(shared_properties):
    """
    Finds the input-output object pair with the highest similarity for each input object.

    Parameters:
        shared_properties (list[dict]): A list of dictionaries containing input-output pairs 
                                         and their similarity scores.

    Returns:
        dict: A dictionary where the keys are `input_id` and the values are the 
              corresponding dictionary for the best matching `output_id`.
    """
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
    """
    Creates a similarity matrix from a list of shared properties dictionaries.

    Parameters:
        shared_properties (list[dict]): A list of dictionaries containing input_id, output_id, 
                                         and their similarity scores.

    Returns:
        tuple: (similarity_matrix, input_ids, output_ids)
               - similarity_matrix (2D np.array): A 2D numpy array representing the similarity matrix.
               - input_ids (list): List of unique input object IDs (row labels).
               - output_ids (list): List of unique output object IDs (column labels).
    """
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


def optimal_one_to_one_assignment_with_dummy(shared_properties):
    """
    Finds the optimal one-to-one assignment of input-output pairs that maximizes the overall similarity,
    while handling unmatched outputs by assigning them a most likely origin.

    Parameters:
        shared_properties (list[dict]): A list of dictionaries containing input-output pairs and their similarity scores.

    Returns:
        list[dict]: A list of dictionaries containing the optimal assignments, including dummy assignments
                    for unmatched outputs.
    """
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

    # Extract the optimal pairs while ignoring dummy matches (padded rows/columns)
    optimal_pairs = []
    unmatched_outputs = set(range(len(output_ids)))  # Track unmatched output indices

    for i, j in zip(row_indices, col_indices):
        if i < len(input_ids) and j < len(output_ids):  # Exclude dummy rows/columns
            optimal_pairs.append({
                "input_id": input_ids[i],
                "output_id": output_ids[j],
                "similarity": similarity_matrix[i, j],
                "marker": "matched"
            })
            unmatched_outputs.discard(j)  # Remove matched output from the unmatched set

    # Handle unmatched outputs by assigning them to a most likely origin
    for unmatched_index in unmatched_outputs:
        # Find the most likely origin (highest similarity from any input)
        similarities_for_output = similarity_matrix[:, unmatched_index]
        most_likely_input_index = np.argmax(similarities_for_output)
        most_likely_input_id = input_ids[most_likely_input_index] if similarities_for_output[most_likely_input_index] > 0 else None

        optimal_pairs.append({
            "input_id": most_likely_input_id,
            "output_id": output_ids[unmatched_index],
            "similarity": similarities_for_output[most_likely_input_index],
            "marker": "unmatched"
        })

    return optimal_pairs



train_set, eval_set = arckit.load_data()
task = train_set[0]
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


optimal_pairs = optimal_one_to_one_assignment_with_dummy(shared_properties)

# Print the results
for pair in optimal_pairs:
    print(pair)