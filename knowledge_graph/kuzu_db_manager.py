import kuzu
import numpy as np
import json


class KuzuDBManager:
    def __init__(self, db_path=''):
       self.db_path = db_path
       self.db = kuzu.Database(db_path)
       self.conn = kuzu.Connection(self.db)

       # Configure DB to allow for json storage type
       self.conn.execute('INSTALL json;')
       self.conn.execute('LOAD EXTENSION json;')

    def create_schema(self):
        
       # Create the object node tables
        self.conn.execute('''CREATE NODE TABLE input_object(
                                   node_class STRING,
                                   id INT32 PRIMARY KEY,
                                   example_id INT32,
                                   color INT32, 
                                   shape JSON, 
                                   bbox_x INT32,
                                   bbox_y INT32,
                                   bbox_width INT32,
                                   bbox_height INT32,
                                   adjacency INT64[]
                             );
                             ''')
       
        self.conn.execute('''CREATE NODE TABLE output_object(
                                   node_class STRING,
                                   id INT32 PRIMARY KEY,
                                   example_id INT32,
                                   color INT32, 
                                   shape JSON, 
                                   bbox_x INT32,
                                   bbox_y INT32,
                                   bbox_width INT32,
                                   bbox_height INT32,
                                   adjacency INT64[]
                             );
                             ''')  #TODO: extend to include things like is_rotation_invariant
        # Group level
        self.conn.execute('''CREATE NODE TABLE input_group(
                                    node_class STRING,
                                    id INT32 PRIMARY KEY,
                                    example_id INT32,                         
                                    type STRING, 
                                    size INT 
                            );
                            ''')
                     
        self.conn.execute('''CREATE NODE TABLE output_group(
                                    node_class STRING,
                                    id INT32 PRIMARY KEY,
                                    example_id INT32,
                                    type STRING, 
                                    size INT
                            );
                            ''')
                     
        # Create the relationship tables

        self.conn.execute('CREATE REL TABLE input_contains(FROM input_group TO input_object, edge_class STRING);')
        self.conn.execute('CREATE REL TABLE output_contains(FROM output_group TO output_object, edge_class STRING);')

    def deserialize_shape(self, shape_json):
        return np.array(json.loads(shape_json))
    
    def serialize_shape(self, shape_array):
        return json.dumps(shape_array.tolist())
    
    def insert_object(self, table_name, id, example_id, color, shape, bbox_x, bbox_y, bbox_width, bbox_height, adjacency):

        query = f"""
        CREATE (n:{table_name} {{
            node_class: '{table_name}',
            id: $id,
            example_id: $example_id,
            color: $color,
            shape: $shape,
            bbox_x: $bbox_x,
            bbox_y: $bbox_y,
            bbox_width: $bbox_width,
            bbox_height: $bbox_height,
            adjacency: $adjacency
        }})
        """
    
        # Create the parameter dictionary
        parameters = {
            "id": id,
            "example_id": example_id,
            "color": color,
           # "shape": self.serialize_shape(shape),  # Serialize as JSON
            "bbox_x": bbox_x,
            "bbox_y": bbox_y,
            "bbox_width": bbox_width,
            "bbox_height": bbox_height, 
            "adjacency": adjacency
        }
   
        # Execute the query
        self.conn.execute(query, parameters=parameters)
   
    def insert_input_object(self, id, example_id, color, shape, bbox_x, bbox_y, bbox_width, bbox_height, adjacency):
        self.insert_object('input_object', id, example_id, color, shape, bbox_x, bbox_y, bbox_width, bbox_height, adjacency)

    def insert_output_object(self, id, example_id, color, shape, bbox_x, bbox_y, bbox_width, bbox_height, adjacency):
        self.insert_object('output_object', id, example_id, color, shape, bbox_x, bbox_y, bbox_width, bbox_height, adjacency)

    def insert_group(self, table_name, id, example_id,  type, size):
        # Define the query
        query = f"""
        CREATE (n:{table_name} {{
            node_class: '{table_name}',
            id: $id,
            example_id : $example_id,
            type: $type,
            size: $size
        }})
        """
        
        # Create the parameter dictionary
        parameters = {
            "id": id,
            "example_id": example_id,
            "type": type,
            "size": size,
        }

        # Execute the query
        self.conn.execute(query, parameters=parameters)

    def insert_input_group(self, id, example_id, type, size):
        self.insert_group('input_group', id, example_id, type, size)
    
    def insert_output_group(self, id, example_id, type, size):
        self.insert_group('output_group', id, example_id, type, size)
    
    def insert_relationship(self, table_name, group_id , group_type, object_id, object_type):
        # Define the query with escaped curly braces
        query = f"""
        MATCH (g:{group_type}), (o:{object_type})
        WHERE g.id = $group_id AND o.id = $object_id
        CREATE (g)-[:{table_name} {{edge_class: '{table_name}'}}]->(o)
        """
        
        # Create the parameter dictionary
        parameters = {
            "group_id": group_id,
            "object_id": object_id,
        }
        # Execute the query
        self.conn.execute(query, parameters=parameters)

    def insert_input_contains_relationship(self, group_id, object_id):
        self.insert_relationship(table_name='input_contains',group_id=group_id, group_type='input_group',object_id=object_id,object_type='input_object')

    def insert_output_contains_relationship(self, group_id, object_id):
        self.insert_relationship(table_name='output_contains',group_id=group_id, group_type='output_group',object_id=object_id,object_type='output_object')

    def get_graph(self):
        nodes = self.conn.execute("MATCH (n) RETURN DISTINCT n.id, n.node_class")
        edges = self.conn.execute("MATCH (src)-[r]->(dest) RETURN DISTINCT src.id, r.edge_class, dest.id")
        return nodes.get_as_df(), edges.get_as_df()
