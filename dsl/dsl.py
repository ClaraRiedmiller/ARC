# Definition of a set of types
from typing import TypeAlias, Tuple, Set

#for base function
from collections import Counter

#basic types
coordinate: TypeAlias = int     #x or y value
color: TypeAlias = int          #color value
boolean: TypeAlias = bool       #boolean values 

#complex types
Pixel: TypeAlias = Tuple[coordinate, coordinate, color]
Object: TypeAlias = Set[Pixel]  # Note that any grid is hence an object
ObjectGrid: TypeAlias = Tuple[Object,Tuple[int,int]] #this type can store gridsize infromattion as width x height 

#Core functions: these functions are not part of the DSL but enable us to detect elements of a structure:
def neighborhood(object: Object, gridesize: int) -> object:     #We want to determine the neighbourhood pixels of a pixel. 
    neighbor = [(-1, 0), (0, -1), (1, 0), (0, 1)]
    outcome = set()
    for pixel in object:
        for change in neighbor:
            if pixel[0] + change[0] >= 0 and pixel[0] + change[0] <= gridesize and pixel[1] + change[1] >= 0 and pixel[1] + change[1] <= gridesize:
                outcome.add((pixel[0] + change[0], pixel[1] + change[1], pixel[2]))
    return outcome

def neighborhood_with_diagonals(object: Object, gridesize: int) -> object:     #We want to determine the neighbourhood pixels of a pixel. 
    neighbor = [(-1, 0), (0, -1), (1, 0), (0, 1), (1,1), (1, -1), (-1,1), (-1,-1)]
    outcome = set()
    for pixel in object:
        for change in neighbor:
            if pixel[0] + change[0] >= 0 and pixel[0] + change[0] <= gridesize and pixel[1] + change[1] >= 0 and pixel[1] + change[1] <= gridesize:
                outcome.add((pixel[0] + change[0], pixel[1] + change[1], pixel[2]))
    return outcome

def only_diagonal_neighborhood(object: Object, gridesize: int) -> object:     #We want to determine the neighbourhood pixels of a pixel. 
    neighbor = [(1,1), (1, -1), (-1,1), (-1,-1)]
    outcome = set()
    for pixel in object:
        for change in neighbor:
            if pixel[0] + change[0] >= 0 and pixel[0] + change[0] <= gridesize and pixel[1] + change[1] >= 0 and pixel[1] + change[1] <= gridesize:
                outcome.add((pixel[0] + change[0], pixel[1] + change[1], pixel[2]))
    return outcome

def pixel_out(object: Object, gridsize: int) -> Object:             # Given an object, we want to the pixels on the outside
    outcome = set()
    for pixel_1 in object:
        neighborhood_pixel_1 = neighborhood(pixel_1, gridsize)
        for pixel_2 in object:
            pixel_2_check = (pixel_2[0],pixel_2[1], pixel_1[2])     # We want to check whether an object is in the 
            if  pixel_2_check in neighborhood_pixel_1:
                neighborhood_pixel_1.remove(pixel_2_check)          
            if len( neighborhood_pixel_1) == 0:                     # This provides a stop if the  neighborhood_pixel_1 is already empty
                break
        if len(neighborhood_pixel_1) != 0:                          # If there is still some neighborhoods which are not covered, we know that the object has empty-space next to it
            outcome.add(pixel_1)
    return outcome

def pixel_in(object: Object, gridsize: int) -> Object:             # Given an object, we want to the pixels in the inside
    result = object
    outcome = set()
    for pixel_1 in object:
        neighborhood_pixel_1 = neighborhood(pixel_1, gridsize)
        for pixel_2 in object:
            pixel_2_check = (pixel_2[0],pixel_2[1], pixel_1[2])     # We want to check whether an object is in the  neighborhood of pixel_1
            if  pixel_2_check in neighborhood_pixel_1:
                neighborhood_pixel_1.remove(pixel_2_check)          
            if len( neighborhood_pixel_1) == 0:                     # This provides a stop if the  neighborhood_pixel_1 is already empty
                break
        if len(neighborhood_pixel_1) == 0:                          # If every neighborhood is covered, we know that the object has no empty-space next to it
            outcome.add(pixel_1)
    for pixel in outcome:
        result.remove(pixel)
    return result

