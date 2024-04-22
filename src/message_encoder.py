import json
from typing import Type
from src.message import Message
from src.helpers.enums import ClassNames


class MessageEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for encoding instances of the Message class.

    Methods
        default(message)
            Convert a Message object to a dictionary for JSON serialization.
    """

    def default(self, message: Type[Message]) -> dict:
        """
        Convert a Message object to a dictionary for JSON serialization.

        Parameters
            message : Type[Message]
                Detected message in the screenshot.

        Return
            dict :
                Dictionary for JSON serialization.
        """
        return {
            'owner': message.owner,
            'quote_owner': message.quote_owner,
            'quote': message.quote.strip() if message.quote is not None else message.quote,
            'text': message.text.strip() if message.text is not None else message.text,
            'time': message.time,
            'changed': message.changed,
            'type': 'Входящие' if message.type == ClassNames.IN_MESSAGE else 'Исходящие'
        }
