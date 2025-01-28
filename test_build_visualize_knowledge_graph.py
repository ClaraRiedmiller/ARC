from knowledge_graph.create_kg import create_knowledge_graph, visualize_knowledge_graph

import arckit

train_set, eval_set = arckit.load_data()
task = train_set[4]
task.show()
db_manager = create_knowledge_graph(task)

# visualize_knowledge_graph(db_manager, 'test.png')


