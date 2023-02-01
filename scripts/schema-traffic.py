from wa_infra_tools.database.PostgresDatabase import PostgresDatabase
import json
import os
import re
db = PostgresDatabase("sbradin", hostname = "tux-144.cae.wisc.edu")

images_front_path = "/Users/sambradin/Downloads/sweeps/CAM_FRONT"
bounding_box_path = "/Users/sambradin/Downloads/nuimages-v1.0-all-metadata/v1.0-train/object_ann.json"
file_name_path = "/Users/sambradin/Downloads/nuimages-v1.0-all-metadata/v1.0-train/sample_data.json"
category_path = "/Users/sambradin/Downloads/nuimages-v1.0-all-metadata/v1.0-train/category.json"

#all specific to the data set and this one has individual files
#bounding box coords and info are in the label
#download to own computer to analyze
#grab token from image, find category(category.json), and bbox(object_ann.json)

#1600x900
IMAGE_WIDTH = 1600# original: 1280
IMAGE_HEIGHT = 900# original: 720

with open(file_name_path) as f:
    labels = json.load(f)
with open(category_path) as f:
    categories = json.load(f)
with open(bounding_box_path) as f:
    bbs = json.load(f)
image_list = os.listdir(images_front_path)

for image in image_list:
    for label in labels:        
        if(label != None):
            if(label["filename"] == "sweeps/CAM_FRONT/" + image):
                token = label["token"]
                
                image_dict = {
                    "x_res": IMAGE_WIDTH,
                    "y_res": IMAGE_HEIGHT,
                    "filepath": "sweeps/CAM_FRONT/" + image
                }
                image_id = db.insert_row_with_image("images", image_dict)
    for box in bbs:
        if(box["token"] == token):
            cat_token = box["category_token"]
            box["bbox"]
            x_1 = box['bbox'][0]
            y_1 = box['bbox'][1]
            x_2 = box['bbox'][2]
            y_2 = box['bbox'][3]
        
            x_center_norm = (x_1 + x_2)/(2 * IMAGE_WIDTH)
            y_center_norm = (y_1 + y_2)/(2 * IMAGE_HEIGHT)
        
            width_norm = abs(x_2 - x_1)/IMAGE_WIDTH
            height_norm = abs(y_2 - y_1)/IMAGE_HEIGHT

    for tokens in categories:
        if(tokens["token"] == cat_token):
            class_id_map = {
                'human' : 0,
                'pedestrian' : 0,
                'vehicle' : 1,
                'moveable_object' : 4,
                'animal' : 5
            }
            if(re.findall(r"^(\w+)\.", tokens["name"])[0] not in class_id_map):
                continue
            category = re.findall(r"^(\w+)\.?", tokens["name"])[0]
            class_id = class_id_map[re.findall(r"^(\w+)\.?", tokens["name"])[0]]

    label_dict = {
        "class_id": class_id,
        "class": category,
        "center_norm_x": x_center_norm,
        "center_norm_y": y_center_norm,
        "width_norm": width_norm,
        "height_norm": height_norm,
        "image_id": image_id,
        "data_set" : "nuimages"
        }
    db.insert_row("bb_labels", label_dict)

db.commit()