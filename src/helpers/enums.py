from enum import Enum


class ScreenshotColor(Enum):
    """
    Enum to represent screenshot colors.

    Attributes
    ----------
    DARK : int
        The value representing a dark color (0).
    WHITE : int
        The value representing a white color (255).
    """

    DARK = 0
    WHITE = 255


class ClassNames(Enum):
    """
    Enum to represent class names.

    Attributes
        CHANNEL : str
            The class name for a channel.
        IN_MESSAGE : str
            The class name for an incoming message.
        MY_MESSAGE : str
            The class name for a user's own message.
    """
    CHANNEL = 'channel name'
    IN_MESSAGE = 'in message'
    MY_MESSAGE = 'my message'
