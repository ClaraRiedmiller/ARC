from knowledge_graph.create_kg import create_knowledge_graph, visualize_knowledge_graph
from knowledge_graph.kuzu_db_manager import *
from knowledge_graph.get_similarity import *
import arckit

import os
import json



def create_isolated_object(grid_size, prop_dict):
    # Create an empty (zeroed) grid
    grid = np.zeros(grid_size, dtype=int)

    color = prop_dict["color"]
    bbox_x = prop_dict["bbox_x"]
    bbox_y = prop_dict["bbox_y"]
    
    # Convert shape from JSON string to a 2D NumPy array
    shape_str = prop_dict["shape"]
    shape_2d = np.array(json.loads(shape_str))
    
    # "Stamp" the color into the grid wherever shape_2d == 1
    for row in range(shape_2d.shape[0]):
        for col in range(shape_2d.shape[1]):
            if shape_2d[row, col] == 1:
                grid[bbox_x + row, bbox_y + col] = color
    
    return grid

def create_input_output_grid_pairs(input_grid_size, output_grid_size, pairs_info):
    results = []
    for info in pairs_info:
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


def get_top_n_matches(possibly_matches, n=5):
    all_matches = []

    # Flatten the dictionary into a list of tuples
    for input_id, match_list in possibly_matches.items():
        for match_info in match_list:
            all_matches.append(
                (input_id, match_info['output_id'], match_info['similarity'])
            )

    # Sort by similarity in descending order
    all_matches.sort(key=lambda x: x[2], reverse=True)

    # Return the top N matches
    return all_matches[:n]
