from knowledge_graph.create_kg import create_knowledge_graph, visualize_knowledge_graph


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