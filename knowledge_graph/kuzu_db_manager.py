import kuzu
import numpy as np
import json


class KuzuDBManager:
    def __init__(self, db_path=''):
        self.db_path = db_path
        self.db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(self.db)

        # Configure DB to allow for JSON storage type
        self.conn.execute('INSTALL json;')
        self.conn.execute('LOAD EXTENSION json;')

    def __enter__(self):
        # Return the instance when entering the context
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the connection or clean up resources
        if self.conn:
            self.conn.close()
        if self.db:
            del self.db  # Free up database resources if needed

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
            "shape": self.serialize_shape(shape),  # Serialize as JSON
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

    def get_shared_properties(self, example_id=None, batch_size=100):
        
        # Base query with dynamic filtering by example_id
        query = f"""
        MATCH (i:input_object), (o:output_object)
        WHERE i.example_id = o.example_id {f"AND i.example_id = $example_id" if example_id is not None else ""}
        RETURN 
            i.id AS input_id, 
            o.id AS output_id,
            (CASE WHEN i.color = o.color THEN 1 ELSE 0 END +
            CASE WHEN i.bbox_x = o.bbox_x THEN 1 ELSE 0 END +
            CASE WHEN i.bbox_y = o.bbox_y THEN 1 ELSE 0 END +
            CASE WHEN i.bbox_width = o.bbox_width THEN 1 ELSE 0 END +
            CASE WHEN i.bbox_height = o.bbox_height THEN 1 ELSE 0 END +
            CASE WHEN i.shape = o.shape THEN 1 ELSE 0 END) AS num_matching_properties,
            [
                CASE WHEN i.color = o.color THEN 'color' ELSE NULL END,
                CASE WHEN i.bbox_x = o.bbox_x THEN 'bbox_x' ELSE NULL END,
                CASE WHEN i.bbox_y = o.bbox_y THEN 'bbox_y' ELSE NULL END,
                CASE WHEN i.bbox_width = o.bbox_width THEN 'bbox_width' ELSE NULL END,
                CASE WHEN i.bbox_height = o.bbox_height THEN 'bbox_height' ELSE NULL END,
                CASE WHEN i.shape = o.shape THEN 'shape' ELSE NULL END
            ] AS matching_properties,
            (CASE WHEN i.color = o.color THEN 5 ELSE 0 END +
            CASE WHEN i.bbox_x = o.bbox_x THEN 5 ELSE 0 END +
            CASE WHEN i.bbox_y = o.bbox_y THEN 5 ELSE 0 END +
            CASE WHEN i.bbox_width = o.bbox_width THEN 2.5 ELSE 0 END +
            CASE WHEN i.bbox_height = o.bbox_height THEN 2.5 ELSE 0 END +
            CASE WHEN i.shape = o.shape THEN 5 ELSE 0 END) * 1.0 / 25 AS normalized_similarity
        """
        # !!!! We want to check whether we should combine bbox_width and bbox_height !!!!

        # Parameters for filtering by example_id
        parameters = {"example_id": example_id} if example_id is not None else {}

        # Result storage
        matches = []
        try:
            # Execute the query
            result = self.conn.execute(query, parameters=parameters)
            batch = []
            while result.has_next():
                row = result.get_next()

                # Adjust based on `row` structure
                if isinstance(row, (list, tuple)):
                    # Access values positionally
                    input_id, output_id, num_matching_properties, matching_properties, normalized_similarity = row
                    matching_properties = [prop for prop in matching_properties if prop is not None]
                elif isinstance(row, dict):
                    # Access values using keys
                    input_id = row["input_id"]
                    output_id = row["output_id"]
                    num_matching_properties = row["num_matching_properties"]
                    matching_properties = [prop for prop in row["matching_properties"] if prop is not None]
                    normalized_similarity = row["normalized_similarity"]
                else:
                    raise ValueError("Unexpected row format returned from query.")

                # Add processed result to the batch
                batch.append({
                    "input_id": input_id,
                    "output_id": output_id,
                    "num_matching_properties": num_matching_properties,
                    "matching_properties": matching_properties,
                    "normalized_similarity": normalized_similarity
                })

                # If batch size is reached, process and reset the batch
                if len(batch) >= batch_size:
                    matches.extend(batch)
                    batch = []

            # Add remaining rows
            matches.extend(batch)
        
        except Exception as e:
            print(f"Error during query execution: {e}")

        return matches

    def shared_properties_across_input(self, example_id_1, example_id_2, batch_size=100):
        query = f"""
        MATCH (i:input_object), (j:input_object)
        WHERE i.example_id <> j.example_id {f"AND i.example_id = $example_id_1" if example_id_1 else ""} {f"AND j.example_id = $example_id_2" if example_id_2 else ""}
        RETURN 
            i.id AS input_i_id, 
            j.id AS input_j_id,
            (CASE WHEN i.color = j.color THEN 1 ELSE 0 END +
            CASE WHEN i.bbox_x = j.bbox_x THEN 1 ELSE 0 END +
            CASE WHEN i.bbox_y = j.bbox_y THEN 1 ELSE 0 END +
            CASE WHEN i.bbox_width = j.bbox_width THEN 1 ELSE 0 END +
            CASE WHEN i.bbox_height = j.bbox_height THEN 1 ELSE 0 END +
            CASE WHEN i.shape = j.shape THEN 1 ELSE 0 END) AS num_matching_properties,
            [
                CASE WHEN i.color = j.color THEN 'color' ELSE NULL END,
                CASE WHEN i.bbox_x = j.bbox_x THEN 'bbox_x' ELSE NULL END,
                CASE WHEN i.bbox_y = j.bbox_y THEN 'bbox_y' ELSE NULL END,
                CASE WHEN i.bbox_width = j.bbox_width THEN 'bbox_width' ELSE NULL END,
                CASE WHEN i.bbox_height = j.bbox_height THEN 'bbox_height' ELSE NULL END,
                CASE WHEN i.shape = j.shape THEN 'shape' ELSE NULL END
            ] AS matching_properties,
            (CASE WHEN i.color = j.color THEN 5 ELSE 0 END +
            CASE WHEN i.bbox_x = j.bbox_x THEN 5 ELSE 0 END +
            CASE WHEN i.bbox_y = j.bbox_y THEN 5 ELSE 0 END +
            CASE WHEN i.bbox_width = j.bbox_width THEN 2.5 ELSE 0 END +
            CASE WHEN i.bbox_height = j.bbox_height THEN 2.5 ELSE 0 END +
            CASE WHEN i.shape = j.shape THEN 5 ELSE 0 END) * 1.0 / 25 AS normalized_similarity
        """
        parameters = {}
        if example_id_1 is not None:
            parameters["example_id_1"] = example_id_1
        if example_id_2 is not None:
            parameters["example_id_2"] = example_id_2

        # Result storage
        matches = []
        try:
            # Execute the query
            result = self.conn.execute(query, parameters=parameters)
            batch = []
            while result.has_next():
                row = result.get_next()

                # Adjust based on `row` structure
                if isinstance(row, (list, tuple)):
                    # Access values positionally
                    input_i_id, input_j_id, num_matching_properties, matching_properties, normalized_similarity = row
                    matching_properties = [prop for prop in matching_properties if prop is not None]
                elif isinstance(row, dict):
                    # Access values using keys
                    input_i_id = row["input_i_id"]
                    output_i_id = row["input_j_id"]
                    num_matching_properties = row["num_matching_properties"]
                    matching_properties = [prop for prop in row["matching_properties"] if prop is not None]
                    normalized_similarity = row["normalized_similarity"]
                else:
                    raise ValueError("Unexpected row format returned from query.")

                # Add processed result to the batch
                batch.append({
                    "input_i_id": input_id,
                    "input_j_id": output_id,
                    "num_matching_properties": num_matching_properties,
                    "matching_properties": matching_properties,
                    "normalized_similarity": normalized_similarity
                })

                # If batch size is reached, process and reset the batch
                if len(batch) >= batch_size:
                    matches.extend(batch)
                    batch = []

            # Add remaining rows
            matches.extend(batch)
        
        except Exception as e:
            print(f"Error during query execution: {e}")

        return matches




