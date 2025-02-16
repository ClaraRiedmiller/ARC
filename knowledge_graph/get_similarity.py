
import numpy as np
from scipy.optimize import linear_sum_assignment
import arckit
from typing import List, Dict


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

def one_to_many_matches_overall_top5(shared_properties, top_n=5, similarity_threshold=0.1):
    all_matches = []

    # Collect all valid matches
    for match in shared_properties:
        if match['normalized_similarity'] >= similarity_threshold:
            all_matches.append({
                "input_id": match['input_id'],
                "output_id": match['output_id'],
                "similarity": match['normalized_similarity']
            })

    # Sort all matches in descending order based on similarity
    all_matches.sort(key=lambda x: x['similarity'], reverse=True)

    # Keep only the top N matches
    top_matches = all_matches[:top_n]  # **Ensuring only the top 5 matches are kept**

    # Convert to dictionary format with limited pairs
    top_n_matches_dict = {}
    for match in top_matches:
        input_id = match["input_id"]
        if input_id not in top_n_matches_dict:
            top_n_matches_dict[input_id] = []
        top_n_matches_dict[input_id].append({
            "output_id": match["output_id"],
            "similarity": match["similarity"]
        })

    return top_n_matches_dict  # **Now this dictionary contains at most 5 total pairs**

def get_unshared_properties_for_matched_pairs(
    shared_properties,
    matched_pairs,
    considered_properties=None
):


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



def get_top_n_pairs_exact(shared_properties, n=5, similarity_threshold=0.1):
    """
    Returns a *list* of exactly the top-n highest-similarity rows 
    from `shared_properties`, each row containing at least:
      {
        "input_id": <int>, 
        "output_id": <int>, 
        "normalized_similarity": <float>,
        ...
      }
    filtered by similarity >= `similarity_threshold`.
    """
    # Filter out any matches below threshold
    valid_matches = [
        sp for sp in shared_properties
        if sp["normalized_similarity"] >= similarity_threshold
    ]
    # Sort by descending similarity
    valid_matches.sort(key=lambda x: x["normalized_similarity"], reverse=True)
    # Return top N
    return valid_matches[:n]


def get_top_n_pairs_unique_output(shared_properties: List[Dict], n: int = 5, similarity_threshold: float = 0.1) -> List[Dict]:
    # Step 1: Filter out matches below the similarity threshold
    valid_matches = [
        sp for sp in shared_properties
        if sp.get("normalized_similarity", 0) >= similarity_threshold
    ]
    
    # Step 2: Sort the valid matches in descending order of similarity
    valid_matches.sort(key=lambda x: x["normalized_similarity"], reverse=True)
    
    # Step 3: Select top-n matches with unique output_ids
    top_matches = []
    seen_output_ids = set()
    
    for match in valid_matches:
        output_id = match.get("output_id")
        
        # Skip if this output_id has already been included
        if output_id in seen_output_ids:
            continue
        
        # Add the match to top_matches and mark the output_id as seen
        top_matches.append(match)
        seen_output_ids.add(output_id)
        
        # Stop if we've collected n matches
        if len(top_matches) == n:
            break
    
    return top_matches

def get_most_similar_to_test(db_manager): 
    i = 1 
    all_similarity = []
    while i < 4: 
        per_example = db_manager.shared_properties_across_input(i, 9)
        all_similarity.extend(per_example)
        i = i+1  
    all_similarity.sort(key=lambda x: x["normalized_similarity"], reverse=True)
    return all_similarity[:5]
        
