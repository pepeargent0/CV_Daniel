import os
import zipfile
import shutil
from tqdm import tqdm
import cv2


def extraer_archivos_zip(directory):
    for file_name in os.listdir(directory):
        if file_name.endswith('.zip'):
            file_path = os.path.join(directory, file_name)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(directory)
            # os.remove(file_path)

def mover_archivos(directory):
    for root, _, files in os.walk(directory):
        images_dir = os.path.join(root, 'dataset/images')
        labels_dir = os.path.join(root, 'dataset/labels')
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(labels_dir, exist_ok=True)

        for file_name in files:
            file_path = os.path.join(root, file_name)
            base_name, ext = os.path.splitext(file_name)
            corresponding_txt = base_name + '.txt'
            corresponding_image = base_name + ext

            if ext in ('.jpg', '.jpeg', '.png', '.bmp', '.gif'):
                if corresponding_txt in files:
                    shutil.move(file_path, os.path.join(images_dir, file_name))
                else:
                    os.remove(file_path)
            elif ext == '.txt':
                if corresponding_image in files:
                    shutil.move(file_path, os.path.join(labels_dir, file_name))
                else:
                    os.remove(file_path)


def validar_anotaciones(images_dir, labels_dir, label_errors_dir):
    extensiones_imagenes = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    archivos_con_errores = 0

    for label_file in tqdm(os.listdir(labels_dir)):
        if label_file.endswith('.txt'):
            label_path = os.path.join(labels_dir, label_file)
            image_path = None

            for ext in extensiones_imagenes:
                potential_image_path = os.path.join(images_dir, os.path.splitext(label_file)[0] + ext)
                if os.path.exists(potential_image_path):
                    image_path = potential_image_path
                    break

            if image_path is None:
                shutil.move(label_path, os.path.join(label_errors_dir, os.path.basename(label_path)))
                archivos_con_errores += 1
                continue

            # Leer imagen
            image = cv2.imread(image_path)
            if image is None:
                shutil.move(label_path, os.path.join(label_errors_dir, os.path.basename(label_path)))
                os.remove(image_path)
                archivos_con_errores += 1
                continue

            height, width, _ = image.shape

            # Leer anotaciones
            with open(label_path, 'r') as f:
                lines = f.readlines()

            error_found = False
            for line in lines:
                parts = line.strip().split()
                if len(parts) == 5:
                    id_clase, x_centro, y_centro, ancho, alto = map(float, parts)
                elif len(parts) == 9:
                    id_clase, x_centro, y_centro, ancho, alto = map(float, parts[:5])
                else:
                    error_found = True

                # Verificar límites
                if not (0 <= x_centro <= 1 and 0 <= y_centro <= 1 and 0 <= ancho <= 1 and 0 <= alto <= 1):
                    error_found = True

                # Verificar que la etiqueta esté en el rango 0-48
                if not (0 <= id_clase <= 48):
                    error_found = True

                if error_found:
                    break

            if error_found:
                archivos_con_errores += 1
                shutil.move(label_path, os.path.join(label_errors_dir, os.path.basename(label_path)))
                os.remove(image_path)

    print(f"Archivos con errores: {archivos_con_errores}")



base_directory = 'drive'
label_errors_directory = 'dataset/label_errors'
extraer_archivos_zip(base_directory)
mover_archivos(base_directory)
for subdir in os.listdir(base_directory):
    subdir_path = os.path.join(base_directory, subdir)
    if os.path.isdir(subdir_path):
        images_dir = os.path.join(subdir_path, 'dataset/images')
        labels_dir = os.path.join(subdir_path, 'dataset/labels')
        if os.path.exists(images_dir) and os.path.exists(labels_dir):
            validar_anotaciones(images_dir, labels_dir, label_errors_directory)
