import fiftyone as fo
import os
import uuid

def create_fiftyone_dataset(image_dir, label_dir):
    name = "dataset_" + str(uuid.uuid4())
    dataset = fo.Dataset(name)

    for filename in os.listdir(image_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            image_path = os.path.join(image_dir, filename)
            label_path = os.path.join(label_dir, os.path.splitext(filename)[0] + '.txt')

            if not os.path.exists(label_path):
                print(f"Etiqueta no encontrada para la imagen {image_path}. Omitiendo.")
                continue

            with open(label_path) as f:
                labels = f.readlines()

            detections = []
            for label in labels:
                parts = label.strip().split()
                class_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])
                detections.append(
                    fo.Detection(
                        label=str(class_id),
                        bounding_box=[
                            x_center - width / 2,
                            y_center - height / 2,
                            width,
                            height,
                        ],
                    )
                )

            sample = fo.Sample(filepath=image_path)
            sample["ground_truth"] = fo.Detections(detections=detections)
            dataset.add_sample(sample)

    return dataset


# Crear datasets de FiftyOne
train_dataset = create_fiftyone_dataset('dataset/train/images', 'dataset/train/labels')
val_dataset = create_fiftyone_dataset('dataset/val/images', 'dataset/val/labels')
test_dataset = create_fiftyone_dataset('dataset/test/images', 'dataset/test/labels')

# Visualizar datasets con FiftyOne
session = fo.launch_app()
session.dataset = train_dataset

print("Visualización del conjunto de entrenamiento en FiftyOne iniciada.")
