import arckit.vis as vis
import drawsvg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .dsl import Transformer
from arckit_handler.arckit_handler import drawGrid, getGrid

def convert_grid_format(grid):

    # convert into Lorenz' prefered format

    # empty Object
    object = []

    for row_index, row in enumerate(grid):
        for column_index, column in enumerate(row):
            object.append([column_index, row_index, column])

    # the above creates a list of lists. The dsl though uses sets of touples. Since we are typing, this is an important distiction! Thus, we convert to a set of touples
    object = {tuple(pixel) for pixel in object}

    return object


def reconvert_grid_format(formatted_grid):

    # get grid dimensions
    width = max(sublist[1] for sublist in formatted_grid) +1
    height = max(sublist[0] for sublist in formatted_grid) +1
    
    # Create an empty grid (numpy array; empty here means filled with 0, which is the bg color in most cases.) with the specified dimensions
    grid = np.array([[0 for _ in range(height)] for _ in range(width)])


    # Iterate over the formatted grid and place the values back into the correct positions
    for item in formatted_grid:
        row_index, column_index, color = item
        grid[column_index][row_index] = color

    return grid


def visualize_transformation(grid, transgrid, transformation_name, grid_title, show):

    def fill_transparent_area(image, fill_color):
        # Ensure the image is in RGBA mode (so it has an alpha channel)
        image = image.convert("RGBA")
        # Get the image size
        width, height = image.size
        # Create a background image with the fill color
        background = Image.new("RGBA", (width, height), fill_color)
        # Paste the original image on top of the background, using its alpha channel as a mask
        background.paste(image, (0, 0), image)
        return background

    file_name_grid = 'pretrans'
    file_name_transgrid = 'posttrans'
    file_name_transformation = transformation_name + '_' + grid_title
    arrow_text = transformation_name
    bg_color = 'grey'

    # combine pre-transformed grid and transformed grid into one plot
    drawGrid(grid, file_name_grid)
    drawGrid(transgrid, file_name_transgrid)


    # Load the two PNG images
    image1 = Image.open('./images/grid_images/' + file_name_grid + '.png')
    image2 = Image.open('./images/grid_images/' + file_name_transgrid + '.png')

    # Fill the transparent areas of the images with the desired background color
    image1_filled = fill_transparent_area(image1, bg_color)
    image2_filled = fill_transparent_area(image2, bg_color)

    # # Ensure both images have the same height (resize if necessary)
    # if image1.height != image2.height:
    #     image2 = image2.resize((int(image2.width * (image1.height / image2.height))), image1.height)

    # Calculate the total width and create a blank canvas
    text_height = 50  # Space for the title and arrow text
    arrow_width = 50  # Width of the arrow area
    combined_width = image1.width + image2.width + arrow_width + 100  # Width for both images and the arrow and padding
    combined_height = text_height + max(image1.height, image2.height) + 20  # Space for the arrow and text
    combined_image = Image.new("RGBA", (combined_width, combined_height), bg_color)

    # Draw title at the top
    draw = ImageDraw.Draw(combined_image)
    font = ImageFont.load_default()  # Use default font

    # Use `textbbox` to calculate the title text size
    text_bbox = draw.textbbox((0, 0), grid_title, font=font)
    title_width, title_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    draw.text(((combined_width - title_width) / 2, 10), grid_title, fill="black", font=font)

    # Draw the arrow text in the middle
    arrow_text_bbox = draw.textbbox((0, 0), arrow_text, font=font)
    arrow_text_width, arrow_text_height = arrow_text_bbox[2] - arrow_text_bbox[0], arrow_text_bbox[3] - arrow_text_bbox[1]
    draw.text(((combined_width - arrow_text_width) / 2, text_height + (image1.height / 2) -15), arrow_text, fill="black", font=font)

    # Draw the arrow between the two images
    arrow_start_x = image1.width + 25 # Start position for the arrow (after the first image)
    arrow_end_x = arrow_start_x + arrow_width + 50  # End position for the arrow (width of the arrow area)
    arrow_y = text_height + (image1.height / 2)  # Vertical position of the arrow
    draw.line([arrow_start_x, arrow_y, arrow_end_x - 5, arrow_y], fill="black", width=4)
    draw.polygon([(arrow_end_x, arrow_y), (arrow_end_x - 5, arrow_y - 5), (arrow_end_x - 5, arrow_y + 5)], fill="black")

    # Paste the two images side by side with the arrow in the middle
    combined_image.paste(image1_filled, (0, text_height + 10))  # Add some padding after the title
    combined_image.paste(image2_filled, (image1.width + arrow_width + 100, text_height + 10))  # After the arrow


    # Save or show the result
    combined_image.save('./images/dsl_images/' + file_name_transformation + '.png')

    if show:
        combined_image.show()


def apply_transformation(grid, grid_name, transformation_name, terminal_visualize = True, image_visualize = True, show=True):

    
    # this dimensionality as input to the transformation only works when reasoning on the grid level. after, we would not be able to read the size from an object and have to pass it along another way

    grid_width, grid_height = np.shape(grid)


    # specify the context for the dsl. Within that context, get the functions.
    transformer = Transformer(color = 1, grid_width = grid_width, grid_height = grid_height)

    # Get the specific function we want
    transformation = getattr(transformer, transformation_name, None)


    formatted_grid = convert_grid_format(grid)


    transgrid = reconvert_grid_format(transformation(formatted_grid))


    if terminal_visualize:
        print('\n', 'Grid:\n', grid, '\n')
        print('\n', 'Transformed Grid:\n', transgrid)

    if image_visualize:
        visualize_transformation(grid, transgrid, transformation.__name__ , grid_name, show)

    return(transgrid)