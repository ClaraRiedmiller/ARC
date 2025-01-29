from typing import TypeAlias, Tuple, Set    # Definition of a set of types
from collections import Counter             #for base function


#basic types
coordinate: TypeAlias = int     #x or y value
color: TypeAlias = int          #color value
boolean: TypeAlias = bool       #boolean values 

#complex types
Pixel: TypeAlias = Tuple[coordinate, coordinate, color]
Object: TypeAlias = Set[Pixel]  # Note that any grid is hence an object
# Gridsize: TypeAlias = Tuple[coordinate, coordinate] # this is the type for the whole grid


class Constraints:
    def __init__(self, color : color, grid_width : coordinate, grid_height : coordinate):
        self.color : color  = color
        self.grid_width : coordinate = grid_width
        self.grid_height : coordinate = grid_height

    
#Core functions: these functions are not part of the DSL but enable us to detect elements of a structure:
def neighborhood(constraints, pixel: Pixel) -> Object:     #We want to determine the neighbourhood pixels of a pixel. 
    neighbor = [(-1, 0), (0, -1), (1, 0), (0, 1)]
    outcome = set()
    for change in neighbor:
        if 0 <= pixel[0] + change[0] <= constraints.grid_width and  0 <= pixel[1] + change[1] <= constraints.grid_height:
            outcome.add((pixel[0] + change[0], pixel[1] + change[1], pixel[2]))
    return outcome

def neighborhood_with_diagonals(constraints, pixel: Pixel) -> Object:     #We want to determine the neighbourhood pixels of a pixel. 
    neighbor = [(-1, 0), (0, -1), (1, 0), (0, 1), (1,1), (1, -1), (-1,1), (-1,-1)]
    outcome = set()
    for change in neighbor:
        if 0 <= pixel[0] + change[0] <= constraints.grid_width  and   0 <= pixel[1] + change[1] <= constraints.grid_height:
            outcome.add((pixel[0] + change[0], pixel[1] + change[1], pixel[2]))
    return outcome

def only_diagonal_neighborhood(constraints, pixel: Pixel) -> Object:     #We want to determine the neighbourhood pixels of a pixel. 
    neighbor = [(1,1), (1, -1), (-1,1), (-1,-1)]
    outcome = set()
    for change in neighbor:
        if  0 <= pixel[0] + change[0] <= constraints.grid_width and 0 <= pixel[1] + change[1] <= constraints.grid_height:
            outcome.add((pixel[0] + change[0], pixel[1] + change[1], pixel[2]))
    return outcome

def pixel_out(constraints, object: Object) -> Object:             # Given an object, we want to the pixels on the outside
    outcome = set()
    for pixel_1 in object:
        neighborhood_pixel_1 = neighborhood(constraints, pixel_1)
        for pixel_2 in object:
            pixel_2_check = (pixel_2[0],pixel_2[1], pixel_1[2])     # We want to check whether an object is in the 
            if  pixel_2_check in neighborhood_pixel_1:
                neighborhood_pixel_1.remove(pixel_2_check)          
            if len( neighborhood_pixel_1) == 0:                     # This provides a stop if the  neighborhood_pixel_1 is already empty
                break
        if len(neighborhood_pixel_1) != 0:                          # If there is still some neighborhoods which are not covered, we know that the object has empty-space next to it
            outcome.add(pixel_1)
    return outcome

def pixel_in(constraints, object: Object) -> Object:             # Given an object, we want to the pixels in the inside
    result = object
    outcome = set()
    for pixel_1 in object:
        neighborhood_pixel_1 = neighborhood(constraints, pixel_1)
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


def holes(constraints, object: Object) -> Object:  # outputs a set containing pixel-holes of an object
    outcome = set()
    object_xy = set((x,y) for x,y,c in object)
    for x in range(constraints.grid_width):
        for y in range(constraints.grid_height):
            if (x,y) in object_xy:
                continue 
            left = (x - 1, y) in object_xy
            right = (x + 1, y) in object_xy
            above = (x, y + 1) in object_xy
            below = (x, y - 1) in object_xy

            if left and right and above and below:
                outcome.add((x,y,constraints.color)) #@Lorenz changed this to outcome from holes. Also, colored it bc otherwise with only coordinates, it is not a set of pixels and hence not an object!
    return outcome 

