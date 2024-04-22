import cv2
import numpy as np
from .enums import ScreenshotColor
from typing import Tuple, List, Type


def threshold(src: np.ndarray,
              color_theme: Type[ScreenshotColor] = ScreenshotColor.WHITE) -> List[float]:
    """
    Calculate the mean values of red, green, and blue channels for pixels for foreground.

    Parameters
        src : np.ndarray
            Input image in BGR format.
        color_theme : Type[ScreenshotColor]
            Value used in the threshold image to identify the color theme of the image.

    Returns
        List[float, float] :
            Mean values of background and foreground.
    """
    src_gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(src_gray, src_gray.mean(), 255, cv2.THRESH_BINARY)

    mask_binary = (binary == color_theme.value)
    mask_binary_inv = ~mask_binary

    channels = [src[:, :, i] for i in range(src.shape[2])]
    masked_binary_channels = [np.ma.masked_array(channel, mask_binary) for channel in channels]
    masked_binary_inv_channels = [np.ma.masked_array(channel, mask_binary_inv) for channel in channels]

    bg_mean_color = tuple(masked_channel.mean() for masked_channel in masked_binary_inv_channels)
    text_mean_color = tuple(masked_channel.mean() for masked_channel in masked_binary_channels)

    return bg_mean_color, text_mean_color
