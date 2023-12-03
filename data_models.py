from enum import Enum


class NeutralityEnum(Enum):
    COURT = 'court'
    CUSTOMER_SERVICE = 'customer_service'


class ReplierEnum(Enum):
    HUMAN = 'human'
    SYSTEM = 'system'


class SpeechEnum(Enum):
    FREE_TYPING = 'free_typing'
    CHOICES_ONLY = 'choices_only'

