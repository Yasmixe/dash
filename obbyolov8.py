import os
import cv2
import numpy as np

# Dossiers
images_dir = r"C:\Users\yasmi\Documents\dash\MyProject.v4i.yolov8-obb\train\images"
labels_dir = r"C:\Users\yasmi\Documents\dash\MyProject.v4i.yolov8-obb\train\labels"

# Fonction pour lire les fichiers YOLO OBB
def read_yolo_obb_label(label_path, img_width, img_height):
    boxes = []
    with open(label_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split()
            if len(parts) != 9:
                continue  # Skip malformed lines
            class_id = int(parts[0])
            coords = list(map(float, parts[1:]))
            # Convertir les coordonnées normalisées en pixels
            coords = [int(coords[i] * (img_width if i % 2 == 0 else img_height)) for i in range(8)]
            boxes.append((class_id, coords))
    return boxes

# Affichage
for img_name in os.listdir(images_dir):
    if not img_name.endswith(('.jpg', '.png')):
        continue
    img_path = os.path.join(images_dir, img_name)
    label_path = os.path.join(labels_dir, os.path.splitext(img_name)[0] + '.txt')

    image = cv2.imread(img_path)
    if image is None:
        print(f"Impossible de lire l'image {img_path}")
        continue

    height, width = image.shape[:2]

    if os.path.exists(label_path):
        boxes = read_yolo_obb_label(label_path, width, height)
        for class_id, coords in boxes:
            # Créer un tableau de points pour le polygone
            pts = np.array([(coords[i], coords[i + 1]) for i in range(0, 8, 2)], dtype=np.int32)
            cv2.polylines(image, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
            # Afficher la classe
            cv2.putText(image, f'Class {class_id}', tuple(pts[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    else:
        print(f"Aucun label trouvé pour {img_name}")

    cv2.imshow("Image avec BBox OBB", image)
    key = cv2.waitKey(0)
    if key == 'q':  # ESC pour quitter
        break

cv2.destroyAllWindows()
