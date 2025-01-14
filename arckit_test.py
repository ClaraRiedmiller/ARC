# these are the important functions of the arckit for us. See all of them here: https://github.com/mxbi/arckit/blob/main/README.md


import arckit
import arckit.vis as vis
train_set, eval_set = arckit.load_data() # Load ARC1 train/eval

# # TaskSets are iterable and indexable
# print(train_set)

# # loading specific tasks by index or id. 
# print(train_set[0])
# print(arckit.load_single('007bbfb7'))


# For the following, let's name this specific problem instance task
task = train_set[0]

# # getting the task id
# print(task.id)

# # getting the type of dataset from a specific task (?)
# print(task.dataset)



# # view the training and test data for the task
# print(task.train)
# print(task.test)

# get specific grid (which example, input 0 or output 1)
firstTrainingInput = task.train[0][0]
# print(firstTrainingInput)


# # with the task index, we can retreive the training set (training input-output, test input) (--> We get the test output as well, it is just not shown here!)
# train_set[0].show()



# visualizations. Draw first, then save (this is often how it works in python). They will be saved to a folder. Format can be svg, png or pdf.
grid = vis.draw_grid(firstTrainingInput, xmax=3, ymax=3, padding=0.5, label="LoLoLorenz")
vis.output_drawing(grid, "./grid_images/LoLoLorenz.png")

grid2 = vis.draw_task(train_set[0], width=10, height=6, label="Problorenz")
vis.output_drawing(grid2, "grid_images/whole_problorenz.png") 


# grid = vis.draw_grid(task.train[0][0], xmax=3, ymax=3, padding=.5, label='Example')
# vis.output_drawing(grid, "images/grid_example.png") # svg/pdf/png
