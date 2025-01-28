# this file contains funcitons that can extract information from our dsl (such as features of a function)

import csv
import pprint
import inspect

import dsl

def get_dsl_dict(excludeAuxiliary = True, excludeObjectOnly=False):

    result = {}
    with open('dsl/dsl_description.csv', mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')  
        for row in reader:
            key = row['function_name']
            subdict = {k: v for k, v in row.items() if k != 'function_name'}
            result[key] = subdict

    # exclude the auxiliary functions
    if excludeAuxiliary:
        result = {key: value for key, value in result.items() if value.get('DSL') == '1'}

    # exclude functions that only work on smaller objects, not the whole grid
    if excludeObjectOnly:
        result = {key: value for key, value in result.items() if value.get('grid_level') == '1'}   
    
    return result



def generate_new_dict():

    # This generates and empty dictionary where each row corresponds to one of the dsl functions. The features can then be filled in manually
    # ------------------------------
    # description:          A short description of what the function does 
    # requires_grid_size    bool, does fct require grid size
    # requires_color        bool, does fct require color
    # grid_size_change      bool, can this fct change the grid size
    # color_change          bool, can this fct change color
    # grid_level:           bool, does this fct work on whole grids
    # object_level:         bool, does this fct work on single objects within grids (that are not the whole grid)
    # additional_comments:  any other relevant notes or comments about the function


    # Create the funciton dictionary
    dsl_functions = {}
    for name, func in inspect.getmembers(dsl, inspect.isfunction):
        dsl_functions[name] = {                         
        'description' : None,                      
        'requires_grid_size' : None,               
        'requires_color': None,    
        'grid_size_change': None, 
        'color_change': None,                
        'grid_level': None,                      
        'object_level': None,                     
        'additional_comments': None
    }    

    return dsl_functions


def save_dict(dict):


    # Ask for confirmation before overwriting the file
    if confirm_overwrite():

        # Specify the CSV file name
        filename = './dsl/dsl_description_empty.csv'

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

        print('Your new dsl function descriptor looks like this:\n')
        pprint.pprint(dict)



def confirm_overwrite():
    
    while True:
        response = input("Are you sure you want to overwrite the dsl_description? [y/n]: ").strip().lower()
        if response in ['yes', 'y']:
            print('\nSuccessfully overwrote dsl description with empty table.\n')
            return True
        elif response in ['no', 'n']:
            print('\nNo changes have been made to your dsl description.\n')
            return False
        else:
            print("Invalid input. Please type 'yes' or 'no'.")