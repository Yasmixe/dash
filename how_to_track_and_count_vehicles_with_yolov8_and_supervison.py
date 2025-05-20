# -*- coding: utf-8 -*-
from IPython import display
display.clear_output()

import ultralytics
import supervision as sv
import numpy as np

SOURCE_VIDEO_PATH = r"C:\Users\yasmi\Documents\dash\videosnew\apres-midi\apresmidi.mp4"

from ultralytics import YOLO

model = YOLO("best_yolov11_obb.pt")


CLASS_NAMES_DICT = model.model.names

SELECTED_CLASS_NAMES = ['0']

SELECTED_CLASS_IDS = [
    {value: key for key, value in CLASS_NAMES_DICT.items()}[class_name]
    for class_name
    in SELECTED_CLASS_NAMES
]

generator = sv.get_video_frames_generator(SOURCE_VIDEO_PATH)

box_annotator = sv.BoxAnnotator(thickness=4)
label_annotator = sv.LabelAnnotator(text_thickness=2, text_scale=1.5, text_color=sv.Color.BLACK)

byte_tracker = sv.ByteTrack(
    track_activation_threshold=0.25,
    lost_track_buffer=30,
    minimum_matching_threshold=0.8,
    frame_rate=30,
    minimum_consecutive_frames=3)

byte_tracker.reset()

video_info = sv.VideoInfo.from_video_path(SOURCE_VIDEO_PATH)

generator = sv.get_video_frames_generator(SOURCE_VIDEO_PATH)

trace_annotator = sv.TraceAnnotator(thickness=4, trace_length=50)

def callback(frame: np.ndarray, index: int) -> np.ndarray:
    results = model(frame, verbose=False)[0]
    detections = sv.Detections.from_ultralytics(results)
    
    detections = detections[np.isin(detections.class_id, SELECTED_CLASS_IDS)]
    
    detections = byte_tracker.update_with_detections(detections)
    
    labels = [
        f"#{tracker_id} {model.model.names[class_id]} {confidence:0.2f}"
        for confidence, class_id, tracker_id
        in zip(detections.confidence, detections.class_id, detections.tracker_id)
    ]
    
    annotated_frame = frame.copy()
    annotated_frame = trace_annotator.annotate(scene=annotated_frame, detections=detections)
    annotated_frame = box_annotator.annotate(scene=annotated_frame, detections=detections)
    annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=detections, labels=labels)

    return annotated_frame

TARGET_VIDEO_PATH = f"poop.mp4"
sv.process_video(
    source_path=SOURCE_VIDEO_PATH,
    target_path=TARGET_VIDEO_PATH,
    callback=callback
)