def pixel_out_with_uncovered_neighbors(constraints, object: Object) -> Tuple[Object, Object]:
    outside_pixels = set()
    uncovered_neighbors = set()

    for pixel_1 in object:
        neighborhood_pixel_1 = neighborhood(constraints,pixel_1)
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

def pixel_out_with_uncovered_neighbors_with_diagonal(constraints, object: Object) -> Tuple[Object, Object]:
    outside_pixels = set()
    uncovered_neighbors = set()

    for pixel_1 in object: 
        neighborhood_pixel_1 = neighborhood_with_diagonals(constraints, pixel_1) #@Lorenz this requires an object, you are giving it a pixel. I changed the function.
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

def pixel_out_with_uncovered_neighbors_only_diagonal_neighborhood(constraints, object: Object) -> Tuple[Object, Object]:
    outside_pixels = set()
    uncovered_neighbors = set()

    for pixel_1 in object:
        neighborhood_pixel_1 = only_diagonal_neighborhood(constraints, pixel_1)
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
    # x_max = object[0][0]            # Initialize with the x-coordinate of the first pixel
    x_max =  next(iter(object))[0]  
    for pixel in object:
        if pixel[0] > x_max:        # Compare the x-coordinate of each pixel
            x_max = pixel[0]
    return x_max

def x_min(object: Object) -> coordinate:
    # x_min = object[0][0]            # Initialize with the x-coordinate of the first pixel
    x_min =  next(iter(object))[0]  
    for pixel in object:
        if pixel[0] < x_min:        # Compare the x-coordinate of each pixel
            x_min = pixel[0]
    return x_min   

def y_max(object: Object) -> coordinate:
    # y_max = object[0][1]            # Initialize with the y-coordinate of the first pixel
    y_max =  next(iter(object))[1]  
    for pixel in object:
        if pixel[1] > y_max:        # Compare the y-coordinate of each pixel
            y_max = pixel[1]
    return y_max

def y_min(object: Object) -> coordinate:
    # y_min = object[0][1]            # Initialize with the y-coordinate of the first pixel @Lorenz: object is a set, not a list! You cannot refer to it like this, instead we just draw an element from the set. I changed it below:
    y_min =  next(iter(object))[1]   
    
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

# mirrors on x axis
def flip_xax(constraints, object: Object) -> Object: #we want to flip the y-value of the pixels
    outcome = set()
    for pixel in object:
        newpixel = (pixel[0], constraints.grid_height - pixel[1] - 1, pixel[2])
        outcome.add(newpixel) 
    return outcome

# mirrors on y axis
def flip_yax(constraints, object: Object) -> Object: #we want to flip the x-value of the pixels
    outcome = set()
    for pixel in object:
        newpixel = (constraints.grid_width - pixel[0] -1, pixel[1], pixel[2])
        outcome.add(newpixel) 
    return outcome

def flip_object_around_own_xax(constraints, object: Object) -> Object:
    outcome = set()
    max_y_value =  y_max(object)
    min_y_value =  y_min(object)
    for pixel in object:
        newpixel = (pixel[0], max_y_value + min_y_value - pixel[1], pixel[2])
        outcome.add(newpixel)
    return outcome

def flip_object_around_own_yax(constraints, object: Object) -> Object:
    outcome = set()
    max_x_value =  x_max(object)
    min_x_value =  x_min(object)
    for pixel in object:
        newpixel = (max_x_value + min_x_value - pixel[0],pixel[1], pixel[2])
        outcome.add(newpixel)
    return outcome

def move_right(constraints, object: Object) -> Object: #we want to move the object one pixel to the right 
    outcome = set()
    for pixel in object:
        if pixel[0] + 1 <= constraints.grid_width:  
            newpixel = (pixel[0] +1 , pixel[1], pixel[2])
            outcome.add(newpixel) 
    return outcome

def move_left(constraints, object: Object) -> Object:  #we want tot move the object one pixel to the right 
    outcome = set()
    for pixel in object:
        if pixel[0] - 1 >= 0:  
            newpixel = (pixel[0]  - 1 , pixel[1], pixel[2])
            outcome.add(newpixel) 
    return outcome

def move_down(constraints, object: Object) -> Object: #we want tot move the object one pixel up 
    outcome = set()
    for pixel in object:
        if pixel[1] + 1 <= constraints.grid_height:  
            newpixel = (pixel[0], pixel[1] + 1, pixel[2])
            outcome.add(newpixel) 
    return outcome

