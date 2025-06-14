import os
import cv2
import pandas as pd
import matplotlib.pyplot as plt
from ultralytics import YOLO
import supervision as sv

# === Paramètres ===
input_folder = r'C:\Users\yasmi\Documents\dash\static\videos\videos'
output_video_folder = r'C:\Users\yasmi\Documents\dash\static\videos\annotated'
output_csv_folder = r'C:\Users\yasmi\Documents\dash\static\videos\csv'
output_graph_folder = r'C:\Users\yasmi\Documents\dash\static\videos\graphe'

model = YOLO(r"C:\Users\yasmi\Documents\dash\runs\obb\train73\weights\bestyoloobb11_hyperparametres.pt", verbose=False)

# === Création des dossiers de sortie si non existants ===
os.makedirs(output_video_folder, exist_ok=True)
os.makedirs(output_csv_folder, exist_ok=True)
os.makedirs(output_graph_folder, exist_ok=True)

# === Traitement de chaque vidéo ===
for filename in os.listdir(input_folder):
    if not filename.endswith('.mp4'):
        continue

    video_path = os.path.join(input_folder, filename)
    base_name = os.path.splitext(filename)[0]

    output_path = os.path.join(output_video_folder, f"{base_name}_annotated.mp4")
    csv_output_path = os.path.join(output_csv_folder, f"detection_data_{base_name}.csv")
    graph_output_path = os.path.join(output_graph_folder, f"chariot_count_plot_{base_name}.png")

    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = None

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_index = 0
    tracker = sv.ByteTrack()

    box_annotator = sv.BoundingBoxAnnotator()
    label_annotator = sv.LabelAnnotator()
    trace_annotator = sv.TraceAnnotator()

    detection_data_list = []
    initial_count = None
    last_interval = -1
    alert_count = 0
    max_chariot_count = 0

    print(f"[INFO] Début du traitement de : {filename}")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame_index += 1
        results = model(frame)[0]

        detections = sv.Detections.from_ultralytics(results)
        detections = detections[detections.confidence > 0.4]
        detections = tracker.update_with_detections(detections)

        chariot_count = sum(
            1 for cid in detections.class_id if results.names[cid].lower() == "0"
        )
        max_chariot_count = max(max_chariot_count, chariot_count)

        if initial_count is None and chariot_count > 0:
            initial_count = chariot_count
            print(f"[INFO] Initial count fixé à {initial_count}")

        alert = False
        alert_message = ""
        if initial_count is not None and chariot_count <= max_chariot_count * 0.5:
            alert = True
            alert_message = f"Alerte : pile presque vide ! Il reste {chariot_count} chariot(s)."
            alert_count += 1
            print(alert_message)

        labels = [
            f"#{tracker_id} {results.names[class_id]}"
            for class_id, tracker_id in zip(detections.class_id, detections.tracker_id)
        ]

        frame = box_annotator.annotate(frame, detections)
        frame = label_annotator.annotate(frame, detections, labels)
        frame = trace_annotator.annotate(frame, detections)

        if video_writer is None:
            height, width, _ = frame.shape
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        video_writer.write(frame)

        video_time = round(frame_index / fps, 2)
        current_interval = int(video_time // 5)

        if current_interval != last_interval:
            detection = {
                "time": video_time,
                "count": chariot_count,
                "alert": alert,
                "message": alert_message
            }
            detection_data_list.append(detection)
            last_interval = current_interval

    cap.release()
    if video_writer:
        video_writer.release()

    print(f"[INFO] Vidéo annotée sauvegardée dans : {output_path}")

    # === Sauvegarde CSV ===
    df = pd.DataFrame(detection_data_list)
    df.to_csv(csv_output_path, index=False)
    print(f"[INFO] CSV sauvegardé dans : {csv_output_path}")

    # === Génération du graphique ===
    times = [entry["time"] for entry in detection_data_list]
    counts = [entry["count"] for entry in detection_data_list]

    plt.figure(figsize=(10, 5))
    plt.plot(times, counts, marker='o', linestyle='-', color='blue')
    plt.title(f"Nombre de chariots détectés - {base_name}")
    plt.xlabel("Temps (secondes)")
    plt.ylabel("Nombre de chariots")
    plt.grid(True)
    plt.savefig(graph_output_path)
    plt.close()
    print(f"[INFO] Graphique sauvegardé dans : {graph_output_path}\n")

print("[INFO] Traitement terminé pour toutes les vidéos.")
