import arckit
import arckit.vis as vis
import drawsvg


def terminalVis(task):

    task.show()



def getGrid(task, is_training, which_example, is_in):

    return(task.train[which_example][int(not is_in)] if is_training else task.test[which_example][int(not is_in)])


def drawGrid(grid, file_name):

    graphic = vis.draw_grid(grid, xmax=3, ymax=3, padding=0.5)
    vis.output_drawing(graphic, './images/grid_images/' + file_name + '.png')

    

def drawProblem(task, file_name):
    
    # Monkey-patch to add embed_google_font to Group
    class GroupWithFont(drawsvg.Group):
        def embed_google_font(self, *args, **kwargs):
            pass  
    vis.drawsvg.Group = GroupWithFont

   
    graphic = vis.draw_task(task, width=14, height=8, label="Problorenz")
    vis.output_drawing(graphic, './images/problem_images/' + file_name + '.png') 



def get_problem(task_id, terminal_visualize = True, image_visualize = True):

    train_set, eval_set = arckit.load_data() 

    # load task
    task = train_set[task_id]

    # visualize task in terminal
    if terminal_visualize:
        terminalVis(task)

    # draw the problem, gets saved into images/problem_images
    if image_visualize:
        problem_image_file_name = str(task_id)
        drawProblem(task, problem_image_file_name)

    return(task.train)



def get_grid(task_id, terminal_visualize = True, image_visualize = True, is_training = True, which_example = 0, is_in = True):

    train_set, eval_set = arckit.load_data() 

    # load task
    task = train_set[task_id]
    grid = getGrid(task, is_training, which_example, is_in)

    if terminal_visualize:
        print(grid)

    # draw grid
    if image_visualize:
        grid_image_file_name = str(task_id) + '_' + str(int(is_training)) + '_' + str(which_example) + '_' + str(is_in)
        drawGrid(grid, grid_image_file_name)

    return(grid)