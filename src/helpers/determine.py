from typing import List, Type
import re
import cv2
import numpy as np
from .threshold import threshold
from .delta_e_cie1976 import delta_e_cie1976
from .enums import ScreenshotColor


def determine_color_theme(coords: List[float], image: np.ndarray) -> Type[ScreenshotColor]:
    """
    Determine color theme of the image.

    Parameters
        coords :List[float]
            Coords of the first bbox.
        image : np.ndarray
            Image.

    Returns:
        Type[ScreenshotColor] :
            Determined color theme of the screenshot
    """

    bbox = [coords[0][0], coords[0][1],
            coords[2][0], coords[2][1]]

    x_min, y_min, x_max, y_max = map(int, bbox)

    cropped_image = image[y_min:y_max, x_min:x_max]
    bg_mean_color, _ = threshold(cropped_image)
    delta_e = delta_e_cie1976((255, 255, 255), bg_mean_color)
    color_theme = ScreenshotColor.WHITE

    if delta_e > 30:
        color_theme = ScreenshotColor.DARK
    return color_theme


def determine_message_color(coords: List[float], text: str, color_theme: Type[ScreenshotColor],
                            image: np.ndarray) -> tuple:
    """
    Determine mean color of last bbox in message.

    Parameters
        coords : List[float]
            Coords of last bbox in message:.
        text : str
            Text in last bbox in message
        color_theme : Type[ScreenshotColor]
            Color theme
        image : np.ndarray
            Image.

    Returns
        tuple :
            Mean colors of blue, green and red channels.
    """
    bbox = [coords[0][0], coords[0][1],
            coords[2][0], coords[2][1]]

    x_min, y_min, x_max, y_max = map(int, bbox)

    cropped_image = image[y_min:y_max, x_min:x_max]

    message_color, _ = threshold(cropped_image, color_theme)

    return message_color
