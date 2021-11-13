from enum import Enum


class MessageType(Enum):
    LOGIN = 0
    MESSAGE = 1
    BROADCAST = 2
    WHOELSE = 3
    WHOELSESINCE = 4
    BLOCK = 5
    UNBLOCK = 6
    LOGOUT = 7
    
    STARTPRIVATE = 8
    PRIVATE = 9
    STOPPRIVATE = 10

class Message(object):
    def __init__(self, content:str, message_type:MessageType):
        self.content = content
        self.type = message_type
