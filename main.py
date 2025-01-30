import arckit
import csv

from dsl import DSL_COLOR_METHODS, DSL_GRID_MUTATION_METHODS
from dsl.transformation import remove_bg, convert_grid_format
from dsl.dsl import Constraints

from dsl.test_problems import get_problem_3

from kg_output import get_task_object_mappings

from search.breadth_fist_search import BreadthFirstSearch
from search.best_first_search import BestFirstSearch
from search.program_search_problem import goal_test, heuristic, expand

from knowledge_graph.get_similarity import get_most_similar_to_test
from knowledge_graph.create_output import create_input_output_grid_pairs


def run_object_level_prediction(task, dsl_fmt_task):
    db_manager, object_mappings =  get_task_object_mappings(task)
    object_mappings = { mapping["input_id"]: mapping
        for mapping in object_mappings
    }

    # object_mappings = [
    #     (remove_bg(input_obj), remove_bg(output_obj))
    #     for input_obj, output_obj in object_mappings
    # ]
    
    most_sim = get_most_similar_to_test(db_manager)
    
    # Get number 1 most similar
    obj = {}
    for i, pair_dict in enumerate(most_sim):
        test_output_obj_id = pair_dict['output_id']
        sim_score = pair_dict['normalized_similarity']
        if test_output_obj_id not in obj:
            obj[test_output_obj_id] = (sim_score, i)
        else:
            current_best_sim_score, _ = obj[test_output_obj_id]
            if current_best_sim_score < sim_score:
                obj[test_output_obj_id] = (sim_score, i)
    
    top_1_similar = []
    for _, index in obj.values():
        top_1_similar.append(most_sim[index])
    
    for pair_dict in top_1_similar:
        input_obj_id = pair_dict['input_id']
        test_output_obj_id = pair_dict['output_id']
        matching_props = pair_dict['matching_properties']

        train_output_obj_id = object_mappings[input_obj_id]['output_id']
        print(input_obj_id, train_output_obj_id)
    #     input_obj = input_obj_id
    #    output_obj = 
    
    #     bfs = BreadthFirstSearch(

    #     )
    # TODO: finish logic
    return None


def run_grid_level_prediction(task):
    # Try search for programs only on the grid level

    problem =task['train'] #initial_state, goal_state, constraints
    operators = DSL_COLOR_METHODS + DSL_COLOR_METHODS
    bfs = BreadthFirstSearch(
        problem=problem, goal_test=goal_test, operators=operators, max_depth=4
    )
    return bfs.search()


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
        "test": [(convert_grid_format(remove_bg(t)), Constraints(
                    color=1,  # TODO: make random
                    grid_width=t.shape[1],
                    grid_height=t.shape[0],
                )) for test in task.test for t in test],
    }
    return fmt_task


def run_grid_level_program(test_input, program):
    test_output, constraints = test_input
    for operation in program:
        test_output = operation(constraints,test_output)
    # TODO: ask about what is the constraints object here
    return test_output


def predict_output(task):
    dsl_fmt_task = format_task(task)
    output = []

    if program := run_grid_level_prediction(dsl_fmt_task):
        for test_input in task.test:
            output_image = run_grid_level_program(test_input, program)
            output.append(output_image)
        return output
    # if program := run_object_level_prediction(task, dsl_fmt_task):
    #     return output  # TODO decide on this output
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


    with open("submission.csv", "a") as submission:
        writer = csv.writer(submission, quoting=csv.QUOTE_NONE)
        for i, pred in enumerate(predictions):
            flat_pred = flatten_prediction(predictions[i])
            writer.writerow([f"{task_id}_{i}", flat_pred + " " + flat_pred])


def training_run():
    train_set, _ = arckit.load_data()

    
    for task in train_set:
        task = get_problem_3()
        predictions = predict_output(task)
        submit_task(task, predictions)
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
        return_correct=False,  # Whether to return a list of which tasks were solved
    )
    print("Score:"+str(score))


evaluation_run()
