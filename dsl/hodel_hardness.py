# in this file, we create a dictionary with name and number of lines of code needed to solve of training problems hodel hand-coded the solution to. This refers to his specific dsl. We consider solutions up to  6 lines of code to solve. 


def get_hodel_hardness():

    with open ("./dsl/hodel_solvers.txt", "r") as myfile:
        hodel_string =  myfile.read()



    # split string into single methods and remove first empty line 
    single_methods = hodel_string.split('def ')
    del single_methods[0]



    # save the problem names, along with the number of lines of code they need to be solved as a dictionary
    problem_hardness = {}

    # generate dictionary that for every problem (indexed by name) specifies the number of code lines for the solution
    for substring in single_methods:

        # count the number of lines in each substring, remove the ones that are empty. remove excess lines (2)
        empty_lines = len([line for line in substring.splitlines() if len(line.strip()) == 0])
        num_lines = len(substring.splitlines()) - empty_lines - 2


        # save these values in a dictionary
        problem_hardness[substring[6:14]] = num_lines

    return problem_hardness



def upper_bound_hardness(upper_bound):

    problem_hardness = get_hodel_hardness() 

    upper_bounded_list = []

    for problem, lines in problem_hardness.items():
        if lines <= upper_bound:
            upper_bounded_list.append(f"{problem}: {lines}")
    
    return(upper_bounded_list)
            