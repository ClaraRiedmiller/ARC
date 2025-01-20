# Definition of a set of types
from typing import TypeAlias, Tuple, Set

#basic types
coordinate: TypeAlias = int     #x or y value
color: TypeAlias = int          #color value
boolean: TypeAlias = bool       #boolean values 

#complex types
Pixel: TypeAlias = Tuple[coordinate, coordinate, color]
Object: TypeAlias = Set[Pixel]  # Note that any grid is hence an object

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
    