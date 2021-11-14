from enum import Enum

class MessageType(Enum):
    NOCOMMAND = -1
    
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
    

class ServerReplyType(Enum):
    ERROR = -1
    
    REQUEST_NEWUSER = 0
    REQUEST_NEEDPASSWORD = 1
    ANNONCEMENT = 2
    TIMEOUT = 3
    ACCOUNT_BLOCK = 4
    


class Message(object):
    def __init__(self, content, message_type):
        self.content = content
        self.type = message_type

    def getContent(self):
        return self.content

    def getType(self):
        return self.type


class ServerReply(object):
    def __init__(self, content, reply_type):
        self.content = content
        self.type = reply_type

    def getContent(self):
        return self.content

    def getType(self):
        return self.type