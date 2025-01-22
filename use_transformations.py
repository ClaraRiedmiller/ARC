
from dsl.transformation import apply_transformation
from dsl.dsl import *
from dsl.hodel_hardness import upper_bound_hardness



apply_transformation(move_left)

print(upper_bound_hardness(2)) 


