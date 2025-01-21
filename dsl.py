# Definition of a set of types
from typing import TypeAlias, Tuple, Set

#basic types
coordinate: TypeAlias = int     #x or y value
color: TypeAlias = int          #color value
boolean: TypeAlias = bool       #boolean values 

#complex types
Pixel: TypeAlias = Tuple[coordinate, coordinate, color]
Object: TypeAlias = Set[Pixel]  # Note that any grid is hence an object


#Core functions: these functions are not part of the DSL but enable us to detect elements of a structure:
def neighborhood(object: Object, gridesize: int) -> object:     #We want to determine the neighbourhood pixels of a pixel. 
    neighbor = [(-1, 0), (0, -1), (1, 0), (0, 1)]
    outcome = set()
    for pixel in object:
        for change in neighbor:
            if pixel[0] + change[0] >= 1 and pixel[0] + change[0] <= gridesize and pixel[1] + change[1] >= 1 and pixel[1] + change[1] <= gridesize:
                outcome.add((pixel[0] + change[0], pixel[1] + change[1], pixel[2]))
    return outcome

def pixel_out(object: Object, gridsize: int) -> Object:             # Given an object, we want to the new the pixels on the outside
    outcome = set{}
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

def pixel_out(object: Object, gridsize: int) -> Object:             # Given an object, we want to the new the pixels in the inside
    outcome = set{}
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
    return outcome

def x_max(object: Object) -> int:
    x_max = object[0][0]            # Initialize with the x-coordinate of the first pixel
    for pixel in object:
        if pixel[0] > x_max:        # Compare the x-coordinate of each pixel
            x_max = pixel[0]
    return x_max

def x_min(object: Object) -> int:
    x_min = object[0][0]            # Initialize with the x-coordinate of the first pixel
    for pixel in object:
        if pixel[0] < x_min:        # Compare the x-coordinate of each pixel
            x_min = pixel[0]
    return x_min   

def y_max(object: Object) -> int:
    y_max = object[0][1]            # Initialize with the y-coordinate of the first pixel
    for pixel in object:
        if pixel[1] > y_max:        # Compare the y-coordinate of each pixel
            y_max = pixel[1]
    return y_max

def y_min(object: Object) -> int:
    y_min = object[0][1]            # Initialize with the y-coordinate of the first pixel
    for pixel in object:
        if pixel[1] < y_min:        # Compare the y-coordinate of each pixel
            y_min = pixel[1]
    return y_min  


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
        if pixel[0] - 1 >= 1:  
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
    min_x_value = min_x(object)
    for pixel in object:
        newpixel = (pixel[0] - min_x_value + 1, pixel[1], pixel[2])
        outcome.add(newpixel)
    return outcome 

def move_right_edge(object: Object, gridsize: int) -> Object:
    outcome = set()
    max_x_value = max_x(object)
    for pixel in object:
        newpixel = (pixel[0] + (gridsize - max_x_value), pixel[1], pixel[2])
        outcome.add(newpixel)
    return outcome 

def move_down_edge(object: Object, gridsize: int) -> Object:
    outcome = set()
    min_y_value = min_y(object)
    for pixel in object:
        newpixel = (pixel[0], pixel[1] - min_y_value + 1, pixel[2])
        outcome.add(newpixel)
    return outcome 

def move_up_edge(object: Object, gridsize: int) -> Object:
    outcome = set()
    max_y_value = max_y(object)
    for pixel in object:
        newpixel = (pixel[0], pixel[1] + (gridsize - max_y_value), pixel[2])
        outcome.add(newpixel)
    return outcome 

