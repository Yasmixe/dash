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
cap_A = cv2.VideoCapture(video_path_A)

fps_A = cap_A.get(cv2.CAP_PROP_FPS)
frame_index_A = 0
tracker_A = sv.ByteTrack()

box_annotator_A = sv.BoundingBoxAnnotator()
label_annotator_A = sv.LabelAnnotator()
trace_annotator_A = sv.TraceAnnotator()

detection_queue_A = Queue()
initial_count_A = None          # mémorise le nombre de chariots au t = 0 s

# Nouvelle variable pour l'agrégation
last_interval_A = -1
def generate_framesA():
    global frame_index_A, last_interval_A, initial_count_A

    while cap_A.isOpened():
        success, frame = cap_A.read()
        if not success:
            break

        frame_index_A += 1
        results_A = model(frame)[0]

        detections = sv.Detections.from_ultralytics(results_A)
        detections = detections[detections.confidence > 0.4]
        detections = tracker_A.update_with_detections(detections)
        
        # nombre de chariots détectés sur cette frame
        chariot_count_A = sum(
            1 for cid in detections.class_id if results_A.names[cid].lower() == "0"
        )
        
        # Initialisation du comptage
       # Initialisation du comptage
        if initial_count_A is None and chariot_count_A > 0:
            initial_count_A = chariot_count_A
            print(f"[INFO] Initial count fixé à {initial_count_A}")

         # ---------- calcul de l'alerte ----------
        alert = False
        alert_message = ""
        if chariot_count_A <= initial_count_A*0.5:
            alert = True
            alert_message = f"Alerte Alerte: pile presque vide ! Il reste {chariot_count_A} chariot{'s' if chariot_count_A > 1 else ''}."
            print(alert_message)

        labels = [
            f"#{tracker_id} {results_A.names[class_id]}"
            for class_id, tracker_id in zip(detections.class_id, detections.tracker_id)
        ]

        frame = box_annotator_A.annotate(frame, detections)
        frame = label_annotator_A.annotate(frame, detections, labels)
        frame = trace_annotator_A.annotate(frame, detections)

        # Temps vidéo en secondes
        video_time_A = round(frame_index_A / fps_A, 2)
        current_interval_A = int(video_time_A // 5)

        if current_interval_A != last_interval_A:
            # on met aussi le flag d'alerte dans la queue
           detection_queue_A.put({"time": video_time_A, "count": chariot_count_A, "alert": alert, "message": alert_message})

           last_interval_A = current_interval_A

        ret_A, buffer_A = cv2.imencode('.jpg', frame)
        frame_bytes_A = buffer_A.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes_A + b'\r\n')
    
