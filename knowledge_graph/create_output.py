from knowledge_graph.create_kg import create_knowledge_graph, visualize_knowledge_graph
from knowledge_graph.kuzu_db_manager import *
from knowledge_graph.get_similarity import *
import arckit

import os
import json



def create_isolated_object(grid_size, prop_dict):
    """
    Creates an empty grid (zeros) and places a single object in it
    based on the bounding box and shape properties in `prop_dict`.
    """
    grid = np.zeros(grid_size, dtype=int)

    color = prop_dict["color"]
    bbox_x = prop_dict["bbox_x"]
    bbox_y = prop_dict["bbox_y"]
    
    shape_data = prop_dict["shape"]
    
    # Ensure shape_data is a list before converting it to a NumPy array
    if isinstance(shape_data, str):
        shape_2d = np.array(json.loads(shape_data))  # If it's a JSON string, load it
    else:
        shape_2d = np.array(shape_data)  # Otherwise, assume it's already a list

    for row in range(shape_2d.shape[0]):
        for col in range(shape_2d.shape[1]):
            if shape_2d[row, col] == 1:
                grid[bbox_x + row, bbox_y + col] = color

    return grid


def create_input_output_grid_pairs(input_grid_size, output_grid_size, pairs_info, max_pairs=5):
    results = []
    
    # print(f"Processing {len(pairs_info)} pairs (before limiting to {max_pairs})")

    for idx, info in enumerate(pairs_info):
        if idx >= max_pairs:
            break  # Stop after processing the top 5 pairs
        
        input_obj_props = info["input_properties"]
        output_obj_props = info["output_properties"]
        
        # Create isolated grids
        input_grid = create_isolated_object(input_grid_size, input_obj_props)
        output_grid = create_isolated_object(output_grid_size, output_obj_props)
        
        results.append((input_grid, output_grid))
    
    return results


def create_isolated_object_grid(grid_size, prop_dict):
    # 1) Initialize an empty (zeroed) grid.
    grid = np.zeros(grid_size, dtype=int)
    
    # 2) Extract object properties from the dictionary.
    color = prop_dict["color"]
    bbox_x = prop_dict["bbox_x"]
    bbox_y = prop_dict["bbox_y"]
    
    shape_str = prop_dict["shape"]
    shape_2d = np.array(json.loads(shape_str))
    
    # 4) Stamp the object's color into the grid wherever shape_2d == 1.
    for row in range(shape_2d.shape[0]):
        for col in range(shape_2d.shape[1]):
            if shape_2d[row, col] == 1:
                # Place the color in the corresponding position
                grid[bbox_x + row, bbox_y + col] = color
                
    return grid



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



def get_properties_for_exact_pairs(db_manager, top_pairs):
    """
    top_pairs is a list of dicts, e.g.:
      [
        {"input_id": 101, "output_id": 201, "normalized_similarity": 0.87, ...},
        ...
      ]
    Returns a list of dicts with 'input_properties' and 'output_properties'.
    Exactly one row per pair (no duplicates).
    """
    if not top_pairs:
        return []

    # Build the WHERE clause with OR conditions
    # e.g. (i.id=101 AND o.id=201) OR (i.id=102 AND o.id=210) ...
    conditions = []
    for pair in top_pairs:
        in_id = pair["input_id"]
        out_id = pair["output_id"]
        conditions.append(f"(i.id = {in_id} AND o.id = {out_id})")

    # Combine them
    where_clause = " OR ".join(conditions)

    query = f"""
    MATCH (i:input_object), (o:output_object)
    WHERE {where_clause}
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

    results = []
    try:
        res = db_manager.conn.execute(query)
        while res.has_next():
            row = res.get_next()

            # Row could be a list/tuple or dict, depending on Kùzu configuration
            if isinstance(row, (list, tuple)):
                (input_id, output_id,
                 input_color, output_color,
                 input_bbox_x, output_bbox_x,
                 input_bbox_y, output_bbox_y,
                 input_shape, output_shape) = row
            elif isinstance(row, dict):
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
                raise ValueError("Unexpected row type from db query.")

            # Store the properties in the exact format needed by create_input_output_grid_pairs
            results.append({
                "input_id": input_id,  # Added top-level input_id
                "output_id": output_id,  # Added top-level output_id
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
    except Exception as e:
        print(f"Error during query execution: {e}")

    return results

