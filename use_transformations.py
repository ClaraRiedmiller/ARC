
from dsl.transformation import apply_transformation
from dsl.dsl import *
from dsl.hodel_hardness import upper_bound_hardness


# apply the transformation move_left to an example grid. We could extend this to take a specific grid as an input as well
apply_transformation(move_left)

# print all problems whose hardness (under hodel) is upper bounded by the paramter specified
print(upper_bound_hardness(2)) 


