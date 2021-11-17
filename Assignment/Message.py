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
    TELL_TARGET_USER_SETUP_PRIVATE_SENDERTHREAD = 8.1
    PRIVATE = 9
    STOPPRIVATE = 10
    STOPPRIVATE_PRIVATE_STOPPED = 10.1
    
    YES = 11
    NO = 12
    

class ServerMessageType(Enum):
    ERROR = -100
    
    REQUEST_NEWUSER = 101
    REQUEST_NEEDPASSWORD = 102
    ANNONCEMENT = 103
    TIMEOUT = 104
    ACCOUNT_BLOCK = 105
    
    ASK_FOR_PRIVATE_CONNECTION = 106
    SEND_REQUESTER_SOCKET_ADDRESS = 107
    SETUP_PRIVATE_SENDERTHREAD = 108
    
    STOP_AND_DELETE_PRIVATE = 109
    STOPPED_PRIVATE_CONFIRM = 110


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