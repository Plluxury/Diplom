import torch
import os
import cv2
from loguru import logger
from typing import Tuple, List
import time
from yolox.data.data_augment import ValTransform
from yolox.utils import postprocess


class Predictor(object):
    """
    Class for predicting labels.
    """

    def __init__(self, model, exp, cls_names: Tuple[str, str, str]):
        """
        Initialize the Predictor.

        Parameters
            model :
                The YOLOX model.
            exp :
                YOLOX configuration.
            cls_names :
                Tuple of class names.
        """
        self.model = model
        self.cls_names = cls_names
        self.num_classes = exp.num_classes
        self.confthre = exp.test_conf
        self.nmsthre = exp.nmsthre
        self.test_size = exp.test_size
        self.device = 'cpu'
        self.preproc = ValTransform(legacy=False)

    def inference(self, img_path: str) -> Tuple[torch.Tensor, dict]:
        """
        Perform model inference on the input image.

        Parameters
            img_path : str
                Path to image.

        Returns
            Tuple[list, dict] :
                The model outputs and image information.
        """

        if isinstance(img_path, str):
            file_name = os.path.basename(img_path)
            print(img_path)
            img = cv2.imread(img_path)
        else:
            file_name = None

        height, width = img.shape[:2]
        ratio = min(self.test_size[0] / img.shape[0],
                    self.test_size[1] / img.shape[1])
        img_info = {
            "id": 0,
            'filename': file_name,
            'height': height,
            'width': width,
            'raw_img': img,
            'ratio': ratio
        }
        img, _ = self.preproc(img, None, self.test_size)
        img = torch.from_numpy(img).unsqueeze(0)
        img = img.float()

        with torch.no_grad():
            t0 = time.time()
            outputs = self.model(img)
            outputs = postprocess(
                outputs, self.num_classes, self.confthre,
                self.nmsthre, class_agnostic=True
            )
            logger.info("Infer time: {:.4f}s".format(time.time() - t0))

        return outputs, img_info
