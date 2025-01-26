from knowledge_graph.kuzu_db_manager import KuzuDBManager
from knowledge_graph.create_obj import label_components, get_unique_labels
from knowledge_graph.create_obj_groups import to_hashable_shape, is_rotation
from knowledge_graph.create_obj_Rel import get_object_adjacency

from typing import List, Tuple, Optional
from arckit import Task

import matplotlib.pyplot as plt
import numpy as np
import networkx as nx

def create_knowledge_graph(task: Task) -> KuzuDBManager:
    """
    Creates a knowledge graph from the given task.
    
    Parameters:
    task (Task): A Task object containing training and test data.
    
    Returns:
    KuzuDBManager: An instance of KuzuDBManager with the knowledge graph.
    """
    db_manager = KuzuDBManager("kuzudb")
    db_manager.create_schema()
    kg_builder = KnowledgeGraphBuilder(db_manager)
    return kg_builder.build_knowledge_graph(task)

def visualize_knowledge_graph(db_manager: KuzuDBManager, plot_name: Optional[str] = None):
    nodes, edges = db_manager.get_graph()

    # Create a NetworkX directed graph
    graph = nx.DiGraph()  

    # Add nodes
    for _, node in nodes.iterrows():
        graph.add_node( node['n.id'], label=node['n.node_class'])
    # Add edges
    for _, edge in edges.iterrows():
        graph.add_edge(edge["src.id"], edge["dest.id"], label=edge['r.edge_class'])

    # Draw the graph
    pos = nx.spring_layout(graph)
    edge_labels=nx.get_edge_attributes(graph, "label")

    nx.draw(graph, 
            pos, 
            with_labels=True, 
            node_size=800, 
            font_size=10)

    nx.draw_networkx_edge_labels(graph, 
                                 pos, 
                                 edge_labels)
    
    if plot_name:
        plt.savefig("images/kg_plots/"+plot_name, dpi=300, bbox_inches="tight")
    # plt.show()

