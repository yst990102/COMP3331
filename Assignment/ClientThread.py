from threading import Thread
import pickle, os

from Message import Message, MessageType, ServerReplyType
from helperfunctions import MessageContentByType, StringToMessageType

class SendThread(Thread):
    def __init__(self, clientSocket):
        Thread.__init__(self)
        self.clientSocket = clientSocket
        self.Alive = True
    
    def run(self):
        self.message_send = ""
        while self.Alive:
            self.message_send = input("")
            [self.message_content, self.message_type] = MessageContentByType(self.message_send)
            
            if self.message_type == MessageType.LOGOUT:
                logout_message = Message(self.message_content, MessageType.LOGOUT)
                self.clientSocket.sendall(pickle.dumps(logout_message))
                print("Log out successfullly.")
                os._exit(0)
            elif self.message_type == MessageType.BROADCAST:
                broadcast_message = Message(self.message_content, MessageType.BROADCAST)
                self.clientSocket.sendall(pickle.dumps(broadcast_message))
                


class ReceiveThread(Thread):
    def __init__(self, clientSocket):
        Thread.__init__(self)
        self.clientSocket = clientSocket
        self.Alive = True
    
    def run(self):
        self.message_received = ""
        while self.Alive:
            data = self.clientSocket.recv(1024)
            self.message_received = pickle.loads(data)
            
            if self.message_received.getType() == ServerReplyType.ANNONCEMENT:
                print(self.message_received.getContent())
            

