from enum import Enum

class MessageStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    SENDING = "SENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    VIEWED = "VIEWED"
    OPENED = "OPENED"
    CANCELED = "CANCELED"
    BOUNCED = "BOUNCED"
    ERROR = "ERROR"
    CLICKED = "CLICKED"

class AvailableChannels(str, Enum):
    EMAIL = "EMAIL"
