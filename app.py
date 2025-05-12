from flask import Flask, render_template, Response, jsonify
from ultralytics import YOLO
import cv2
from datetime import datetime
import os
import base64
from flask import request, jsonify
import pandas as pd
from flask import Flask, render_template, request, redirect, jsonify
from flaskext.mysql import MySQL
import json
import random
import matplotlib.pyplot as plt
from io import BytesIO
import time
import threading
from IPython import display
display.clear_output()
import ultralytics
import supervision as sv
import numpy as np

model = YOLO("best_model_last_images.pt")
app = Flask(__name__)
#-----------------------------------------connection mysql-flask------------------------------------------------------------------------------------------------------------------------------------------------------------------------
app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_PORT"] = 3306
app.config["MYSQL_DATABASE_USER"] = "yasmine"
app.config["MYSQL_DATABASE_PASSWORD"] = "yasminehanafi"
app.config["MYSQL_DATABASE_DB"] = "airportchariot"
mysql = MySQL()
mysql.init_app(app)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------les routes-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/stats')
def index():
    
    return render_template('stats.html')
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/')
def calendar():
    return render_template('dashboard.html')
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/api/data1")
def doGetData():
    selected_date = request.args.get('date') 
    data1 = []

    conn = mysql.connect()
    cursor = conn.cursor()    
    query = """
        SELECT zone, COUNT(*) as nombre_de_chariots
        FROM chariot
        WHERE date = %s
        GROUP BY zone
    """
    cursor.execute(query, (selected_date,))
    results = cursor.fetchall()

    for row in results:
        data1.append({"zone": row[0], "nombre_de_chariots": row[1]})

    cursor.close()
    return json.dumps(data1)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/api/data2")
def doGetData2():
    selected_date = request.args.get('date')  
    data = []

    conn = mysql.connect()
    cursor = conn.cursor()

    # Compter les chariots par zone et classe pour la date donnée
    query = """
        SELECT zone, classe, COUNT(*) as nombre_de_chariots
        FROM chariot
        WHERE date = %s
        GROUP BY zone, classe
        ORDER BY zone, classe
    """
    cursor.execute(query, (selected_date,))
    results = cursor.fetchall()

    for row in results:
        data.append({
            "zone": row[0],
            "classe": row[1], 
            "nombre_de_chariots": row[2]
        })

    cursor.close()
    return json.dumps(data)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/api/data3")
def doGetData3():
    selected_date = request.args.get('date')

    data = []
    conn = mysql.connect()
    cursor = conn.cursor()

    query = """
        SELECT zone, COUNT(*) as nombre_alertes
        FROM alertetable
        WHERE date = %s
        GROUP BY zone
    """
    cursor.execute(query, (selected_date,))
    results = cursor.fetchall()

    for row in results:
        data.append({
            "zone": row[0],
            "nombre_alertes": row[1]
        })

    cursor.close()

    return jsonify(data)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/api/data4")
def doGetData4():
    selected_date = request.args.get('date')  
    data = []

    conn = mysql.connect()
    cursor = conn.cursor()

    query = """
        SELECT zone, alerte, COUNT(*) as nombre
        FROM alertetable
        WHERE DATE(date) = %s
        GROUP BY zone, alerte
    """
    cursor.execute(query, (selected_date,))
    results = cursor.fetchall()

    for row in results:
        data.append({
            "zone": row[0],
            "alerte": row[1],
            "nombre": row[2]
        })

    cursor.close()
    return json.dumps(data)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/api/data5")
def zones_plus_de_vide():
    selected_date = request.args.get('date') 
    data = []

    conn = mysql.connect()
    cursor = conn.cursor()

    # les zones ou y a le plus de chariots vides
    query = """
        SELECT zone, COUNT(*) as nombre_vide
        FROM chariot
        WHERE date = %s AND classe = 'chariot vide'
        GROUP BY zone
        ORDER BY nombre_vide DESC
    """
    cursor.execute(query, (selected_date,))
    results = cursor.fetchall()

    for row in results:
        data.append({
            "zone": row[0],
            "nombre_vide": row[1]
        })

    cursor.close()
    return json.dumps(data)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
from flask import request, jsonify

@app.route("/api/data6")
def evolution_alertes():
    selected_date = request.args.get('date')  
    data = []

    conn = mysql.connect()
    cursor = conn.cursor()

    query = """
        SELECT zone, DATE_FORMAT(heure, '%H:%i') as heure, COUNT(*) as nombre
        FROM alertetable
        WHERE DATE(date) = %s AND alerte = 'pile presque vide'
        GROUP BY zone, heure
        ORDER BY heure
    """
    cursor.execute(query, (selected_date,))
    results = cursor.fetchall()

    for row in results:
        data.append({
            "zone": row[0],
            "heure": row[1],
            "nombre": row[2]
        })

    cursor.close()
    return jsonify(data)


#-----------------------------------------------------------Simuler la pile et les alertes-------------------------------------------------------------------------------------------------------------------------------------------------
# pour chaque pile dans une zone: capacite ta3 les chariots, le temps qu'elle met pour se vider (selon les zones, za3ma li 9edam france se vide kter men li 9edam qatar)
zone_config = {
    'A': [45, 5],
    'B': [36, 15],
    'C': [38, 12],
    'D': [40, 8],
    'E': [42, 10],
    'F': [44, 6]
}

seuils = {
    "pre_alerte": 0.35,
    "alerte_critique": 0.2
}

piles_etats = {zone: zone_config[zone][0] for zone in zone_config}
piles_evolution = {zone: [] for zone in zone_config}
alertes_table = []


