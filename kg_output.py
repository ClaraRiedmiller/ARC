import arckit
import numpy as np
import json

# Imports from knowledge_graph
from knowledge_graph.create_kg import *
from knowledge_graph.kuzu_db_manager import KuzuDBManager
from knowledge_graph.get_similarity import *
from knowledge_graph.create_output import *



def get_example_object_mappings(task, db_manager, example_id):


    
    shared_properties = db_manager.get_shared_properties(example_id=example_id +1, batch_size=50) #@Paul @Lucrezia: Did you start counting the examples from one instead of 0? it looks like it
    print("Total rows in shared_properties:", len(shared_properties))


    # get the dimensions of the input and output array
    training_examples = task.train
    dim_input = tuple(np.shape(training_examples[example_id][0]))
    dim_output = tuple(np.shape(training_examples[example_id][1]))


    top_5_pairs = get_top_n_pairs_exact(
        shared_properties,
        n=5,
        similarity_threshold=0.1
    )
    # print("\n=== Global Top-5 Pairs ===")
    # for idx, pair_info in enumerate(top_5_pairs, start=1):
    #     print(f"{idx}. Input={pair_info['input_id']}  "
    #           f"Output={pair_info['output_id']}  "
    #           f"Similarity={pair_info['normalized_similarity']:.3f}")

    top_5_with_props = get_properties_for_exact_pairs(db_manager, top_5_pairs)
    # print(f"\nWe have {len(top_5_with_props)} property rows for the top 5 matches.")

    pairs_top_5 = create_input_output_grid_pairs(
        input_grid_size=dim_input,
        output_grid_size=dim_output,
        pairs_info=top_5_with_props,
        max_pairs=5
    )

    # # Print out how many we got
    # print(f"\n--- Built {len(pairs_top_5)} (input, output) grids for global top-5 ---")

    # print(pairs_top_5)


    #Now, we implement the one-to-one matches

    one_to_one_results = optimal_one_to_one_assignment_with_valid_dummies(
        shared_properties,
        similarity_threshold=0.2
    )

    matched_pairs = [row for row in one_to_one_results if row['marker'] == 'matched']

    matched_props = get_properties_for_matched_pairs(db_manager, matched_pairs, batch_size=100)
    # print(f"\nOne-to-one matched object count: {len(matched_props)}")

    # B4) Build up to 5 grid pairs for these matched objects
    one_to_one_grids = create_input_output_grid_pairs(
        input_grid_size=dim_input,
        output_grid_size=dim_output,
        pairs_info=matched_props,
        max_pairs=5
    )

    print('\nmappigs of one exmaple:\n', pairs_top_5)
    return(one_to_one_grids)


def get_task_object_mappings(task):

    # create the kg
    db_manager = create_knowledge_graph(task)

    # collect the mappings in this list
    task_object_mappings = []

    # iterate over the trainnig examples and see which program produces the correct output
    for no, ex in enumerate(task.train):
        print('example number: ', no)
        example_object_mappings = get_example_object_mappings(task=task, db_manager=db_manager, example_id=no)
        task_object_mappings.append(example_object_mappings)

    return(task_object_mappings)




    

    # print(f"\n--- Built {len(one_to_one_grids)} (input, output) grids for one-to-one matches ---")

    # for i, (inp_grid, out_grid) in enumerate(one_to_one_grids, start=1):
    #     print(f"\n--- One-to-One Match Pair #{i} ---")
    #     print("Input Grid:\n", inp_grid)
    #     print("Output Grid:\n", out_grid)
    #     if i >= 5:
    #         break  

# if __name__ == "__main__":
#     main()
