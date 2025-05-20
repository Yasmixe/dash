import cv2
import numpy as np
from ultralytics import YOLO
import matplotlib.pyplot as plt
import matplotlib
import tkinter
matplotlib.use('Qt5Agg')  # Requires PyQt5

model = YOLO(r'C:\Users\yasmi\Documents\dash\best.pt')
results = model.predict(r"C:\Users\yasmi\Documents\dash\IMG_3713.JPG", conf=0.4)  # conf = seuil de confiance

# Afficher les résultats
results[0].show()