def move_up(constraints, object: Object) -> Object:  #we want to move the object one pixel down
    outcome = set()
    for pixel in object:
        if pixel[1] - 1 >= 0:  
            newpixel = (pixel[0], pixel[1] - 1, pixel[2])
            outcome.add(newpixel) 
    return outcome

def move_left_edge(constraints, object: Object) -> Object: # move to left edge
    outcome = set()
    min_x_value = x_min(object)
    for pixel in object:
        newpixel = (pixel[0] - min_x_value, pixel[1], pixel[2])
        outcome.add(newpixel)
    return outcome 

def move_right_edge(constraints, object: Object) -> Object: #move to right edge
    outcome = set()
    max_x_value = x_max(object)
    for pixel in object:
        newpixel = (pixel[0] + (constraints.grid_width - max_x_value - 1), pixel[1], pixel[2])
        outcome.add(newpixel)
    return outcome 

def move_up_edge(constraints, object: Object) -> Object: # move to bottom edge
    outcome = set()
    min_y_value = y_min(object)
    for pixel in object:
        newpixel = (pixel[0], pixel[1] - min_y_value, pixel[2])
        outcome.add(newpixel)
    return outcome 

def move_down_edge(constraints, object: Object) -> Object: # move to top edge
    outcome = set()
    max_y_value = y_max(object)
    for pixel in object:
        newpixel = (pixel[0], pixel[1] + (constraints.grid_height - max_y_value - 1), pixel[2])
        outcome.add(newpixel)
    return outcome 

### DSL Transform 
def isolate(constraints, object: Object) -> (Object): #isolate an object
    outcome= set()
    for pixel in object:
        newpixel = (pixel[0] - x_min(object), pixel[1] - y_min(object), pixel[2])
        outcome.add(newpixel)
    #newgridsize = (x_max(object) - x_min(object),y_max(object)-y_min(object) )
    print('these would be the new values for x_max and y_max:', x_max(object), y_max(object))
    constraints.grid_width = x_max(object) - x_min(object) +1                # to be checked @Natasha
    constraints.grid_height = y_max(object) - y_min(object) +1               # to be checked @Natasha
    return outcome

def color_object_max(constraints, object: Object) -> (Object):
    outcome = set()
    tobecolor = color_max(object)
    for pixel in object:
        outcome.add((pixel[0], pixel[1], tobecolor))
    return outcome

def color_object_min(constraints, object: Object) -> (Object):
    outcome = set()
    tobecolor = color_min(object)
    for pixel in object:
        outcome.add((pixel[0], pixel[1], tobecolor))
    return outcome

def project_dupliate(constraints, object: Object) -> Object: #duplication of an object
    outcome = set()
    for (pixel) in object: 
        for x_value in range(0,2):
            for y_value in range(0,2):
                newpixel = (pixel[0] * 2 + x_value, pixel[1] * 2 + y_value, pixel[2]) 
                outcome.add(newpixel)
    constraints.grid_height = constraints.grid_height *2
    constraints.grid_width = constraints.grid_width *2
    return outcome

def project_triplicate(constraints, object: Object) -> Object: #triplication of an object
    outcome = set()
    for (pixel) in object: 
        for x_value in range(0,3):
            for y_value in range(0,3):
                newpixel = (pixel[0] * 3 + x_value, pixel[1] * 3 + y_value, pixel[2]) 
                outcome.add(newpixel)
    constraints.grid_height = constraints.grid_height *3
    constraints.grid_width = constraints.grid_width *3
    return outcome

def project_quintuplicate(constraints, object: Object) -> Object: #quintuplication of an object
    outcome = set()
    for (pixel) in object: 
        for x_value in range(0,5):
            for y_value in range(0,5):
                newpixel = (pixel[0] * 5 + x_value, pixel[1] *5 + y_value, pixel[2]) 
                outcome.add(newpixel)
    constraints.grid_height = constraints.grid_height *5
    constraints.grid_width = constraints.grid_width *5
    return outcome
    

