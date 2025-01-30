# this file stores our testgrids

import numpy as np
import arckit
from arckit.data import Task

# get example grid so we can test our transformations
train_set, eval_set = arckit.load_data() 

# Problem 1: 
# This is one of the training problems that is just one big object transformation (where the object is the size of the grid). It only requires learning a program that takes the object and flips it along the x-axis
def get_problem_1():
    problem1 = train_set['68b16354']

    return(problem1)



# Problem 2: 
# This problem was just to test the format of the problem we need to specify
def get_problem_2():
    train = [{'input': [[2]], 'output': [[2]]}, {'input': [[2]], 'output': [[2]]}]
    test = [{'input': [[2]], 'output': [[2]]}]
    problem2 = Task(id='0', test=test, train=train)

    return(problem2)




# Problem 3: 
# This is the problem we talked about earlier: Every yellow object (single pixel, col 4) needs to be moved one to the left, every blue object (single pixel, col 1) one up.
def get_problem_3():
    train = [{'input': [[0, 0, 4, 0],
                        [0, 0, 0, 0],
                        [0, 0, 1, 0]], 'output': [[0, 4, 0, 0],
                                                  [0, 0, 1, 0],
                                                  [0, 0, 0, 0]]}, 
            {'input': [[0, 0, 0, 0],
                        [0, 4, 0, 0],
                        [0, 0, 0, 1]], 'output': [[0, 0, 0, 0],
                                                  [4, 0, 0, 1],
                                                  [0, 0, 0, 0]]}, 
            {'input': [[0, 0, 0, 0, 0],
                        [0, 0, 0, 1, 0],
                        [0, 0, 0, 0, 0],
                        [0, 0, 4, 0, 0]], 'output': [[0, 0, 0, 1, 0],
                                                     [0, 0, 0, 0, 0],
                                                     [0, 0, 0, 0, 0],
                                                     [0, 4, 0, 0, 0]]}]
    test = [{'input': [[0, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 4, 0]], 'output': [[0, 1, 0, 0],
                                                  [0, 0, 0, 0],
                                                  [0, 4, 0, 0]]}]
    problem3 = Task(id='0', test=test, train=train)

    # edit test

    return(problem3)



# Problem 4:
# More complex version of problem 2: More objects. 4 goes left, 5 goes right, 1 goes up
def get_problem_4():
    train = [{'input': [[0, 0, 4, 0],
                        [0, 0, 0, 0],
                        [0, 5, 0, 0],
                        [0, 0, 0, 0],
                        [0, 0, 1, 0]], 'output': [[0, 4, 0, 0],
                                                  [0, 0, 0, 0],
                                                  [0, 0, 5, 0],
                                                  [0, 0, 1, 0],
                                                  [0, 0, 0, 0]]}, 
            {'input': [[0, 0, 5, 0],
                        [0, 4, 0, 0],
                        [0, 0, 0, 1]], 'output': [[0, 0, 0, 5],
                                                  [4, 0, 0, 1],
                                                  [0, 0, 0, 0]]}, 
            {'input': [[0, 5, 0, 0, 0],
                        [0, 0, 0, 1, 0],
                        [0, 0, 0, 0, 0],
                        [0, 0, 4, 0, 0]], 'output': [[0, 0, 5, 1, 0],
                                                     [0, 0, 0, 0, 0],
                                                     [0, 0, 0, 0, 0],
                                                     [0, 4, 0, 0, 0]]}]
    test = [{'input': [[0, 0, 5, 0],
                        [0, 1, 0, 0],
                        [0, 0, 4, 0]], 'output': [[0, 1, 0, 0],
                                                  [0, 0, 0, 0],
                                                  [0, 4, 0, 0]]}]
    problem3 = Task(id='0', test=test, train=train)

    # edit test

    return(problem3)



# modification of 3, where the objects are closer together - we would still need to be able to detect them as single objects

# modification of 3, where there are multiple of each object in the examples

# modification of 3, where the grid also changes independently of the objects


