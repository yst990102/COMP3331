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
from ClientThreads import ReceiveThread, SendThread

from Message import Message, MessageType, ServerReplyType

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


receivethread = ReceiveThread(clientSocket)
sendthread = SendThread(clientSocket)
receivethread.start()

# input user name and password for validation
username = input("Username: ")
username_message = Message({"username":username}, MessageType.LOGIN)
clientSocket.send(pickle.dumps(username_message))                    # send out username

while True:
    
    # receive the check info from server
    data = clientSocket.recv(1024)
    receivedMessage = pickle.loads(data)
    
    if receivedMessage.getType() == ServerReplyType.REQUEST_NEEDPASSWORD:
        password = input(receivedMessage.getContent() + "Password: ")
        password_message = Message({"password":password}, MessageType.LOGIN)
        clientSocket.send(pickle.dumps(password_message))                    # send out password
    elif receivedMessage.getType() == ServerReplyType.REQUEST_NEWUSER:
        password = input(receivedMessage.getContent() + "Enter a password: ")
        password_message = Message({"newpassword":password}, MessageType.LOGIN)
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