def project_half(constraints, object: Object) -> Object: #project on grid of half size
    outcome = set()
    grid_x_value = x_max(object) - x_min(object) + 1
    grid_y_value = y_max(object) - y_min(object) + 1
    
    if grid_x_value % 2 != 0 or grid_y_value % 2 != 0:
        return object

    for value_1 in range(2): #to shrink x-value
        for value_2 in range(2): # to shrink y-value
            subgrid = set()
            for (x,y,c) in object:
                if value_1 <= x // 2 < value_1 + 1 and value_2 <= y // 2 < value_2 + 1:
                    subgrid.add((x,y,c))
            if color_max(subgrid) is not None:    
                outcome.add((value_1, value_2, color_max(subgrid))) #add new pixel to final object
            # else:
            #     outcome.add((value_1, value_2, 0))

    constraints.grid_height = int(constraints.grid_height /2)
    constraints.grid_width = int(constraints.grid_width /2)
    return outcome 

def project_third(constraints, object: Object) -> Object: #project on grid of third size
    outcome = set()
    grid_x_value = x_max(object) - x_min(object) + 1
    grid_y_value = y_max(object) - y_min(object) + 1
    
    if grid_x_value % 3 != 0 or grid_y_value % 3 != 0:
        return object

    for value_1 in range(3): #to shrink x-value
        for value_2 in range(3): # to shrink y-value
            subgrid = set()
            for (x,y,c) in object:
                if value_1 <= x // 3 < value_1 + 1 and value_2 <= y // 3 < value_2 + 1:
                    subgrid.add((x,y,c))
            if color_max(subgrid) is not None:    
                outcome.add((value_1, value_2, color_max(subgrid))) #add new pixel to final object
            # else:
            #     outcome.add((value_1, value_2, 0))

    constraints.grid_height = int(constraints.grid_height /3)
    constraints.grid_width = int(constraints.grid_width /3)
    return outcome 

def project_fifth(constraints, object: Object) -> Object: #project on grid of fifth size
    outcome = set()
    grid_x_value = x_max(object) - x_min(object) + 1
    grid_y_value = y_max(object) - y_min(object) + 1
    
    if grid_x_value % 5 != 0 or grid_y_value % 5 != 0:
        return object

    for value_1 in range(5): #to shrink x-value
        for value_2 in range(5): # to shrink y-value
            subgrid = set()
            for (x,y,c) in object:
                if value_1 <= x // 5 < value_1 + 1 and value_2 <= y // 5 < value_2 + 1:
                    subgrid.add((x,y,c))
            if color_max(subgrid) is not None:    
                outcome.add((value_1, value_2, color_max(subgrid))) #add new pixel to final object
    constraints.grid_height = int(constraints.grid_height /5)
    constraints.grid_width = int(constraints.grid_width /5)
    return outcome 


def add_star_around_object(constraints, object: Object) -> Object: # add star-like pixels
    outcome = object
    outside_pixels, uncovered_neighbors = pixel_out_with_uncovered_neighbors(constraints, object) # then we add the surronding objects
    for pixel in uncovered_neighbors:
        outcome.add((pixel[0],pixel[1], constraints.color)) #they get the assigned color
    
    return object

def add_corners_around_object(constraints, object: Object) -> Object: # add diagonal corners
    outcome = object
    outside_pixels, uncovered_neighbors = pixel_out_with_uncovered_neighbors_only_diagonal_neighborhood(constraints, object) # then we add the surronding corners
    for pixel in uncovered_neighbors:
        outcome.add((pixel[0],pixel[1], constraints.color)) #they get the assigned color
    
    return object

def add_border_around_object(constraints, object: Object) -> Object: # add boundary
    outcome = object
    outside_pixels, uncovered_neighbors = pixel_out_with_uncovered_neighbors_with_diagonal(constraints, object) # then we add the surronding corners
    for pixel in uncovered_neighbors:
        outcome.add((pixel[0],pixel[1], constraints.color)) #they get the assigned color
    
    return outcome

def change_color_pixel_out(constraints, object: Object) -> Object: # only change the color of pixels classified as out-side pixels 
    outcome = set()
    for pixel in pixel_in(constraints, object):
        outcome.add(pixel)
    for  pixel in pixel_out(constraints, object):
        outcome.add((pixel[0], pixel [1], constraints.color))
    return outcome

def change_color_pixel_in(constraints, object: Object) -> (Object): # only change the color of pixels classified as in-side pixels 
    outcome = set()
    for pixel in pixel_in(constraints, object):
        outcome.add((pixel[0], pixel [1], constraints.color))
    for  pixel in pixel_out(constraints, object):
        outcome.add(pixel)
    return outcome

def fill_pixel(constraints, object: Object) -> Object: # fill pixel within an object
    outcome = set()
    detected_holes = holes(constraints, object)
    for pixel in object:
        outcome.add(pixel)
    for pixel in detected_holes: #@Lorenz I changed object here to holes
        outcome.add((pixel[0], pixel[1], constraints.color))
    return outcome

