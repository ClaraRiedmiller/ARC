import arckit
import csv
import numpy as np

from dsl import (
    DSL_COLOR_METHODS,
    DSL_GRID_MUTATION_METHODS,
    DSL_OBJECT_SHAPE_MUTATION_METHODS,
    DSL_OBJECT_MOVE_METHODS,
    flip_xax
)
from dsl.transformation import (
    remove_bg,
    convert_grid_format,
    add_bg,
    reconvert_grid_format,
)
from dsl.dsl import Constraints

from dsl.test_problems import get_problem_1, get_problem_3, get_problem_4

from kg_output import get_task_object_mappings

from search.breadth_fist_search import BreadthFirstSearch
from search.program_search_problem import goal_test
from knowledge_graph.get_similarity import get_most_similar_to_test
from knowledge_graph.create_output import create_isolated_object


def overlay_arrays(arrays):
    """Overlay multiple NumPy arrays such that the most recent non-zero integer value is retained."""
    if not arrays:
        return None
    
    # Stack arrays along a new axis
    stacked = np.stack(arrays)
    
    # Create a mask of nonzero values
    mask = stacked != 0
    
    # Use np.where to get the last nonzero value, keeping zeros where no nonzero values exist
    result = np.where(mask.any(axis=0), np.max(stacked * mask, axis=0), 0)
    
    return result


def run_object_level_prediction(task, dsl_fmt_task):
    db_manager, object_mappings = get_task_object_mappings(task)
    object_mappings = {mapping["input_id"]: mapping for mapping in object_mappings}
    test_object_properties = db_manager.get_test_properties()
    # Get top 5 most similar to test
    most_sim = get_most_similar_to_test(db_manager)

    # Get number 1 most similar to test
    obj = {}
    for i, pair_dict in enumerate(most_sim):
        test_output_obj_id = pair_dict["output_id"]
        sim_score = pair_dict["normalized_similarity"]
        if test_output_obj_id not in obj:
            obj[test_output_obj_id] = (sim_score, i)
        else:
            current_best_sim_score, _ = obj[test_output_obj_id]
            if current_best_sim_score < sim_score:
                obj[test_output_obj_id] = (sim_score, i)

    top_1_similar = []
    for _, index in obj.values():
        top_1_similar.append(most_sim[index])

    prediction_panes = []
    # Get grids for training_input, training_output and test_output
    for pair_dict in top_1_similar:
        # GET TRAINING PAIR
        train_input_obj_id = pair_dict["input_id"]
        train_output_obj_id = object_mappings[train_input_obj_id]["output_id"]

        train_input_properties = object_mappings[train_input_obj_id]["input_properties"]
        train_output_properties = object_mappings[train_input_obj_id][
            "output_properties"
        ]

        train_input_example_id = int(str(train_input_obj_id)[0])
        train_output_example_id = int(str(train_output_obj_id)[0])
        assert train_input_example_id == train_output_example_id, (
            "Input/output similarity pairs are expected to be from the same examples"
        )

        dim_train_input = tuple(np.shape(task.train[train_input_example_id][0]))
        dim_train_output = tuple(np.shape(task.train[train_output_example_id][1]))

        train_input_object_img = create_isolated_object(
            grid_size=dim_train_input, prop_dict=train_input_properties
        )
        train_output_object_img = create_isolated_object(
            grid_size=dim_train_output, prop_dict=train_output_properties
        )

        # RUN SEARCH FOR PROGRAM
        problem = [
            (
                convert_grid_format(remove_bg(train_input_object_img)),
                convert_grid_format(remove_bg(train_output_object_img)),
                Constraints(
                    color=train_output_properties["color"],
                    grid_width=train_input_object_img.shape[1],
                    grid_height=train_input_object_img.shape[0],
                ),
            )
        ]
        operators = (
            DSL_OBJECT_MOVE_METHODS
            + DSL_OBJECT_SHAPE_MUTATION_METHODS
            + DSL_COLOR_METHODS
        )

        bfs = BreadthFirstSearch(
            problem=problem, goal_test=goal_test, operators=operators, max_depth=5
        )
        program = bfs.search()

        if program:
            # GET TEST
            test_input_obj_id = pair_dict["output_id"]
            test_input_properties = test_object_properties[test_input_obj_id]
            test_id = 0  # TODO: fix so that this can handle more than one test
            dim_test_input = tuple(np.shape(task.test[test_id][0]))

            test_input_object = create_isolated_object(
                grid_size=dim_test_input, prop_dict=test_input_properties
            )

            # APPLY PROGRAM
            prediction_panes.append(
                run_program(
                    test_input=(
                        convert_grid_format(remove_bg(test_input_object)),
                        Constraints(
                            color=train_output_properties["color"],
                            grid_width=test_input_object.shape[1], # @Natasha I just had to change this to the test input dimensions instead of the training :) Turns out, one of the object was most similar to one that was in a bigger grid
                            grid_height=test_input_object.shape[0],
                        ),
                    ),
                    program=program,
                )
            )

    if prediction_panes:
        print(prediction_panes)
        return overlay_arrays(prediction_panes)

    return None


