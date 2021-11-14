from socket import socket
from threading import Thread
import pickle, os

from Message import Message, MessageType, ServerReplyType
from helperfunctions import MessageContentByType

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
            
            if self.message_type == MessageType.NOCOMMAND:
                print("No such Command, please re-type.")
                continue
            elif self.message_type == MessageType.MESSAGE:
                messaged_message = Message(self.message_content, MessageType.MESSAGE)
                self.clientSocket.send(pickle.dumps(messaged_message))
                continue
            elif self.message_type == MessageType.BROADCAST:
                broadcast_message = Message(self.message_content, MessageType.BROADCAST)
                self.clientSocket.send(pickle.dumps(broadcast_message))
                continue
            elif self.message_type == MessageType.WHOELSE:
                whoelse_message = Message(self.message_content, MessageType.WHOELSE)
                self.clientSocket.send(pickle.dumps(whoelse_message))
                continue
            elif self.message_type == MessageType.WHOELSESINCE:
                whoelsesince_message = Message(self.message_content, MessageType.WHOELSESINCE)
                self.clientSocket.send(pickle.dumps(whoelsesince_message))
                continue
            elif self.message_type == MessageType.BLOCK:
                block_message = Message(self.message_content, MessageType.BLOCK)
                self.clientSocket.send(pickle.dumps(block_message))
                continue
            elif self.message_type == MessageType.UNBLOCK:
                block_message = Message(self.message_content, MessageType.UNBLOCK)
                self.clientSocket.send(pickle.dumps(block_message))
                continue
            elif self.message_type == MessageType.LOGOUT:
                # tell server that client has logout
                logout_message = Message(self.message_content, MessageType.LOGOUT)
                self.clientSocket.send(pickle.dumps(logout_message))
                
                # print logout message & terminate client
                print("Log out successfullly.")
                os._exit(0)


class ReceiveThread(Thread):
    def __init__(self, clientSocket:socket):
        Thread.__init__(self)
        self.clientSocket = clientSocket
        self.Alive = True
    
    def run(self):
        self.message_received = ""
        while self.Alive:
            data = self.clientSocket.recv(1024)
            self.message_received = pickle.loads(data)
            
            if self.message_received.getType() == ServerReplyType.ANNONCEMENT:
                # print the announcement from server
                print(self.message_received.getContent())
            elif self.message_received.getType() == ServerReplyType.TIMEOUT:
                # print timeout message & terminate client
                print(self.message_received.getContent())
                os._exit(0)
            elif self.message_received.getType() == ServerReplyType.ACCOUNT_BLOCK:
                # print account blocked message & terminate client
                print(self.message_received.getContent())
                os._exit(0)
            elif self.message_received.getType() == ServerReplyType.ERROR:
                # print error message
                error_message = f"== Error : {self.message_received.getContent()}"
                print(error_message)