def simulation_background():
    while True:
        now = datetime.now().strftime('%H:%M')
        for zone, (pile_initiale, temps_vidange) in zone_config.items():
            taux_depletion = pile_initiale / temps_vidange
            depletion = taux_depletion + random.uniform(-0.2, 0.2)
            piles_etats[zone] -= depletion
            
            pourcentage = piles_etats[zone] / pile_initiale

            if pourcentage <= seuils["alerte_critique"]:
                alertes_table.append({'Zone': zone, 'Heure': now, 'Niveau': 'Critique'})
                piles_etats[zone] = pile_initiale  # Re-remplissage

            elif seuils["alerte_critique"] < pourcentage <= seuils["pre_alerte"]:
                # Vérifier si une pré-alerte récente existe
                if not any(a['Zone'] == zone and a['Niveau'] == 'Pré-Alerte' and a['Heure'] == now for a in alertes_table[-10:]):
                    alertes_table.append({'Zone': zone, 'Heure': now, 'Niveau': 'Pré-Alerte'})

            # Mise à jour historique
            piles_evolution[zone].append(piles_etats[zone])
            if len(piles_evolution[zone]) > 60:
                piles_evolution[zone].pop(0)

        time.sleep(60)  # Une minute réelle

threading.Thread(target=simulation_background, daemon=True).start()
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/data')
def data():
    return jsonify({
        'piles': piles_evolution,
        'alertes': alertes_table[-50:]  # dernières alertes
    })
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------ByteTracking------------------------------------------------------------------------------------------------------------------------
'''SOURCE_VIDEO_PATH = "C:\\Users\\yasmi\\Documents\\detection\\vehicles.mp4"

# Dictionnaire de mappage entre class_id et class_name
CLASS_NAMES_DICT = model.model.names

# Les noms des classes que nous avons choisis
SELECTED_CLASS_NAMES = ['car', 'motorcycle', 'bus', 'truck']

# Les IDs des classes correspondant aux noms des classes sélectionnées
SELECTED_CLASS_IDS = [
    {value: key for key, value in CLASS_NAMES_DICT.items()}[class_name]
    for class_name
    in SELECTED_CLASS_NAMES
]

# Générateur de frames vidéo
generator = sv.get_video_frames_generator(SOURCE_VIDEO_PATH)

# Création des annotateurs
box_annotator = sv.BoxAnnotator(thickness=4)
label_annotator = sv.LabelAnnotator(text_thickness=2, text_scale=1.5, text_color=sv.Color.BLACK)

# Création de l'instance ByteTracker
byte_tracker = sv.ByteTrack(
    track_activation_threshold=0.25,
    lost_track_buffer=30,
    minimum_matching_threshold=0.8,
    frame_rate=30,
    minimum_consecutive_frames=3)

byte_tracker.reset()

# Création d'une instance VideoInfo
video_info = sv.VideoInfo.from_video_path(SOURCE_VIDEO_PATH)

# Création d'un générateur de frames
generator = sv.get_video_frames_generator(SOURCE_VIDEO_PATH)

trace_annotator = sv.TraceAnnotator(thickness=4, trace_length=50)

def callback(frame: np.ndarray, index: int) -> np.ndarray:
    results = model(frame, verbose=False)[0]
    detections = sv.Detections.from_ultralytics(results)
    
    detections = detections[np.isin(detections.class_id, SELECTED_CLASS_IDS)]
    
    # Suivi des détections
    detections = byte_tracker.update_with_detections(detections)
    
    # Création des étiquettes avec les IDs
    labels = [
        f"#{tracker_id} {model.model.names[class_id]} {confidence:0.2f}"
        for confidence, class_id, tracker_id
        in zip(detections.confidence, detections.class_id, detections.tracker_id)
    ]
    
    # Annotation des boîtes et des étiquettes
    annotated_frame = frame.copy()
    annotated_frame = trace_annotator.annotate(scene=annotated_frame, detections=detections)
    annotated_frame = box_annotator.annotate(scene=annotated_frame, detections=detections)
    annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=detections, labels=labels)

    return annotated_frame

TARGET_VIDEO_PATH = f"resultat_vehicule.mp4"
sv.process_video(
    source_path=SOURCE_VIDEO_PATH,
    target_path=TARGET_VIDEO_PATH,
    callback=callback
)'''

@app.route('/predict_video', methods=['POST'])
def predict_video():
    data = request.get_json()
    video_path = data['video_path']

    # Corriger le chemin pour matcher la vidéo réellement utilisée
    full_video_path = os.path.join(os.getcwd(), video_path.lstrip('/'))

    if not os.path.exists(full_video_path):
        return jsonify({'error': f'Video not found: {full_video_path}'}), 404

    cap = cv2.VideoCapture(full_video_path)
    detected_objects = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret or frame_count >= 5:
            break

        results = model(frame)
        boxes = results[0].boxes

        for i in range(len(boxes)):
            box = boxes[i]
            class_id = int(box.cls[0])
            detected_objects.append({
                'frame': frame_count,
                'xmin': float(box.xyxy[0][0]),
                'ymin': float(box.xyxy[0][1]),
                'xmax': float(box.xyxy[0][2]),
                'ymax': float(box.xyxy[0][3]),
                'confidence': float(box.conf[0]),
                'class_id': class_id,
                'class_name': results[0].names[class_id]
            })

        frame_count += 1

    cap.release()

    class_counts = {}
    for obj in detected_objects:
        name = obj['class_name']
        class_counts[name] = class_counts.get(name, 0) + 1

    return jsonify({
        'video_name': os.path.basename(video_path),
        'detections': detected_objects,
        'class_counts': class_counts
    })

@app.route('/camera')
def camera_view():
    return render_template("camera.html")


if __name__ == '__main__':
    app.run(debug=True)
