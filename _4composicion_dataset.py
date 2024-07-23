import matplotlib.pyplot as plt
import os
def contar_clases(label_dir):
    class_counts = {}
    for filename in os.listdir(label_dir):
        if filename.endswith('.txt'):
            with open(os.path.join(label_dir, filename), 'r') as f:
                lines = f.readlines()
                for line in lines:
                    class_id = line.split()[0]
                    if class_id not in class_counts:
                        class_counts[class_id] = 0
                    class_counts[class_id] += 1
    return class_counts

train_class_counts = contar_clases('dataset/train/labels')
val_class_counts = contar_clases('dataset/val/labels')
test_class_counts = contar_clases('dataset/test/labels')

# Graficar la distribución de clases
def graficar_distribucion_clases(class_counts, title):
    plt.figure(figsize=(36, 8))
    plt.bar(class_counts.keys(), class_counts.values())
    plt.xlabel('Clases')
    plt.ylabel('Frecuencia')
    plt.title(title)
    plt.xticks(rotation=45)
    plt.show()

graficar_distribucion_clases(train_class_counts, 'Distribución de Clases - Entrenamiento')
graficar_distribucion_clases(val_class_counts, 'Distribución de Clases - Validación')
graficar_distribucion_clases(test_class_counts, 'Distribución de Clases - Prueba')
