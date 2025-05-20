if __name__ == '__main__':

    from ultralytics import RTDETR

# Load a COCO-pretrained RT-DETR-l model
    model = RTDETR("rtdetr-l.pt")


# Entraîner le modèle sur le dataset COCO8 (exemple) pendant 100 epochs
    results = model.train(data=r"C:\Users\yasmi\Documents\dash\data\data.yaml", 
              epochs=100, 
               imgsz=512,
               batch=2,  
               workers=0,      
               device=0)