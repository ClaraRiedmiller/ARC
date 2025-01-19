import numpy as np
from scipy.ndimage import label, binary_fill_holes
from scipy.ndimage import binary_dilation

import arckit
import arckit.vis as vis
train_set, eval_set = arckit.load_data() # Load ARC1 train/eval


def label_by_color(color, mode="direct"):
    # 4-connectivity structure (up, down, left, right)
    # Define structuring elements for each mode:
    # 1) direct (orthogonal neighbors only)
    direct_structure = np.array([[0, 1, 0],
                                [1, 1, 1],
                                [0, 1, 0]], dtype=bool)
    
    # 2) diagonal (the 4 corners only)
    diagonal_structure = np.array([[1, 0, 1],
                                [0, 0, 0],
                                [1, 0, 1]], dtype=bool)
    
    # 3) 8-way (all neighbors including diagonals)
    eight_structure = np.ones((3,3), dtype=bool)
    
    # Choose the desired structure
    if mode == "direct":
        structure = direct_structure
    elif mode == "diagonal":
        structure = diagonal_structure
    elif mode == "8-way":
        structure = eight_structure
    else:
        raise ValueError(f"Unknown mode='{mode}'. Must be 'direct', 'diagonal', or '8-way'.")
    
    # Find all unique colors (excluding 0 if your data has zeros that are "background")
    unique_vals = np.unique(color)
    
    # Initialize output
    out = np.zeros_like(color, dtype=int)
    
    for val in unique_vals:
        # Create a binary mask for this particular color
        if val == 0:
            continue
        
        mask = (color == val)
        
        # Label the connected components *within* this mask
        labeled_mask, n_comp = label(mask, structure=structure)
        # labeled_mask will have values in [0, 1, 2, ..., n_comp]
        # 0 means "not in the mask" or background, 1..n_comp are distinct objects.
        
        # Assign final labels: color * 100 + component_id
        for comp_id in range(1, n_comp + 1):
            out[labeled_mask == comp_id] = val * 100 + comp_id

    return out

def get_unique_labels(labeled_array, exclude_zero=True):

    unique_vals = np.unique(labeled_array)
    if exclude_zero:
        unique_vals = unique_vals[unique_vals != 0]
    return unique_vals

def label_coordinates_dict(labeled_array, exclude_zero=True):
    unique_labels = np.unique(labeled_array)
    
    if exclude_zero:
        unique_labels = unique_labels[unique_labels != 0]
    
    # Build the dictionary
    label_coords = {}
    for lbl in unique_labels:
        # Rows and cols where labeled_array == lbl
        rows, cols = np.where(labeled_array == lbl)
        # Combine them into (row, col) tuples
        coords = list(zip(rows, cols))
        label_coords[lbl] = coords
    
    return label_coords


def extract_object_shapes(grid):

    # Get unique labels excluding 0 (background)
    unique_labels = np.unique(grid)
    unique_labels = unique_labels[unique_labels != 0]
    
    object_shapes = {}
    
    for label in unique_labels:
        # Find the coordinates of the object
        coords = np.argwhere(grid == label)
        if coords.size == 0:
            continue
        
        # Get the bounding box of the object
        min_row, min_col = coords.min(axis=0)
        max_row, max_col = coords.max(axis=0)
        
        # Extract the submatrix for the object
        submatrix = grid[min_row:max_row + 1, min_col:max_col + 1]
        
        # Create a binary representation of the object's shape
        binary_shape = (submatrix == label).astype(int)
        
        # Store the binary shape in the dictionary
        object_shapes[label] = binary_shape
    
    return object_shapes
