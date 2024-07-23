import torch
from ultralytics import YOLO
import onnx
import onnxruntime as ort
import time

# Forzar el uso de la CPU
device = 'cpu'
print("Usando CPU para entrenamiento y exportación.")

imgsz = 640

# Cargar el modelo YOLO
model = YOLO("yolov5s.pt")

# Inicializar listas para guardar métricas
epoch_list = []
precision_list = []
recall_list = []
map50_list = []
map50_95_list = []

# Entrenar el modelo con el tamaño de imagen especificado
try:
    print("Iniciando el entrenamiento...")
    for epoch in range(100):  # Cambia 10 al número de épocas que desees
        model.train(data="dataset/dataset.yaml", epochs=1, imgsz=imgsz, batch=16, device=device)
        metrics = model.val()

        # Guardar métricas para la época actual
        epoch_list.append(epoch + 1)
        if hasattr(metrics, 'box'):
            precision_list.append(metrics.box.map50)
            recall_list.append(metrics.box.r if hasattr(metrics.box, 'r') else 0)
            map50_list.append(metrics.box.map50)
            map50_95_list.append(metrics.box.map)

        print(
            f"Época {epoch + 1}/10 - Precision: {precision_list[-1]:.4f}, Recall: {recall_list[-1]:.4f}, mAP@50: {map50_list[-1]:.4f}, mAP@50-95: {map50_95_list[-1]:.4f}")

    print("Entrenamiento completado.")
    # Guardar el modelo entrenado
    model.save("yolov5s_trained.pt")
    print("Modelo entrenado guardado como 'yolov5s_trained.pt'")
except Exception as e:
    print(f"Error durante el entrenamiento: {e}")

# Exportar el modelo a ONNX
onnx_file_path = "yolov5s_trained.onnx"
try:
    print("Exportando el modelo a ONNX...")
    model.export(format="onnx", path=onnx_file_path)
    print(f"Modelo exportado a ONNX en: {onnx_file_path}")
except Exception as e:
    print(f"Error durante la exportación a ONNX: {e}")

# Visualizar el progreso del entrenamiento
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 5))
plt.plot(epoch_list, precision_list, label='Precision')
plt.plot(epoch_list, recall_list, label='Recall')
plt.plot(epoch_list, map50_list, label='mAP@50')
plt.plot(epoch_list, map50_95_list, label='mAP@50-95')
plt.xlabel('Épocas')
plt.ylabel('Métricas')
plt.title('Progreso del Entrenamiento')
plt.legend()
plt.grid(True)
plt.show()
