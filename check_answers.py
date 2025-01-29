from questions_DSL import *
from knowledge_graph.create_kg import *
from knowledge_graph.kuzu_db_manager import *
from knowledge_graph.get_similarity import *
from knowledge_graph.utils import remove_folder_if_exists

import arckit

train_set, eval_set = arckit.load_data()
task = train_set[4]
task.show()
db_manager = create_knowledge_graph(task)

print(questions(task,db_manager,1))