"""
    Code for Multi-Threaded Server
    Python 3
    Usage: python3 TCPserver3.py server_port block_duration timeout
    coding: utf-8
    
    Author: z5192519
"""
from socket import *
from threading import Thread
import sys, select, pickle, datetime



from Message import MessageType, ServerReply, ServerReplyType
from helperfunctions import AddUserDataToTXT, LoadUserData

# debug
debug = 0


# acquire server host and port from command line parameter
if len(sys.argv) != 4:
    print(len(sys.argv))
    print("\n===== Error usage. Please follow format: (python3 TCPserver3.py server_port block_duration timeout) ======\n")
    exit(0)
serverHost = "127.0.0.1"
serverPort = int(sys.argv[1])
block_duration = int(sys.argv[2])
timeout = int(sys.argv[3])

serverAddress = (serverHost, serverPort)

# define socket for the server side and bind address
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(serverAddress)

# User Data
UserData = LoadUserData('credentials.txt')
if debug : print(UserData)

OnLine_list = []

clientThread_list = []


"""
    Define multi-thread class for client
    This class would be used to define the instance for each connection from each client
    For example, client-1 makes a connection request to the server, the server will call
    class (ClientThread) to define a thread for client-1, and when client-2 make a connection
    request to the server, the server will call class (ClientThread) again and create a thread
    for client-2. Each client will be runing in a separate therad, which is the multi-threading
"""
class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = False
        
        self.block_duration = block_duration
        self.timeout = timeout
        
        print("===== New connection created for: ", clientAddress)
        self.clientAlive = True
        
    def run(self):
        self.message = ''
        
        while self.clientAlive:
            # use recv() to receive message from the client
            data = self.clientSocket.recv(1024)
            self.message = pickle.loads(data)
            
            self.message_content = self.message.getContent()
            self.message_type = self.message.getType()
            
            if debug : print(self.message_content)
            if debug : print(self.message_type)
            if debug : print()
            
            if self.message_type == MessageType.LOGIN:
                if self.process_login() == False:
                    continue

                login_info = (self.username, datetime.datetime.now())
                # add user to the global online list
                OnLine_list.append(login_info)
                
                print("[check] Successfully Login! Time - " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))    # print login finished & time 
                login_success_message = ServerReply("Welcome to the greatest messaging application ever!", ServerReplyType.ANNONCEMENT)
                self.clientSocket.send(pickle.dumps(login_success_message))
            elif self.message_type == MessageType.BROADCAST:
                self.process_broadcast()
                continue
            elif self.message_type == MessageType.WHOELSE:
                continue
            elif self.message_type == MessageType.WHOELSESINCE:
                continue
            elif self.message_type == MessageType.BLOCK:
                continue
            elif self.message_type == MessageType.UNBLOCK:
                continue
            elif self.message_type == MessageType.LOGOUT:
                self.process_logout()
                break
    
    """
        You can create more customized APIs here, e.g., logic for processing user authentication
        Each api can be used to handle one specific function, for example:
        def process_login(self):
            message = 'user credentials request'
            self.clientSocket.send(message.encode())
    """
    def process_login(self):
        if 'username' in self.message_content.keys():
            self.process_login_username()
            return False
        elif 'password' in self.message_content.keys():
            return self.process_login_olduser()
        elif 'newpassword' in self.message_content.keys():
            self.process_login_newuser()
        return True
        
    def process_login_username(self):
        self.username = self.message_content['username']
        
        # refresh the user data before check user
        UserData = LoadUserData('credentials.txt')
        
        # check if username in credential txt
        if self.username in UserData.keys():
            print("[recv] User already exists!! Check password!!")
            # request for password checking
            passwd_request = ServerReply("", ServerReplyType.REQUEST_NEEDPASSWORD)
            self.clientSocket.send(pickle.dumps(passwd_request))
        else:
            print("[recv] New User, please create password!")
            # request for new password
            passwd_request = ServerReply("This is a new user.", ServerReplyType.REQUEST_NEWUSER)
            self.clientSocket.send(pickle.dumps(passwd_request))
            
    def process_login_newuser(self):
        self.passwd = self.message.getContent()['newpassword']
        print("[recv] new password = %s" %self.passwd)
        
        # add new user data into USERDATA and TXT
        AddUserDataToTXT('credentials.txt', {"username":self.username, "password":self.passwd})
        UserData.update({"username":self.username, "password":self.passwd})
        print("[check] New User Added. Successfully Login!")
        
    def process_login_olduser(self):
        self.passwd = self.message.getContent()['password']
        
        # refresh the user data before check password
        UserData = LoadUserData('credentials.txt')
        
        print("[recv] password = %s" %self.passwd)
        if UserData[self.username] == self.passwd:
            print("[check] Password Correct.")
            return True
        else:
            print("[check] Invalid Password. Please Re-type Password.")
            passwd_request = ServerReply("Invalid Password. Please try again.", ServerReplyType.REQUEST_NEEDPASSWORD)
            self.clientSocket.send(pickle.dumps(passwd_request))
            return False
        
        
    def process_broadcast(self):
        for thread in clientThread_list:
            if thread.username != self.username:
                broadcast_message_content = "[broadcast] " + self.username + ": "+ self.message_content["message"]
                broadcast_message = ServerReply(broadcast_message_content, ServerReplyType.ANNONCEMENT)
                thread.clientSocket.send(pickle.dumps(broadcast_message))
        return
    
    def process_logout(self):
        # get logout message, print diconnected announcement
        self.clientAlive = False
        print("===== the user disconnected - ", self.clientAddress)
        # remove user from online list
        for user in OnLine_list[:]:
            if user[0] == self.username:
                OnLine_list.remove(user)
        # broadcast logout message to all unblocked user
        return

print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")


while True:
    serverSocket.listen()
    clientSockt, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSockt)
    # add the new thread to thread_list
    clientThread_list.append(clientThread)
    clientThread.start()