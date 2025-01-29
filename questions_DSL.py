def questions(task, db_manager, ex):
    answers = []
    #check if grid is changed, just on task

    props = db_manager.get_shared_properties(example_id=ex, batch_size=100)
            
            # Do matching on the properties and take the first five objects
    top_5_pairs = get_top_n_pairs_exact(
        props,
        n=5,
        similarity_threshold=0.1
    )
    first_five_props = get_properties_for_exact_pairs(db_manager, top_5_pairs)
    j = 0
    while j < 5:
        obj_pair = first_five_props[j]
        object_1 = obj_pair["input_id"]
        object_2 = obj_pair["output_id"]

        changes = {}
        # check if object is scaled 
        shape_1 = object_1.get('shape')
        shape_2 = object_2.get('shape')
        if is_same_shape(shape_1, shape_2): 
            changes["shape"] = "No"
        elif is_scaled_quadratic(shape_1,shape_2): 
            changes["shape"] = "Scaled x2"
        elif is_scaled_quadratic_inverse(shape_1, shape_2):
            changes["shape"] = "Scaled x0.5"
        elif is_flip(shape_1, shape_2): 
            changes["shape"] = "Flip"
        elif is_rotation(shape_1, shape_2):
            changes["shape"] = "Rotation"
        else: 
            changes["shape"] = "Not Detected"

#check if object is moved 
        x_coordinate_1 = object_1.get("bbox_x")
        x_coordinate_2 = object_2.get("bbox_x")
        if x_coordinate_1 == x_coordinate_2:
            changes["bbox_x"] = "No changes"
        elif x_coordinate_1 > x_coordinate_2:
            changes["bbox_x"] = str(x_coordinate_1 - x_coordinate_2) + " left"
        else: 
            changes["bbox_x"] = str(x_coordinate_2 - x_coordinate_1) + " right"
        y_coordinate_1 = object_1.get("bbox_y")
        y_coordinate_2 = object_2.get("bbox_y")
        if y_coordinate_1 == y_coordinate_2:
            changes["bbox_y"] = "No changes"
        elif y_coordinate_1 > y_coordinate_2:
            changes["bbox_y"] = str(y_coordinate_1 - y_coordinate_2) + " down"
        else: 
            changes["bbox_y"] = str(y_coordinate_2 - y_coordinate_1) + " up"
        #check if object changes color
        color_1 =  object_1.get('color')
        color_2 = object_2.get('color')
        if color_1 == color_2:
            changes["color"] = "No"
        else:
            changes["color"] = "Yes"
        
        answers.append(changes)
        j = j+1 
    grid_input = np.shape(task.train[ex][0])
    grid_output = np.shape(task.train[ex][1])
    grid = {}
    if grid_input == grid_output:
        grid["size"] = "unchanged"
    else: grid["size"] = "changed"
    #check if rows are added/deleted
    if grid_input(0) > grid_output(0):
        grid["height_change"] = str(grid_input[0] - grid_output[0]) + " rows deleted"
    else: 
        grid["height_change"] = str(grid_output[0] - grid_input[0]) + " rows added"
    #check if columns are added/deleted
    if grid_input(1) > grid_output(1):
        grid["width_change"] = str(grid_input[1] - grid_output[1]) + " columns deleted"
    else: 
        grid["width_change"] = str(grid_output[1] - grid_input[1]) + " columns added"
    answers.append(grid)

    return answers

def majority_answers(answers, first_five_props):
    if not answers:
        return {"uniform": {}, "majority": {}, "grid_info": {}}
    
    keys = answers[0].keys()
    uniform = {}
    majority = {}
    grid_values = {"size": [], "height_change": [], "width_change": []}
    
    for key in keys:
        values = [ans[key] for ans in answers if key in ans]
        value_counts = Counter(values)
        most_common_value, most_common_count = value_counts.most_common(1)[0]
        
        if len(value_counts) == 1:
            uniform[key] = most_common_value
        else:
            occurrences = []
            for idx, ans in enumerate(answers):
                if key in ans and ans[key] == most_common_value:
                    input_id = first_five_props[idx]["input_id"]
                    output_id = first_five_props[idx]["output_id"]
                    occurrences.append({"input_id": input_id, "output_id": output_id})
            
            majority[key] = {
                "value": most_common_value,
                "occurrences": occurrences
            }
    
    # Process grid information separately
    for ans in answers:
        if "size" in ans:
            grid_values["size"].append(ans["size"])
        if "height_change" in ans:
            grid_values["height_change"].append(ans["height_change"])
        if "width_change" in ans:
            grid_values["width_change"].append(ans["width_change"])
    
    grid_info = {}
    
    # Compute majority for grid values
    for key, values in grid_values.items():
        if values:
            value_counts = Counter(values)
            most_common_value, most_common_count = value_counts.most_common(1)[0]
            grid_info[key] = most_common_value
    
    return {"uniform": uniform, "majority": majority, "grid_info": grid_info}



    
   






