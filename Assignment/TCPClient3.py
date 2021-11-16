"""
    Python 3
    Usage: python3 TCPClient3.py server_port
    coding: utf-8
    
    Author: Wei Song (Tutor for COMP3331/9331)
"""
import os
from socket import *
import sys
import pickle

from Message import Message, MessageType, ServerReplyType
from helperfunctions import MessageContentByType
from threading import Thread
# debug switch
debug = 1

#Server would be running on the same host as Client
if len(sys.argv) != 2:
    print("\n===== Error usage, Please follow format: (python TCPClient3.py server_port) ======\n")
    exit(0)
serverHost = "localhost"
serverPort = int(sys.argv[1])
serverAddress = (serverHost, serverPort)

# define a socket for the client side, it would be used to communicate with the server
clientSocket = socket(AF_INET, SOCK_STREAM)

# build connection with the server and send message to it
clientSocket.connect(serverAddress)

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
                print("== Error : Invalid command")
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


# define sendThread and receiveThread
receivethread = ReceiveThread(clientSocket)
sendthread = SendThread(clientSocket)

# start receiving : may have login timeout
receivethread.start()

# input user name and password for validation
username = input("Username: ")
username_message = Message({"username":username}, MessageType.LOGIN_USERNAME)
clientSocket.send(pickle.dumps(username_message))                    # send out username

while True:
    
    # receive the check info from server
    data = clientSocket.recv(1024)
    receivedMessage = pickle.loads(data)
    
    if receivedMessage.getType() == ServerReplyType.REQUEST_NEEDPASSWORD:
        password = input(receivedMessage.getContent() + "Password: ")
        password_message = Message({"password":password}, MessageType.LOGIN_PASSWD)
        clientSocket.send(pickle.dumps(password_message))                    # send out password
    elif receivedMessage.getType() == ServerReplyType.REQUEST_NEWUSER:
        password = input(receivedMessage.getContent() + "Enter a password: ")
        password_message = Message({"newpassword":password}, MessageType.LOGIN_NEWPASSWD)
        clientSocket.send(pickle.dumps(password_message))                    # send out password
    elif receivedMessage.getType() == ServerReplyType.ANNONCEMENT:
        # print the login success message from server
        print(receivedMessage.getContent())
        break
    elif receivedMessage.getType() == ServerReplyType.ACCOUNT_BLOCK:
        # print account block message & terminate client
        print(receivedMessage.getContent())
        os._exit(0)

sendthread.start()