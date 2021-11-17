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
from typing import Tuple

from Message import Message, MessageType, ServerMessageType
from helperfunctions import MessageContentByType
from threading import Thread
# debug switch
debug = 0

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

message_send = ""
message_received = ""

confirm_wait = False
requester = ""

username = None
password = None

class SendThread(Thread):
    def __init__(self, clientSocket:socket):
        Thread.__init__(self)
        self.clientSocket = clientSocket
        self.Alive = True
    
    def run(self):
        global message_send
        global message_received
        global username
        global password
        global confirm_wait
        
        while self.Alive:
            if username == None:
                # input user name and password for validation
                username = input("Username: ")
                username_message = Message({"username":username}, MessageType.LOGIN_USERNAME)
                clientSocket.send(pickle.dumps(username_message))                    # send out username
                continue
            elif password == None:
                continue
            else:
                message_send = input()
                [self.message_content, self.message_type] = MessageContentByType(message_send)
                
                if debug: print([self.message_content, self.message_type])
                
                if confirm_wait == True:
                    if message_send in ['y', 'n']:
                        if self.message_type == MessageType.YES:
                            print(f"TODO： send confirm message. {message_received.getContent()}")
                            confirmed_message = Message(message_received.getContent(), MessageType.YES)
                            self.clientSocket.send(pickle.dumps(confirmed_message))
                        elif self.message_type == MessageType.NO:
                            print(f"TODO： send refuse message.")
                            refused_message = Message(self.message_content, MessageType.NO)
                            self.clientSocket.send(pickle.dumps(refused_message))
                        confirm_wait = False
                        continue
                    else:
                        print("Please enter y or n: ")
                        continue
                else:
                    if self.message_type == MessageType.NOCOMMAND:
                        print("=== Error : Invalid command ===")
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
                        # turn off socket & exit
                        self.clientSocket.close()
                        os._exit(0)
                    elif self.message_type == MessageType.STARTPRIVATE:
                        print(f"TODO： send start private. {self.message_content} {self.message_type}")
                        # ask server to send request
                        startprivate_message = Message(self.message_content, MessageType.STARTPRIVATE)
                        self.clientSocket.send(pickle.dumps(startprivate_message))
                        continue
                    elif self.message_type == MessageType.PRIVATE:
                        print("TODO： send private.")
                        continue
                    elif self.message_type == MessageType.STOPPRIVATE:
                        print("TODO： send stop private.")
                        continue

class ReceiveThread(Thread):
    def __init__(self, clientSocket:socket):
        Thread.__init__(self)
        self.clientSocket = clientSocket
        self.Alive = True
    
    def run(self):
        global message_received
        global username
        global password
        global confirm_wait
        
        while self.Alive:
            data = self.clientSocket.recv(1024)
            message_received = pickle.loads(data)
            
            if debug: print(message_received)
            
            if message_received.getType() == ServerMessageType.REQUEST_NEEDPASSWORD:
                password = input(message_received.getContent() + "Password: ")
                password_message = Message({"password":password}, MessageType.LOGIN_PASSWD)
                clientSocket.send(pickle.dumps(password_message))                    # send out password
                continue
            elif message_received.getType() == ServerMessageType.REQUEST_NEWUSER:
                password = input(message_received.getContent() + "Enter a password: ")
                password_message = Message({"newpassword":password}, MessageType.LOGIN_NEWPASSWD)
                clientSocket.send(pickle.dumps(password_message))                    # send out password
                continue
            elif message_received.getType() == ServerMessageType.ANNONCEMENT:
                # print the announcement from server
                print(message_received.getContent())
            elif message_received.getType() == ServerMessageType.TIMEOUT:
                # print timeout message & terminate client
                print(message_received.getContent())
                # turn off socket & exit
                self.clientSocket.close()
                os._exit(0)
            elif message_received.getType() == ServerMessageType.ACCOUNT_BLOCK:
                # print account blocked message & terminate client
                print(message_received.getContent())
                # turn off socket & exit
                self.clientSocket.close()
                os._exit(0)
            elif message_received.getType() == ServerMessageType.ERROR:
                # print error message
                error_message = f"=== Error : {message_received.getContent()} ==="
                print(error_message)
                
                if "already online" in message_received.getContent():
                    print("Please re-type your Username")
                    username = None
            elif message_received.getType() == ServerMessageType.REQUEST_PRIVATE:
                # print private request message
                print(message_received.getContent())
                print("enter y or n: ")
                confirm_wait = True
            elif message_received.getType() == ServerMessageType.SEND_ADDRESS:
                # print target private_client_address
                print(f"Got ClientAddress : {message_received.getContent()}")


# define sendThread and receiveThread
receivethread = ReceiveThread(clientSocket)
sendthread = SendThread(clientSocket)

# start receiving : may have login timeout
receivethread.start()
sendthread.start()