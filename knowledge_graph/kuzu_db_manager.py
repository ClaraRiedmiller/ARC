import kuzu
import numpy as np
from typing import List, Tuple, Optional, Dict, Set

class KuzuDBManager:
    def __init__(self, db_path=''):
        self.db_path = db_path
        self.db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(self.db)

    def __enter__(self):
        # Return the instance when entering the context
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the connection or clean up resources
        if self.conn:
            self.conn.close()
        if self.db:
            self.db.close()
        del self

    def create_schema(self):
        
       # Create the object node tables
        self.conn.execute('''CREATE NODE TABLE input_object(
                                   node_class STRING,
                                   id INT32 PRIMARY KEY,
                                   example_id INT32,
                                   color INT32, 
                                   shape INT64[][], 
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
                                   shape INT64[][], 
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

    def deserialize_shape(self, shape_list):
        return np.array(shape_list)
    
    def serialize_shape(self, shape_array):
        return shape_array.tolist()
    
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
            "shape": self.serialize_shape(shape),  
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

    def shared_properties_across_input(self, example_id_1=None, example_id_2=None, batch_size=100):
        """
        Compare input objects from two different example_ids 
        (or all if None) and return their matching properties & similarity.
        """
        # 1) Build query with optional parameters
        query = f"""
        MATCH (i:input_object), (j:input_object)
        WHERE i.example_id <> j.example_id
            {f"AND i.example_id = $example_id_1" if example_id_1 else ""}
            {f"AND j.example_id = $example_id_2" if example_id_2 else ""}
        RETURN 
            i.id AS input_i_id, 
            j.id AS input_j_id,
            (
                CASE WHEN i.color = j.color THEN 1 ELSE 0 END +
                CASE WHEN i.bbox_x = j.bbox_x THEN 1 ELSE 0 END +
                CASE WHEN i.bbox_y = j.bbox_y THEN 1 ELSE 0 END +
                CASE WHEN i.bbox_width = j.bbox_width THEN 1 ELSE 0 END +
                CASE WHEN i.bbox_height = j.bbox_height THEN 1 ELSE 0 END +
                CASE WHEN i.shape = j.shape THEN 1 ELSE 0 END
            ) AS num_matching_properties,
            [
                CASE WHEN i.color = j.color THEN 'color' ELSE NULL END,
                CASE WHEN i.bbox_x = j.bbox_x THEN 'bbox_x' ELSE NULL END,
                CASE WHEN i.bbox_y = j.bbox_y THEN 'bbox_y' ELSE NULL END,
                CASE WHEN i.bbox_width = j.bbox_width THEN 'bbox_width' ELSE NULL END,
                CASE WHEN i.bbox_height = j.bbox_height THEN 'bbox_height' ELSE NULL END,
                CASE WHEN i.shape = j.shape THEN 'shape' ELSE NULL END
            ] AS matching_properties,
            (
                CASE WHEN i.color = j.color THEN 5 ELSE 0 END +
                CASE WHEN i.bbox_x = j.bbox_x THEN 5 ELSE 0 END +
                CASE WHEN i.bbox_y = j.bbox_y THEN 5 ELSE 0 END +
                CASE WHEN i.bbox_width = j.bbox_width THEN 2.5 ELSE 0 END +
                CASE WHEN i.bbox_height = j.bbox_height THEN 2.5 ELSE 0 END +
                CASE WHEN i.shape = j.shape THEN 5 ELSE 0 END
            ) * 1.0 / 25 AS normalized_similarity
        """
        parameters = {}
        if example_id_1 is not None:
            parameters["example_id_1"] = example_id_1
        if example_id_2 is not None:
            parameters["example_id_2"] = example_id_2

        matches = []
        try:
            result = self.conn.execute(query, parameters=parameters)
            batch = []
            while result.has_next():
                row = result.get_next()

                if isinstance(row, (list, tuple)):
                    # Access values positionally
                    (input_i_id, 
                    input_j_id, 
                    num_matching_properties, 
                    matching_props, 
                    normalized_similarity) = row
                elif isinstance(row, dict):
                    # Access values by keys
                    input_i_id           = row["input_i_id"]
                    input_j_id           = row["input_j_id"]
                    num_matching_properties = row["num_matching_properties"]
                    matching_props       = row["matching_properties"]
                    normalized_similarity = row["normalized_similarity"]
                else:
                    raise ValueError("Unexpected row format returned from query.")

                # Filter out None from matching_props
                matching_props = [prop for prop in matching_props if prop is not None]

                # Add processed result
                batch.append({
                    "input_i_id": input_i_id,
                    "input_j_id": input_j_id,
                    "num_matching_properties": num_matching_properties,
                    "matching_properties": matching_props,
                    "normalized_similarity": normalized_similarity
                })

                if len(batch) >= batch_size:
                    matches.extend(batch)
                    batch = []

            matches.extend(batch)
        except Exception as e:
            print(f"Error during query execution: {e}")

        return matches

    
    def task_not_solvable(self):
    # Initialize counters
        unmatched_counter = 0
        many_objects_counter = 0
        
        # check for unmatched objects and too many matched objects
        for i in range(1, 4):  # Loop over 3, 2, 1
            # Obtain properties
            props = self.get_shared_properties(example_id=i, batch_size=100)
            
            # Do matching on the properties
            matchings = optimal_one_to_one_assignment_with_valid_dummies(props)
            
            # Count unmatched and matched objects
            unmatched_count = sum(1 for item in matchings if item['marker'] == 'unmatched')
            matched_count = sum(1 for item in matchings if item['marker'] == 'matched')
            
            if unmatched_count > 0:
                unmatched_counter += 1
            if matched_count > 5:
                many_objects_counter += 1

        # If the majority of the examples have unmatched objects, disregard task
        if unmatched_counter > 1:
            return "Task not solvable, non-trackable objects appear"
        # If the majority of the examples have too many objects, disregard task
        elif many_objects_counter > 1:
            return "Task not solvable, too many objects"

        #check for low similarity on the top 5 objects
        low_similarity_counter = 0
        for j in range(1, 4):  # Loop over 3, 2, 1
            # Obtain properties
            props = self.get_shared_properties(example_id=j, batch_size=100)
            
            # Do matching on the properties and take the first five objects
            matchings = optimal_one_to_one_assignment_with_valid_dummies(props)
            
            sorted_matchings = sorted(my_list, key=lambda x: x['similarity'])

            first_five = sorted_matchings[:5]
            # Count how many objects have a low similarity score
            low_similarity_count = sum(1 for item in first_five if item['similarity'] < 0.2)
            
            # If all top 5 objects have a low similarity count
            if low_similarity_count >= 5:
                low_similarity_counter += 1

        # If the majority of examples have low similarity between input and output, disregard task
        if low_similarity_counter > 1:
            return "Task not solvable, output cannot be tracked from input"
        else:
            return "We can attempt to solve this task!"

    def get_group_features(self, example_id: int, group_id: int) -> Dict:
        """
        Retrieves features of a specific group from the knowledge graph.
        """
        query = f"""
        MATCH (g:input_group {{id: {group_id}, example_id: {example_id}}})-[:CONTAINS]->(o:input_object)
        RETURN 
            g.id AS group_id,
            g.type AS group_type,
            g.size AS group_size,
            collect(o.color) AS colors,
            collect(o.shape) AS shapes,
            collect(o.bbox_x) AS bbox_xs,
            collect(o.bbox_y) AS bbox_ys
        """
        result = self.db_manager.conn.execute(query)
        if not result.has_next():
            return {}
        
        row = result.get_next()
        if isinstance(row, (list, tuple)):
            (group_id, group_type, group_size, colors, shapes, bbox_xs, bbox_ys) = row
        elif isinstance(row, dict):
            group_id = row["group_id"]
            group_type = row["group_type"]
            group_size = row["group_size"]
            colors = row["colors"]
            shapes = row["shapes"]
            bbox_xs = row["bbox_xs"]
            bbox_ys = row["bbox_ys"]
        else:
            raise ValueError("Unexpected row format returned from query.")

        return {
            "group_id": group_id,
            "group_type": group_type,
            "group_size": group_size,
            "colors": colors,
            "shapes": shapes,
            "bbox_xs": bbox_xs,
            "bbox_ys": bbox_ys
        }

    def compare_groups_between_examples(self, example_id_1: int, example_id_2: int) -> Dict:
        """
        Compares groups between two examples and identifies relationships based on group features.
        """
        # Step 1: Retrieve all groups for both examples
        query = f"""
        MATCH (g:input_group)
        WHERE g.example_id = {example_id_1} OR g.example_id = {example_id_2}
        RETURN g.id AS group_id, g.example_id AS example_id, g.type AS group_type, g.size AS group_size
        """
        result = self.db_manager.conn.execute(query)
        groups_example_1 = []
        groups_example_2 = []

        while result.has_next():
            row = result.get_next()
            if isinstance(row, (list, tuple)):
                group_id, example_id, group_type, group_size = row
            elif isinstance(row, dict):
                group_id = row["group_id"]
                example_id = row["example_id"]
                group_type = row["group_type"]
                group_size = row["group_size"]
            else:
                raise ValueError("Unexpected row format returned from query.")

            group_info = {
                "group_id": group_id,
                "group_type": group_type,
                "group_size": group_size,
                "features": self.get_group_features(example_id, group_id)
            }

            if example_id == example_id_1:
                groups_example_1.append(group_info)
            else:
                groups_example_2.append(group_info)

        # Step 2: Compare groups based on desired features
        relations = {
            "color_group_matches": [],
            "shape_group_matches": [],
            "shape_color_group_matches": [],
            "rotation_group_matches": [],
            "composite_adjacency_group_matches": []
        }

        # A) Color Group Matches
        color_groups_1 = {}
        color_groups_2 = {}
        for group in groups_example_1:
            if group["group_type"] == "color":
                color = group["features"]["colors"][0] if group["features"]["colors"] else None
                if color is not None:
                    color_groups_1.setdefault(color, []).append(group)
        for group in groups_example_2:
            if group["group_type"] == "color":
                color = group["features"]["colors"][0] if group["features"]["colors"] else None
                if color is not None:
                    color_groups_2.setdefault(color, []).append(group)
        
        for color, groups1 in color_groups_1.items():
            groups2 = color_groups_2.get(color, [])
            for g1 in groups1:
                for g2 in groups2:
                    relations["color_group_matches"].append({
                        "color": color,
                        "group1_id": g1["group_id"],
                        "group2_id": g2["group_id"],
                        "group1_size": g1["group_size"],
                        "group2_size": g2["group_size"],
                        "similar_size": g1["group_size"] == g2["group_size"]
                    })

        # B) Shape Group Matches
        shape_groups_1 = {}
        shape_groups_2 = {}
        for group in groups_example_1:
            if group["group_type"] == "shape":
                shape_key = tuple(tuple(row) for row in group["features"]["shapes"][0]) if group["features"]["shapes"] else None
                if shape_key is not None:
                    shape_groups_1.setdefault(shape_key, []).append(group)
        for group in groups_example_2:
            if group["group_type"] == "shape":
                shape_key = tuple(tuple(row) for row in group["features"]["shapes"][0]) if group["features"]["shapes"] else None
                if shape_key is not None:
                    shape_groups_2.setdefault(shape_key, []).append(group)
        
        for shape_key, groups1 in shape_groups_1.items():
            groups2 = shape_groups_2.get(shape_key, [])
            for g1 in groups1:
                for g2 in groups2:
                    relations["shape_group_matches"].append({
                        "shape_key": shape_key,
                        "group1_id": g1["group_id"],
                        "group2_id": g2["group_id"],
                        "group1_size": g1["group_size"],
                        "group2_size": g2["group_size"],
                        "similar_size": g1["group_size"] == g2["group_size"]
                    })

        # C) Shape+Color Group Matches
        shape_color_groups_1 = {}
        shape_color_groups_2 = {}
        for group in groups_example_1:
            if group["group_type"] == "shape_color":
                shapes = group["features"]["shapes"]
                color = group["features"]["colors"][0] if group["features"]["colors"] else None
                shape_key = tuple(tuple(row) for row in shapes[0]) if shapes else None
                if shape_key is not None and color is not None:
                    shape_color_groups_1.setdefault((shape_key, color), []).append(group)
        for group in groups_example_2:
            if group["group_type"] == "shape_color":
                shapes = group["features"]["shapes"]
                color = group["features"]["colors"][0] if group["features"]["colors"] else None
                shape_key = tuple(tuple(row) for row in shapes[0]) if shapes else None
                if shape_key is not None and color is not None:
                    shape_color_groups_2.setdefault((shape_key, color), []).append(group)
        
        for key, groups1 in shape_color_groups_1.items():
            groups2 = shape_color_groups_2.get(key, [])
            for g1 in groups1:
                for g2 in groups2:
                    relations["shape_color_group_matches"].append({
                        "shape_key": key[0],
                        "color": key[1],
                        "group1_id": g1["group_id"],
                        "group2_id": g2["group_id"],
                        "similar_size": g1["group_size"] == g2["group_size"]
                    })

        # D) Rotation Group Matches
        # For simplicity, we'll match rotation groups based on group type and size
        rotation_groups_1 = [g for g in groups_example_1 if g["group_type"] == "rotation"]
        rotation_groups_2 = [g for g in groups_example_2 if g["group_type"] == "rotation"]

        for g1 in rotation_groups_1:
            for g2 in rotation_groups_2:
                if g1["group_size"] == g2["group_size"]:
                    relations["rotation_group_matches"].append({
                        "group1_id": g1["group_id"],
                        "group2_id": g2["group_id"],
                        "group1_size": g1["group_size"],
                        "group2_size": g2["group_size"],
                        "match_reason": "same_size_rotation_group"
                    })

        # E) Composite Adjacency Group Matches
        composite_groups_1 = [g for g in groups_example_1 if g["group_type"] == "composite_object"]
        composite_groups_2 = [g for g in groups_example_2 if g["group_type"] == "composite_object"]

        for g1 in composite_groups_1:
            for g2 in composite_groups_2:
                if g1["group_size"] == g2["group_size"]:
                    relations["composite_adjacency_group_matches"].append({
                        "group1_id": g1["group_id"],
                        "group2_id": g2["group_id"],
                        "group1_size": g1["group_size"],
                        "group2_size": g2["group_size"],
                        "match_reason": "same_size_composite_group"
                    })

        return relations

    def identify_similar_group_transformations(self, example_id_1: int, example_id_2: int) -> Dict:
        """
        Identifies objects that are in groups undergoing similar transformations between two examples.
        """
        # Step 1: Compare groups between examples
        group_relations = self.compare_groups_between_examples(example_id_1, example_id_2)

        # Step 2: For each type of group match, identify object-level correspondences
        similar_objects = {
            "color_group_similar_objects": [],
            "shape_group_similar_objects": [],
            "shape_color_group_similar_objects": [],
            "rotation_group_similar_objects": [],
            "composite_adjacency_group_similar_objects": []
        }

        # A) Color Group Similar Objects
        for match in group_relations["color_group_matches"]:
            group1_id = match["group1_id"]
            group2_id = match["group2_id"]

            # Fetch objects in both groups
            objects1 = self.get_objects_in_group(example_id_1, group1_id)
            objects2 = self.get_objects_in_group(example_id_2, group2_id)

            similar_objects["color_group_similar_objects"].append({
                "group1_id": group1_id,
                "group2_id": group2_id,
                "objects1": objects1,
                "objects2": objects2
            })

        # B) Shape Group Similar Objects
        for match in group_relations["shape_group_matches"]:
            group1_id = match["group1_id"]
            group2_id = match["group2_id"]

            objects1 = self.get_objects_in_group(example_id_1, group1_id)
            objects2 = self.get_objects_in_group(example_id_2, group2_id)

            similar_objects["shape_group_similar_objects"].append({
                "group1_id": group1_id,
                "group2_id": group2_id,
                "objects1": objects1,
                "objects2": objects2
            })

        # C) Shape+Color Group Similar Objects
        for match in group_relations["shape_color_group_matches"]:
            group1_id = match["group1_id"]
            group2_id = match["group2_id"]

            objects1 = self.get_objects_in_group(example_id_1, group1_id)
            objects2 = self.get_objects_in_group(example_id_2, group2_id)

            similar_objects["shape_color_group_similar_objects"].append({
                "group1_id": group1_id,
                "group2_id": group2_id,
                "objects1": objects1,
                "objects2": objects2
            })

        # D) Rotation Group Similar Objects
        for match in group_relations["rotation_group_matches"]:
            group1_id = match["group1_id"]
            group2_id = match["group2_id"]

            objects1 = self.get_objects_in_group(example_id_1, group1_id)
            objects2 = self.get_objects_in_group(example_id_2, group2_id)

            similar_objects["rotation_group_similar_objects"].append({
                "group1_id": group1_id,
                "group2_id": group2_id,
                "objects1": objects1,
                "objects2": objects2
            })

        # E) Composite Adjacency Group Similar Objects
        for match in group_relations["composite_adjacency_group_matches"]:
            group1_id = match["group1_id"]
            group2_id = match["group2_id"]

            objects1 = self.get_objects_in_group(example_id_1, group1_id)
            objects2 = self.get_objects_in_group(example_id_2, group2_id)

            similar_objects["composite_adjacency_group_similar_objects"].append({
                "group1_id": group1_id,
                "group2_id": group2_id,
                "objects1": objects1,
                "objects2": objects2
            })

        return similar_objects

    def get_objects_in_group(self, example_id: int, group_id: int) -> List[int]:
        """
        Retrieves object IDs contained within a specific group.
        """
        query = f"""
        MATCH (g:input_group {{id: {group_id}, example_id: {example_id}}})-[:CONTAINS]->(o:input_object)
        RETURN o.id AS object_id
        """
        result = self.db_manager.conn.execute(query)
        objects = []
        while result.has_next():
            row = result.get_next()
            if isinstance(row, (list, tuple)):
                (object_id,) = row
            elif isinstance(row, dict):
                object_id = row["object_id"]
            else:
                raise ValueError("Unexpected row format returned from query.")
            objects.append(object_id)
        return objects

