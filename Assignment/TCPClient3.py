"""
    Python 3
    Usage: python3 TCPClient3.py server_port
    coding: utf-8
    
    Author: Wei Song (Tutor for COMP3331/9331)
"""
from socket import *
import sys

from types import Message, MessageType

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

# input user name and password for validation
while True:
    username = input("Username: ")
    password = input("Password: ")
    login_message_content = {"username":username, "password":password}
    login_message = Message(login_message_content, MessageType.LOGIN)
    if debug : print(login_message)

while True:
    message = input("===== Please type any messsage you want to send to server: =====\n")
    if message == "logout":
        print("Log out successfullly.")
        break
    clientSocket.sendall(message.encode())

    # receive response from the server
    # 1024 is a suggested packet size, you can specify it as 2048 or others
    data = clientSocket.recv(1024)
    receivedMessage = data.decode()

    # parse the message received from server and take corresponding actions
    if receivedMessage == "":
        print("[recv] Message from server is empty!")
    elif receivedMessage == "user credentials request":
        print("[recv] You need to provide username and password to login")
    elif receivedMessage == "download filename":
        print("[recv] You need to provide the file name you want to download")
    else:
        print("[recv] Message makes no sense")
        
    ans = input('\nDo you want to continue(y/n) :')
    if ans == 'y':
        continue
    else:
        break

# close the socket
clientSocket.close()
