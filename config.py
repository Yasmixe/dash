_base_ = 'cascade-rcnn_r50_fpn_1x_coco.py'

data = dict(
    train=dict(
        ann_file=r'C:\Users\yasmi\Documents\dash\data\annotations\_annotations_train_coco.json',
        img_prefix=r'C:\Users\yasmi\Documents\dash\data\train'),
    val=dict(
        ann_file=r'C:\Users\yasmi\Documents\dash\data\annotations\_annotations_valid_coco.json',
        img_prefix=r'C:\Users\yasmi\Documents\dash\data\valid'),
    test=dict(
        ann_file=r'C:\Users\yasmi\Documents\dash\data\annotations\_annotations_test_coco.json',
        img_prefix=r'C:\Users\yasmi\Documents\dash\data\test'))

model = dict(
    roi_head=dict(
        bbox_head=[
            dict(
                type='Shared2FCBBoxHead',
                in_channels=256,
                fc_out_channels=1024,
                roi_feat_size=7,
                num_classes=2,
                bbox_coder=dict(
                    type='DeltaXYWHBBoxCoder',
                    target_means=[0.0, 0.0, 0.0, 0.0],
                    target_stds=[0.1, 0.1, 0.2, 0.2]
                ),
                reg_class_agnostic=False,
                loss_cls=dict(
                    type='CrossEntropyLoss',
                    use_sigmoid=False,
                    loss_weight=1.0
                ),
                loss_bbox=dict(
                    type='L1Loss',
                    loss_weight=1.0
                )
            ),
            dict(
                type='Shared2FCBBoxHead',
                in_channels=256,
                fc_out_channels=1024,
                roi_feat_size=7,
                num_classes=2,
                bbox_coder=dict(
                    type='DeltaXYWHBBoxCoder',
                    target_means=[0.0, 0.0, 0.0, 0.0],
                    target_stds=[0.05, 0.05, 0.1, 0.1]
                ),
                reg_class_agnostic=False,
                loss_cls=dict(
                    type='CrossEntropyLoss',
                    use_sigmoid=False,
                    loss_weight=1.0
                ),
                loss_bbox=dict(
                    type='L1Loss',
                    loss_weight=1.0
                )
            ),
            dict(
                type='Shared2FCBBoxHead',
                in_channels=256,
                fc_out_channels=1024,
                roi_feat_size=7,
                num_classes=2,
                bbox_coder=dict(
                    type='DeltaXYWHBBoxCoder',
                    target_means=[0.0, 0.0, 0.0, 0.0],
                    target_stds=[0.033, 0.033, 0.067, 0.067]
                ),
                reg_class_agnostic=False,
                loss_cls=dict(
                    type='CrossEntropyLoss',
                    use_sigmoid=False,
                    loss_weight=1.0
                ),
                loss_bbox=dict(
                    type='L1Loss',
                    loss_weight=1.0
                )
            )
        ]
    )
)


# Adjust training schedule (small dataset? reduce epochs)
optimizer = dict(lr=0.02 / 1)  # Learning rate for 8 GPUs (adjust if using 1 GPU)
runner = dict(max_epochs=1)    # Train for 12 epochs