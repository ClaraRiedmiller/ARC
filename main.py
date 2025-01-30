import arckit
import csv

from dsl import DSL_COLOR_METHODS, DSL_GRID_MUTATION_METHODS
from dsl.transformation import remove_bg, convert_grid_format
from dsl.dsl import Constraints

from kg_output import get_task_object_mappings

from search.breadth_fist_search import BreadthFirstSearch
from search.best_first_search import BestFirstSearch
from search.program_search_problem import goal_test, heuristic, expand

# from knowledge_graph.get_similarity import


def run_object_level_prediction(task):
    object_mappings = [
        (remove_bg(input_obj), remove_bg(output_obj))
        for input_obj, output_obj in get_task_object_mappings(task)
    ]
    print(len(object_mappings))
    # TODO: finish logic
    return None


def run_grid_level_prediction(task):
    # Try search for programs only on the grid level
    operators = DSL_COLOR_METHODS + DSL_COLOR_METHODS
    bfs = BreadthFirstSearch(
        problem=task, goal_test=goal_test, operators=operators, max_depth=1
    )
    return bfs.search()


def format_task(task):
    fmt_task = {
        "train": [
            (
                convert_grid_format(remove_bg(input_img)),
                convert_grid_format(remove_bg(output_img)),
                Constraints(  # TODO: ask if this need to be over written for the other search
                    color=1,  # TODO: make random
                    grid_width=input_img.shape[1],
                    grid_height=input_img.shape[0],
                ),
            )
            for input_img, output_img in task.train
        ],
        "test": [convert_grid_format(remove_bg(test)) for test in task.test],
    }
    return fmt_task


def predict_program(task):
    fmt_task = format_task(task)
    if program := run_grid_level_prediction(fmt_task):
        return program
    if program := run_object_level_prediction(fmt_task):
        return program  # TODO decide on this output
    return None


def run_program(test_input, program):
    # TODO: ask about what is the constraints object here
    return


def run_task(task):
    program = predict_program(task)
    if program:
        output = []
        for test_input in task.test:
            output_image = run_program(test_input, program)
            output.append(output_image)
        return output
    return None


# array flattener from kaggle to put the output in the correct format as required by the arckit evaluator
def flatten_prediction(prediction):
    str_pred = str([row for row in prediction])
    str_pred = str_pred.replace(", ", "")
    str_pred = str_pred.replace("[[", "|")
    str_pred = str_pred.replace("][", "|")
    str_pred = str_pred.replace("]]", "|")
    return str_pred


def submit_task(task, predictions):
    task_id = task.id

    # TODO transform predictions from np.arrays to list format
    if not predictions:  # If no solution: return shark picture
        predictions = [
            [
                [0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 1, 1, 1, 1, 0, 0],
                [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
                [0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
                [0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
                [0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            ]
        ]

    with open("submission.csv", "a") as submission:
        writer = csv.writer(submission, quoting=csv.QUOTE_NONE)
        for i, pred in enumerate(predictions):
            flat_pred = flatten_prediction(predictions[i])
            writer.writerow([f"{task_id}_{i}", flat_pred + " " + flat_pred])


def training_run():
    train_set, _ = arckit.load_data()

    for task in train_set:
        predictions = run_task(task)
        break
        submit_task(task, predictions)
    # TODO: evaluate with arc kit


def evaluation_run():
    _, eval_set = arckit.load_data()

    for task in eval_set:
        predictions = run_task(task)
        submit_task(task, predictions)

    eval_set.score_submission(
        "submission.csv",  # Submission with two columns output_id,output in Kaggle fomrat
        topn=2,  # How many predictions to consider (default: 3)
        return_correct=True,  # Whether to return a list of which tasks were solved
    )
    return


training_run()
