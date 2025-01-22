import arckit
import arckit.vis as vis
import drawsvg
import numpy as np

from hodel_solver import get_problem_hardness
from dsl import *

def terminalVis(task):

    task.show()



def getGrid(task, is_training, which_example, is_in):

    return(task.train[which_example][int(not is_in)] if is_training else task.test[which_example][int(not is_in)])


def drawGrid(grid, file_name):

    graphic = vis.draw_grid(grid, xmax=3, ymax=3, padding=0.5, label="LoLoLorenz")
    vis.output_drawing(graphic, './images/grid_images/' + file_name + '.png')

    

def drawProblem(task, file_name):
    
    # Monkey-patch to add embed_google_font to Group
    class GroupWithFont(drawsvg.Group):
        def embed_google_font(self, *args, **kwargs):
            pass  
    vis.drawsvg.Group = GroupWithFont

   
    graphic = vis.draw_task(task, width=14, height=8, label="Problorenz")
    vis.output_drawing(graphic, './images/problem_images/' + file_name + '.png') 




def get_prblm_hrdns_one(train_set):

    problem_hardness = get_problem_hardness() 


    for problem, lines in problem_hardness.items():
        if lines < 3:
            print(f"{problem}: {lines}")

            problem_image_file_name = 'hardness_' + str(lines) + '_problem_' + str(problem)
            drawProblem(train_set[problem], problem_image_file_name)





def convert_grid_format(grid):

    # convert into Lorenz' prefered format

    # empty Object
    Object = []

    for row_index, row in enumerate(grid):
        for column_index, column in enumerate(row):
            Object.append([column_index, row_index, column])

    return Object


def reconvert_grid_format(formatted_grid):

    # get og grid dimensions
    width = max(sublist[1] for sublist in formatted_grid) +1
    height = max(sublist[0] for sublist in formatted_grid) +1
    
    # Create an empty grid (numpy array) with the specified dimensions
    grid = np.array([[None for _ in range(height)] for _ in range(width)])


    # Iterate over the formatted grid and place the values back into the correct positions
    for item in formatted_grid:
        row_index, column_index, color = item
        grid[column_index][row_index] = color

    return grid



def main():

    train_set, eval_set = arckit.load_data() 

    # get_prblm_hrdns_one(train_set)

    # get specific grid
    grid = getGrid(train_set['68b16354'], True, 0, True)

    print('\n', 'Grid:\n', grid, '\n', type(grid))
    drawGrid(grid, 'pre_rotated')

    formatted_grid = convert_grid_format(grid)
    print('\n', 'Formatted grid:\n', formatted_grid)


    recovered_grid = reconvert_grid_format(formatted_grid)
    print('\n', 'Reformatted Grid:\n', recovered_grid)


    test_output = move_left(formatted_grid, 5)
    formatted_test_output = reconvert_grid_format(test_output)
    print('\n', 'Test Output:\n', test_output)
    print('\n', 'Formatted Test Output:\n', formatted_test_output)
    # drawGrid(formatted_test_output, 'rotated_test')



main()