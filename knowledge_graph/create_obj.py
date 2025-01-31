from knowledge_graph.utils import StructuringElementMode

import numpy as np
from scipy.ndimage import label, binary_fill_holes
from scipy.ndimage import binary_dilation

def label_components(grid, example_id, mode="direct"):          # formerly called label_by_color
     # Convert mode to StructuringElementMode enum
    try:
        mode_enum = StructuringElementMode(mode)
    except ValueError:
        raise ValueError(f"Unknown mode='{mode}'. Must be 'direct', 'diagonal', or '8-way'.")

    structure = mode_enum.get_structuring_element()
    
    # Find all unique colors 
    unique_colors = np.unique(grid)
    
    # Initialize output
    out = np.zeros_like(grid, dtype=int)
    
    for color_value in unique_colors:
        # Create a binary mask for this particular color
        if color_value == 0:
            continue
        
        mask = (grid == color_value)
        
        # Label the connected components *within* this mask
        # labeled_mask will have values in [0, 1, 2, ..., n_components]
        labeled_mask, n_components = label(mask, structure=structure)
        # 0 means "not in the mask" or background, 1...n_components are distinct objects.
        
        # Assign final labels:example_id * 10_000 color_value * 1000 + component_id; upper bound is 900 (30x30) objects in a grid
        for comp_id in range(1, n_components + 1):
            out[labeled_mask == comp_id] = + (10_000 * example_id) + (color_value * 1000) + comp_id

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

def get_quadrant(labeled_array): #Or other orientation to maybe use in group building process
    pass

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

# Functions to find features on objects shapes:

def max_height_and_width(object_shape): 
    #Basically unnecessary as function but we might want it as a feature for objects
    return object_shape.shape

def number_of_elements(object_shape): 
    #Basically unnecessary as function but we might want it as a feature for objects
    return np.count_nonzero(object_shape)

def find_centroid(object_shape): # Finds the "center of mass"
    coords = np.argwhere(object_shape == 1)
    if coords.size == 0:
        return (None, None)
    
    r_mean = coords[:, 0].mean()
    c_mean = coords[:, 1].mean()

    return (r_mean, c_mean)

def find_holes(object_shape):
    #We use flood-first algo to find holes
    pass