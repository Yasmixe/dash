import os
import cv2
import time
import tempfile
import matplotlib.pyplot as plt
import numpy as np
from ultralytics import YOLO
from inference_sdk import InferenceHTTPClient

# Charger les modèles YOLO locaux
models = {
    "YOLOv11": YOLO(r"C:\Users\yasmi\Documents\dash\best_model_last_images.pt"),
    "YOLOv11-OBB": YOLO(r"C:\Users\yasmi\Documents\dash\best_yolov11_obb.pt"),
    "RT-Detr": YOLO(r"C:\Users\yasmi\Documents\dash\runs\detect\train8\weights\best.pt")
}

# Initialiser Roboflow
roboflow_client = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="qYNmk1DMrtRsc7vjTOUh"
)

# Stockage des temps
inference_times = {name: [] for name in models}
inference_times["RF-Detr"] = []

total_times = {name: 0 for name in models}
total_times["RF-Detr"] = 0

frame_counts = {name: 0 for name in models}
frame_counts["RF-Detr"] = 0

#  Charger la vidéo
video_path = "video4.mp4"
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Writer pour sauvegarder la vidéo résultante
out = cv2.VideoWriter('output_comparison3.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (width * 2, height * 2))

# Fonction prédiction Roboflow
def predict_roboflow(frame):
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
        temp_path = tmp_file.name
        cv2.imwrite(temp_path, frame)

    start = time.time()
    result = roboflow_client.infer(temp_path, model_id="myproject-iwt1z/4")
    end = time.time()

    # Dessin des bounding boxes
    for pred in result['predictions']:
        x, y, w, h = pred['x'], pred['y'], pred['width'], pred['height']
        x1 = int(x - w / 2)
        y1 = int(y - h / 2)
        x2 = int(x + w / 2)
        y2 = int(y + h / 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{pred['class']} {pred['confidence']:.2f}"
        cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

    return frame, end - start

frame_idx = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret or frame_idx > 100:  # Pour test rapide
        break

    frame_idx += 1
    print(f"\n Frame {frame_idx}")
    annotated_frames = []

    for name, model in models.items():
        start = time.time()
        results = model.predict(frame, verbose=False)[0]
        end = time.time()
        duration = end - start
        inference_times[name].append(duration)
        total_times[name] += duration
        frame_counts[name] += 1
        print(f"{name} ⏱️ {duration:.3f}s")

        # Annoter l'image
        annotated = results.plot()
        annotated_frames.append(annotated)

    # RF-Detr
    try:
        rf_annotated, rf_duration = predict_roboflow(frame.copy())
        inference_times["RF-Detr"].append(rf_duration)
        total_times["RF-Detr"] += rf_duration
        frame_counts["RF-Detr"] += 1
        print(f"RF-Detr {rf_duration:.3f}s")
        annotated_frames.append(rf_annotated)
    except Exception as e:
        print(f" RF-Detr error: {e}")
        annotated_frames.append(frame.copy())

    #  Fusionner les 4 images dans une grille 2x2
    top = np.hstack(annotated_frames[:2])
    bottom = np.hstack(annotated_frames[2:4]) if len(annotated_frames) > 2 else np.hstack([annotated_frames[2], frame])
    combined = np.vstack([top, bottom])
    out.write(combined)

cap.release()
out.release()

#  Tracer les temps d’inférence
plt.figure(figsize=(12, 6))
for name in inference_times:
    times = inference_times[name]
    if times:
        plt.plot(times, label=f"{name} (avg {sum(times)/len(times):.2f}s)")
plt.xlabel("Frame")
plt.ylabel("Inference Time (s)")
plt.title("Comparaison des temps d'inférence par modèle")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

#  Résumé final
print("\n Résumé des FPS et Inference Time:")
for name in total_times:
    count = frame_counts[name]
    total_time = total_times[name]
    fps_model = count / total_time if total_time > 0 else 0
    avg_inf = (total_time / count) * 1000 if count > 0 else 0
    print(f"{name}: FPS = {fps_model:.2f}, Temps moyen = {avg_inf:.2f} ms")
