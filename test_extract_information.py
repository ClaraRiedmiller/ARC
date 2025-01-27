from knowledge_graph.create_kg import create_knowledge_graph, visualize_knowledge_graph


import arckit

train_set, eval_set = arckit.load_data()
task = train_set[4]
task.show()
db_manager = create_knowledge_graph(task)

# Get shared properties for a specific example_id
shared_properties = db_manager.get_shared_properties(example_id=1, batch_size=5)

sorted_properties = sorted(shared_properties, key=lambda x: x['normalized_similarity'], reverse=True)

# Print sorted results
for match in sorted_properties:
    print(match)