from objects import *



def get_object_adjacency_scipy(labeled_array, mode="direct"):
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
    
    adjacency = {}
    
    # Gather non-zero labels (ignore background=0)
    unique_labels = np.unique(labeled_array)
    unique_labels = unique_labels[unique_labels != 0]
    
    for lbl in unique_labels:
        # 1) Binary mask for this label
        mask = (labeled_array == lbl)
        
        # 2) Dilate mask using the chosen structuring element
        dilated = binary_dilation(mask, structure=structure)
        
        # 3) Check which labels appear in the dilated region
        neighbor_labels = np.unique(labeled_array[dilated])
        
        # 4) Exclude background and the label itself
        neighbor_labels = neighbor_labels[
            (neighbor_labels != 0) & (neighbor_labels != lbl)
        ]
        
        adjacency[lbl] = set(neighbor_labels)
    
    return adjacency
