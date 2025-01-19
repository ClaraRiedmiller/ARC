import arckit
import arckit.vis as vis
import drawsvg


def terminalVis(task):

    task.show()



def getGrid(task, is_training, which_example, is_in):

    return(task.train[which_example][int(not is_in)] if is_training else task.test[which_example][int(not is_in)])


def drawGrid(grid, file_name):

    graphic = vis.draw_grid(grid, xmax=3, ymax=3, padding=0.5, label="LoLoLorenz")
    vis.output_drawing(graphic, './grid_images/' + file_name + '.png')

    

def drawProblem(task, file_name):
    
    # Monkey-patch to add embed_google_font to Group
    class GroupWithFont(drawsvg.Group):
        def embed_google_font(self, *args, **kwargs):
            pass  
    vis.drawsvg.Group = GroupWithFont

   
    graphic = vis.draw_task(task, width=14, height=8, label="Problorenz")
    vis.output_drawing(graphic, './problem_images/' + file_name + '.png') 




def main():

    train_set, eval_set = arckit.load_data() 


    ## looking at the whole problem

    # set parameters for task
    taskId = '5582e5ca'
    problem_image_file_name = str(taskId)

    # load task
    task = train_set[taskId]

    # visualize task in terminal
    terminalVis(task)

    # draw whole problem
    drawProblem(task, problem_image_file_name)



    ## looking at specific grid

    # set paramters 
    is_training = True
    which_example = 0
    is_in = True
    grid_image_file_name = str(taskId) + '_' + str(int(is_training)) + '_' + str(which_example) + '_' + str(is_in)

    # retreive and draw grid
    grid = getGrid(task, is_training, which_example, is_in)
    drawGrid(grid, grid_image_file_name)
   


main()