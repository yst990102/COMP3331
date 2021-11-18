# !/usr/bin/python3
"""
    Python 3
    Usage: python3 TCPClient3.py server_port
    coding: utf-8
    
    Author: z5192519
"""
import os
from socket import *
import sys
import pickle

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
requester_list = []

username = None
password = None

# private threads
# format : {user: private_thread, ...}
private_send_thread_list = {}

private_receive_thread_list = {}

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
            print(f"[private] {username} : {self.message.getContent()}")
            
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
        self.private_socket.sendall(pickle.dumps(message))
        
    def getSocket(self):
        return self.private_socket

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
        global private_thread_list
        
        while self.Alive:

            message_send = input()
            [self.message_content, self.message_type] = MessageContentByType(message_send)
            
            if confirm_wait == True and requester_list != []:
                if debug : print("confirm_wait == ", confirm_wait," , requester_list ==" , requester_list)
                if message_send in ['y', 'n']:
                    if self.message_type == MessageType.YES:
                        # create a private socket
                        private_socket = socket(AF_INET, SOCK_STREAM)
                        private_receive_thread = PrivateReceiveThread(private_socket, False)
                        private_receive_thread.start()
                        
                        # add private thread in to private_receive_thread_list
                        private_receive_thread_list.update({requester_list[0] : private_receive_thread})
                        
                        message = {"requester" : requester_list[0]}         # message = {"requester" : requester_username}
                        message.update({"private_address":private_socket.getsockname()})
                        
                        confirmed_message = Message(message, MessageType.YES)
                        self.clientSocket.sendall(pickle.dumps(confirmed_message))
                        
                        # remove the confirmed requester
                        del requester_list[0]
                    elif self.message_type == MessageType.NO:
                        print(f"You refused the request.")
                        refused_message = Message({"requester" : requester_list[0]}, MessageType.NO)
                        self.clientSocket.sendall(pickle.dumps(refused_message))
                        
                        # remove the confirmed requester
                        del requester_list[0]
                        
                    if requester_list == []:
                        confirm_wait = False
                    continue
                else:
                    print("Please enter y or n: ")
                    continue
            else:
                if self.message_type == MessageType.NOCOMMAND or self.message_type == MessageType.YES or self.message_type == MessageType.NO:
                    print("=== Error : Invalid command ===")
                    continue
                elif self.message_type == MessageType.MESSAGE:
                    messaged_message = Message(self.message_content, MessageType.MESSAGE)
                    self.clientSocket.sendall(pickle.dumps(messaged_message))
                    continue
                elif self.message_type == MessageType.BROADCAST:
                    broadcast_message = Message(self.message_content, MessageType.BROADCAST)
                    self.clientSocket.sendall(pickle.dumps(broadcast_message))
                    continue
                elif self.message_type == MessageType.WHOELSE:
                    whoelse_message = Message(self.message_content, MessageType.WHOELSE)
                    self.clientSocket.sendall(pickle.dumps(whoelse_message))
                    continue
                elif self.message_type == MessageType.WHOELSESINCE:
                    whoelsesince_message = Message(self.message_content, MessageType.WHOELSESINCE)
                    self.clientSocket.sendall(pickle.dumps(whoelsesince_message))
                    continue
                elif self.message_type == MessageType.BLOCK:
                    block_message = Message(self.message_content, MessageType.BLOCK)
                    self.clientSocket.sendall(pickle.dumps(block_message))
                    continue
                elif self.message_type == MessageType.UNBLOCK:
                    block_message = Message(self.message_content, MessageType.UNBLOCK)
                    self.clientSocket.sendall(pickle.dumps(block_message))
                    continue
                elif self.message_type == MessageType.LOGOUT:
                    # tell server that client has logout
                    logout_message = Message(self.message_content, MessageType.LOGOUT)
                    self.clientSocket.sendall(pickle.dumps(logout_message))
                    
                    # print logout message & terminate client
                    print("Log out successfullly.")
                    # turn off socket & exit
                    self.clientSocket.close()
                    os._exit(0)
                elif self.message_type == MessageType.STARTPRIVATE:
                    target_user = self.message_content['user']
                    if target_user in private_send_thread_list.keys() and target_user in private_receive_thread_list.keys():
                        print(f"=== Error : You have already set private channel with {target_user}")
                        continue
                    elif target_user == username:
                        print(f"=== Error : You can't start private with yourself.")
                        continue
                    else:
                        # ask server to send request
                        startprivate_message = Message(self.message_content, MessageType.STARTPRIVATE)
                        self.clientSocket.sendall(pickle.dumps(startprivate_message))
                        continue
                elif self.message_type == MessageType.PRIVATE:
                    target_user = self.message_content['user']
                    message_content = self.message_content['message']
                    
                    message = Message(message_content, self.message_type)
                    
                    if target_user in private_send_thread_list.keys():
                        send_thread = private_send_thread_list[target_user]
                        send_thread.sendmessage(message)
                    else:
                        if target_user == username:
                            print(f"=== Error : You can't private message to yourself.")
                        else:
                            print(f"=== Error : Private messaging to {target_user} not enabled.")
                    continue
                elif self.message_type == MessageType.STOPPRIVATE:
                    target_user = self.message_content['user']
                    if target_user in private_receive_thread_list.keys() and target_user in private_send_thread_list.keys():
                        del private_receive_thread_list[target_user]
                        del private_send_thread_list[target_user]
                        # TODO : send message to target user to let him stop private messaging
                        stopprivate_message_content = {"deluser" : username, "user" : target_user}
                        stopprivate_message = Message(stopprivate_message_content, MessageType.STOPPRIVATE)
                        self.clientSocket.sendall(pickle.dumps(stopprivate_message))
                        continue
                    else:
                        print(f"=== Error : Stop Private messaging with {target_user} not enabled. Target logged out or No private tunnel setup.")
                    continue
                elif self.message_type == MessageType.ARGUMENT_ERROR:
                    print("=== Error : Argument Error ===")
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
            
            if message_received.getType() == ServerMessageType.ANNONCEMENT:
                # print the announcement from server
                print(message_received.getContent())
                continue
            elif message_received.getType() == ServerMessageType.LOGOUT_ANNOUNCEMENT:
                # print the logout announcement from server
                logout_user = message_received.getContent()['logout_user']
                # remove private tunnel with logout_user
                if logout_user in private_receive_thread_list.keys() and logout_user in private_send_thread_list.keys():
                    del private_receive_thread_list[logout_user]
                    del private_send_thread_list[logout_user]
                print(f"{logout_user} logged out.")
                continue
            elif message_received.getType() == ServerMessageType.TIMEOUT:
                # print timeout message & terminate client
                print(message_received.getContent())
                # turn off socket & exit
                self.clientSocket.close()
                os._exit(0)
            elif message_received.getType() == ServerMessageType.ERROR:
                # print error message
                error_message = f"=== Error : {message_received.getContent()} ==="
                print(error_message)
                continue
            elif message_received.getType() == ServerMessageType.ASK_FOR_PRIVATE_CONNECTION:
                print("enter y or n: ")
                confirm_wait = True
                requester = message_received.getContent()['requester']
                requester_list.append(requester)
                continue
            elif message_received.getType() == ServerMessageType.SEND_REQUESTER_SOCKET_ADDRESS:
                # create private_socket
                requester_socket_send = socket(AF_INET, SOCK_STREAM)
                target_socket_address = message_received.getContent()['private_address']
                requester_socket_send.connect(target_socket_address)
                private_send_thread = PrivateSendThread(requester_socket_send)
                
                requester_socket_receive = socket(AF_INET, SOCK_STREAM)
                private_receive_thread = PrivateReceiveThread(requester_socket_receive, False)
                private_send_thread.start()
                private_receive_thread.start()
                
                
                private_send_thread_list.update({message_received.getContent()['target_user'] : private_send_thread})
                private_receive_thread_list.update({message_received.getContent()['target_user'] : private_receive_thread})

                ask_target_start_private_sender_thread_message = Message({"target_user" : message_received.getContent()['target_user'], "private_address":requester_socket_receive.getsockname()}, MessageType.TELL_TARGET_USER_SETUP_PRIVATE_SENDERTHREAD)
                self.clientSocket.sendall(pickle.dumps(ask_target_start_private_sender_thread_message))
                continue
            elif message_received.getType() == ServerMessageType.SETUP_PRIVATE_SENDERTHREAD:
                requester_username = message_received.getContent()['requester']
                requester_private_address = message_received.getContent()['private_address']
                
                
                requester_socket = socket(AF_INET, SOCK_STREAM)
                requester_socket.connect(requester_private_address)
                receivethread = PrivateSendThread(requester_socket)
                receivethread.start()
                
                private_send_thread_list.update({requester_username:receivethread})
                
                continue
            elif message_received.getType() == ServerMessageType.STOP_AND_DELETE_PRIVATE:
                deluser = message_received.getContent()['deluser']
                # delete relevant thread from list
                del private_receive_thread_list[deluser]
                del private_send_thread_list[deluser]
                
                # print private stopped message and send confirmed stopped message to server
                print(f"Private messaging was stopped by {deluser}")
                stopped_message = Message({"deleteduser" : deluser}, MessageType.STOPPRIVATE_PRIVATE_STOPPED)
                self.clientSocket.sendall(pickle.dumps(stopped_message))
                continue
            elif message_received.getType() == ServerMessageType.STOPPED_PRIVATE_CONFIRM:
                # print feedback message
                print(message_received.getContent())
                continue


