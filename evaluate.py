# this file evaluates our performance

import arckit
import numpy as np
import csv


# generate our solutions: iterate over the evaluation set and produce an output in a kaggle format for every test.

# array flattener from kaggle to put the output in the correct format
def flattener(pred):
    str_pred = str([row for row in pred])
    str_pred = str_pred.replace(', ', '')
    str_pred = str_pred.replace('[[', '|')
    str_pred = str_pred.replace('][', '|')
    str_pred = str_pred.replace(']]', '|')
    return str_pred




# get example grid so we can test our transformations
train_set, eval_set = arckit.load_data()

# iterate over the problems
for problem in eval_set:
    # pred = solve(problem)
    pred = [[1],[2]]

    flattened_pred = flattener(pred)

    

    

    # # depending on whether one or two test cases
    # with open('submission.csv','a') as fd:
    #     if len(problem.test) == 2:
    #         fd.write(f'{problem.id}_0'+ flattened_pred + ' ' + flattened_pred)
    #         fd.write(f'{problem.id}_1'+ flattened_pred + ' ' + flattened_pred)
    #     else:
    #         print(len(problem.test))
    #         fd.write(f'{problem.id}_0'+ flattened_pred + ' ' + flattened_pred)


    with open('submission.csv','a') as sbm:
        writer = csv.writer(sbm)

        if len(problem.test) == 2:
            writer.writerow([f'{problem.id}_0,'+ flattened_pred + ' ' + flattened_pred])
            writer.writerow([f'{problem.id}_1,'+ flattened_pred + ' ' + flattened_pred])
        else:
            print(len(problem.test))
            writer.writerow([f'{problem.id}_0,'+ flattened_pred + ' ' + flattened_pred])

    
        # writer.writerow(line)





# eval_set.score_submission(
#     'submission.csv', # Submission with two columns output_id,output in Kaggle fomrat
#     topn=2,           # How many predictions to consider (default: 3)
#     return_correct=False # Whether to return a list of which tasks were solved
#     )