if __name__ == '__main__':

    from detectron2 import model_zoo
    from detectron2.config import get_cfg
    from detectron2.engine import DefaultTrainer
    from detectron2.evaluation import COCOEvaluator, inference_on_dataset
    from detectron2.data import build_detection_test_loader
    from detectron2.data.datasets import register_coco_instances

    import os

    # Enregistrer les datasets
    register_coco_instances(
        "my_dataset_train", {},
        r"C:\Users\yasmi\Documents\dash\data\annotations\_annotations_train_coco.json",
        r"C:\Users\yasmi\Documents\dash\data\train"
    )

    register_coco_instances(
        "my_dataset_val", {},
        r"C:\Users\yasmi\Documents\dash\data\annotations\_annotations_valid_coco.json",
        r"C:\Users\yasmi\Documents\dash\data\valid"
    )

    cfg = get_cfg()

    # Utiliser Cascade R-CNN
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/cascade_rcnn_R_50_FPN_3x.yaml"))

    cfg.DATASETS.TRAIN = ("my_dataset_train",)
    cfg.DATASETS.TEST = ("my_dataset_val",)
    cfg.DATALOADER.NUM_WORKERS = 0
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/cascade_rcnn_R_50_FPN_3x.yaml")

    cfg.SOLVER.IMS_PER_BATCH = 2
    cfg.SOLVER.BASE_LR = 0.00025
    cfg.SOLVER.MAX_ITER = 1000
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 64
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 2  # à adapter à ton nombre de classes

    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

    trainer = DefaultTrainer(cfg)
    trainer.resume_or_load(resume=False)
    trainer.train()

    # Évaluation
    evaluator = COCOEvaluator("my_dataset_val", cfg, False, output_dir="./output")
    val_loader = build_detection_test_loader(cfg, "my_dataset_val")
    inference_on_dataset(trainer.model, val_loader, evaluator)
