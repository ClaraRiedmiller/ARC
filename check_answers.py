from questions_DSL import *
from knowledge_graph.create_kg import *
from knowledge_graph.kuzu_db_manager import *
from knowledge_graph.get_similarity import *
from knowledge_graph.utils import remove_folder_if_exists
from knowledge_graph.create_output import *


import arckit

train_set, eval_set = arckit.load_data()
task = train_set[4]
task.show()
db_manager = create_knowledge_graph(task)
props = db_manager.get_shared_properties(example_id=1, batch_size=100)
            
            # Do matching on the properties and take the first five objects
top_5_pairs = get_top_n_pairs_exact(
        props,
        n=5,
        similarity_threshold=0.1)
first_five_props = get_properties_for_exact_pairs(db_manager, top_5_pairs)
print(first_five_props)

print(questions(task,db_manager,1))
whatever = questions(task,db_manager,1)

print(majority_answers(whatever, db_manager ))