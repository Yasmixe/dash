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
from queue import Queue
from threading import Thread
model = YOLO(r"C:\Users\yasmi\Documents\dash\best_yolov11_obb.pt", verbose=False)
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
#--------------------------------------------------les routes-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/zoneA')
def zoneA():
    return render_template('zoneA.html')

@app.route('/zoneB')
def zoneB():
    return render_template('zoneB.html')

@app.route('/zoneC')
def zoneC():
    return render_template('zoneC.html')


@app.route('/zoneD')
def zoneD():
    return render_template('zoneD.html')
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
#------------------------------------------------------------------------------------------Zone A----------------------------------------------------------------------------------------------

video_path_A = r'C:\Users\yasmi\Documents\dash\static\video\zoneA.mp4'
cap = cv2.VideoCapture(video_path_A)

fps = cap.get(cv2.CAP_PROP_FPS)
frame_index = 0
tracker = sv.ByteTrack()

box_annotator = sv.BoundingBoxAnnotator()
label_annotator = sv.LabelAnnotator()
trace_annotator = sv.TraceAnnotator()

detection_queue = Queue()
initial_count = None          # mémorise le nombre de chariots au t = 0 s

# Nouvelle variable pour l'agrégation
last_interval = -1
def generate_framesA():
    global frame_index, last_interval, initial_count

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame_index += 1
        results = model(frame)[0]

        detections = sv.Detections.from_ultralytics(results)
        detections = detections[detections.confidence > 0.4]
        detections = tracker.update_with_detections(detections)
        
        # nombre de chariots détectés sur cette frame
        chariot_count = sum(
            1 for cid in detections.class_id if results.names[cid].lower() == "0"
        )
        
        # Initialisation du comptage
       # Initialisation du comptage
        if initial_count is None and chariot_count > 0:
            initial_count = chariot_count
            print(f"[INFO] Initial count fixé à {initial_count}")

         # ---------- calcul de l'alerte ----------
        alert = False
        alert_message = ""
        if chariot_count <= initial_count*0.5:
            alert = True
            alert_message = f"Alerte Alerte: pile presque vide ! Il reste {chariot_count} chariot{'s' if chariot_count > 1 else ''}."
            print(alert_message)

        labels = [
            f"#{tracker_id} {results.names[class_id]}"
            for class_id, tracker_id in zip(detections.class_id, detections.tracker_id)
        ]

        frame = box_annotator.annotate(frame, detections)
        frame = label_annotator.annotate(frame, detections, labels)
        frame = trace_annotator.annotate(frame, detections)

        # Temps vidéo en secondes
        video_time = round(frame_index / fps, 2)
        current_interval = int(video_time // 5)

        if current_interval != last_interval:
            # on met aussi le flag d'alerte dans la queue
           detection_queue.put({"time": video_time, "count": chariot_count, "alert": alert, "message": alert_message})

           last_interval = current_interval

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
@app.route('/video_feedA')
def video_feedA():
    return Response(generate_framesA(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detection_dataA')
def detection_dataA():
    data = []
    while not detection_queue.empty():
        data.append(detection_queue.get())
    return jsonify(data)   
#----------------------------------------------------------------------

video_path_B = r'C:\Users\yasmi\Documents\dash\static\video\zoneB.mp4'
cap = cv2.VideoCapture(video_path_B)

fps = cap.get(cv2.CAP_PROP_FPS)
frame_index = 0
tracker = sv.ByteTrack()

box_annotator = sv.BoundingBoxAnnotator()
label_annotator = sv.LabelAnnotator()
trace_annotator = sv.TraceAnnotator()

detection_queue = Queue()
initial_count = None          # mémorise le nombre de chariots au t = 0 s

# Nouvelle variable pour l'agrégation
last_interval = -1
def generate_framesB():
    global frame_index, last_interval, initial_count

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame_index += 1
        results = model(frame)[0]

        detections = sv.Detections.from_ultralytics(results)
        detections = detections[detections.confidence > 0.4]
        detections = tracker.update_with_detections(detections)
        
        # nombre de chariots détectés sur cette frame
        chariot_count = sum(
            1 for cid in detections.class_id if results.names[cid].lower() == "0"
        )
        
        # Initialisation du comptage
       # Initialisation du comptage
        if initial_count is None and chariot_count > 0:
            initial_count = chariot_count
            print(f"[INFO] Initial count fixé à {initial_count}")

         # ---------- calcul de l'alerte ----------
        alert = False
        alert_message = ""
        if chariot_count <= initial_count*0.5:
            alert = True
            alert_message = f"Alerte Alerte: pile presque vide ! Il reste {chariot_count} chariot{'s' if chariot_count > 1 else ''}."
            print(alert_message)

        labels = [
            f"#{tracker_id} {results.names[class_id]}"
            for class_id, tracker_id in zip(detections.class_id, detections.tracker_id)
        ]

        frame = box_annotator.annotate(frame, detections)
        frame = label_annotator.annotate(frame, detections, labels)
        frame = trace_annotator.annotate(frame, detections)

        # Temps vidéo en secondes
        video_time = round(frame_index / fps, 2)
        current_interval = int(video_time // 5)

        if current_interval != last_interval:
            # on met aussi le flag d'alerte dans la queue
           detection_queue.put({"time": video_time, "count": chariot_count, "alert": alert, "message": alert_message})

           last_interval = current_interval

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
@app.route('/video_feedB')
def video_feedB():
    return Response(generate_framesB(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detection_dataB')
def detection_dataB():
    data = []
    while not detection_queue.empty():
        data.append(detection_queue.get())
    return jsonify(data)   


#----------------------------------------------------------------------

video_path_C = r'C:\Users\yasmi\Documents\dash\static\video\zoneC.mp4'
cap = cv2.VideoCapture(video_path_C)

fps = cap.get(cv2.CAP_PROP_FPS)
frame_index = 0
tracker = sv.ByteTrack()

box_annotator = sv.BoundingBoxAnnotator()
label_annotator = sv.LabelAnnotator()
trace_annotator = sv.TraceAnnotator()

detection_queue = Queue()
initial_count = None          # mémorise le nombre de chariots au t = 0 s

# Nouvelle variable pour l'agrégation
last_interval = -1
def generate_framesC():
    global frame_index, last_interval, initial_count

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame_index += 1
        results = model(frame)[0]

        detections = sv.Detections.from_ultralytics(results)
        detections = detections[detections.confidence > 0.4]
        detections = tracker.update_with_detections(detections)
        
        # nombre de chariots détectés sur cette frame
        chariot_count = sum(
            1 for cid in detections.class_id if results.names[cid].lower() == "0"
        )
        
        # Initialisation du comptage
       # Initialisation du comptage
        if initial_count is None and chariot_count > 0:
            initial_count = chariot_count
            print(f"[INFO] Initial count fixé à {initial_count}")

         # ---------- calcul de l'alerte ----------
        alert = False
        alert_message = ""
        if chariot_count <= initial_count*0.5:
            alert = True
            alert_message = f"Alerte Alerte: pile presque vide ! Il reste {chariot_count} chariot{'s' if chariot_count > 1 else ''}."
            print(alert_message)

        labels = [
            f"#{tracker_id} {results.names[class_id]}"
            for class_id, tracker_id in zip(detections.class_id, detections.tracker_id)
        ]

        frame = box_annotator.annotate(frame, detections)
        frame = label_annotator.annotate(frame, detections, labels)
        frame = trace_annotator.annotate(frame, detections)

        # Temps vidéo en secondes
        video_time = round(frame_index / fps, 2)
        current_interval = int(video_time // 5)

        if current_interval != last_interval:
            # on met aussi le flag d'alerte dans la queue
           detection_queue.put({"time": video_time, "count": chariot_count, "alert": alert, "message": alert_message})

           last_interval = current_interval

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
@app.route('/video_feedC')
def video_feedC():
    return Response(generate_framesC(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detection_dataC')
def detection_dataC():
    data = []
    while not detection_queue.empty():
        data.append(detection_queue.get())
    return jsonify(data)   


#----------------------------------------------------------------------

video_path_D = r'C:\Users\yasmi\Documents\dash\static\video\zoneD.mp4'
cap = cv2.VideoCapture(video_path_D)

fps = cap.get(cv2.CAP_PROP_FPS)
frame_index = 0
tracker = sv.ByteTrack()

box_annotator = sv.BoundingBoxAnnotator()
label_annotator = sv.LabelAnnotator()
trace_annotator = sv.TraceAnnotator()

detection_queue = Queue()
initial_count = None          # mémorise le nombre de chariots au t = 0 s

# Nouvelle variable pour l'agrégation
last_interval = -1
def generate_framesD():
    global frame_index, last_interval, initial_count

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame_index += 1
        results = model(frame)[0]

        detections = sv.Detections.from_ultralytics(results)
        detections = detections[detections.confidence > 0.4]
        detections = tracker.update_with_detections(detections)
        
        # nombre de chariots détectés sur cette frame
        chariot_count = sum(
            1 for cid in detections.class_id if results.names[cid].lower() == "0"
        )
        
        # Initialisation du comptage
       # Initialisation du comptage
        if initial_count is None and chariot_count > 0:
            initial_count = chariot_count
            print(f"[INFO] Initial count fixé à {initial_count}")

         # ---------- calcul de l'alerte ----------
        alert = False
        alert_message = ""
        if chariot_count <= initial_count*0.5:
            alert = True
            alert_message = f"Alerte Alerte: pile presque vide ! Il reste {chariot_count} chariot{'s' if chariot_count > 1 else ''}."
            print(alert_message)

        labels = [
            f"#{tracker_id} {results.names[class_id]}"
            for class_id, tracker_id in zip(detections.class_id, detections.tracker_id)
        ]

        frame = box_annotator.annotate(frame, detections)
        frame = label_annotator.annotate(frame, detections, labels)
        frame = trace_annotator.annotate(frame, detections)

        # Temps vidéo en secondes
        video_time = round(frame_index / fps, 2)
        current_interval = int(video_time // 5)

        if current_interval != last_interval:
            # on met aussi le flag d'alerte dans la queue
           detection_queue.put({"time": video_time, "count": chariot_count, "alert": alert, "message": alert_message})

           last_interval = current_interval

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
@app.route('/video_feedD')
def video_feedD():
    return Response(generate_framesD(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detection_dataD')
def detection_dataD():
    data = []
    while not detection_queue.empty():
        data.append(detection_queue.get())
    return jsonify(data) 


if __name__ == '__main__':
    app.run(debug=True)
