# %load /kaggle/working/LGSC-for-FAS/train.py
import paddle.fluid as fluid
from models.scan import SCAN
from utils.runner import Runnner
from dataset.faceforensics import FaceForensics
import warnings
warnings.filterwarnings("ignore")

model_cfg = dict(
    backbone=dict(
        depth=18,
        out_indices=(0, 1, 2, 3),
        frozen_stages=-1),
    neck=dict(
        norm_cfg=dict(type='IN')),
    head=dict(
        depth=18,
        out_indices=(3,),
        norm_cfg=dict(type='BN'),
        dropout=0.5),
    train_cfg=dict(
        w_cls=5.0,
        w_tri=1.0,
        w_reg=5.0,
        with_mask=False),
    test_cfg=dict(
        thr=0.5),
    pretrained='./pretrained/resnet18-torch',
#    pretrained=None,
)

checkpoint_cfg = dict(
    work_dir='./checkpoint/ff_add_val',
    load_from='./checkpoint/ff_c23/Best_model',
    save_interval=1000,
    eval_interval=500,
    log_interval=250,
    eval_type='acc'
)

optimizer_cfg = dict(
    lr=0.0005,
    type='Adam',
    warmup_iter=1000,
    decay_epoch=[5, 8, 12],
    decay=0.3,
    regularization=0.0005,
)

extra_aug = dict(
    #photo_metric_distortion=dict(
    #    brightness_delta=32,
    #    contrast_range=(0.5, 1.5),
    #    saturation_range=(0.8, 1.2),
    #    hue_delta=16),
    #random_erasing=dict(
    #    probability=0.5,
    #    area=(0.01, 0.03),
    #    mean=(80, 80, 80)),
    random_cutout=None,
    ramdom_rotate=None,
    ramdom_crop=None,
    photo_metric_distortion=None,
    random_erasing=None,
    #random_cutout=dict(
    #    probability=0.5,
    #    max_edge=20),
    #ramdom_rotate=dict(
    #    probability=0.5,
    #    angle=30),
    #ramdom_crop=dict(
    #    probability=0.5,
    #    w_h=(0.12, 0.12))
)

data_root = '/'
train_dataset = FaceForensics(
    img_prefix=data_root,
    ann_file='/kaggle/working/train.txt',
    mask_file=None,
    img_scale=(224, 224),
    img_norm_cfg=dict(mean=(100, 100, 100), std=(80, 80, 80)),
    extra_aug=extra_aug,
    crop_face=False,
)

val_dataset = FaceForensics(
    img_prefix=data_root,
    ann_file='/kaggle/working/valid.txt',
    img_scale=(224, 224),
    img_norm_cfg=dict(mean=(100, 100, 100), std=(80, 80, 80)),
    extra_aug=dict(),
    test_mode=True,
    crop_face=False,
)


with fluid.dygraph.guard():
    model = SCAN(**model_cfg)

runner = Runnner(
    model,
    train_dataset,
    val_dataset=val_dataset,
    batch_size=64,
    checkpoint_config=checkpoint_cfg,
    optimizer_config=optimizer_cfg)

runner.train(max_epochs=30)
