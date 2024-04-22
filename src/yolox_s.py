#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Copyright (c) Megvii, Inc. and its affiliates.
import os

from yolox.exp import Exp


class Exp(Exp):
    def __init__(self):
        super(Exp, self).__init__()
        self.depth = 0.33
        self.width = 0.375
        self.input_size = (640, 640)
        #self.mosaic_scale = (0.5, 1.5)
        self.random_size = (10, 20)
        self.test_size = (640, 640) # ???
        self.exp_name = os.path.split(os.path.realpath(__file__))[1].split(".")[0]
        #self.enable_mixup = False     

        # Define yourself dataset path
        self.data_dir = r"datasets/coco"
        self.train_ann = r"instances_train2017.json"
        self.val_ann = r"instances_val2017.json"
        self.num_classes = 3 #количество классов	
        self.max_epoch = 800
        self.data_num_workers = 4 #4
        self.eval_interval = 1
        
        # --------------- transform config ----------------- #
        # prob of applying mosaic aug (try to off) 
        self.mosaic_prob = 0.0
        # prob of applying mixup aug (try to off)
        self.mixup_prob = 0.0
        # prob of applying hsv aug (change colors)
        self.hsv_prob = 1.0
        # prob of applying flip aug (flip img)
        self.flip_prob = 0.0
        # rotation angle range, for example, if set to 2, the true range is (-2, 2)
        self.degrees = 0.0
        # translate range, for example, if set to 0.1, the true range is (-0.1, 0.1)
        self.translate = 0.1 
        self.mosaic_scale = (0.0, 0.0) # (try to off)
        # apply mixup aug or not
        self.enable_mixup = False
        self.mixup_scale = (0.0, 0.0) # (try to off)
        # shear angle range, for example, if set to 2, the true range is (-2, 2)
        self.shear = 2.0

        # -----------------  testing config ------------------ #
        # output image size during evaluation/test
        self.test_size = (640, 640)
        # confidence threshold during evaluation/test,
        # boxes whose scores are less than test_conf will be filtered
        self.test_conf = 0.7
        # nms threshold
        self.nmsthre = 0.45