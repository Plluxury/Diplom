from typing import Type, List, Tuple
import cv2
import numpy
import math
from src.helpers.delta_e_cie1976 import delta_e_cie1976
from src.helpers.determine import determine_color_theme
from src.helpers.threshold import threshold
from src.helpers.enums import ScreenshotColor


class ChannelName(object):
    """
    Class for detecting channel names in cropped images.

    Parameters
        cropped_image : numpy.ndarray
            Cropped image data.

    Methods
        detect_channel_name() -> Tuple[str, int]:
            Detect channel name in the cropped box.

    """
    WHITE_COLOR = (255, 255, 255)
    BLACK_COLOR = (0, 0, 0)
    ERROR = 20

    def __init__(self, cropped_image: numpy.ndarray):
        """
        Initialize the ChannelName.

        Parameters
            cropped_image : numpy.ndarray
                Cropped image data.

        """
        self.text = None
        self.cropped_image = cropped_image

    def detect_channel_name(self, reader) -> Type[ScreenshotColor]:
        """
        Detect channel name in the cropped box.

        Parameters
            reader : Type[easyocr.Reader]
                EasyOCR reader instance.
        Returns
            Type[ScreenshotColor] :
                Color theme of the screenshot.

        """

        result = reader.readtext(self.cropped_image)

        if len(result) == 0:
            return

        color_theme = determine_color_theme(result[0][0], self.cropped_image)
        delta_correct_name_color = 0.0

        for coords, text, _ in result:
            bbox = [coords[0][0], coords[0][1],
                    coords[2][0], coords[2][1]]

            x_min, y_min, x_max, y_max = map(int, bbox)

            cropped_text = self.cropped_image[y_min:y_max, x_min:x_max]

            _, text_mean_color = threshold(cropped_text, color_theme)

            if color_theme == ScreenshotColor.WHITE:
                txt_delta_e = delta_e_cie1976(self.BLACK_COLOR, text_mean_color)
            else:
                txt_delta_e = delta_e_cie1976(self.WHITE_COLOR, text_mean_color)

            if math.isclose(delta_correct_name_color, 0.0):
                delta_correct_name_color = txt_delta_e

            if delta_correct_name_color - self.ERROR <= txt_delta_e <= delta_correct_name_color + self.ERROR:
                self.text = self.text.join([' ', text]) if self.text is not None else text + ' '

        return color_theme