class KnowledgeGraphBuilder:
    def __init__(self, db_manager: KuzuDBManager):
        self.db_manager = db_manager

    def extract_objects(self, grid: np.ndarray, example_id: int) -> List[dict]:
        """
        Extracts object-level nodes from a grid.
        
        Parameters:
        grid (np.ndarray): A 2D numpy array representing the grid.
        
        Returns:
        List[dict]: A list of dictionaries representing the object-level nodes.
        """
        labeled_grid = label_components(grid)
        component_labels = get_unique_labels(labeled_grid)
        adjacency = get_object_adjacency(labeled_grid)

        nodes = []
        for label in component_labels:
            # Create a mask for the current label
            mask = (labeled_grid == label)
            
            # Find the bounding box coordinates
            bbox_x, bbox_y = np.where(mask)
            bbox_width = bbox_x.max() - bbox_x.min() + 1
            bbox_height = bbox_y.max() - bbox_y.min() + 1
            
            # Extract the subarray corresponding to the bounding box
            bbox = mask[bbox_x.min():bbox_x.max() + 1, bbox_y.min():bbox_y.max() + 1]
    
            # Convert to binary representation to represent shape
            binary_shape = bbox.astype(int)
            nodes.append({
                'id': int(label) + (10_000 * example_id),
                'example_id': example_id,
                'color': int(str(label)[0]),
                'shape': binary_shape,
                'bbox_x': int(bbox_x.min()),
                'bbox_y': int(bbox_y.min()),
                'bbox_width': int(bbox_width),
                'bbox_height': int(bbox_height),
                'adjacency' : list( int(neighbour) for neighbour in adjacency[label]),
            })
        return nodes
       
    def create_color_groups(self,  object_nodes: List[dict]) -> dict[set]:
        color_groups = {}
        for node in object_nodes:
            label = node['id']
            color = node['color']

            if color not in color_groups:
                color_groups[color] = set()
            color_groups[color].add(label)
        return list(list(group) for group in color_groups.values())
    
    def create_shape_groups(self, object_nodes: List[dict]) -> List[set]:
        shape_groups = {}
        for node in object_nodes:
            label = node['id']
            shape = node['shape']
            shape_key = to_hashable_shape(shape)
        
            if shape_key not in shape_groups:
                shape_groups[shape_key] = set()
            shape_groups[shape_key].add(label)
        
        return list(list(group) for group in shape_groups.values())
    
    def create_shape_color_groups(self, object_nodes: List[dict]) -> List[set]:
        shape_color_groups = {}
        for node in object_nodes:
            label = node['id']
            shape = node['shape']
            color = node['color']

            shape_key = to_hashable_shape(shape)
            group_key = (shape_key, color)

            if group_key not in shape_color_groups:
                shape_color_groups[group_key] = set()
            shape_color_groups[group_key].add(label)

        return list(list(group) for group in shape_color_groups.values())
    
    def create_rotation_groups(self, object_nodes: List[dict]) -> List[set]:
        visited = set()
        rotation_groups = dict()
        
        for node in object_nodes:
            label = node['id']
            shape = node['shape']
            
            if label in visited:
                continue
            else:
                visited.add(label)

                # Initialize a new group for shapes that rotate into this one
                rotation_set = {label}

                for other_node in object_nodes:
                    other_label = other_node['id']
                    other_shape = other_node['shape']

                    if other_label not in visited:
                        if is_rotation(shape, other_shape):
                            rotation_set.add(other_label)
                            visited.add(other_label)
                
                if len(rotation_set) >= 2:
                    rotation_groups[label] = list(rotation_set)
        
        return list(rotation_groups.values())

    def create_composite_objects_groups(self, object_nodes: List[dict]) -> List[set]:
        node_adjacency = {node['id']: node['adjacency'] for node in object_nodes}

        visited = set()
        composite_groups = {} 

        def dfs(start_label, component):
            stack = [start_label]
            while stack:
                label = stack.pop()
                for neighbor in node_adjacency[label]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        component.add(neighbor)
                        stack.append(neighbor)

        for label in sorted(node_adjacency.keys()):
            if label not in visited:
                visited.add(label)
                new_group = {label}
                dfs(label, new_group)
                composite_groups[label] = list(new_group)

        return list(composite_groups.values())

    def extract_groups(self, object_nodes: List[dict], example_id: int) -> Tuple[List[Tuple[int, int]], List[dict]]:
        """
        Extracts group-level nodes from a grid.
        
        Parameters:
        grid (np.ndarray): A 2D numpy array representing the grid.
        
        Returns:
        List[dict]: A list of dictionaries representing the group-level nodes.
        """

        color_groups = self.create_color_groups(object_nodes)
        shape_groups = self.create_shape_groups(object_nodes)
        shape_color_groups = self.create_shape_color_groups(object_nodes)
        rotation_groups = self.create_rotation_groups(object_nodes)
        composite_object_group = self.create_composite_objects_groups(object_nodes)

        groups_by_type = [('color', color_groups),
                  ('shape', shape_groups),
                  ('shape_color', shape_color_groups),
                  ('rotation', rotation_groups),
                  ('composite_object', composite_object_group)]
        
        nodes = []
        group_objects_mapping = []
        group_id = 1 + (10_000 * example_id)
        for group_type, groups in groups_by_type:
            for group in groups:
                nodes.append({
                    'id': group_id,
                    'example_id': example_id,
                    'type': group_type,
                    'size': len(group)
                })

                group_objects_mapping.append((group_id, group))

                group_id+=1

        return group_objects_mapping, nodes

    def build_knowledge_graph(self, task: Task) -> KuzuDBManager:
        """
        Creates a knowledge graph from the given task.
        
        Parameters:
        task (Task): A Task object containing training and test data.
        
        Returns:
        KuzuDBManager: An instance of KuzuDBManager with the knowledge graph.
        """
        for example_id, (input_grid, output_grid) in enumerate(task.train):
            # Increment to start example_id by 1
            example_id = example_id + 1 

            # Extract and insert object-level nodes
            input_objects = self.extract_objects(input_grid, example_id)
            output_objects = self.extract_objects(output_grid, example_id)
            for obj in input_objects:
                self.db_manager.insert_input_object(**obj)
            for obj in output_objects:
                self.db_manager.insert_output_object(**obj)

            # Create and insert group-level nodes
            input_group_object_mapping, input_groups = self.extract_groups(input_objects, example_id)
            output_group_object_mapping, output_groups = self.extract_groups(output_objects, example_id)
            for group in input_groups:
                self.db_manager.insert_input_group(**group)
            for group in output_groups:
                self.db_manager.insert_output_group(**group)

             # Insert contains relations
            for group_id, objects in input_group_object_mapping:
                for object_id in objects:
                    self.db_manager.insert_input_contains_relationship(group_id, object_id)
            
            for group_id, objects in output_group_object_mapping:
                for object_id in objects:
                    self.db_manager.insert_output_contains_relationship(group_id, object_id)

            # TODO: Extend to add task.test to the knowledge graph so we can make predictions
        return self.db_manager