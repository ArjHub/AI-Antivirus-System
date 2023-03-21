import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import utils.utils as utils
data_parmas = utils.config_parse('MALBINIMG_DATASET')   

root_dir = data_parmas['root_dir']
annotation_path = os.path.join('./annotation.txt')
label_map_path = os.path.join('./label_map.txt')

label_map = {}
images = []

with open(annotation_path, 'w') as f_annotation, open(label_map_path, 'w') as f_label_map:
    for label_index, class_name in enumerate(os.listdir(root_dir)):
        print(label_index)
        class_dir = os.path.join(root_dir, class_name)
        if not os.path.isdir(class_dir):
            continue
        label_map[label_index] = class_name
        for filename in os.listdir(class_dir):
            image_path = os.path.join(class_dir, filename)
            images.append((image_path, label_index))
            full_path = os.path.abspath(image_path)
            f_annotation.write(f'{full_path} {label_index}\n')

    for label_number, label_word in label_map.items():
        f_label_map.write(f'{label_number} {label_word}\n')
