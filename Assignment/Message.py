from enum import Enum

class MessageType(Enum):
    NOCOMMAND = -1

    LOGIN_USERNAME = 0.1
    LOGIN_PASSWD = 0.2
    LOGIN_NEWPASSWD = 0.3
    
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
    
    YES = 11
    NO = 12
    

class ServerMessageType(Enum):
    ERROR = -100
    
    REQUEST_NEWUSER = 101
    REQUEST_NEEDPASSWORD = 102
    ANNONCEMENT = 103
    TIMEOUT = 104
    ACCOUNT_BLOCK = 105
    
    REQUEST_PRIVATE = 106
    SEND_ADDRESS = 107


class Message(object):
    def __init__(self, content, message_type):
        self.content = content
        self.type = message_type

    def getContent(self):
        return self.content

    def getType(self):
        return self.type


class ServerMessage(object):
    def __init__(self, content, reply_type):
        self.content = content
        self.type = reply_type

    def getContent(self):
        return self.content

    def getType(self):
        return self.type