def run_grid_level_prediction(task):
    # Try search for programs only on the grid level

    problem = task["train"]  # initial_state, goal_state, constraints
    operators = DSL_COLOR_METHODS + DSL_GRID_MUTATION_METHODS
    bfs = BreadthFirstSearch(
        problem=problem, goal_test=goal_test, operators=operators, max_depth=4
    )
    return bfs.search()


def run_program(test_input, program):
    test_output, constraints = test_input
    for operation in program: #@Natasha this applies the wrong program to the objects (should be exactly switched). After some digging, this seems to be not wrong indexing but a kg issue - the closest object is just not of the same color. Maybe we could just value color stronger in the similarity so that it always wins and we have one working testcase. Or I manipulate the problem until it works
        test_output = operation(constraints, test_output)
        print(operation)
        print(test_output)
    return add_bg(reconvert_grid_format(test_output,  grid_width = constraints.grid_width, grid_height = constraints.grid_height))


def format_task(task):
    fmt_task = {
        "train": [
            (
                convert_grid_format(remove_bg(input_img)),
                convert_grid_format(remove_bg(output_img)),
                Constraints(
                    color=1,  # TODO: make random
                    grid_width=input_img.shape[1],
                    grid_height=input_img.shape[0],
                ),
            )
            for input_img, output_img in task.train
        ],
        "test": [
            (
                convert_grid_format(remove_bg(input_img)),
                Constraints(
                    color=1,  # TODO: make random
                    grid_width=input_img.shape[1],
                    grid_height=input_img.shape[0],
                ),
            )
            for input_img, _ in task.test
        ],
    }
    return fmt_task


def predict_output(task):
    dsl_fmt_task = format_task(task)
    output = []

    output = run_object_level_prediction(task, dsl_fmt_task)

    print(output)

    if output.any():
        return output
    else:
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


    if not predictions.any():  # If no solution: return shark picture
        fail_pred = [
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

        predictions = [fail_pred for _ in task.test]

    # flatten prediction
    flattened_pred = flatten_prediction(predictions.tolist())

    # for i, pred in enumerate(predictions):
    #         flat_pred = flatten_prediction(predictions[i])
    #         writer.writerow([f"{task_id}_{i}", flat_pred + " " + flat_pred])


    # since right now, we are only making one guess, we just repeat it twice to fill up our guesses (checking correctness does not take long). Further, we ignore tasks with two training inputs so we just output the prediction for the first twice.
    with open("submission.csv", "a") as submission:
        writer = csv.writer(submission, quoting=csv.QUOTE_NONE)

        if len(task.test) == 2:
            writer.writerow([f'{task_id}_0', flattened_pred + ' ' + flattened_pred])
            writer.writerow([f'{task_id}_1', flattened_pred + ' ' + flattened_pred])
        else:
            print(len(task.test))
            writer.writerow([f'{task_id}_0', flattened_pred + ' ' + flattened_pred])



def training_run():
    train_set, _ = arckit.load_data()

    with open("submission.csv", "w") as submission:
        writer = csv.writer(submission, quoting=csv.QUOTE_NONE)
        writer.writerow(["output_id", "output"])

    for task in train_set:
        task = get_problem_4()
        predictions = predict_output(task)
        submit_task(task, predictions)
        break
    # TODO: evaluate with arc kit


def evaluation_run():
    _, eval_set = arckit.load_data()

    with open("submission.csv", "w") as submission:
        writer = csv.writer(submission, quoting=csv.QUOTE_NONE)
        writer.writerow(["output_id", "output"])

    for task in eval_set:
        predictions = predict_output(task)
        submit_task(task, predictions)

    score = eval_set.score_submission(
        "submission.csv",  # Submission with two columns output_id,output in Kaggle fomrat
        topn=2,  # How many predictions to consider (default: 3)
        return_correct=True,  # Whether to return a list of which tasks were solved
    )

    print("Score:" + str(score))


training_run()