@app.route('/video_feedA')
def video_feedA():
    return Response(generate_framesA(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detection_dataA')
def detection_dataA():
    dataA = []
    while not detection_queue_A.empty():
        dataA.append(detection_queue_A.get())
    return jsonify(dataA)   
#----------------------------------------------------------------------

video_path_B = r'C:\Users\yasmi\Documents\dash\static\video\zoneB.mp4'
cap_B = cv2.VideoCapture(video_path_B)

fps_B = cap_B.get(cv2.CAP_PROP_FPS)
frame_index_B = 0
tracker_B = sv.ByteTrack()

box_annotator_B = sv.BoundingBoxAnnotator()
label_annotator_B = sv.LabelAnnotator()
trace_annotator_B = sv.TraceAnnotator()

detection_queue_B = Queue()
initial_count_B = None          # mémorise le nombre de chariots au t = 0 s

# Nouvelle variable pour l'agrégation
last_interval_B = -1
def generate_framesB():
    global frame_index_B, last_interval_B, initial_count_B

    while cap_B.isOpened():
        success, frame = cap_B.read()
        if not success:
            break

        frame_index_B += 1
        results_B = model(frame)[0]

        detections = sv.Detections.from_ultralytics(results_B)
        detections = detections[detections.confidence > 0.4]
        detections = tracker_B.update_with_detections(detections)
        
        # nombre de chariots détectés sur cette frame
        chariot_count_B = sum(
            1 for cid in detections.class_id if results_B.names[cid].lower() == "0"
        )
        
        # Initialisation du comptage
       # Initialisation du comptage
        if initial_count_B is None and chariot_count_B > 0:
            initial_count_B = chariot_count_B
            print(f"[INFO] Initial count fixé à {initial_count_B}")

         # ---------- calcul de l'alerte ----------
        alert = False
        alert_message = ""
        if chariot_count_B <= initial_count_B*0.5:
            alert = True
            alert_message = f"Alerte Alerte: pile presque vide ! Il reste {chariot_count_B} chariot{'s' if chariot_count_B > 1 else ''}."
            print(alert_message)

        labels = [
            f"#{tracker_id} {results_B.names[class_id]}"
            for class_id, tracker_id in zip(detections.class_id, detections.tracker_id)
        ]

        frame = box_annotator_B.annotate(frame, detections)
        frame = label_annotator_B.annotate(frame, detections, labels)
        frame = trace_annotator_B.annotate(frame, detections)

        # Temps vidéo en secondes
        video_time_B = round(frame_index_B / fps_B, 2)
        current_interval_B = int(video_time_B // 5)

        if current_interval_B != last_interval_B:
            # on met aussi le flag d'alerte dans la queue
           detection_queue_B.put({"time": video_time_B, "count": chariot_count_B, "alert": alert, "message": alert_message})

           last_interval_B = current_interval_B

        ret_B, buffer_B = cv2.imencode('.jpg', frame)
        frame_bytes_B = buffer_B.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes_B + b'\r\n')
    
@app.route('/video_feedB')
def video_feedB():
    return Response(generate_framesB(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detection_dataB')
def detection_dataB():
    dataB = []
    while not detection_queue_B.empty():
        dataB.append(detection_queue_B.get())
    return jsonify(dataB)   

#----------------------------------------------------------------------

video_path_D = r'C:\Users\yasmi\Documents\dash\static\video\zoneD.mp4'
cap_D = cv2.VideoCapture(video_path_D)

fps_D = cap_D.get(cv2.CAP_PROP_FPS)
frame_index_D = 0
tracker_D = sv.ByteTrack()

box_annotator_D = sv.BoundingBoxAnnotator()
label_annotator_D = sv.LabelAnnotator()
trace_annotator_D = sv.TraceAnnotator()
detection_queue_D = Queue()
initial_count_D = None          # mémorise le nombre de chariots au t = 0 s

# Nouvelle variable pour l'agrégation
last_interval_D = -1
def generate_framesD():
    global frame_index_D, last_interval_D, initial_count_D

    while cap_D.isOpened():
        success, frame = cap_D.read()
        if not success:
            break

        frame_index_D += 1
        results_D = model(frame)[0]

        detections = sv.Detections.from_ultralytics(results_D)
        detections = detections[detections.confidence > 0.4]
        detections = tracker_D.update_with_detections(detections)
        
        # nombre de chariots détectés sur cette frame
        chariot_count_D = sum(
            1 for cid in detections.class_id if results_D.names[cid].lower() == "0"
        )
        
        # Initialisation du comptage
       # Initialisation du comptage
        if initial_count_D is None and chariot_count_D > 0:
            initial_count_D = chariot_count_D
            print(f"[INFO] Initial count fixé à {initial_count_D}")

         # ---------- calcul de l'alerte ----------
        alert = False
        alert_message = ""
        if chariot_count_D <= initial_count_D*0.5:
            alert = True
            alert_message = f"Alerte Alerte: pile presque vide ! Il reste {chariot_count_D} chariot{'s' if chariot_count_D > 1 else ''}."
            print(alert_message)

        labels = [
            f"#{tracker_id} {results_D.names[class_id]}"
            for class_id, tracker_id in zip(detections.class_id, detections.tracker_id)
        ]

        frame = box_annotator_D.annotate(frame, detections)
        frame = label_annotator_D.annotate(frame, detections, labels)
        frame = trace_annotator_D.annotate(frame, detections)

        # Temps vidéo en secondes
        video_time_D = round(frame_index_D / fps_D, 2)
        current_interval_D = int(video_time_D // 5)

        if current_interval_D != last_interval_D:
            # on met aussi le flag d'alerte dans la queue
           detection_queue_D.put({"time": video_time_D, "count": chariot_count_D, "alert": alert, "message": alert_message})

           last_interval_D = current_interval_D

        ret_D, buffer_D = cv2.imencode('.jpg', frame)
        frame_bytes_D = buffer_D.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes_D + b'\r\n')
    
@app.route('/video_feedD')
def video_feedD():
    return Response(generate_framesD(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detection_dataD')
def detection_dataD():
    dataD = []
    while not detection_queue_D.empty():
        dataD.append(detection_queue_D.get())
    return jsonify(dataD) 

#----------------------------------------------------------------------

video_path_C = r'C:\Users\yasmi\Documents\dash\static\video\zoneC.mp4'
cap_C = cv2.VideoCapture(video_path_C)

fps_C = cap_C.get(cv2.CAP_PROP_FPS)
frame_index_C = 0
tracker_C = sv.ByteTrack()

box_annotator_C = sv.BoundingBoxAnnotator()
label_annotator_C = sv.LabelAnnotator()
trace_annotator_C = sv.TraceAnnotator()
detection_queue_C = Queue()
initial_count_C = None          # mémorise le nombre de chariots au t = 0 s

# Nouvelle variable pour l'agrégation
last_interval_C = -1
def generate_framesC():
    global frame_index_C, last_interval_C, initial_count_C

    while cap_C.isOpened():
        success, frame = cap_C.read()
        if not success:
            break

        frame_index_C += 1
        results_C = model(frame)[0]

        detections = sv.Detections.from_ultralytics(results_C)
        detections = detections[detections.confidence > 0.4]
        detections = tracker_C.update_with_detections(detections)
        
        # nombre de chariots détectés sur cette frame
        chariot_count_C = sum(
            1 for cid in detections.class_id if results_C.names[cid].lower() == "0"
        )
        
        # Initialisation du comptage
       # Initialisation du comptage
        if initial_count_C is None and chariot_count_C > 0:
            initial_count_C = chariot_count_C
            print(f"[INFO] Initial count fixé à {initial_count_C}")

         # ---------- calcul de l'alerte ----------
        alert = False
        alert_message = ""
        if chariot_count_C <= initial_count_C*0.5:
            alert = True
            alert_message = f"Alerte Alerte: pile presque vide ! Il reste {chariot_count_C} chariot{'s' if chariot_count_C > 1 else ''}."
            print(alert_message)

        labels = [
            f"#{tracker_id} {results_C.names[class_id]}"
            for class_id, tracker_id in zip(detections.class_id, detections.tracker_id)
        ]

        frame = box_annotator_C.annotate(frame, detections)
        frame = label_annotator_C.annotate(frame, detections, labels)
        frame = trace_annotator_C.annotate(frame, detections)

        # Temps vidéo en secondes
        video_time_C = round(frame_index_C / fps_C, 2)
        current_interval_C = int(video_time_C // 5)

        if current_interval_C != last_interval_C:
            # on met aussi le flag d'alerte dans la queue
           detection_queue_C.put({"time": video_time_C, "count": chariot_count_C, "alert": alert, "message": alert_message})

           last_interval_C = current_interval_C

        ret_C, buffer_C = cv2.imencode('.jpg', frame)
        frame_bytes_C = buffer_C.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes_C + b'\r\n')
    
@app.route('/video_feedC')
def video_feedC():
    return Response(generate_framesC(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detection_dataC')
def detection_dataC():
    dataC = []
    while not detection_queue_C.empty():
        dataC.append(detection_queue_C.get())
    return jsonify(dataC)  


if __name__ == '__main__':
    app.run(debug=True)
