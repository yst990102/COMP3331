"""
    Code for Multi-Threaded Server
    Python 3
    Usage: python3 TCPserver3.py server_port block_duration timeout
    coding: utf-8
    
    Author: z5192519
"""
from socket import *
from threading import Thread
import sys, select, pickle, datetime, time



from time import sleep
from Message import MessageType, ServerReply, ServerReplyType
from TimeThread import TimeThread
from helperfunctions import AddUserDataToTXT, InitializeBlockerList, LoadUserData


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
timeout_duration = int(sys.argv[3])

serverAddress = (serverHost, serverPort)

# define socket for the server side and bind address
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(serverAddress)

# User Data
UserData = LoadUserData('credentials.txt')

# online_list have all the login message of online_users
# online_list format : [{user: login_time_of_user}, ...]
OnLine_list = []

# loghistory will be similar to online_list, but will not remove user when they logout
# loghistory format : [{user: login_time_of_user}, ...]
Log_history = []

# login_blocked_list have all the users that be banned from login
# login_blocked_list format : [{username : timerThread}, ...]
login_blocked_list = []

# clientThread_list has all the Client Thread that running
# clientThread_list format : [ClientThread01, ClientThread02, ...]
clientThread_list = []

# blocker_list format : {user: people_blocked_by_user, ...}
blocker_list = InitializeBlockerList(UserData)


