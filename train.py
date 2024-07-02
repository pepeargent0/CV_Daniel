from ultralytics import YOLO
model = YOLO("yolov8s.pt")
model.train(data="/Users/pepeargentoo/CV_Daniel/dataset/dataset.yaml", epochs=100, imgsz=640, batch=16)
metrics = model.val()
print(f"Precision: {metrics.box.map50:.4f}")
print(f"Recall: {metrics.box.map50:.4f}")
print(f"mAP@50: {metrics.box.map50:.4f}")
print(f"mAP@50:95: {metrics.box.map:.4f}")
for i, class_name in enumerate(metrics.names):
    precision = metrics.box.p[i] if i < len(metrics.box.p) else 0
    recall = metrics.box.r[i] if i < len(metrics.box.r) else 0
    ap50 = metrics.box.ap50[i] if i < len(metrics.box.ap50) else 0
    ap = metrics.box.ap[i] if i < len(metrics.box.ap) else 0
    print(f"Class {i} ({class_name}): Precision: {precision:.4f}, Recall: {recall:.4f}, AP@50: {ap50:.4f}, AP@50:95: {ap:.4f}")

path = model.export(format="onnx")
