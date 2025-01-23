from create_Obj import *

#Grid related relations:

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

###### Functions between objects (independent of the grid): #######


def same_color(object1, object2):
    # Maybe it would be smarter to extract that information earlier
    color1 = object1_label // 100
    color2 = object2_label // 100
    return color1 == color2



# We define functions to compare the objects through their shapes:

def is_same_shape(arr1, arr2):

    if arr1 is None or arr1.size == 0:
        return arr2 is None or arr2.size == 0
    if arr2 is None or arr2.size == 0:
        return arr1 is None or arr1.size == 0

    return (arr1.shape == arr2.shape) and np.array_equal(arr1, arr2)

def size_mod_is_zero(shape1, shape2):
    # Sum over all elements of the shape matrix; check for |shape1| mod |shape2| == 0
    size1 = np.count_nonzero(shape1)
    size2 = np.count_nonzero(shape2)
    
    if size2 == 0:
    # Nothing state is never related in size
        return False
    
    return (size1 % size2) == 0


def is_scaled_quadratic(shape1, shape2): 
    r1, c1 = shape1.shape
    r2, c2 = shape2.shape
    
    # Check dimension scaling
    if r2 != 2 * r1 or c2 != 2 * c1:
        return False
    
    # Check each cell
    for i in range(r1):
        for j in range(c1):
            block = shape2[2*i : 2*i+2, 2*j : 2*j+2]
            if shape1[i, j] == 1:
                # Block should be all 1s
                if not np.all(block == 1):
                    return False
            else:
                # Block should be all 0s
                if not np.all(block == 0):
                    return False
    
    return True

def is_scaled_quadratic_inverse(shape2, shape1): #reuse is_scaled with switched arguments
    r1, c1 = shape1.shape
    r2, c2 = shape2.shape
    
    # Check dimension scaling
    if r2 != 2 * r1 or c2 != 2 * c1:
        return False
    
    # Check each cell
    for i in range(r1):
        for j in range(c1):
            block = shape2[2*i : 2*i+2, 2*j : 2*j+2]
            if shape1[i, j] == 1:
                # Block should be all 1s
                if not np.all(block == 1):
                    return False
            else:
                # Block should be all 0s
                if not np.all(block == 0):
                    return False
    
    return True

def is_rotation(shape1, shape2):
    # 0° rotation (Identity excluded; excludes also squares)
    if shape1.shape == shape2.shape and np.array_equal(shape1, shape2):
        return False
    
    # Check 90°, 180°, 270° using np.rot90
    for k in [1, 2, 3]:
        rotated = np.rot90(shape1, k)
        if rotated.shape == shape2.shape and np.array_equal(rotated, shape2):
            return True
    
    return False

def is_flip(shape1, shape2):
        # Horizontal flip (left-right)
    if shape1.shape == shape2.shape and np.array_equal(shape1, shape2):
        return False

    if np.array_equal(np.fliplr(shape1), shape2):
        return True
    
    # Vertical flip (up-down)
    if np.array_equal(np.flipud(shape1), shape2):
        return True
    
    # Flip across the main diagonal (transpose)
    if np.array_equal(shape1.T, shape2):
        return True
    
    # Flip across the secondary diagonal: rotate 180, then transpose
    # or equivalently flip shape1 along both axes
    if np.array_equal(np.flipud(np.fliplr(shape1)), shape2.T):
        return True
    
    return False


# Create Relations between objects on different grids:

