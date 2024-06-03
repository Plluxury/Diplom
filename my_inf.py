#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import json
import easyocr
from typing import Tuple, Union, Type, List
from datetime import datetime
import os
from loguru import logger
import cv2
import torch

from yolox.exp import get_exp

from src.message_encoder import MessageEncoder
from src.predictor import Predictor
from src.message import Message
from src.channel_name import ChannelName
from src.helpers.getters import get_bboxes, get_image_list
from src.helpers.enums import ClassNames

COCO_CLASSES = (
    "channel name",
    "in message",
    "my message"
)
app_root = os.path.dirname(__file__)
EXP_FILE = 'src/yolox_s.py'
CKPT_DICT = {'telegram': os.path.join(app_root, 'src/best_ckpt_tg.pth'),
             'whatsapp': os.path.join(app_root, 'src/best_ckpt_whatsapp.pth')}


def create_json(predictor: Predictor, path: str, directory_path: str):
    """
    Create JSON files from image predictions.
    Parameters
        predictor : Type[Predictor]
            An instance of the Predictor class.
        path : str
            Path to images.
        directory_path : str
            Directory path to save JSON files.
    """
    if os.path.isdir(path):
        files = get_image_list(path)
    else:
        files = [path]
    files.sort()
    reader = easyocr.Reader(['ru', 'en'])
    data = {'channel name': '', 'messages': []}
    results_dir = os.path.join('results', directory_path)
    os.makedirs(results_dir)
    for image_name in files:
        outputs, img_info = predictor.inference(image_name)
        save_path = os.path.join(results_dir, f'{os.path.splitext(os.path.split(image_name)[1])[0]}.json')
        image = cv2.imread(image_name)
        result = get_bboxes(outputs[0], img_info)
        if len(result[0]) == 0:
            data = {'info': 'Скриншот не содержит сообщений'}
            with open(save_path, "w") as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=2)
            continue
        classes, bboxes = result[0], result[1]
        logger.info(image_name)
        color_theme = None
        for i in range(len(bboxes)):
            x_min, y_min, x_max, y_max = map(int, bboxes[i])
            class_id = int(classes[i])
            class_name = ClassNames(COCO_CLASSES[class_id])
            cropped_image = image[y_min:y_max + 10, x_min:x_max + 30]
            if class_id == 0:
                channel_detector = ChannelName(cropped_image)
                color_theme = channel_detector.detect_channel_name(reader)
                data['channel name'] = channel_detector.text.strip()
            else:
                message = Message(cropped_image, color_theme, class_name)
                message.detect_message_text(reader)
                data['messages'].append(message)
        with open(save_path, "w") as json_file:
            json.dump(data, json_file, cls=MessageEncoder, ensure_ascii=False, indent=2)


def run_inf(path, messenger):
    """
    Main function to run the YOLOX demo.

    Parameters
        path :
            path to image
        messenger :
            chosen ml model telegram or whatsapp
    """

    exp = get_exp(EXP_FILE)
    model = exp.get_model()
    model.eval()

    ckpt_file = CKPT_DICT[messenger]
    logger.info("loading checkpoint")
    ckpt = torch.load(ckpt_file, map_location="cpu")
    model.load_state_dict(ckpt["model"])
    logger.info("loaded checkpoint done.")

    predictor = Predictor(
        model, exp, COCO_CLASSES,
    )

    now = datetime.now()

    directory_path = f'{str(now).split(".")[0]}'.replace(':', '-')

    create_json(predictor, path, directory_path)

    return directory_path
