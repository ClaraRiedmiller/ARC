from knowledge_graph.create_kg import create_knowledge_graph, visualize_knowledge_graph

import numpy as np
from scipy.optimize import linear_sum_assignment
import arckit


def get_highest_similarity_pairs(shared_properties):
    best_pairs = {}

    for match in shared_properties:
        input_id = match['input_id']
        # If we don't have an entry yet, or this match is better than the stored one, update it
        if (input_id not in best_pairs 
                or match['normalized_similarity'] > best_pairs[input_id]['normalized_similarity']):
            best_pairs[input_id] = match

    return best_pairs


def create_similarity_matrix(shared_properties):
    # Get sorted unique IDs
    input_ids = sorted({match['input_id'] for match in shared_properties})
    output_ids = sorted({match['output_id'] for match in shared_properties})
    
    # Create index mappings
    input_index = {id_: idx for idx, id_ in enumerate(input_ids)}
    output_index = {id_: idx for idx, id_ in enumerate(output_ids)}

    # Initialize the matrix
    similarity_matrix = np.zeros((len(input_ids), len(output_ids)))

    # Fill in the matrix with similarity scores
    for match in shared_properties:
        row = input_index[match['input_id']]
        col = output_index[match['output_id']]
        similarity_matrix[row, col] = match['normalized_similarity']

    return similarity_matrix, input_ids, output_ids


def optimal_one_to_one_assignment_with_valid_dummies(shared_properties, similarity_threshold=0.2):
    # Create the similarity matrix
    similarity_matrix, input_ids, output_ids = create_similarity_matrix(shared_properties)

    # Determine the size for padding (larger of #inputs vs. #outputs)
    max_size = max(len(input_ids), len(output_ids))

    # Pad with zeros (meaning no similarity for those dummy pairs)
    padded_matrix = np.zeros((max_size, max_size))
    padded_matrix[:len(input_ids), :len(output_ids)] = similarity_matrix

    # Convert to negative to apply Hungarian Algorithm which minimizes
    cost_matrix = -padded_matrix
    row_indices, col_indices = linear_sum_assignment(cost_matrix)

    # Track matched outputs and unmatched outputs
    matched_outputs = set()
    unmatched_outputs = set(range(len(output_ids)))  # all outputs initially unmatched

    results = []

    for i, j in zip(row_indices, col_indices):
        if i < len(input_ids) and j < len(output_ids):
            # A real input-output match (not padding)
            similarity = similarity_matrix[i, j]
            if similarity >= similarity_threshold:
                results.append({
                    "input_id": input_ids[i],
                    "output_id": output_ids[j],
                    "similarity": similarity,
                    "marker": "matched"
                })
                matched_outputs.add(j)
                unmatched_outputs.discard(j)
            else:
                # Below threshold => treat as unmatched
                unmatched_outputs.add(j)
        elif j < len(output_ids):
            # This was a dummy input (i >= len(input_ids)) assigned to a real output
            unmatched_outputs.add(j)

    # Assign "dummy" inputs to any remaining unmatched outputs
    for unmatched_index in unmatched_outputs:
        if unmatched_index not in matched_outputs:
            results.append({
                "input_id": None,  # Dummy
                "output_id": output_ids[unmatched_index],
                "similarity": 0.0,
                "marker": "unmatched"
            })

    return results


def one_to_many_matches_dict(shared_properties, similarity_threshold=0.1):
    matches_by_input = {}

    # Filter & group
    for match in shared_properties:
        if match['normalized_similarity'] >= similarity_threshold:
            input_id = match['input_id']
            # Initialize list if this is the first time we see input_id
            if input_id not in matches_by_input:
                matches_by_input[input_id] = []
            matches_by_input[input_id].append({
                "output_id": match['output_id'],
                "similarity": match['normalized_similarity']
            })

    # Sort each input's matches in descending order by similarity
    for in_id in matches_by_input:
        matches_by_input[in_id].sort(key=lambda x: x['similarity'], reverse=True)

    return matches_by_input