def fill_pixel_right(constraints, object: Object) -> Object: # combine pixels on the same x-value but with a gap 
    outcome = set()
    gaps = set()
    for y_value in range(0,constraints.grid_width):
        y_pixel = set(pixel for pixel in object if pixel[1] == y_value)
        sorted_y_pixel = sorted(y_pixel, key=lambda pixel: pixel[0])
        for i in range(len(sorted_y_pixel)-1):              #generate pxiels to be compared
            (x1, y1, color1) = sorted_y_pixel[i]
            (x2, y2, color2) = sorted_y_pixel[i + 1]
            if x2 > x1 + 1:                                     # There is a gap if the x-coordinate
                for x in range(x1 + 1, x2):                     # Store x,y value of gap
                    gaps.add((x, y_value)) 
    for pixel in object: 
        outcome.add(pixel)
    for pixel in gaps:
        outcome.add((pixel[0], pixel[1], constraints.color))
    return outcome

def fill_pixel_down(constraints, object: Object) -> Object: # combine pixels on the same y-value but with a gap
    outcome = set()
    gaps = set()
    for x_value in range(0,constraints.grid_height):
        x_pixel = set(pixel for pixel in object if pixel[0] == x_value)
        sorted_y_pixel = sorted(x_pixel, key=lambda pixel: pixel[1]) #@Lorenz I changed sorted_x_pixel tosorted_y_pixel
        for i in range(len(sorted_y_pixel)-1):              # generate pixels to be compared 
            (x1, y1, color1) = sorted_y_pixel[i]
            (x2, y2, color2) = sorted_y_pixel[i + 1]
            if y2 > y1 + 1:                                     # There is a gap if the x-coordinate
                for y in range(y1 + 1, y2):                     # Store x,y value of gap
                    gaps.add((y, x_value)) 
    for pixel in object: 
        outcome.add(pixel)
    for pixel in gaps:
        outcome.add((pixel[0], pixel[1], constraints.color))
    return outcome


# DSL grid modifications
def grid_add_down(constraints, object: Object) -> Object: #add one more gridline at the bottom
    outcome = set()
    for pixel in object:
        outcome.add(pixel) # @Lorenz, why not outcome=object instead of this loop?
    # for x_value in (range, constraints.grid_width): # @Lorenz: LOL, siehe unten
    for x_value in range(constraints.grid_width): 
        newpixel = (x_value, constraints.grid_height, constraints.color)
        outcome.add(newpixel)
    constraints.grid_height = constraints.grid_height +1
    return outcome

def grid_add_up(constraints, object: Object) -> Object: #add one more gridline at the top
    outcome = set()
    for pixel in object:
        newpixel = (pixel[0], pixel[1] + 1, pixel[2])
        outcome.add(newpixel)
    for x_value in range(constraints.grid_width):
        newpixel = (x_value, 0, constraints.color)
        outcome.add(newpixel)
    constraints.grid_height = constraints.grid_height +1
    return outcome

def grid_add_right(constraints, object: Object) -> Object: #add one more gridline right
    outcome = set()
    for pixel in object:
        outcome.add(pixel)
    for y_value in range(constraints.grid_height):
        newpixel = (constraints.grid_width, y_value, constraints.color)
        outcome.add(newpixel)
    constraints.grid_width = constraints.grid_width +1
    return outcome

def grid_add_left(constraints, object: Object) -> Object: #add one more gridline left
    outcome = set()
    for pixel in object:
        newpixel = (pixel[0] +1, pixel[1], pixel[2])
        outcome.add(newpixel)
    for y_value in range(constraints.grid_height):
        newpixel = (0, y_value, constraints.color)
        outcome.add(newpixel)
    constraints.grid_width = constraints.grid_width +1
    return outcome

def grid_add_up_and_down (constraints, object: Object) -> Object: #add one more gridline at top and bottom
    outcome = set()
    for pixel in object:
        newpixel = (pixel[0], pixel[1] + 1, pixel[2])
        outcome.add(newpixel)
    for x_value in range(constraints.grid_width):
        newpixel_1 = (x_value, 0, constraints.color) #first line 
        outcome.add(newpixel_1)
        newpixel_2 = (x_value, constraints.grid_height + 1, constraints.color) #last line #@Lorenz: what happens with this?
        outcome.add(newpixel_2)
    constraints.grid_height = constraints.grid_height +2
    return outcome

