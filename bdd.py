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
app.config["MYSQL_DATABASE_DB"] = "airportchariot"

mysql = MySQL(app)

base_path = r'C:\Users\yasmi\Documents\dash\static\videos\zone B'
videos_folder = os.path.join(base_path, 'videos')
processed_folder = os.path.join(base_path, 'processed_videos')
csv_folder = os.path.join(base_path, 'csv_data')
graph_folder = os.path.join(base_path, 'graphs')

start_date = datetime(2025, 4, 1)
video_files = [f for f in os.listdir(videos_folder) if f.endswith('.mp4') or f.endswith('.mov')]

with app.app_context():
    conn = mysql.connect()
    cursor = conn.cursor()    

    for i, video_file in enumerate(sorted(video_files)):
        nom = os.path.splitext(video_file)[0]  # ex: 'zoneD'
        date = start_date + timedelta(days=i)
        formatted_date = date.strftime('%Y-%m-%d')

        processed_path = os.path.join('static', 'videos', 'zone B', 'processed_videos', f'{nom}_annotated.mp4')
        csv_path = os.path.join('static', 'videos', 'zone B', 'csv_data', f'detection_data_{nom}.csv')
        graph_path = os.path.join('static', 'videos', 'zone B', 'graphs', f'chariot_count_plot_{nom}.png')

        # Chargement du CSV
        csv_full_path = os.path.join(csv_folder, f'detection_data_{nom}.csv')
        if not os.path.exists(csv_full_path):
            print(f"[⚠️] CSV manquant pour {nom}, ignoré.")
            continue

        df = pd.read_csv(csv_full_path)
        nbr_chariot = df['count'].max()
        nbr_alertes = df['alert'].sum()

        # Insertion
        cursor.execute('''
            INSERT INTO pile (id, zone, nbr_chariot, nbr_alertes, date, video_path, graph_path, csv_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            i + 14,
            'zone B',
            int(nbr_chariot),
            int(nbr_alertes),
            formatted_date,
            processed_path,
            graph_path,
            csv_path
        ))

    conn.commit()
    cursor.close()
    print("[✅] Données insérées dans la base MySQL.")