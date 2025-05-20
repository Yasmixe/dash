import os
import cv2
from inference_sdk import InferenceHTTPClient

# Initialiser le client Roboflow
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="qYNmk1DMrtRsc7vjTOUh"
)

# Dossier contenant les images
input_folder = r"C:\Users\yasmi\OneDrive\Desktop\images\Nouveau dossier\images"
output_folder = os.path.join(input_folder, "output")

# Créer le dossier de sortie s'il n'existe pas
os.makedirs(output_folder, exist_ok=True)

# Parcourir toutes les images du dossier
for filename in os.listdir(input_folder):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        image_path = os.path.join(input_folder, filename)
        print(f"Traitement de : {filename}")

        # Charger l’image
        image = cv2.imread(image_path)
        orig_height, orig_width = image.shape[:2]

        # Appeler Roboflow
        try:
            result = CLIENT.infer(image_path, model_id="myproject-iwt1z/4")
        except Exception as e:
            print(f"Erreur d'inférence sur {filename} : {e}")
            continue

        rf_width = result['image']['width']
        rf_height = result['image']['height']
        x_scale = orig_width / rf_width
        y_scale = orig_height / rf_height

        # Dessiner les prédictions
        for prediction in result['predictions']:
            x = prediction['x']
            y = prediction['y']
            w = prediction['width']
            h = prediction['height']
            conf = prediction['confidence']
            label = prediction['class']

            x1 = int((x - w / 2) * x_scale)
            y1 = int((y - h / 2) * y_scale)
            x2 = int((x + w / 2) * x_scale)
            y2 = int((y + h / 2) * y_scale)

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f"{label} ({conf:.2f})", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Sauvegarder l’image annotée
        output_path = os.path.join(output_folder, filename)
        cv2.imwrite(output_path, image)

print("✅ Toutes les images ont été traitées et enregistrées dans le dossier 'output'.")
