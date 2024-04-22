import re
import easyocr
import cv2
import numpy as np
from typing import Type, List, Tuple
from src.helpers.delta_e_cie1976 import delta_e_cie1976
from src.helpers.determine import determine_message_color, determine_color_theme
from src.helpers.threshold import threshold
from src.helpers.enums import ClassNames, ScreenshotColor


class Message(object):
    """
    Class for detecting message text in cropped images.

    Attributes
        BG_DELTA : int
            Value for comparing background values.
        TXT_DARK_DELTA : int
            Value for comparing foreground values in the dark theme.
        TXT_LIGHT_DELTA : int
            Value for comparing foreground values in the light theme.

    Parameters
        quote : None
            Detected quote text.
        text : None
            Variable for storing text.
        time : None
            Variable for storing time.
        quote_owner : None
            Owner of the detected quote.
        owner : None
            Owner of the detected message.
        type : Type[ClassNames]
            Type of the message.
        cropped_image : np.ndarray
            Cropped image data.
        color_theme : Type[ScreenshotColor]
            Color theme of the image.

    Methods
        process_black(text, bg_delta_e, txt_delta_e).
            Process text detection for dark theme images.

        detect_message_text(reader).
            Detect text in the cropped boxes.

    """
    BG_DELTA = 12
    TXT_DARK_DELTA = 130
    TXT_LIGHT_DELTA = 240

    TIME_PATTERN = re.compile(r'\d{1,2}[-.,;*:+ ]\d{1,2}|\d{1,2}\d{1,2}')
    CHANGE_PATTERN = re.compile(r'^[a-zA-Zа-яА-Я]+$')

    def __init__(self, cropped_image: np.ndarray, color_theme: Type[ScreenshotColor], class_name: Type[ClassNames]):
        """
        Initialize the MessageDetector.

        Parameters
            cropped_image : np.ndarray
                Cropped image data.
            color_theme : Type[ScreenshotColor]
                Color theme of the image.
            class_name : Type[ClassNames]
                Type of the message.

        """
        self.quote = None
        self.text = None
        self.time = None
        self.quote_owner = None
        self.owner = None
        self.type = class_name
        self.changed = None
        self.cropped_image = cropped_image
        self.color_theme = color_theme

    def process_text(self,
                     text: str,
                     bg_delta_e: float,
                     txt_delta_e: float):
        """
        Process text detection for light theme images.

        Parameters
            text : str
                Detected text.
            bg_delta_e : float
                Color difference in the background.
            txt_delta_e : float
                Color difference in the text.
        """
        temp = self.TXT_DARK_DELTA if self.color_theme == ScreenshotColor.DARK else self.TXT_LIGHT_DELTA

        if bg_delta_e <= self.BG_DELTA:
            if txt_delta_e > temp and not self.owner and self.type == ClassNames.IN_MESSAGE:
                self.owner = text
            elif txt_delta_e < temp:
                self.text = self.text + text + ' ' if self.text is not None else text + ' '
        elif not self.quote:
            self.quote_owner = text
            self.quote = ' '
        else:
            self.quote = self.text + text + ' ' if self.text is not None else text + ' '

    def detect_message_text(self, reader):
        """
        Detect text in the cropped boxes.

        Parameters
            reader : Type[easyocr.Reader]
                EasyOCR reader instance.
        """
        result = reader.readtext(self.cropped_image)

        if not result:
            return

        if self.color_theme is None:
            self.color_theme = determine_color_theme(result[0][0], self.cropped_image)

        message_color = determine_message_color(result[len(result) - 1][0],
                                                result[len(result) - 1][1],
                                                self.color_theme,
                                                self.cropped_image)

        for i, (coords, text, _) in enumerate(result[:-1]):
            bbox = [coords[0][0], coords[0][1],
                    coords[2][0], coords[2][1]]

            x_min, y_min, x_max, y_max = map(int, bbox)
            cropped_text = self.cropped_image[y_min:y_max, x_min:x_max]

            if message_color is not None:
                bg_mean_color, text_mean_color = threshold(cropped_text, self.color_theme)

                bg_delta_e = delta_e_cie1976(message_color, bg_mean_color)
                txt_delta_e = delta_e_cie1976((255, 255, 255),
                                              text_mean_color) if self.color_theme == ScreenshotColor.DARK \
                    else delta_e_cie1976((0, 0, 0), text_mean_color)

                self.process_text(text, bg_delta_e, txt_delta_e)

        text = result[-1][1]
        if len(text) > 0:
            time_match = self.TIME_PATTERN.search(text)
            change_match = self.CHANGE_PATTERN.search(text.split(' ')[0])
            self.changed = True if change_match else False
            if time_match:
                self.time = time_match.group()
            else:
                self.text = self.text + text + ' ' if self.text is not None else text + ' '
