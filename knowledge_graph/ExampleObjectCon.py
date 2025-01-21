import numpy as np
from scipy.ndimage import label, binary_fill_holes
from scipy.ndimage import binary_dilation

import arckit
import arckit.vis as vis
from create_Obj import *
from create_obj_Rel import get_object_adjacency_scipy
from arckit_handler import drawProblem

train_set, eval_set = arckit.load_data() # Load ARC1 train/eval

if __name__ == "__main__":
    # Example array with multiple "colors" (values)
    task = train_set[100]
    drawProblem(task, "ForGraphTest")

    for j in range(len(task.train[0])):     
        for i in range(2):                  
            example_grid = task.train[j][i]
            if i == 0:
                print("New Task:\n ------Input------:\n")
            else:
                print("------Output------:\n")
            
            labeled_array = label_by_color(example_grid, mode="direct")
            print("Labeled Object-Grid:\n", labeled_array)
            
            print("\n List of Objects: \n", [int(labeled_object) for labeled_object in get_unique_labels(labeled_array)])
            
            object_shapes = extract_object_shapes(labeled_array)
            converted_shapes_dict = {
                int(k): v.astype(int).tolist() 
                for k, v in object_shapes.items()
            }
            print("Shape dictionary:\n ",converted_shapes_dict)                
            
            # Convert dictionary keys and values
            coordinate_dict = label_coordinates_dict(labeled_array, exclude_zero=True)
            converted_coordinate_dict = {int(key): [(int(x), int(y)) for x, y in value] for key, value in coordinate_dict.items()}
            print("\n Coordinate Dict:", converted_coordinate_dict)
                
            # Direct adjacency dictionary
            adj_direct = get_object_adjacency_scipy(labeled_array, mode="direct")
            converted_adj_direct = {int(key): [int(n) for n in neighbors] for key, neighbors in adj_direct.items()}
            print("\n Direct adjacent objects: \n", converted_adj_direct)
                    
            # Diagonal adjacency dictionary
            adj_diagonal = get_object_adjacency_scipy(labeled_array, mode="diagonal")
            converted_adj_diagonal = {int(key): [int(n) for n in neighbors] for key, neighbors in adj_diagonal.items()}
            print("\n Diagonally adjacent objects: \n", converted_adj_diagonal)

