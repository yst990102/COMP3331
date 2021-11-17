import pickle
from socket import socket
from threading import Thread

class PrivateReceiveThread(Thread):
    def __init__(self, private_socket:socket, skip_listen:bool):
        Thread.__init__(self)
        self.private_socket = private_socket
        self.skip_listen = skip_listen
        
    def run(self):
        if self.skip_listen == False:
            self.private_socket.listen()
            self.target_socket, self.target_address = self.private_socket.accept()
        # print("PrivateReceiveThread set up.")
        self.message = ''
        while True:
            try:
                data = self.target_socket.recv(1024)
                self.message = pickle.loads(data)
            except Exception:
                break
            print(f"[private] {self.message.getContent()}")
            
    def getSocket(self):
        return self.private_socket
            
        
class PrivateSendThread(Thread):
    def __init__(self, private_socket:socket):
        Thread.__init__(self)
        self.private_socket = private_socket
    
    def run(self):
        # print("PrivateSendThread set up.")
        return
        
    def sendmessage(self,message:str):
        self.private_socket.send(pickle.dumps(message))
        
    def getSocket(self):
        return self.private_socket