"""
    Define multi-thread class for client
    This class would be used to define the instance for each connection from each client
    For example, client-1 makes a connection request to the server, the server will call
    class (ClientThread) to define a thread for client-1, and when client-2 make a connection
    request to the server, the server will call class (ClientThread) again and create a thread
    for client-2. Each client will be runing in a separate therad, which is the multi-threading
"""
class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket:socket):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        
        self.attempts = 0
        self.clientAlive = False
        
        print("===== New connection created for: ", clientAddress)
        self.clientAlive = True

    
    def run(self):
        self.message = ''
        
        while self.clientAlive:
            # use recv() to receive message from the client
            try:
                data = self.clientSocket.recv(1024)
                self.message = pickle.loads(data)
            except timeout:
                # auto logout when timeout reached
                print("Socket Timeout. current time == ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                self.process_timeout()
                break
            except EOFError:
                print("Account has been blocked!")
                if debug: print("login_blocked_list == ",login_blocked_list)
                self.process_logout()
                break

            self.message_content = self.message.getContent()
            self.message_type = self.message.getType()
            
            if debug: print("Processing: %s" % self.message_content)
            
            if self.message_type == MessageType.LOGIN:
                # before process login, check the login_block_list , remove all unblocked user
                for (user, timer) in login_blocked_list[:]:
                    if timer.is_alive() == False:
                        login_blocked_list.remove((user, timer))
                
                # if user is still blocked , continue
                is_user_blocked = False
                for (user, timer) in login_blocked_list:
                    self.username = self.message_content['username']
                    if self.username == user:
                        block_message_content = f"You have been incorrect for 3 times. Account blocked for {timer.block_duration} sec."
                        block_message = ServerReply(block_message_content, ServerReplyType.ACCOUNT_BLOCK)
                        self.clientSocket.send(pickle.dumps(block_message))
                        is_user_blocked = True
                if is_user_blocked: continue
                
                # process login
                # 1. when login finished - True
                # 2. when login unfinished - False
                if self.process_login() == False:
                    continue
                else:
                    self.clientSocket.settimeout(timeout_duration)

                    # add user to the global online list
                    login_info = (self.username, datetime.datetime.now())
                    OnLine_list.append(login_info)
                    Log_history.append(login_info)
                    
                    print("[check] Successfully Login! Time - " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))    # print login finished & time 
                    if debug: print("login_blocked_list == ",login_blocked_list)
                    login_success_message = ServerReply("Welcome to the greatest messaging application ever!", ServerReplyType.ANNONCEMENT)
                    self.clientSocket.send(pickle.dumps(login_success_message))
                    
                    # log in broadcast
                    self.process_login_broadcast()
                    continue
            elif self.message_type == MessageType.MESSAGE:
                self.process_message()
                continue
            elif self.message_type == MessageType.BROADCAST:
                self.process_broadcast()
                continue
            elif self.message_type == MessageType.WHOELSE:
                self.process_whoelse()
                continue
            elif self.message_type == MessageType.WHOELSESINCE:
                self.process_whoelsesince()
                continue
            elif self.message_type == MessageType.BLOCK:
                self.process_block()
                continue
            elif self.message_type == MessageType.UNBLOCK:
                self.process_unblock()
                continue
            elif self.message_type == MessageType.LOGOUT:
                self.process_logout()
                continue
    
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
        
        # check if username in credential txt
        if self.username in UserData.keys():
            print("[recv] User already exists!! Check password!!")

            # request for password checking
            passwd_request = ServerReply("This is a old user. ", ServerReplyType.REQUEST_NEEDPASSWORD)
            self.clientSocket.send(pickle.dumps(passwd_request))
        # username is not in credential txt
        else:
            print("[recv] New User, please create password!")
            # request for new password
            passwd_request = ServerReply("This is a new user. ", ServerReplyType.REQUEST_NEWUSER)
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
        
        # print recv message in server
        print("[recv] password = %s" %self.passwd)
        
        # check password correction
        if UserData[self.username] == self.passwd:
            print("[check] Password Correct.")
            return True
        else:
            print("[check] Invalid Password. Please Re-type Password.")
            print("attempts == %d" %self.attempts)
            self.attempts += 1
            if self.attempts == 3:
                # start a timethread for block counting
                timeThread = TimeThread(block_duration)
                login_blocked_list.append((self.username, timeThread))
                timeThread.start()
                
                block_message_content = f"You have been incorrect for 3 times. Account blocked for {timeThread.block_duration} sec."
                block_message = ServerReply(block_message_content, ServerReplyType.ACCOUNT_BLOCK)
                self.clientSocket.send(pickle.dumps(block_message))
            else:
                passwd_request = ServerReply("Invalid Password. Please try again.", ServerReplyType.REQUEST_NEEDPASSWORD)
                self.clientSocket.send(pickle.dumps(passwd_request))
            return False

    def process_login_broadcast(self):
        for thread in clientThread_list:
            if thread.username != self.username and thread.is_alive():
                broadcast_message_content = self.username + " logged in"
                broadcast_message = ServerReply(broadcast_message_content, ServerReplyType.ANNONCEMENT)
                thread.clientSocket.send(pickle.dumps(broadcast_message))
        return

    def process_message(self):
        target_user = self.message_content["user"]
        target_message = self.message_content["message"]
        
        for (user, login_time) in OnLine_list:
            for thread in clientThread_list:
                if thread.username == target_user and thread.is_alive():
                    message_content = f"[message] {self.username} : {target_message}"
                    message_send = ServerReply(message_content, ServerReplyType.ANNONCEMENT)
                    thread.clientSocket.send(pickle.dumps(message_send))
                    return
        return
    
    def process_broadcast(self):
        print("[broadcast] " + self.username + " is broadcasting \"%s\"" %self.message_content["message"])
        for thread in clientThread_list:
            if thread.username != self.username:
                broadcast_message_content = f"[broadcast] {self.username} : " + self.message_content["message"]
                broadcast_message = ServerReply(broadcast_message_content, ServerReplyType.ANNONCEMENT)
                thread.clientSocket.send(pickle.dumps(broadcast_message))
        return
    
    def process_whoelse(self):
        for (username, login_time) in OnLine_list:
            if username != self.username:
                whoelse_messge = ServerReply(username, ServerReplyType.ANNONCEMENT)
                self.clientSocket.send(pickle.dumps(whoelse_messge))
        return
    
    def process_whoelsesince(self):
        time_now = datetime.datetime.now()
        time_now_stamp = time.mktime(time_now.timetuple())
        
        required_time_diff = self.message_content["time"]
        suitable_users = []
        for (username, login_time) in Log_history:
            login_time_stamp = time.mktime(login_time.timetuple())
            if username != self.username:
                if debug: print(f"time_now == {time_now}, time_diff = {(time_now_stamp - login_time_stamp)}")
                if (time_now_stamp - login_time_stamp) < required_time_diff:
                    suitable_users.append(username)
        # deletet all repeat user log
        suitable_users = list(set(suitable_users))
        for username  in suitable_users:
            whoelse_messge = ServerReply(username, ServerReplyType.ANNONCEMENT)
            self.clientSocket.send(pickle.dumps(whoelse_messge))
        return
    
    def process_block(self):
        blocked_user = self.message_content["user"]
        if self.username != blocked_user and blocked_user not in blocker_list[self.username]:
            blocker_list[self.username].append(blocked_user)
            
            blocked_message_content = f"{blocked_user} is blocked."
            blocked_message = ServerReply(blocked_message_content, ServerReplyType.ANNONCEMENT)
            self.clientSocket.send(pickle.dumps(blocked_message))
        else:
            if self.username == blocked_user:
                error_message_content = f"You can't block yourself!"
            elif blocked_user in blocker_list[self.username]:
                error_message_content = f"You have already block {blocked_user}"
            error_message = ServerReply(error_message_content, ServerReplyType.ERROR)
            self.clientSocket.send(pickle.dumps(error_message))
        return
    
    def process_unblock(self):
        unblocked_user = self.message_content["user"]
        if self.username != unblocked_user and unblocked_user in blocker_list[self.username]:
            blocker_list[self.username].remove(unblocked_user)
            
            unblocked_message_content = f"{unblocked_user} is unblocked."
            unblocked_message = ServerReply(unblocked_message_content, ServerReplyType.ANNONCEMENT)
            self.clientSocket.send(pickle.dumps(unblocked_message))
        else:
            if self.username == unblocked_user:
                error_message_content = f"You can't unblock yourself!"
            elif unblocked_user not in blocker_list[self.username]:
                error_message_content = f"You haven't block {unblocked_user}"
            error_message = ServerReply(error_message_content, ServerReplyType.ERROR)
            self.clientSocket.send(pickle.dumps(error_message))
        return
    
    def process_logout(self):
        # get logout message, print diconnected announcement
        self.clientAlive = False
        print("===== the user disconnected - ", self.clientAddress)
        # remove user from online list
        for user in OnLine_list[:]:
            if user[0] == self.username:
                OnLine_list.remove(user)
        # log out broadcast
        self.process_logout_broadcast()
        return

    def process_logout_broadcast(self):
        # broadcast logout message to all unblocked user
        for thread in clientThread_list:
            if thread.username != self.username and thread.is_alive():
                broadcast_message_content = self.username + " logged out"
                broadcast_message = ServerReply(broadcast_message_content, ServerReplyType.ANNONCEMENT)
                thread.clientSocket.send(pickle.dumps(broadcast_message))

    def process_timeout(self):
        # send timeout server reply
        timeout_message = ServerReply("Timeout ! Client has been terminated.", ServerReplyType.TIMEOUT)
        self.clientSocket.send(pickle.dumps(timeout_message))
        # process logout
        self.process_logout()
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