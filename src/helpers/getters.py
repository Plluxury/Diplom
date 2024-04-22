from typing import Tuple, List
import torch
import os


IMAGE_EXT = ".png"


def get_bboxes(output: list, img_info: dict) -> Tuple[List[str], List[list]]:
    """
    Get bounding box coordinates from the model output.

    Parameters
        output : list
            Model output.
        img_info : dict
            Image information.

    Returns
        Tuple[list, list] :
            List of classes and list of bounding boxes.
    """
    ratio = img_info["ratio"]

    if output is None or len(output) == 0:
        return [], []

    output = output.cpu()

    bboxes = output[:, 0:4]
    bboxes /= ratio

    cls = output[:, 6]
    sorted_indices = torch.argsort(bboxes[:, 1])
    cls = cls[sorted_indices]
    bboxes = bboxes[sorted_indices]

    return cls, bboxes


def get_image_list(path: str) -> List[str]:
    """
    Get a list of image names path.

    Parameters
        path : str
            The path to the directory containing images.

    Returns
        list[str] :
            List of image names.
    """
    image_names = []
    for maindir, subdir, file_name_list in os.walk(path):
        for filename in file_name_list:
            apath = os.path.join(maindir, filename)
            ext = os.path.splitext(apath)[1]
            if ext.lower() == IMAGE_EXT:
                image_names.append(apath)

    return image_names
