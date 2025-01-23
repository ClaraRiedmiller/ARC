import kuzu
import numpy as np
import json


class KuzuDBManager:
    def __init__(self, db_path=''):
       self.db_path = db_path
       self.db = kuzu.Database(db_path)
       self.conn = self.db.connect()

    def create_schema(self):
        
       # Create the object node tables
        self.conn.execute('''CREATE NODE TABLE input_object(
                                   id INTEGER PRIMARY KEY,
                                   example_id INTEGER,
                                   colour INTEGER, 
                                   shape JSON, 
                                   bbox_x INTEGER,
                                   bbox_y INTEGER,
                                   bbox_width INTEGER,
                                   bbox_height INTEGER,
                                   is_rotation_invariant BOOLEAN
                             );
                             ''')
       
        self.conn.execute('''CREATE NODE TABLE output_object(
                                   id INTEGER PRIMARY KEY,
                                   example_id INTEGER,
                                   colour INTEGER, 
                                   shape JSON, 
                                   bbox_x INTEGER,
                                   bbox_y INTEGER,
                                   bbox_width INTEGER,
                                   bbox_height INTEGER,
                                   is_rotation_invariant BOOLEAN,
                             );
                             ''')
       # Group level

        self.conn.execute('''CREATE NODE TABLE input_group(
                                   id INTEGER PRIMARY KEY,
                                   example_id INTEGER,                         
                                   group_type STRING, 
                                   group_size JSON, 
                                   avg_colour INTEGER
                            );
                            ''')
                     
        self.conn.execute('''CREATE NODE TABLE output_group(
                                   id INTEGER PRIMARY KEY,
                                   example_id INTEGER,
                                   group_type STRING, 
                                   group_size JSON, 
                                   avg_colour INTEGER,
                            );
                            ''')
                     
        # Create the relationship tables

        self.conn.execute('CREATE REL TABLE input_contains(from_id INTEGER, to_id INTEGER, FROM input_group, TO input_object);')
        self.conn.execute('CREATE REL TABLE output_contains(from_id INTEGER, to_id INTEGER, FROM output_group, TO output_object);')

    def commit(self):
        self.db.commit()

    def deserialize_shape(self, shape_json):
        return np.array(json.loads(shape_json))
    
    def serialize_shape(self, shape_array):
        return json.dumps(shape_array.tolist())
    
    def insert_input_object(self, id, colour, shape_array, bbox_x, bbox_y, bbox_width, bbox_height, is_rotation_invariant):
        shape_json = self.serialize_shape(shape_array)
        self.conn.execute('''
        INSERT INTO input_object (id, colour, shape, bbox_x, bbox_y, bbox_width, bbox_height, is_rotation_invariant)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (id, colour, shape_json, bbox_x, bbox_y, bbox_width, bbox_height, is_rotation_invariant))

    def insert_output_object(self, id, colour, shape_array, bbox_x, bbox_y, bbox_width, bbox_height, is_rotation_invariant):
        shape_json = self.serialize_shape(shape_array)
        self.conn.execute('''
        INSERT INTO output_object (id, colour, shape, bbox_x, bbox_y, bbox_width, bbox_height, is_rotation_invariant)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (id, colour, shape_json, bbox_x, bbox_y, bbox_width, bbox_height, is_rotation_invariant))

    def insert_input_group(self, id, group_type, group_size, avg_colour):
        self.conn.execute('''
        INSERT INTO input_group (id, group_type, group_size, avg_colour)
        VALUES (?, ?, ?, ?);
        ''', (id, group_type, json.dumps(group_size), avg_colour))

    def insert_output_group(self, id, group_type, group_size, avg_colour):
        self.conn.execute('''
        INSERT INTO output_group (id, group_type, group_size, avg_colour)
        VALUES (?, ?, ?, ?);
        ''', (id, group_type, json.dumps(group_size), avg_colour))

    def create_relationship(self, table, from_id, to_id):
        self.conn.execute(f'INSERT INTO {table} (from_id, to_id) VALUES (?, ?);', (from_id, to_id))