# define sendThread and receiveThread
receivethread = ReceiveThread(clientSocket)
sendthread = SendThread(clientSocket)

# start receiving : may have login timeout
receivethread.start()

username = input("Username: ")
username_message = Message({'username' : username}, MessageType.LOGIN_USERNAME)
clientSocket.sendall(pickle.dumps(username_message))

while True:
    
    data = clientSocket.recv(1024)
    message_received = pickle.loads(data)
    
    if message_received.getType() == ServerMessageType.REQUEST_NEEDPASSWORD:
        password = input(message_received.getContent() + "Password: ")
        password_message = Message({"password":password}, MessageType.LOGIN_PASSWD)
        clientSocket.sendall(pickle.dumps(password_message))                    # send out password
        continue
    elif message_received.getType() == ServerMessageType.REQUEST_NEWUSER:
        password = input(message_received.getContent() + "Enter a password: ")
        password_message = Message({"newpassword":password}, MessageType.LOGIN_NEWPASSWD)
        clientSocket.sendall(pickle.dumps(password_message))                    # send out password
        break
    elif message_received.getType() == ServerMessageType.ERROR:
        username = input()
        print(message_received.getContent())
        continue
    elif message_received.getType() == ServerMessageType.ACCOUNT_BLOCK:
        print(message_received.getContent())
        os._exit(0)
    elif message_received.getType() == ServerMessageType.ANNONCEMENT:
        print(message_received.getContent())
        break
    
sendthread.start()