def get_unshared_properties_for_matched_pairs(
    shared_properties,
    matched_pairs,
    considered_properties=None
):
    """
    Returns a list of dicts describing which properties are unshared 
    for each *matched* pair in `matched_pairs`.

    :param shared_properties: The full list from `db_manager.get_shared_properties(...)`, 
        each dict having at least:
        {
          "input_id": <int>,
          "output_id": <int>,
          "matching_properties": <list of strings> ...,
        }
    :param matched_pairs: A list of dicts with keys:
        {
          "input_id": <int or None>,
          "output_id": <int>,
          "similarity": <float>,
          "marker": "matched" or "unmatched"
        }
      Typically from `optimal_one_to_one_assignment_with_valid_dummies`.
    :param considered_properties: The full set of properties to check 
        (e.g. ["color", "bbox_x", "bbox_y", "bbox_width", "bbox_height", "shape"]).
        If None, defaults to the usual 6 property names used in matching.
    
    :return: A list of dicts, one per matched pair, e.g.:
        [
          {
            "input_id": <int>,
            "output_id": <int>,
            "unshared_properties": [...],
          },
          ...
        ]
    """

    # 1) Define default properties if not provided
    if considered_properties is None:
        considered_properties = [
            "color", "bbox_x", "bbox_y", 
            "bbox_width", "bbox_height", "shape"
        ]

    # 2) Build a quick lookup from (input_id, output_id) -> matching_properties
    #    by iterating the raw shared_properties
    row_map = {}
    for row in shared_properties:
        in_id = row["input_id"]
        out_id = row["output_id"]
        # storing the list of matching props
        row_map[(in_id, out_id)] = row.get("matching_properties", [])

    # 3) For each matched pair, find the row in row_map, compute unshared
    results = []
    for pair in matched_pairs:
        if pair["marker"] == "matched" and pair["input_id"] is not None:
            in_id = pair["input_id"]
            out_id = pair["output_id"]
            # If we have a row for (in_id, out_id), get its matching props
            if (in_id, out_id) in row_map:
                matched_props = row_map[(in_id, out_id)]
            else:
                # If somehow the pair doesn't exist in shared_properties, treat as no match
                matched_props = []

            # unshared = everything in considered_properties that is NOT matched
            unshared = sorted(set(considered_properties) - set(matched_props))

            results.append({
                "input_id": in_id,
                "output_id": out_id,
                "unshared_properties": unshared
            })

    return results


def return_objects_query(db_manager, input_id, output_id):
    """
    Takes an input_id and output_id for objects and queries the Kùzu database
    for matching nodes with those IDs, returning all node attributes in
    a list of dicts.
    """
    query = """
    MATCH (n)
    WHERE n.id = $node1_id OR n.id = $node2_id
    RETURN n
    """
    parameters = {
        "node1_id": input_id,
        "node2_id": output_id
    }
    result = db_manager.conn.execute(query, parameters=parameters)

    objects = []
    while result.has_next():
        row = result.get_next()
        # row is typically a list (or tuple) with one element: the node data.
        node_data = row[0]
        
        # If node_data is already a dict, just append it directly:
        # e.g. node_data might look like {"id": 12001, "color": 5, "shape": ...}
        objects.append(node_data)

    return objects

