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
import mysql.connector
from datetime import date
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
def doGetData1():
    selected_date = request.args.get('date')  
    data1 = []

    conn = mysql.connect()
    cursor = conn.cursor()

    # Requête pour récupérer nbr_chariot pour chaque zone à une date donnée
    query = """
        SELECT zone, nbr_chariot
        FROM pile
        WHERE date = %s
        ORDER BY zone
    """
    cursor.execute(query, (selected_date,))
    results = cursor.fetchall()

    for row in results:
        data1.append({
            "zone": row[0],
            "nombre_de_chariots": row[1]
        })

    cursor.close()
    return json.dumps(data1)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/api/data3")
def doGetData3():
    selected_date = request.args.get('date')

    data = []
    conn = mysql.connect()
    cursor = conn.cursor()

    query = """
       SELECT zone, nbr_alertes
        FROM pile
        WHERE date = %s
        ORDER BY zone
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

@app.route('/camera')
def camera_view():
    return render_template("camera.html")
#------------------------------------------------------------------------------------------Zone A----------------------------------------------------------------------------------------------

@app.route('//api/media')
def get_data_by_date():
    selected_date = request.args.get('date')
    cursor = mysql.connect().cursor()
    query = "SELECT graph_path, video_path FROM pile WHERE date = %s"
    cursor.execute(query, (selected_date,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return json.dumps({"image": result[0], "video": result[1]})
    else:
        return json.dumps({"image": None, "video": None})
#----------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True)