def holes(object: Object, gridsize: int) -> Object:  # outputs a set containing pixel-holes of an object
    outcome = set()
    object_xy = set((x,y) for x,y,c in object)
    for x in range(gridsize):
        for y in range(gridsize):
            if (x,y) in object_xy:
                continue 
            left = (x - 1, y) in object_xy
            right = (x + 1, y) in object_xy
            above = (x, y + 1) in object_xy
            below = (x, y - 1) in object_xy

            if left and right and above and below:
                holes.add((x,y))
    return outcome 

def pixel_out_with_uncovered_neighbors(object: Object, gridsize: int) -> (Object, Object):
    outside_pixels = set()
    uncovered_neighbors = set()

    for pixel_1 in object:
        neighborhood_pixel_1 = neighborhood(pixel_1, gridsize)
        local_uncovered = set(neighborhood_pixel_1)  # Start with all neighbors.

        for pixel_2 in object:
            pixel_2_check = (pixel_2[0], pixel_2[1], pixel_1[2])  # Align dimensions for comparison.
            if pixel_2_check in local_uncovered:
                local_uncovered.remove(pixel_2_check)  # Remove covered neighbors.
            if len(local_uncovered) == 0:  # Stop early if no uncovered neighbors remain.
                break

        if len(local_uncovered) != 0:  # If there are uncovered neighbors:
            outside_pixels.add(pixel_1)  # Add to outside pixels.
            uncovered_neighbors.update(local_uncovered)  # Collect uncovered neighbors.

    return outside_pixels, uncovered_neighbors


def pixel_out_with_uncovered_neighbors_with_diagonal(object: Object, gridsize: int) -> (Object, Object):
    outside_pixels = set()
    uncovered_neighbors = set()

    for pixel_1 in object: 
        neighborhood_pixel_1 = neighborhood_with_diagonal(pixel_1, gridsize)
        local_uncovered = set(neighborhood_pixel_1)  # Start with all neighbors.

        for pixel_2 in object:
            pixel_2_check = (pixel_2[0], pixel_2[1], pixel_1[2])  # Align dimensions for comparison.
            if pixel_2_check in local_uncovered:
                local_uncovered.remove(pixel_2_check)  # Remove covered neighbors.
            if len(local_uncovered) == 0:  # Stop early if no uncovered neighbors remain.
                break

        if len(local_uncovered) != 0:  # If there are uncovered neighbors:
            outside_pixels.add(pixel_1)  # Add to outside pixels.
            uncovered_neighbors.update(local_uncovered)  # Collect uncovered neighbors.

    return outside_pixels, uncovered_neighbors

def pixel_out_with_uncovered_neighbors_only_diagonal_neighborhood(object: Object, gridsize: int) -> (Object, Object):
    outside_pixels = set()
    uncovered_neighbors = set()

    for pixel_1 in object:
        neighborhood_pixel_1 = only_diagonal_neighborhood(pixel_1, gridsize)
        local_uncovered = set(neighborhood_pixel_1)  # Start with all neighbors.

        for pixel_2 in object:
            pixel_2_check = (pixel_2[0], pixel_2[1], pixel_1[2])  # Align dimensions for comparison.
            if pixel_2_check in local_uncovered:
                local_uncovered.remove(pixel_2_check)  # Remove covered neighbors.
            if len(local_uncovered) == 0:  # Stop early if no uncovered neighbors remain.
                break

        if len(local_uncovered) != 0:  # If there are uncovered neighbors:
            outside_pixels.add(pixel_1)  # Add to outside pixels.
            uncovered_neighbors.update(local_uncovered)  # Collect uncovered neighbors.

    return outside_pixels, uncovered_neighbors

def x_max(object: Object) -> coordinate:
    x_max = object[0][0]            # Initialize with the x-coordinate of the first pixel
    for pixel in object:
        if pixel[0] > x_max:        # Compare the x-coordinate of each pixel
            x_max = pixel[0]
    return x_max

