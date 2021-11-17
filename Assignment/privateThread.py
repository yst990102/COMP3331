import pickle
from socket import socket
from threading import Thread

class PrivateReceiveThread(Thread):
    def __init__(self, targetUser:str,privateSocket:socket):
        Thread.__init__(self)
        self.targetUser = targetUser
        self.privateSocket = privateSocket
        self.Alive = True
    
    def run(self):
        while self.Alive:
            data = self.privateSocket.recv(1024)
            message_received = pickle.loads(data)
            
            message_received_content = message_received.getContent()
            print(f"[private] {self.targetUser}: {message_received_content}")