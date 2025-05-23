import os
import cv2
import pandas as pd
import matplotlib.pyplot as plt
from ultralytics import YOLO
from collections import deque
from queue import Queue
import supervision as sv

# === Chargement du modèle et chemins ===
model = YOLO(r"C:\Users\yasmi\Documents\dash\best_yolov11_obb.pt", verbose=False)
video_path_A = r'C:\Users\yasmi\Documents\dash\static\videos\zone B\videos\zoneD.mp4'
output_path_A = r'C:\Users\yasmi\Documents\dash\static\videos\zone B\processed_videos\zoneD_annotated.mp4'
csv_output_path_A = r'C:\Users\yasmi\Documents\dash\static\videos\zone B\csv_data\detection_data_zoneD.csv'
graph_output_path_A = r'C:\Users\yasmi\Documents\dash\static\videos\zone B\graphs\chariot_count_plot_zoneD.png'

cap_A = cv2.VideoCapture(video_path_A)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer_A = None

fps_A = cap_A.get(cv2.CAP_PROP_FPS)
frame_index_A = 0
tracker_A = sv.ByteTrack()

box_annotator_A = sv.BoundingBoxAnnotator()
label_annotator_A = sv.LabelAnnotator()
trace_annotator_A = sv.TraceAnnotator()

detection_data_list_A = []
initial_count_A = None
last_interval_A = -1
alert_count_A = 0
max_chariot_count_A = 0

print("[INFO] Début du traitement vidéo...")

while cap_A.isOpened():
    success, frame = cap_A.read()
    if not success:
        break

    frame_index_A += 1
    results_A = model(frame)[0]

    detections = sv.Detections.from_ultralytics(results_A)
    detections = detections[detections.confidence > 0.4]
    detections = tracker_A.update_with_detections(detections)

    chariot_count_A = sum(
        1 for cid in detections.class_id if results_A.names[cid].lower() == "0"
    )
    max_chariot_count_A = max(max_chariot_count_A, chariot_count_A)

    if initial_count_A is None and chariot_count_A > 0:
        initial_count_A = chariot_count_A
        print(f"[INFO] Initial count fixé à {initial_count_A}")

    alert = False
    alert_message = ""
    if initial_count_A is not None and chariot_count_A <= max_chariot_count_A * 0.5:
        alert = True
        alert_message = f"Alerte : pile presque vide ! Il reste {chariot_count_A} chariot(s)."
        alert_count_A += 1
        print(alert_message)

    labels = [
        f"#{tracker_id} {results_A.names[class_id]}"
        for class_id, tracker_id in zip(detections.class_id, detections.tracker_id)
    ]

    frame = box_annotator_A.annotate(frame, detections)
    frame = label_annotator_A.annotate(frame, detections, labels)
    frame = trace_annotator_A.annotate(frame, detections)

    if video_writer_A is None:
        height, width, _ = frame.shape
        video_writer_A = cv2.VideoWriter(output_path_A, fourcc, fps_A, (width, height))
    video_writer_A.write(frame)

    video_time_A = round(frame_index_A / fps_A, 2)
    current_interval_A = int(video_time_A // 5)

    if current_interval_A != last_interval_A:
        detection = {
            "time": video_time_A,
            "count": chariot_count_A,
            "alert": alert,
            "message": alert_message
        }
        detection_data_list_A.append(detection)
        last_interval_A = current_interval_A

cap_A.release()
video_writer_A.release()
print(f"[INFO] Vidéo annotée sauvegardée dans : {output_path_A}")

# === Sauvegarde CSV ===
df = pd.DataFrame(detection_data_list_A)
df.to_csv(csv_output_path_A, index=False)
print(f"[INFO] Fichier CSV sauvegardé dans : {csv_output_path_A}")

# === Génération du graphique ===
times = [entry["time"] for entry in detection_data_list_A]
counts = [entry["count"] for entry in detection_data_list_A]

plt.figure(figsize=(10, 5))
plt.plot(times, counts, marker='o', linestyle='-', color='blue')
plt.title("Nombre de chariots détectés dans le temps")
plt.xlabel("Temps (secondes)")
plt.ylabel("Nombre de chariots")
plt.grid(True)
plt.savefig(graph_output_path_A)
plt.close()
print(f"[INFO] Graphique sauvegardé dans : {graph_output_path_A}")


