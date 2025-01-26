### We want to generate some examples such that we can test our DSL

# Fix the Grid
grid_size = [5,5]
grid = [[0 for x in range(grid_size[0])] for y in range(grid_size[1])]

#Fix test color (if needed)
color = 3

# Specify test object 

# test object for any object function
object_1 = set()
for x in range(1,4):
    for y in range(1,4):
        object_1.add((x,y,color))
object_1.remove((2,2,color))