def x_min(object: Object) -> coordinate:
    x_min = object[0][0]            # Initialize with the x-coordinate of the first pixel
    for pixel in object:
        if pixel[0] < x_min:        # Compare the x-coordinate of each pixel
            x_min = pixel[0]
    return x_min   

def y_max(object: Object) -> coordinate:
    y_max = object[0][1]            # Initialize with the y-coordinate of the first pixel
    for pixel in object:
        if pixel[1] > y_max:        # Compare the y-coordinate of each pixel
            y_max = pixel[1]
    return y_max

def y_min(object: Object) -> coordinate:
    y_min = object[0][1]            # Initialize with the y-coordinate of the first pixel
    for pixel in object:
        if pixel[1] < y_min:        # Compare the y-coordinate of each pixel
            y_min = pixel[1]
    return y_min  

def color_max(object: Object) -> color:
    colorlist = [pixel[2] for pixel in object]  # Collect all colors
    colorcounts = Counter(colorlist)           # Count occurrences of each color
    max_count = 0
    max_color = None
    for farbe, count in colorcounts.items():
        if farbe != 1 and max_count < count:  # Exclude background and ensure color appears
            max_color = farbe
            max_count = count
    return max_color


def color_min(object: Object) -> color:
    colorlist = [pixel[2] for pixel in object]  # Collect all colors
    colorcounts = Counter(colorlist)            # Count occurrences of each color
    min_count = float('inf')
    min_color = None
    for farbe, count in colorcounts.items():
        if farbe != 1 and 0 < count < min_count:  # Exclude background and ensure color appears
            min_color = farbe
            min_count = count
    return min_color

def color_order(object: Object) -> list[color]: # Generalisation of min, max
    colorlist = [pixel[2] for pixel in object]  # Collect all colors
    colorcounts = Counter(colorlist)            # Count occurrences of each color
    
    sorted_colors = sorted([(farbe, count) for farbe, count in colorcounts.items() if farbe != 1], key=lambda x: x[1], reverse=True) #sorts color and cound by decending order
    
    return [farbe for farbe, count in sorted_colors] #return only color


# Movement DSL 
def rotate_vertical(object: Object, gridsize: int) -> Object: #we want to flip the y-value of the pixels
    outcome = set()
    for pixel in object:
        newpixel = (pixel[0], gridsize - pixel[1] + 1, pixel[2])
        outcome.add(newpixel) 
    return outcome

def rotate_horizontal(object: Object, gridsize: int) -> Object: #we want to flip the x-value of the pixels
    outcome = set()
    for pixel in object:
        newpixel = (gridsize - pixel[0] +1, pixel[1], pixel[2])
        outcome.add(newpixel) 
    return outcome

def move_right(object: Object, gridsize: int) -> Object: #we want tot move the object one pixel to the right 
    outcome = set()
    for pixel in object:
        if pixel[0] + 1 <= gridsize:  
            newpixel = (pixel[0] +1 , pixel[1], pixel[2])
            outcome.add(newpixel) 
    return outcome

def move_left(object: Object, gridsize: int) -> Object:  #we want tot move the object one pixel to the right 
    outcome = set()
    for pixel in object:
        if pixel[0] - 1 >= 0:  
            newpixel = (pixel[0]  - 1 , pixel[1], pixel[2])
            outcome.add(newpixel) 
    return outcome

def move_up(object: Object, gridsize: int) -> Object: #we want tot move the object one pixel up 
    outcome = set()
    for pixel in object:
        if pixel[1] + 1 <= gridsize:  
            newpixel = (pixel[0], pixel[1] + 1, pixel[2])
            outcome.add(newpixel) 
    return outcome

def move_down(object: Object, gridsize: int) -> Object:  #we want tot move the object one pixel down
    outcome = set()
    for pixel in object:
        if pixel[1] - 1 >= 1:  
            newpixel = (pixel[0], pixel[1] - 1, pixel[2])
            outcome.add(newpixel) 
    return outcome

