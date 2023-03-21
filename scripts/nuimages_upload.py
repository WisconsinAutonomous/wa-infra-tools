from wa_infra_tools.database.PostgresDatabase import PostgresDatabase
import json
import os
import re
import pandas as pd
db = PostgresDatabase("sbradin", hostname = "tux-144.cae.wisc.edu")

images_front_path = "/Users/sambradin/Downloads/samples/CAM_FRONT"
bounding_box_path = "/Users/sambradin/Downloads/nuimages-v1.0-all-metadata/v1.0-train/object_ann.json"
file_name_path = "/Users/sambradin/Downloads/nuimages-v1.0-all-metadata/v1.0-train/sample_data.json"
category_path = "/Users/sambradin/Downloads/nuimages-v1.0-all-metadata/v1.0-train/category.json"

#1600x900
IMAGE_WIDTH = 1600
IMAGE_HEIGHT = 900

with open(file_name_path) as f:
    labels = json.load(f)
    labels_dict = {label['filename']: label for label in labels}
with open(category_path) as f:
    categories = json.load(f)
    cat_dict = {cat['token']: cat for cat in categories}
with open(bounding_box_path) as f:
    bbs = json.load(f)
    bb_dict =  {bb['sample_data_token']: bb for bb in bbs}
image_list = os.listdir(images_front_path)

total = len(image_list)

grouped_bounding_boxes = {}
for bounding_box in bbs:
    id_val = bounding_box["sample_data_token"]
    if(id_val not in grouped_bounding_boxes):
        grouped_bounding_boxes[id_val] = []
    grouped_bounding_boxes[id_val].append(bounding_box)


df = pd.DataFrame()
class_id = "not found"
category = "not found"
x_center_norm = "not found"
y_center_norm = "not found"
width_norm = "not found"
height_norm = "not found"
image_id = "not found"

for image in image_list:
    if(labels_dict.get("samples/CAM_FRONT/" + image) != None):
        token = labels_dict.get("samples/CAM_FRONT/" + image)["token"]
            
        image_dict = {
            "x_res": IMAGE_WIDTH,
            "y_res": IMAGE_HEIGHT,
            "filepath": "/Users/sambradin/Downloads/samples/CAM_FRONT/" + image
            
        }
            
        image_id = db.insert_row_with_image("images", image_dict)
        if(token in grouped_bounding_boxes):
            for box in grouped_bounding_boxes[token]:
                #multiple bounding boxes per image so need to iterate
                if(box["sample_data_token"] == token):
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
                   
                    if(cat_dict.get(cat_token) != None):
                       
                        class_id_map = {
                            'human' : 0,
                            'pedestrian' : 0,
                            'vehicle' : 1,
                            'movable_object' : 4,
                            'animal' : 5
                        }
                       

                        if(re.findall(r"^(\w+)\.?", cat_dict.get(cat_token)["name"])[0] not in class_id_map):
                            continue
                        category = re.findall(r"^(\w+)\.?", cat_dict.get(cat_token)["name"])[0]
                        class_id = class_id_map[re.findall(r"^(\w+)\.?", cat_dict.get(cat_token)["name"])[0]]
                

                label_dict = {
                    "class_id": class_id,
                    "class": category,
                    "center_norm_x": x_center_norm,
                    "center_norm_y": y_center_norm,
                    "width_norm": width_norm,
                    "height_norm": height_norm,
                    "image_id": image_id,
                    "dataset" : "nuimages"
                    }
                db.insert_row("bb_labels", label_dict)
    
db.commit()