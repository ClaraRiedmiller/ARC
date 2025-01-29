def questions(task, db_manager, i):
    answers = []
    #check if grid is changed, just on task


    props = db_manager.get_shared_properties(example_id=i, batch_size=100)
            
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
            changes[shape] = "No"
        elif is_scaled_quadratic(shape_1,shape_2): 
            changes[shape] = "Scaled x2"
        elif is_scaled_quadratic_inverse(shape_1, shape_2):
            changes[shape] = "Scaled x0.5"
        else: 
            changes[shape] = None

#check if object is moved 
        x_coordinate_1 = object_1.get("bbox_x")
        x_coordinate_2 = object_2.get("bbox_x")
        if x_coordinate_1 == x_coordinate_2:
            changes[x_coordinate] = "No changes"
        elif x_coordinate_1 > x_coordinate_2:
            changes[x_coordinate] = str(x_coordinate_1 - x_coordinate_2) + " left"
        else: 
            changes[x_coordinate] = str(x_coordinate_2 - x_coordinate_1) + " right"
        y_coordinate_1 = object_1.get("bbox_y")
        y_coordinate_2 = object_2.get("bbox_y")
        if y_coordinate_1 == y_coordinate_2:
            changes[x_coordinate] = "No changes"
        elif y_coordinate_1 > y_coordinate_2:
            changes[y_coordinate] = str(y_coordinate_1 - y_coordinate_2) + " down"
        else: 
            changes[x_coordinate] = str(y_coordinate_2 - y_coordinate_1) + " up"
        #check if object changes color
        color_1 =  object_1.get('color')
        color_2 = object_2.get('color')
        if color_1 == color_2:
            changes[color] = "No"
        else:
            changes[color] = "Yes"
        
        answers.append(changes)
        j = j+1 

    return answers

def majority_changes(task, db_manager):
    majority_answers = []
    while i < 4: 
        majority_answers.append(questions(task, db_manager, i))
        i = i+1
    
    #check what is the majority change 
    






