from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import json
from ultralytics import YOLO
from flaskext.mysql import MySQL
import mysql.connector
from datetime import date
from functools import wraps
import mysql.connector
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
model = YOLO(r"C:\Users\yasmi\Documents\dash\runs\obb\train73\weights\bestyoloobb11_hyperparametres.pt", verbose=False)
from werkzeug.security import check_password_hash, generate_password_hash
app = Flask(__name__)
app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_PORT"] = 3306
app.config["MYSQL_DATABASE_USER"] = "yasmine"
app.config["MYSQL_DATABASE_PASSWORD"] = "yasminehanafi"
app.config["MYSQL_DATABASE_DB"] = "entrepot_airport"
mysql = MySQL()
mysql.init_app(app)

CORS(app)


app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

global video_path

# Initialize YOLO model and trackers
print('torch.cuda.is_available:', torch.cuda.is_available())
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print(f'Using device: {device}')

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


app.secret_key = 'votre_cle_secrete_ici'  # Ne pas la changer après lancement en production

USERS = {
    'staff.airport@gmail.com': generate_password_hash('staff123'),
    'admin.airport@gmail.com': generate_password_hash('admin123')
}

# Décorateur de protection
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash("Veuillez vous connecter pour accéder à cette page", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')

        if not user_id or not password:
            flash('Veuillez remplir tous les champs', 'error')
            return render_template('login.html')

        if user_id in USERS and check_password_hash(USERS[user_id], password):
            session['user_id'] = user_id
            flash('Connexion réussie !', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Identifiant ou mot de passe incorrect', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Vous avez été déconnecté', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user_id=session['user_id'])


@app.route('/home')
@login_required
def home():
    return render_template('home.html', user_id=session['user_id'])



# ---------------------
@app.route('/camera')
def camera_view():
    return render_template("camera.html")
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#afficher le nombre de chariot detectes dans chaque zone 
@app.route("/api/data1")
def doGetData1():
    selected_date = request.args.get('date')  
    data1 = []

    conn = mysql.connect()
    cursor = conn.cursor()

    # Requête adaptée pour récupérer nbr_chariot_detected par zone pour une date donnée
    query = """
        SELECT z.nom_zone, SUM(f.nbr_chariot_detected) as total_chariots
        FROM F_ZONE f
        JOIN DIM_ZONE z ON f.id_zone = z.id_zone
        JOIN DIM_TEMPS t ON f.id_temps = t.id_temps
        WHERE t.date = %s
        GROUP BY z.nom_zone
        ORDER BY z.nom_zone
    """
    cursor.execute(query, (selected_date,))
    results = cursor.fetchall()

    for row in results:
        data1.append({
            "zone": row[0],  # nom_zone (par exemple, "zone A")
            "nombre_de_chariots": row[1]  # total_chariots
        })

    cursor.close()
    conn.close()  # Fermer la connexion pour éviter les fuites
    return jsonify(data1)  # Utiliser jsonify pour un format JSON propre
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#afficher le nombre d'alertes  detectes dans chaque zone 
@app.route("/api/data3")
def doGetData3():
    selected_date = request.args.get('date')

    data = []
    conn = mysql.connect()
    cursor = conn.cursor()

    # Requête adaptée pour récupérer le nombre d'alertes par zone pour une date donnée
    query = """
        SELECT z.nom_zone, SUM(a.nb_alerte) as total_alertes
        FROM F_ZONE f
        JOIN DIM_ZONE z ON f.id_zone = z.id_zone
        JOIN DIM_TEMPS t ON f.id_temps = t.id_temps
        JOIN DIM_ALERTE a ON f.id_alerte = a.id_alerte
        WHERE t.date = %s
        GROUP BY z.nom_zone
        ORDER BY z.nom_zone
    """
    cursor.execute(query, (selected_date,))
    results = cursor.fetchall()

    for row in results:
        data.append({
            "zone": row[0],  # nom_zone (par exemple, "zone A")
            "nombre_alertes": row[1] if row[1] is not None else 0  # total_alertes
        })

    cursor.close()
    conn.close()  # Fermer la connexion pour éviter les fuites
    return jsonify(data)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------Zone A----------------------------------------------------------------------------------------------
#taux d'alertes

@app.route('/api/data2')
def get_data_by_date():
    selected_date = request.args.get('date')
    data = []
    conn = mysql.connect()
    cursor = conn.cursor()

    # Requête pour récupérer uniquement nom_zone et alerte_rate
    query = """
        SELECT 
            z.nom_zone,
            (COALESCE(SUM(a.nb_alerte), 0) * 100.0 / NULLIF(COALESCE(SUM(f.nbr_chariot_detected), 0), 0)) as alerte_rate
        FROM F_ZONE f
        JOIN DIM_ZONE z ON f.id_zone = z.id_zone
        JOIN DIM_TEMPS t ON f.id_temps = t.id_temps
        JOIN DIM_ALERTE a ON f.id_alerte = a.id_alerte
        WHERE t.date = %s
        GROUP BY z.nom_zone
        ORDER BY z.nom_zone
    """
    cursor.execute(query, (selected_date,))
    results = cursor.fetchall()

    for row in results:
        data.append({
            "zone": row[0],  # nom_zone
            "alerte_rate": row[1] if row[1] is not None else 0  # alerte_rate (0 si indéfini)
        })

    cursor.close()
    conn.close()
    return jsonify(data)
#----------------------------------------------------------------------


#correlation entre chariot et alertes
@app.route('/api/data4')
def get_alert_rate_by_date():
    data = []
    conn = mysql.connect()
    cursor = conn.cursor()

    # Récupérer le premier et le dernier jour dans DIM_TEMPS
    query_dates = """
        SELECT MIN(date) as start_date, MAX(date) as end_date
        FROM DIM_TEMPS
    """
    cursor.execute(query_dates)
    date_range = cursor.fetchone()

    if date_range[0] is None or date_range[1] is None:
        return jsonify({"error": "Aucune date trouvée dans DIM_TEMPS"}), 400

    start_date = date_range[0].strftime('%Y-%m-%d')
    end_date = date_range[1].strftime('%Y-%m-%d')

    # Requête pour récupérer le taux d'alertes par date
    query = """
        SELECT 
            t.date,
            (COALESCE(SUM(a.nb_alerte), 0) * 100.0 / NULLIF(COALESCE(SUM(f.nbr_chariot_detected), 0), 0)) as alerte_rate
        FROM F_ZONE f
        JOIN DIM_TEMPS t ON f.id_temps = t.id_temps
        JOIN DIM_ALERTE a ON f.id_alerte = a.id_alerte
        WHERE t.date BETWEEN %s AND %s
        GROUP BY t.date
        ORDER BY t.date
    """
    cursor.execute(query, (start_date, end_date))
    results = cursor.fetchall()

    # Préparer la réponse avec uniquement la date et le taux
    for row in results:
        data.append({
            "date": row[0].strftime('%Y-%m-%d'),  # Formater la date
            "alerte_rate": row[1] if row[1] is not None else 0  # Taux d'alertes (0 si indéfini)
        })

    cursor.close()
    conn.close()
    return jsonify(data)


#------------------------------------------------------------------------------------------------------------
# pour chaque jour le nbr d'alerte maximal
@app.route('/api/data5')
def get_max_alerts_by_date():
    data = []
    conn = mysql.connect()
    cursor = conn.cursor()

    # Récupérer le premier et le dernier jour dans DIM_TEMPS
    query_dates = """
        SELECT MIN(date) as start_date, MAX(date) as end_date
        FROM DIM_TEMPS
    """
    cursor.execute(query_dates)
    date_range = cursor.fetchone()

    if date_range[0] is None or date_range[1] is None:
        return jsonify({"error": "Aucune date trouvée dans DIM_TEMPS"}), 400

    start_date = date_range[0].strftime('%Y-%m-%d')
    end_date = date_range[1].strftime('%Y-%m-%d')

    # Requête pour obtenir la zone avec le plus d'alertes par jour
    query = """
        SELECT 
            t.date,
            z.nom_zone,
            COALESCE(SUM(a.nb_alerte), 0) as max_alertes
        FROM F_ZONE f
        JOIN DIM_TEMPS t ON f.id_temps = t.id_temps
        JOIN DIM_ZONE z ON f.id_zone = z.id_zone
        JOIN DIM_ALERTE a ON f.id_alerte = a.id_alerte
        WHERE t.date BETWEEN %s AND %s
        GROUP BY t.date, z.nom_zone
        HAVING COALESCE(SUM(a.nb_alerte), 0) = (
            SELECT COALESCE(SUM(a2.nb_alerte), 0)
            FROM F_ZONE f2
            JOIN DIM_TEMPS t2 ON f2.id_temps = t2.id_temps
            JOIN DIM_ZONE z2 ON f2.id_zone = z2.id_zone
            JOIN DIM_ALERTE a2 ON f2.id_alerte = a2.id_alerte
            WHERE t2.date = t.date
            GROUP BY z2.nom_zone
            ORDER BY COALESCE(SUM(a2.nb_alerte), 0) DESC
            LIMIT 1
        )
        ORDER BY t.date
    """
    cursor.execute(query, (start_date, end_date))
    results = cursor.fetchall()

    # Préparer la réponse
    current_date = None
    for row in results:
        date_str = row[0].strftime('%Y-%m-%d')
        if current_date != date_str:
            data.append({
                "date": date_str,
                "zone_max_alertes": row[1],  # Nom de la zone avec le max d'alertes
                "max_alertes": row[2]       # Nombre d'alertes
            })
            current_date = date_str

    cursor.close()
    conn.close()
    return jsonify(data)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/api/data6', methods=['GET'])
def chariots_min_max_par_zone():
    data = []
    conn = mysql.connect()
    cursor = conn.cursor()

    query = """
        SELECT
    stats.nom_zone,
    MAX(stats.total_chariots) AS max_chariots,
    MIN(stats.total_chariots) AS min_chariots
FROM (
    SELECT
        z.nom_zone,
        t.date,
        SUM(f.nbr_chariot_detected) AS total_chariots
    FROM F_ZONE f
    JOIN DIM_ZONE z ON f.id_zone = z.id_zone
    JOIN DIM_TEMPS t ON f.id_temps = t.id_temps
    GROUP BY z.nom_zone, t.date
) AS stats
GROUP BY stats.nom_zone
ORDER BY stats.nom_zone;

    """

    cursor.execute(query)
    results = cursor.fetchall()

    for row in results:
        data.append({
            "zone": row[0],
            "max_chariots": row[1],
            "min_chariots": row[2]
        })

    cursor.close()
    conn.close()
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