def move_left_edge(object: Object, gridsize: int) -> Object:
    outcome = set()
    min_x_value = x_min(object)
    for pixel in object:
        newpixel = (pixel[0] - min_x_value + 1, pixel[1], pixel[2])
        outcome.add(newpixel)
    return outcome 

def move_right_edge(object: Object, gridsize: int) -> Object:
    outcome = set()
    max_x_value = x_max(object)
    for pixel in object:
        newpixel = (pixel[0] + (gridsize - max_x_value), pixel[1], pixel[2])
        outcome.add(newpixel)
    return outcome 

def move_down_edge(object: Object, gridsize: int) -> Object:
    outcome = set()
    min_y_value = y_min(object)
    for pixel in object:
        newpixel = (pixel[0], pixel[1] - min_y_value + 1, pixel[2])
        outcome.add(newpixel)
    return outcome 

def move_up_edge(object: Object, gridsize: int) -> Object:
    outcome = set()
    max_y_value = y_max(object)
    for pixel in object:
        newpixel = (pixel[0], pixel[1] + (gridsize - max_y_value), pixel[2])
        outcome.add(newpixel)
    return outcome 

### DSL Transform 
def isolate(object: Object, gridsize: int) -> ObjectGrid: 
    outcome= set()
    for pixel in object:
        newpixel = (pixel[0] - x_min(object) + 1, pixel[1] - y_min(object) + 1, pixel[2])
        outcome.add(newpixel)
    newgridsize = (x_max(object) - x_min(object),y_max(object)-y_min(object) )
    return (outcome, newgridsize)

def color_object_max(object: Object, gridesize: int) -> (Object):
    outcome = set()
    tobecolor = color_max(object)
    for pixel in object:
        outcome.add((pixel[0], pixel[1], tobecolor))
    return outcome

def color_object_min(object: Object, gridesize: int) -> (Object):
    outcome = set()
    tobecolor = color_min(object)
    for pixel in object:
        outcome.add((pixel[0], pixel[1], tobecolor))
    return outcome

def project_bigger(object: Object, gridsize: int) -> ObjectGrid: #assumes that same ratio for x and y coordinate
    outcome = set()
    grid_x_value = max_x(object) - min_x(object) + 1
    # grid_y_value = max_y(object) - min_y(object) + 1
    grid_ratio = gridsize / grid_x_value #we assume that gridsize value is bigger (because of project_bigger)
    if not grid_ratio.is_integer():
        return (object, gridsize)
    
    for pixel in object: # duplicates the pixel into multiple pixels according to the ratio
        for x_value in range(0,grid_ratio): 
            for y_value in range(0,grid_ratio):
                    outcome.add((pixel[0]*grid_ratio - x_value,pixel[1]*grid_ratio - y_value,pixel[3]))
    
    outcome_grid_size = (max_x(outcome) - min_x(outcome) +1, max_y(outcome) - min_y(outcome) + 1) #calculates new gridsize
    return (outcome, outcome_grid_size)

def project_smaller(object: Object, gridsize: int) -> ObjectGrid: #assumes that same ratio for x and y coordinate
    outcome = set()
    grid_x_value = max_x(object) - min_x(object) + 1
    # grid_y_value = max_y(object) - min_y(object) + 1
    grid_ratio =  grid_x_value / gridsize
    if not grid_ratio.is_integer():
        return (object, gridsize)
    
    for value_1 in range(1,grid_ratio +1): #to shrink x-value
        for value_2 in range(1, grid_ratio +1): # to shirk y-value
            subgrid = set()
            for pixel in object:
                if pixel[0] / grid_ratio < value_1 and pixel[1] / grid_ratio < value_2:
                    subgrid.add(pixel)
            if color_max(subgrid) is not None: # does this work??   
                outcome.add(value_1, value_2, color_max(subgrid)) #add new pixel to final object
            else:
                outcome.add(value_1, value_2, 0)
    return outcome 

