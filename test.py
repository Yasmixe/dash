import numpy as np
import supervision as sv
from ultralytics import YOLO
import os
model = YOLO(r"C:\Users\yasmi\Documents\dash\best_yolov11_obb.pt")
box_annotator = sv.BoundingBoxAnnotator()
label_annotator = sv.LabelAnnotator()
trace_annotator = sv.TraceAnnotator()
global tracker 


def callback(frame: np.ndarray, _: int) -> np.ndarray:
    results = model(frame)[0]
    detections = sv.Detections.from_ultralytics(results)
    detections = detections[detections.confidence > 0.3]
    detections = tracker.update_with_detections(detections)

    labels = [
        f"#{tracker_id} {results.names[class_id]}"
        for class_id, tracker_id
        in zip(detections.class_id, detections.tracker_id)
    ]

    annotated_frame = box_annotator.annotate(
        frame.copy(), detections=detections)
    annotated_frame = label_annotator.annotate(
        annotated_frame, detections=detections, labels=labels)
    return trace_annotator.annotate(
        annotated_frame, detections=detections)
# Dossier où enregistrer les vidéons annotées
source_folder = r"C:\Users\yasmi\Documents\dash\videosnew\apres-midi"
output_folder = r"C:\Users\yasmi\Documents\dash\videosnew\output"
os.makedirs(output_folder, exist_ok=True)

video_extensions = ['.mp4', '.avi', '.mov', '.mkv']

# Parcourir toutes les vidéos du dossier source
for filename in os.listdir(source_folder):
    print(filename)
    if any(filename.lower().endswith(ext) for ext in video_extensions):
        source_path = os.path.join(source_folder, filename)
        target_path = os.path.join(output_folder, filename.split(".MOV")[0] + '.mp4')

        print(f"Traitement de la vidéo : {filename}")
        tracker = sv.ByteTrack()

        # Appeler la fonction avec les bons chemins
        sv.process_video(
            source_path=source_path,
            target_path=target_path,
            callback=callback
        )
