import json
import os

def convert(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = box[0] + box[2] / 2.0
    y = box[1] + box[3] / 2.0
    w = box[2]
    h = box[3]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)

def convert_annotation(coco_json, output_dir):
    with open(coco_json) as f:
        data = json.load(f)

    # Crear un diccionario para mapear image_id a información de la imagen
    image_dict = {image['id']: image for image in data['images']}

    # Crear archivos de anotaciones YOLO
    for annotation in data['annotations']:
        image_id = annotation['image_id']
        category_id = annotation['category_id']
        bbox = annotation['bbox']
        image_info = image_dict[image_id]
        size = (image_info['width'], image_info['height'])

        yolo_box = convert(size, bbox)
        class_id = category_id - 1  # Asumiendo que category_id comienza en 1

        image_filename = image_info['file_name']
        label_filename = os.path.splitext(image_filename)[0] + '.txt'
        label_filepath = os.path.join(output_dir, label_filename)

        with open(label_filepath, 'a') as f:
            f.write(f"{class_id} " + " ".join(map(str, yolo_box)) + '\n')

# Directorio donde están los archivos COCO JSON
coco_json_dir = 'dataset/valid/labels'
# Directorio donde se guardarán los archivos YOLO
output_dir = 'dataset/valid/labels'

# Crear el directorio de salida si no existe
os.makedirs(output_dir, exist_ok=True)

# Recorrer todos los archivos JSON en el directorio
for file_name in os.listdir(coco_json_dir):
    if file_name.endswith(".json"):
        json_path = os.path.join(coco_json_dir, file_name)
        convert_annotation(json_path, output_dir)