def get_properties_for_matched_pairs(self, optimal_pairs, batch_size=100):
    # Extract matched pairs
    matched_pairs = [
        (pair['input_id'], pair['output_id'])
        for pair in optimal_pairs
        if pair['marker'] == 'matched'
    ]
    
    # Handle cases where there are no matched pairs
    if not matched_pairs:
        print("No matched pairs found.")
        return []

    # Create a condition string for the matched pairs
    matched_condition = " OR ".join(
        f"(i.id = {input_id} AND o.id = {output_id})"
        for input_id, output_id in matched_pairs if input_id is not None
    )

    # Base query for matched pairs
    query = f"""
    MATCH (i:input_object), (o:output_object)
    WHERE {matched_condition}
    RETURN 
        i.id AS input_id, 
        o.id AS output_id,
        i.color AS input_color,
        o.color AS output_color,
        i.bbox_x AS input_bbox_x,
        o.bbox_x AS output_bbox_x,
        i.bbox_y AS input_bbox_y,
        o.bbox_y AS output_bbox_y,
        i.shape AS input_shape,
        o.shape AS output_shape
    """

    # Result storage
    matches = []
    try:
        # Execute the query
        result = self.conn.execute(query)
        batch = []
        while result.has_next():
            row = result.get_next()

            # Adjust based on `row` structure
            if isinstance(row, (list, tuple)):
                # Access values positionally
                input_id, output_id, input_color, output_color, input_bbox_x, output_bbox_x, \
                input_bbox_y, output_bbox_y, input_shape, output_shape = row
            elif isinstance(row, dict):
                # Access values using keys
                input_id = row["input_id"]
                output_id = row["output_id"]
                input_color = row["input_color"]
                output_color = row["output_color"]
                input_bbox_x = row["input_bbox_x"]
                output_bbox_x = row["output_bbox_x"]
                input_bbox_y = row["input_bbox_y"]
                output_bbox_y = row["output_bbox_y"]
                input_shape = row["input_shape"]
                output_shape = row["output_shape"]
            else:
                raise ValueError("Unexpected row format returned from query.")

            # Add processed result to the batch
            batch.append({
                "input_id": input_id,
                "output_id": output_id,
                "input_properties": {
                    "color": input_color,
                    "bbox_x": input_bbox_x,
                    "bbox_y": input_bbox_y,
                    "shape": input_shape
                },
                "output_properties": {
                    "color": output_color,
                    "bbox_x": output_bbox_x,
                    "bbox_y": output_bbox_y,
                    "shape": output_shape
                }
            })

            # If batch size is reached, process and reset the batch
            if len(batch) >= batch_size:
                matches.extend(batch)
                batch = []

        # Add remaining rows
        matches.extend(batch)

    except Exception as e:
        print(f"Error during query execution: {e}")

    return matches

def task_not_solvable(db_manager):
    # if there are unmatched objects in the output (they appear and we can't track why)
    # if there are more than 5 matched objects 
    i = 3 
    unmatched_counter = 0
    many_objects_counter = 0
    while i > 0: 
    #obtain properties
        props =  get_shared_properties(db_manager, example_id=i, batch_size=100)
      #do matching on the properties 
        matchings = optimal_one_to_one_assignment_with_valid_dummies(props)
      #count how many outputs are unmatched 
        unmatched_count = sum(1 for item in matchings if item['marker'] == 'unmatched')
        matched_count = sum(1 for item in matchings if item['marker'] == 'matched')
        if unmatched_count > 0:
            unmatched_counter += 1 
        if matched_count > 5:
            many_objects_counter += 1
        i = i -1 
    if unmatched_counter > 1: 
        return "Task not solvable, non-trackable objects appear"
    elif many_objects_counter > 1:
        return "Task not solvable, too many objects"
    else: 
        continue 
    j = 3
    low_similarity_counter = 0 
    while i > 0: 
        #obtain properties
        props =  get_shared_properties(db_manager, example_id=i, batch_size=100)
      #do matching on the properties 
        matchings = optimal_one_to_one_assignment_with_valid_dummies(props)
        #check for how low the similarity indices are for the top 5 objects
        low_similarity_count = sum(1 for item in data if item['similarity'] < 0.2)
        #if all top 5 objects have a low similarity count
        if low_similarity_count >= 5:
            low_similarity_counter += 1
        else: 
            continue 
        j = j-1
    
        if low_similarity_counter > 1:    
            return "Task not solvable, output cannot be tracked from input"
        else: 
            return "We can attempt to solve this task!"
