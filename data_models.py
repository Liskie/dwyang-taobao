from enum import Enum
from typing import Optional


class NeutralityEnum(Enum):
    COURT = 'court'
    CUSTOMER_SERVICE = 'customer_service'


class ReplierEnum(Enum):
    HUMAN = 'human'
    SYSTEM = 'system'


class SpeechEnum(Enum):
    FREE_TYPING = 'free_typing'
    CHOICES_ONLY = 'choices_only'


class User:

    def __init__(self, name: str, student_id: str, gender: str, phone: Optional[str] = None):
        self.name: str = name
        self.student_id: str = student_id
        self.gender: str = gender
        self.phone: Optional[str] = phone

        self.neutrality_variable: Optional[NeutralityEnum] = None
        self.replier_variable: Optional[ReplierEnum] = None
        self.speech_variable: Optional[SpeechEnum] = None

        self.expected_compensation: Optional[float] = None

        self.conversation: list[dict[str, str]] = []
        # self.conversation = [
        #     {'role': 'system', 'content': '你好'},
        #     {'role': 'user', 'content': '你好, 我想问一下...'}, ...
        # ]

    def add_conversation_round(self, role: str, content: str):
        self.conversation.append({'role': role, 'content': content})

    @classmethod
    def from_dict(cls, user_properties: dict):
        user = cls(name=user_properties['name'],
                   student_id=user_properties['student_id'],
                   gender=user_properties['gender'],
                   phone=user_properties['phone'])
        return user


if __name__ == '__main__':
    for i in range(8):
        flags = list(bin(i).lstrip('0b').zfill(3))
        print(f'{i}: {flags}')
