from ultralytics import YOLO

# Cargar un modelo preentrenado
model = YOLO("yolov8s.pt")

# Entrenar el modelo
model.train(data="/Users/pepeargentoo/CV_Daniel/dataset/dataset.yaml", epochs=16, imgsz=640, batch=16)

# Evaluar el modelo
metrics = model.val()

# Imprimir las métricas de evaluación
print(f"Precision: {metrics.box.map50:.4f}")
print(f"Recall: {metrics.box.map50:.4f}")
print(f"mAP@50: {metrics.box.map50:.4f}")
print(f"mAP@50:95: {metrics.box.map:.4f}")

# Exportar el modelo a formato ONNX
path = model.export(format="onnx")
