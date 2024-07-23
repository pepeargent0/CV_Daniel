import os
import shutil
import cv2
from tqdm import tqdm
from sklearn.model_selection import train_test_split

# Directorios de entrada y salida
temp_images_directory = 'dataset_tmp/images'
temp_labels_directory = 'dataset_tmp/labels'
final_images_directory = 'dataset_tmp/images'  # Directorio final para imágenes válidas
final_labels_directory = 'dataset_tmp/labels'  # Directorio final para etiquetas válidas
label_errors_directory = 'dataset/label_errors'
os.makedirs(final_images_directory, exist_ok=True)
os.makedirs(final_labels_directory, exist_ok=True)
os.makedirs(label_errors_directory, exist_ok=True)

# Función para verificar y unificar anotaciones en formato YOLOv5
def validar_y_unificar_anotaciones(images_dir, labels_dir, final_images_dir, final_labels_dir, label_errors_dir):
    extensiones_imagenes = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    archivos_procesados = 0
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
            height, width, _ = image.shape

            # Leer anotaciones
            with open(label_path, 'r') as f:
                lines = f.readlines()

            valid_lines = []
            error_found = False
            for line in lines:
                parts = line.strip().split()
                if len(parts) == 5:
                    id_clase, x_centro, y_centro, ancho, alto = map(float, parts)
                elif len(parts) == 9:
                    id_clase, x_centro, y_centro, ancho, alto = map(float, parts[:5])
                else:
                    error_found = True

                # Verificar límites y convertir a formato YOLOv5
                if not (0 <= x_centro <= 1 and 0 <= y_centro <= 1 and 0 <= ancho <= 1 and 0 <= alto <= 1):
                    error_found = True

                # Verificar que la etiqueta esté en el rango 0-48
                if not (0 <= id_clase <= 48):
                    error_found = True

                if error_found:
                    break
                else:
                    valid_lines.append(f"{int(id_clase)} {x_centro} {y_centro} {ancho} {alto}\n")

            if error_found:
                archivos_con_errores += 1
                shutil.move(label_path, os.path.join(label_errors_dir, os.path.basename(label_path)))
                os.remove(image_path)
            else:
                # Escribir anotaciones válidas y mover archivos
                with open(os.path.join(final_labels_dir, os.path.basename(label_path)), 'w') as f:
                    f.writelines(valid_lines)
                archivos_procesados += 1

    print(f"Archivos procesados: {archivos_procesados}")
    print(f"Archivos con errores: {archivos_con_errores}")

validar_y_unificar_anotaciones(temp_images_directory, temp_labels_directory, final_images_directory, final_labels_directory, label_errors_directory)


# División del dataset en entrenamiento, validación y prueba
image_files = [f for f in os.listdir(final_images_directory) if f.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))]
train_files, test_files = train_test_split(image_files, test_size=0.2, random_state=42)
train_files, val_files = train_test_split(train_files, test_size=0.25, random_state=42)

# Crear directorios para los splits
split_dirs = {
    'train': {'images': 'dataset/train/images', 'labels': 'dataset/train/labels'},
    'val': {'images': 'dataset/val/images', 'labels': 'dataset/val/labels'},
    'test': {'images': 'dataset/test/images', 'labels': 'dataset/test/labels'}
}

for split in split_dirs:
    os.makedirs(split_dirs[split]['images'], exist_ok=True)
    os.makedirs(split_dirs[split]['labels'], exist_ok=True)

# Función para mover archivos a sus directorios correspondientes
def mover_archivos(files, split):
    for file in files:
        shutil.copy(os.path.join(final_images_directory, file), split_dirs[split]['images'])
        shutil.copy(os.path.join(final_labels_directory, os.path.splitext(file)[0] + '.txt'), split_dirs[split]['labels'])

mover_archivos(train_files, 'train')
mover_archivos(val_files, 'val')
mover_archivos(test_files, 'test')

# Reporte de la cantidad de imágenes en cada split
print(f"Cantidad de imágenes en el conjunto de entrenamiento: {len(train_files)}")
print(f"Cantidad de imágenes en el conjunto de validación: {len(val_files)}")
print(f"Cantidad de imágenes en el conjunto de prueba: {len(test_files)}")