def grid_add_left_and_right (constraints, object: Object) -> Object: #add one more gridline at left and right 
    outcome = set()
    for pixel in object:
        newpixel = (pixel[0] + 1, pixel[1], pixel[2])
        outcome.add(newpixel)
    for y_value in range(constraints.grid_height):
        newpixel_1 = (0, y_value, constraints.color) #first line 
        outcome.add(newpixel_1)
        newpixel_2 = (constraints.grid_width + 1, y_value, constraints.color) #last line 
        outcome.add(newpixel_2)
    constraints.grid_width = constraints.grid_width +2
    return outcome

def grid_duplicate_down(constraints, object: Object) -> Object: #add one more gridline by duplication the bottom line
    outcome = set()
    for pixel in object:
        outcome.add(pixel)
    filtered_pixels = filter(lambda pixel: pixel[1] == constraints.grid_height - 1, object)
    for pixel in filtered_pixels:
        newpixel = (pixel[0], constraints.grid_height, pixel[2])
        outcome.add(newpixel)
    constraints.grid_height = constraints.grid_height +1
    return outcome

def grid_duplicate_up(constraints, object: Object) -> Object: #add one more gridline by duplication the top line
    outcome = set()
    for pixel in object:      
        newpixel = (pixel[0], pixel[1] + 1, pixel[2])
        outcome.add(newpixel)
    filtered_pixels = filter(lambda pixel: pixel[1] == 0, object)
    for pixel in filtered_pixels:
        newpixel = (pixel[0], 0, pixel[2])
        outcome.add(newpixel)
    constraints.grid_height = constraints.grid_height +1
    return outcome

def grid_duplicate_right(constraints, object: Object) -> Object: #add one more gridline by duplication the right line
    outcome = set()
    for pixel in object:
        outcome.add(pixel)
    filtered_pixels = filter(lambda pixel: pixel[0] == constraints.grid_width - 1, object)
    for pixel in filtered_pixels:
        newpixel = (constraints.grid_width, pixel[1], pixel[2])
        outcome.add(newpixel)
    constraints.grid_width = constraints.grid_width +1
    return outcome

def grid_duplicate_left(constraints, object: Object) -> Object: ##add one more gridline by duplication the left line
    outcome = set()
    for pixel in object:
        newpixel = (pixel[0] +1, pixel[1], pixel[2])
        outcome.add(newpixel)
    filtered_pixels = filter(lambda pixel: pixel[0] == 0, object)
    for pixel in filtered_pixels:
        newpixel = (0, pixel[1], pixel[2])
        outcome.add(newpixel)
    constraints.grid_width = constraints.grid_width +1
    return outcome


def grid_duplicate_up_and_down (constraints, object: Object) -> Object: #duplication of top and bottom
    outcome = set()
    for pixel in object:
        newpixel = (pixel[0], pixel[1] + 1, pixel[2])
        outcome.add(newpixel)
    sorted_object_up = filter(lambda pixel: pixel[1] == 0, object)
    sorted_object_down = filter(lambda pixel: pixel[1] == constraints.grid_height - 1, object)
    for pixel in sorted_object_up:   # new first line
        newpixel = (pixel[0], 0, pixel[2])
        outcome.add(newpixel)
    for pixel in sorted_object_down: # new last line 
        newpixel = (pixel[0], constraints.grid_height + 1, pixel[2])
        outcome.add(newpixel)
    constraints.grid_height = constraints.grid_height +2
    return outcome

def grid_duplicate_left_and_right (constraints, object: Object) -> Object: #duplication of left and right
    outcome = set()
    for pixel in object:
        newpixel = (pixel[0] + 1, pixel[1], pixel[2])
        outcome.add(newpixel)
    sorted_object_left = filter(lambda pixel: pixel[0] == 0, object)
    sorted_object_down = filter(lambda pixel: pixel[0] == constraints.grid_width - 1, object)
    for pixel in sorted_object_left:   # new first line
        newpixel = (0, pixel[1], pixel[2])
        outcome.add(newpixel)
    for pixel in sorted_object_down: # new last line 
        newpixel = (constraints.grid_width + 1, pixel[1] ,pixel[2])
        outcome.add(newpixel)
    constraints.grid_width = constraints.grid_width +2
    return outcome