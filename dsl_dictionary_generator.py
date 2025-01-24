import csv
import pprint

from dsl.transformation import apply_transformation
from dsl.dsl import *
from dsl.dsl_features import get_dsl_functions


def get_and_mod_dsl_dict():
    # get the dsl funcitons and their names
    dsl_functions = get_dsl_functions()

    # we add new fields to the dicitionary: # Fields to add with default value None
    new_fields = ['description', 'requires_grid_size', 'requires_color', 'grid_size_change', 'color_change', 'grid_level', 'object_level', 'additional_comments']

    # Add the new fields to each function
    for func_name, attributes in dsl_functions.items():
        for field in new_fields:
            attributes[field] = None

    return dsl_functions


def save_dict(dict):
    # Specify the CSV file name
    filename = './dsl/dsl_description.csv'

    # # Get the field names (keys of the inner dictionaries)
    # fieldnames = ['function_name'] + list(next(iter(dict.values())).keys())

    # Automatically extract all unique field names from the dictionary
    fieldnames = ['function_name'] + list(
        set(key for attributes in dict.values() for key in attributes.keys())
    )

    # Write the dictionary to the CSV file
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()

        # Write each function and its attributes
        for func_name, attributes in dict.items():
            row = {'function_name': func_name, **attributes}
            writer.writerow(row)



def main():

    dsl_functions = get_dsl_functions()

    # now, @Lorenz fill in the details of each. The entries should be the following:
    # ------------------------------
    # inputs:               [Auto generated] Input types of the fct
    # output:               [Auto generated] Return types of the fct
    # ------------------------------
    # description:          A short description of what the function does 
    # requires_grid_size    bool, does fct require grid size
    # requires_color       bool, does fct require color
    # grid_size_change      bool, can this fct change the grid size
    # color_change          bool, can this fct change color
    # grid_level:           bool, does this fct work on whole grids
    # object_level:         bool, does this fct work on single objects within grids (that are not the whole grid)
    # additional_comments:  any other relevant notes or comments about the function

    dsl_functions['function_name_here'] = {
        'inputs': ['input1', 'input2', 'input3'],  # List of required inputs (e.g., 'object', 'color', 'gridsize')
        'output': None,                           # Expected output type/structure (e.g., Tuple, Set, etc.)
        'description': None,                      # Short description of what the function does
        'grid_size_change': None,                 # Impact on grid size (e.g., 'increases by 1', 'no change')
        'requires_color': None,                   # True/False if the function depends on color
        'grid_level': None,                       # Specify grid level operation (e.g., 'affects entire grid')
        'object_level': None,                     # Specify object-level operation (e.g., 'adds a border to object')
        'additional_comments': None               # Any additional notes or comments about the function
    }


    save_dict(dsl_functions)

    pprint.pprint(dsl_functions)


main()