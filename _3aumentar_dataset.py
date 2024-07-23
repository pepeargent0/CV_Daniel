import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2
import os
import random
import numpy as np

# Transformaciones de aumentación con bbox_params
transform = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.5),
    A.RandomRotate90(p=0.5),
    A.RandomBrightnessContrast(p=0.2),
    A.HueSaturationValue(p=0.2),
    A.Blur(p=0.2),
    A.Normalize(),
    ToTensorV2(),
], bbox_params=A.BboxParams(format='yolo', label_fields=['category_ids'], min_area=0.0, min_visibility=0.0))


def is_valid_bbox(bbox):
    x_centro, y_centro, ancho, alto = bbox
    return 0 <= x_centro <= 1 and 0 <= y_centro <= 1 and 0 <= ancho <= 1 and 0 <= alto <= 1


def augment_images(image_dir, label_dir, augment_times=10, max_attempts=120):
    augmented_images_dir = image_dir
    augmented_labels_dir = label_dir

    error_images = []

    for filename in os.listdir(image_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')) and not filename.startswith('aug_'):
            image_path = os.path.join(image_dir, filename)
            label_path = os.path.join(label_dir, os.path.splitext(filename)[0] + '.txt')

            image = cv2.imread(image_path)
            height, width, _ = image.shape

            with open(label_path, 'r') as f:
                lines = f.readlines()

            annotations = []
            category_ids = []
            for line in lines:
                parts = line.strip().split()
                id_clase = int(parts[0])
                x_centro = float(parts[1])
                y_centro = float(parts[2])
                ancho = float(parts[3])
                alto = float(parts[4])
                annotations.append([x_centro, y_centro, ancho, alto])
                category_ids.append(id_clase)

            for _ in range(augment_times):
                valid = False
                attempts = 0
                while not valid and attempts < max_attempts:
                    try:
                        transformed = transform(image=image, bboxes=annotations, category_ids=category_ids)
                        transformed_image = transformed['image'].permute(1, 2,
                                                                         0).cpu().numpy()  # Convertir tensor a numpy array
                        transformed_image = (transformed_image * 255).astype(np.uint8)  # Convertir de [0,1] a [0,255]
                        transformed_bboxes = transformed['bboxes']

                        if all(is_valid_bbox(bbox) for bbox in transformed_bboxes):
                            valid = True
                        attempts += 1
                    except Exception as e:
                        print(f"Error al transformar la imagen {filename}: {e}")
                        error_images.append(filename)
                        break

                if valid:
                    output_image_path = os.path.join(augmented_images_dir, f"aug_{random.randint(0, 9999)}_{filename}")
                    output_label_path = os.path.join(augmented_labels_dir,
                                                     os.path.splitext(f"aug_{random.randint(0, 9999)}_{filename}")[
                                                         0] + '.txt')

                    cv2.imwrite(output_image_path, transformed_image)

                    with open(output_label_path, 'w') as f:
                        for bbox, category_id in zip(transformed_bboxes, transformed['category_ids']):
                            x_centro, y_centro, ancho, alto = bbox
                            f.write(f"{category_id} {x_centro} {y_centro} {ancho} {alto}\n")
                else:
                    error_images.append(filename)




augment_images('dataset/train/images', 'dataset/train/labels')
augment_images('dataset/test/images', 'dataset/test/labels')
augment_images('dataset/val/images', 'dataset/val/labels')

