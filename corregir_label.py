import os
import cv2

# Función para detectar el formato de la etiqueta
def detect_label_format(parts):
    if len(parts) == 5:
        return "YOLO Format"
    elif len(parts) == 4:
        return "COCO Format"
    elif len(parts) == 6:
        return "Pascal VOC Format"
    elif len(parts) > 5 and len(parts) % 2 == 1:
        return "LabelMe Format"
    else:
        return "Unknown Format"

# Función para normalizar las coordenadas
def normalize_coordinates(coords, img_width, img_height):
    return [str(float(coord) / img_width if i % 2 == 0 else float(coord) / img_height) for i, coord in enumerate(coords)]

# Función para verificar y corregir etiquetas incorrectas
def verify_and_fix_labels(image_directory, label_directory):
    incorrect_labels = []
    for img_name in os.listdir(image_directory):
        if os.path.splitext(img_name)[1].lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            img_path = os.path.join(image_directory, img_name)
            img = cv2.imread(img_path)
            img_height, img_width, _ = img.shape

            label_name = os.path.splitext(img_name)[0] + '.txt'
            label_path = os.path.join(label_directory, label_name)
            if os.path.exists(label_path):
                try:
                    with open(label_path, 'r') as file:
                        labels = file.readlines()

                    corrected_labels = []
                    for label in labels:
                        parts = label.strip().split()
                        format_detected = detect_label_format(parts)
                        print(f"Etiqueta: {label.strip()}, Formato detectado: {format_detected}")

                        if format_detected == "YOLO Format":
                            x_center, y_center, width, height = map(float, parts[1:])
                            if x_center < 0 or y_center < 0 or width < 0 or height < 0:
                                incorrect_labels.append((img_path, label_path))
                                break
                            corrected_labels.append(label)
                        elif format_detected == "COCO Format":
                            class_id, x, y, width, height = parts
                            x_center = float(x) + float(width) / 2
                            y_center = float(y) + float(height) / 2
                            if x_center < 0 or y_center < 0 or float(width) < 0 or float(height) < 0:
                                incorrect_labels.append((img_path, label_path))
                                break
                            coords = [x_center, y_center, width, height]
                            normalized_coords = normalize_coordinates(coords, img_width, img_height)
                            corrected_label = f"{class_id} {' '.join(normalized_coords)}\n"
                            corrected_labels.append(corrected_label)
                        elif format_detected == "Pascal VOC Format":
                            class_id, xmin, ymin, xmax, ymax = parts
                            x_center = (float(xmin) + float(xmax)) / 2
                            y_center = (float(ymin) + float(ymax)) / 2
                            width = float(xmax) - float(xmin)
                            height = float(ymax) - float(ymin)
                            if x_center < 0 or y_center < 0 or width < 0 or height < 0:
                                incorrect_labels.append((img_path, label_path))
                                break
                            coords = [x_center, y_center, width, height]
                            normalized_coords = normalize_coordinates(coords, img_width, img_height)
                            corrected_label = f"{class_id} {' '.join(normalized_coords)}\n"
                            corrected_labels.append(corrected_label)
                        elif format_detected == "LabelMe Format":
                            class_id = parts[0]
                            coords = parts[1:5]  # Tomar solo las primeras 4 coordenadas
                            if any(float(coord) < 0 for coord in coords):
                                incorrect_labels.append((img_path, label_path))
                                break
                            normalized_coords = normalize_coordinates(coords, img_width, img_height)
                            corrected_label = f"{class_id} {' '.join(normalized_coords)}\n"
                            corrected_labels.append(corrected_label)
                            print(f"Corregido: {corrected_label.strip()}")
                        else:
                            print(f"Error en la etiqueta {label_path}: Formato desconocido {label}")

                    if corrected_labels:
                        with open(label_path, 'w') as file:
                            file.writelines(corrected_labels)
                except Exception as e:
                    print(f"Error al leer la etiqueta {label_path}: {e}")
            else:
                print(f"Etiqueta no encontrada: {label_name}")

    # Manejar etiquetas incorrectas
    for img_path, label_path in incorrect_labels:
        if os.path.exists(img_path):
            os.remove(img_path)
        if os.path.exists(label_path):
            os.remove(label_path)
        print(f"Eliminados: {img_path} y {label_path}")

# Ruta al directorio de imágenes y etiquetas
image_directory = "/Users/pepeargentoo/CV_Daniel/dataset/valid/images"
label_directory = "/Users/pepeargentoo/CV_Daniel/dataset/valid/labels"

# Verificar y corregir las etiquetas en el directorio especificado
verify_and_fix_labels(image_directory, label_directory)