def add_star_around_object(object: Object, color: color, gridsize: int) -> ObjectGrid:
    outcome = set()
    for pixel in object: # first we add all the pixels of the object
        outcome.add(pixel)
    out_pixels = pixel_out_with_uncovered_neighbors(object, gridsize) # then we add the surronding objects
    for pixel in out_pixels:
        outcome.add(pixel[0],pixel[1], color) #they get the assigned color
    
    return object, gridesize

def add_corners_around_object(object: Object, color: color, gridsize: int) -> ObjectGrid:
    outcome = set()
    for pixel in object: # first we add all the pixels of the object
        outcome.add(pixel)
    out_pixels = pixel_out_with_uncovered_neighbors_only_diagonal_neighborhood(object, gridsize) # then we add the surronding corners
    for pixel in out_pixels:
        outcome.add(pixel[0],pixel[1], color) #they get the assigned color
    
    return object, gridesize

def add_border_around_object(object: Object, color: color, gridsize: int) -> ObjectGrid:
    outcome = set()
    for pixel in object: # first we add all the pixels of the object
        outcome.add(pixel)
    out_pixels = pixel_out_with_uncovered_neighbors_with_diagonal(object, gridsize) # then we add the surronding corners
    for pixel in out_pixels:
        outcome.add(pixel[0],pixel[1], color) #they get the assigned color
    
    return object, gridesize

def change_color_pixel_in(object: Object, color: color, gridsize) -> ObjectGrid: # only change the color of pixels classified as out-side pixels 
    outcome = set()
    for pixel in pixel_in(object, gridsize):
        outcome.add(pixel)
    for  pixel in pixel_out(object, gridsize):
        outcome.add(pixel[0], pixel [1], color)
    return outcome

def change_color_pixel_in(object: Object, color: color, gridsize:int) -> ObjectGrid: # only change the color of pixels classified as out-side pixels 
    outcome = set()
    for pixel in pixel_in(object, gridsize):
        outcome.add(pixel[0], pixel [1], color)
    for  pixel in pixel_out(object, gridsize):
        outcome.add(pixel)
    return outcome

def fill_pixel(object: Object, color: color, gridsize: int) -> Object: 
    outcome = set()
    holes = holes(object, gridsize)
    for pixel in object:
        outcome.add(pixel)
    for pixel in object:
        outcome.add((pixel[0], pixel[1], color))
    return outcome

def fill_pixel_right(object: Object, color: color, gridsize: int) -> Object:
    outcome = set()
    gaps = set()
    for y_value in range(0,gridsize):
        y_pixel = set(pixel for pixel in object if pixel[1] == y_value)
        sorted_y_pixel = sorted(y_pixel, key=lambda pixel: pixel[0])
        for i in range(len(sorted_y_pixel)-1):              #generate pxiels to be compared
            (x1, y1, color1) = sorted_pixels[i]
            (x2, y2, color2) = sorted_pixels[i + 1]
            if x2 > x1 + 1:                                     # There is a gap if the x-coordinate
                for x in range(x1 + 1, x2):                     # Store x,y value of gap
                    gaps.add((x, y_value)) 
    for pixel in object: 
        outcome.add(pixel)
    for pixel in gaps:
        outcome.add((pixel[0], pixel[1], color))
    return outcome

def fill_pixel_down(object: Object, color: color, gridsize: int) -> Object:
    outcome = set()
    gaps = set()
    for x_value in range(0,gridsize):
        x_pixel = set(pixel for pixel in object if pixel[0] == x_value)
        sorted_x_pixel = sorted(x_pixel, key=lambda pixel: pixel[1])
        for i in range(len(sorted_y_pixel)-1):              # generate pixels to be compared
            (x1, y1, color1) = sorted_pixels[i]
            (x2, y2, color2) = sorted_pixels[i + 1]
            if y2 > y1 + 1:                                     # There is a gap if the x-coordinate
                for y in range(y1 + 1, y2):                     # Store x,y value of gap
                    gaps.add((y, x_value)) 
    for pixel in object: 
        outcome.add(pixel)
    for pixel in gaps:
        outcome.add((pixel[0], pixel[1], color))
    return outcome




 # , connect pixels_x, connect pixel_y, connect pixel_diagonal, connect pixel_insight