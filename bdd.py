import os
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, jsonify
from flaskext.mysql import MySQL

# === Connexion à la base SQLite ===

app = Flask(__name__)
app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_PORT"] = 3306
app.config["MYSQL_DATABASE_USER"] = "yasmine"
app.config["MYSQL_DATABASE_PASSWORD"] = "yasminehanafi"
app.config["MYSQL_DATABASE_DB"] = "entrepot_airport"

mysql = MySQL(app)

base_path = r'C:\Users\yasmi\Documents\dash\static\videos\zone D'

processed_folder = os.path.join(base_path, 'video')
csv_folder = os.path.join(base_path, 'csv')
graph_folder = os.path.join(base_path, 'graphe')

start_date = datetime(2025, 6, 1)
video_files = [f for f in os.listdir(processed_folder) if f.endswith('.mp4') or f.endswith('.mov')]

with app.app_context():
    conn = mysql.connect()
    cursor = conn.cursor()    

    for i, video_file in enumerate(sorted(video_files)):
        nom_complet = os.path.splitext(video_file)[0]  # IMG_4287_annotated
        nom = nom_complet.replace("_annotated", "")
        date = start_date + timedelta(days=i)
        formatted_date = date.strftime('%Y-%m-%d')

        processed_path = os.path.join('static', 'videos', 'zone D', 'videos', f'{nom}_annotated.mp4')
        csv_path = os.path.join('static', 'videos', 'zone D', 'csv', f'detection_data_{nom}.csv')
        graph_path = os.path.join('static', 'videos', 'zone D', 'graphe', f'chariot_count_plot_{nom}.png')

        # Chargement du CSV
        csv_full_path = os.path.join(csv_folder, f'detection_data_{nom}.csv')
        if not os.path.exists(csv_full_path):
            print(f"[⚠️] CSV manquant pour {nom}, ignoré.")
            continue

        import pandas as pd

        df = pd.read_csv(csv_path)
        nbr_chariot_max = df['count'].max()
        nbr_chariot_min = df['count'].min()
        nbr_alertes = df['alert'].sum()
        id_zone = i+11
        id_temps = i + 11
        id_info = i + 11
        id_alerte = i + 11
        
# Insertion dans DIM_ZONE (si ce n’est pas déjà fait)
        cursor.execute('''
    INSERT INTO DIM_ZONE (id_zone, nom_zone)
    VALUES (%s, %s)
''', (id_zone, 'zone D'))

# Insertion dans DIM_TEMPS
        cursor.execute('''
    INSERT INTO DIM_TEMPS (id_temps, date)
    VALUES (%s, %s)
''', (id_temps, formatted_date))

# Insertion dans DIM_ALERTE
        cursor.execute('''
    INSERT INTO DIM_ALERTE (id_alerte, type_alerte, id_zone, nb_alerte)
    VALUES (%s, %s, %s, %s)
''', (id_alerte, 'chariot presque vide', id_zone, int(nbr_alertes)))

# Insertion dans DIM_info
        cursor.execute('''
    INSERT INTO DIM_info (id_info, chemin_video_avant, chemin_video_apres, csv_file, graphe_file, id_zone)
    VALUES (%s, %s, %s, %s, %s, %s)
''', (id_info, '', processed_path, csv_path, graph_path, id_zone))

# Insertion dans la table de faits F_ZONE
        cursor.execute('''
    INSERT INTO F_ZONE (id_zone, id_temps, id_alerte, id_info, nbr_chariot_detected)
    VALUES (%s, %s, %s, %s, %s)
''', (id_zone, id_temps, id_alerte, id_info, int(nbr_chariot_max - nbr_chariot_min)))

        

    conn.commit()
    cursor.close()
    print("[✅] Données insérées dans la base MySQL.")