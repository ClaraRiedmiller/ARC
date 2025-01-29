import arckit
import numpy as np
import json

# Imports from knowledge_graph
from knowledge_graph.create_kg import *
from knowledge_graph.kuzu_db_manager import KuzuDBManager
from knowledge_graph.get_similarity import *
from knowledge_graph.create_output import *

def main():
    train_set, eval_set = arckit.load_data()
    task = train_set[4]
    task.show()  # Just to visualize the puzzle

    db_manager = create_knowledge_graph(task)
    
    shared_properties = db_manager.get_shared_properties(example_id=1, batch_size=50)
    print("Total rows in shared_properties:", len(shared_properties))

    top_5_pairs = get_top_n_pairs_exact(
        shared_properties,
        n=5,
        similarity_threshold=0.1
    )
    print("\n=== Global Top-5 Pairs ===")
    for idx, pair_info in enumerate(top_5_pairs, start=1):
        print(f"{idx}. Input={pair_info['input_id']}  "
              f"Output={pair_info['output_id']}  "
              f"Similarity={pair_info['normalized_similarity']:.3f}")

    top_5_with_props = get_properties_for_exact_pairs(db_manager, top_5_pairs)
    print(f"\nWe have {len(top_5_with_props)} property rows for the top 5 matches.")

    pairs_top_5 = create_input_output_grid_pairs(
        input_grid_size=(30, 30),
        output_grid_size=(30, 30),
        pairs_info=top_5_with_props,
        max_pairs=5
    )

    # Print out how many we got
    print(f"\n--- Built {len(pairs_top_5)} (input, output) grids for global top-5 ---")

    one_to_one_results = optimal_one_to_one_assignment_with_valid_dummies(
        shared_properties,
        similarity_threshold=0.2
    )

    matched_pairs = [row for row in one_to_one_results if row['marker'] == 'matched']

    matched_props = get_properties_for_matched_pairs(db_manager, matched_pairs, batch_size=100)
    print(f"\nOne-to-one matched object count: {len(matched_props)}")

    # B4) Build up to 5 grid pairs for these matched objects
    one_to_one_grids = create_input_output_grid_pairs(
        input_grid_size=(30, 30),
        output_grid_size=(30, 30),
        pairs_info=matched_props,
        max_pairs=5
    )

    print(f"\n--- Built {len(one_to_one_grids)} (input, output) grids for one-to-one matches ---")

    for i, (inp_grid, out_grid) in enumerate(one_to_one_grids, start=1):
        print(f"\n--- One-to-One Match Pair #{i} ---")
        print("Input Grid:\n", inp_grid)
        print("Output Grid:\n", out_grid)
        if i >= 5:
            break  

if __name__ == "__main__":
    main()
