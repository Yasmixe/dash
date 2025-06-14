from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from ultralytics import YOLO
import supervision as sv
import cv2
import base64
import numpy as np
import torch
import os
import json
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app)


app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

global video_path

# Initialize YOLO model and trackers
print('torch.cuda.is_available:', torch.cuda.is_available())
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print(f'Using device: {device}')
model = YOLO(r"C:\Users\yasmi\Documents\dash\runs\obb\train73\weights\bestyoloobb11_hyperparametres.pt").to(device)
imgz = (256, 256)  # Réduite pour améliorer la performance
annotator = sv.BoxAnnotator(thickness=2)
label_annotator = sv.LabelAnnotator(text_scale=1)
tracker = sv.ByteTrack()
video_path = None

def run_detection(image):
    print("Processing frame for detection")
    results = model(image, imgsz=256, nms=True, device=device)[0]
    detection = sv.Detections.from_ultralytics(results)
    detection = detection[detection.confidence > 0.3]
    detection = tracker.update_with_detections(detection)
    annotated_image = annotator.annotate(image, detection)
    annotated_image = label_annotator.annotate(annotated_image, detection)
    return annotated_image, len(detection)

@socketio.on('connect')
def start_websocket():
    print("Starting WebSocket server")
    
@socketio.on('frame')
def message_received(data):
    try:
        img_data = base64.b64decode(data.split(",")[1])
        img_array = np.frombuffer(img_data, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        # frame = cv2.resize(img_array, (512, 512))
        # frame = cv2.flip(frame, 1)

        if frame is None:
            return

        frame, detection_size = run_detection(frame)
        _, encoded_frame = cv2.imencode('.jpg', frame)
        encoded_frame_str = base64.b64encode(encoded_frame.tobytes()).decode('utf-8')

        payload = {
            'count': detection_size,
            'image': f'data:image/jpeg;base64,{encoded_frame_str}',
                # 'timestamp': time.time()
        }
        socketio.emit('response', json.dumps(payload))
        # await asyncio.sleep(0.03)

    except Exception as e:
        print(f"Error: {e}")

@socketio.on('disconnect')
def client_left():
    print("WebSocket client disconnected")

@app.route('/realtime')
def serve_index():
    print("Serving real_time.html")
    return send_file('real_time.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    
    print("Handling video upload")
    print("Received upload request")
    if 'video' not in request.files:
        print("No video file provided")
        return jsonify({'error': 'No video file provided'}), 400
    file = request.files['video']
    video_path = os.path.join('uploads', file.filename)
    os.makedirs('uploads', exist_ok=True)
    file.save(video_path)
    print(f"Video saved to {video_path}")
    return jsonify({'message': 'Video uploaded successfully'})



if __name__ == '__main__':
    print("Starting Flask server")
    app.run(host='0.0.0.0', port=5000)