# !/usr/bin/python3
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



from Message import MessageType, ServerMessage, ServerMessageType
from TimeThread import TimeThread
from helperfunctions import AddUserDataToTXT, InitializeBlockerList, InitializeStoredMessageList, LoadUserData


# server print
server_print = 1

# debug
debug = 0


# acquire server host and port from command line parameter
if len(sys.argv) != 4:
    print(len(sys.argv))
    print("\n===== Error usage. Please follow format: (python3 TCPserver3.py server_port block_duration timeout) ======\n")
    exit(0)
serverHost = "localhost"
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
# online_list format : [(user, login_time_of_user), ...]
OnLine_list = []

# loghistory will be similar to online_list, but will not remove user when they logout
# loghistory format : [(user: login_time_of_user), ...]
Log_history = []

# login_blocked_list have all the users that be banned from login
# login_blocked_list format : [(username : timerThread), ...]
login_blocked_list = []

# clientThread_list has all the Client Thread that running
# clientThread_list format : [ClientThread01, ClientThread02, ...]
clientThread_list = []

# blocker_list format : {user: [people_blocked_by_user], ...}
blocker_list = InitializeBlockerList(UserData)

# stored_message_list
# format : {target_user1: [msg1, msg2, ...], targer_user2: [], ...}
stored_message_list = InitializeStoredMessageList(UserData)

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
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        
        self.attempts = 0
        self.login = False
        self.clientAlive = False
        
        if server_print : print("===== New connection created for: ", clientAddress)
        self.clientAlive = True

    
    def run(self):
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        self.message = ''
        while self.clientAlive:
            # use recv() to receive message from the client
            try:
                data = self.clientSocket.recv(1024)
                self.message = pickle.loads(data)
            except timeout:
                # auto logout when timeout reached
                if server_print : print("[Timeout] Current time == ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                self.process_timeout()
                break
            except EOFError or ConnectionResetError:
                if server_print : print(f"===== Connection {self.clientAddress} was shut down.")
                self.process_logout()
                break

            self.message_content = self.message.getContent()
            self.message_type = self.message.getType()
            
            # before process everything , remove all unblocked user
            for (user, timer) in login_blocked_list[:]:
                if timer.is_alive() == False:
                    login_blocked_list.remove((user, timer))

            
            if self.message_type == MessageType.LOGIN_USERNAME:                
                # if user is still blocked , continue
                if self.IsUserAccouBlocked(self.message_content['username']):
                    break
                else:
                    self.process_login()
                    continue
            elif self.message_type == MessageType.LOGIN_PASSWD:
                self.process_login_olduser()
                continue
            elif self.message_type == MessageType.LOGIN_NEWPASSWD:
                self.process_login_newuser()
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
            elif self.message_type == MessageType.STARTPRIVATE:
                if server_print : print(f"[recv] received startprivate message from {self.username}")
                self.process_startprivate()
                continue
            elif self.message_type == MessageType.STOPPRIVATE:
                self.process_stopprivate()
                continue
            elif self.message_type == MessageType.STOPPRIVATE_PRIVATE_STOPPED:
                self.process_stopped_private_feedback()
                continue
            elif self.message_type == MessageType.YES:
                if server_print : print("[Request] Request has been confirmed!")
                # search for requester thread
                for thread in clientThread_list:
                    if thread.login == True:
                        if thread.username == self.message_content['requester']:
                            confirmed_feedback = ServerMessage(f"{self.username} has confirmed your request.", ServerMessageType.ANNONCEMENT)
                            thread.clientSocket.sendall(pickle.dumps(confirmed_feedback))
                            
                            # send feedback to requester
                            requester_feedback = ServerMessage({"target_user": self.username, "private_address":self.message_content['private_address']}, ServerMessageType.SEND_REQUESTER_SOCKET_ADDRESS)
                            thread.clientSocket.sendall(pickle.dumps(requester_feedback))
                            break
                continue
            elif self.message_type == MessageType.NO:
                if server_print : print("[Request] Request has been refused!")
                
                # tell requester that his requeset has been refused.
                requester = self.message_content['requester']
                for thread in clientThread_list:
                    if thread.login == True:
                        if thread.username == requester:
                            refused_feedback = ServerMessage(f"{self.username} has refused your request.", ServerMessageType.ANNONCEMENT)
                            thread.clientSocket.sendall(pickle.dumps(refused_feedback))
                            break
                continue
            elif self.message_type == MessageType.TELL_TARGET_USER_SETUP_PRIVATE_SENDERTHREAD:
                target_username = self.message_content['target_user']
                requester_socket_address = self.message_content['private_address']
                for thread in clientThread_list:
                    if thread.login == True:
                        if thread.username == target_username and thread.is_alive():
                            if self.username not in blocker_list[thread.username]:      # only when you are not in that user's block list
                                ask_message = ServerMessage({"requester":self.username, "private_address":requester_socket_address}, ServerMessageType.SETUP_PRIVATE_SENDERTHREAD)
                                thread.clientSocket.sendall(pickle.dumps(ask_message))
                        
    """
        You can create more customized APIs here, e.g., logic for processing user authentication
        Each api can be used to handle one specific function, for example:
        def process_login(self):
            message = 'user credentials request'
            self.clientSocket.send(message.encode())
    """    
    def process_login(self):
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        self.username = self.message_content['username']
        # if user is already online
        is_user_online = False
        for user in OnLine_list[:]:
            if user[0] == self.username:
                # user is already online
                online_error = ServerMessage(f"{self.username} is already online.", ServerMessageType.ERROR)
                self.clientSocket.sendall(pickle.dumps(online_error))
                is_user_online = True
        if is_user_online == True: return
        
        # check if user is old or new
        # old : ask for passwd, send request_needpassword
        # new : ask for passwd, send request_newuser
        if self.username in UserData.keys():
            if server_print : print("[recv] User already exists!! Check password!!")
            time.sleep(0.01)
            # request for password checking
            passwd_request = ServerMessage("This is a old user. ", ServerMessageType.REQUEST_NEEDPASSWORD)
            self.clientSocket.sendall(pickle.dumps(passwd_request))
        else:
            if server_print : print("[recv] New User, please create password!")
            time.sleep(0.01)
            # request for new password
            passwd_request = ServerMessage("This is a new user. ", ServerMessageType.REQUEST_NEWUSER)
            self.clientSocket.sendall(pickle.dumps(passwd_request))

    def process_login_olduser(self):
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        self.passwd = self.message_content['password']
        
        # print recv message in server
        if server_print : print("[recv] password = %s" %self.passwd)
        
        # check password correction
        if UserData[self.username] == self.passwd:
            if server_print : print("[check] Password Correct.")

            # login_success
            self.process_login_success()
            return
        else:
            if server_print : print("[check] Invalid Password. Please Re-type Password.")
            if debug : print("attempts == %d" %self.attempts)
            
            self.attempts += 1
            if self.attempts == 3:
                # start a timethread for block counting
                timeThread = TimeThread(block_duration)
                login_blocked_list.append((self.username, timeThread))
                timeThread.start()
                
                block_message_content = f"You have been incorrect for 3 times. Account blocked for {timeThread.block_duration} sec."
                block_message = ServerMessage(block_message_content, ServerMessageType.ACCOUNT_BLOCK)
                self.clientSocket.sendall(pickle.dumps(block_message))
            else:
                passwd_request = ServerMessage("Invalid Password. Please try again. ", ServerMessageType.REQUEST_NEEDPASSWORD)
                self.clientSocket.sendall(pickle.dumps(passwd_request))
            return
    
    def process_login_newuser(self):
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        self.passwd = self.message_content['newpassword']
        if server_print : print("[recv] new password = %s" %self.passwd)
        
        # add new user data into USERDATA and TXT
        AddUserDataToTXT('credentials.txt', {"username":self.username, "password":self.passwd})
        UserData = LoadUserData('credentials.txt')
        blocker_list.update({self.username:[]})
        stored_message_list.update({self.username:[]})
        
        if server_print : print("[check] New User Added. Successfully Login!")

        # login_success
        self.process_login_success()
        return

    def process_login_success(self):
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        self.login = True
        self.clientSocket.settimeout(timeout_duration)

        # add user to the global online list
        login_info = (self.username, datetime.datetime.now())
        OnLine_list.append(login_info)
        Log_history.append(login_info)
        
        # print success login in info on server
        if server_print : print("[check] Successfully Login! Time - " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))    # print login finished & time 

        # return welcome message to the client
        login_success_message_content = """
    =========================================================================
    ========== Welcome to the greatest messaging application ever! ==========
    =========================================================================
        """
        login_success_message = ServerMessage(login_success_message_content, ServerMessageType.ANNONCEMENT)
        self.clientSocket.sendall(pickle.dumps(login_success_message))
        
        # return all the stored message to the client        
        if stored_message_list[self.username] != []:
            
            time.sleep(0.01)    # add interval time between continous message sending
            
            stored_split_line1 = ServerMessage("\n************* Here is your stored messages *************", ServerMessageType.ANNONCEMENT)
            self.clientSocket.sendall(pickle.dumps(stored_split_line1))
            
            time.sleep(0.01)    # add interval time between continous message sending
            
            stored_messages = stored_message_list[self.username]
            for stored_message in stored_messages[:]:
                if server_print : print(f"[Loading Stored Message] message content == {stored_message.getContent()}, type == {stored_message.getType()}")
                self.clientSocket.sendall(pickle.dumps(stored_message))
                stored_message_list[self.username].remove(stored_message)   # remove the stored message that have been re-sent
                time.sleep(0.01)    # add interval time between continous message sending
            
            stored_split_line2 = ServerMessage("********************************************************\n", ServerMessageType.ANNONCEMENT)
            self.clientSocket.sendall(pickle.dumps(stored_split_line2))
            time.sleep(0.01)    # add interval time between continous message sending
        
        # log in broadcast
        self.process_login_broadcast()
        return

    def process_login_broadcast(self):
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        for thread in clientThread_list:
            # only tell the online people
            if thread.login == True:
                if thread.username != self.username and thread.is_alive():
                    if self.username not in blocker_list[thread.username]:      # only when you are not in that user's block list
                        broadcast_message_content = self.username + " logged in"
                        broadcast_message = ServerMessage(broadcast_message_content, ServerMessageType.ANNONCEMENT)
                        thread.clientSocket.sendall(pickle.dumps(broadcast_message))
                        time.sleep(0.01)    # add interval time between continous message sending
        return

    def IsUserAccouBlocked(self, checked_user):
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        # if user is still blocked , continue
        is_user_blocked = False
        for (user, timer) in login_blocked_list:
            if checked_user == user:
                block_message_content = f"Too many incorrect password entried. Account blocked for {timer.block_duration} sec."
                block_message = ServerMessage(block_message_content, ServerMessageType.ACCOUNT_BLOCK)
                self.clientSocket.sendall(pickle.dumps(block_message))
                is_user_blocked = True
        return is_user_blocked

    def process_message(self):
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        target_user = self.message_content["user"]
        # validate the targer user
        if target_user not in UserData.keys():
            if server_print : print(f"[Error] : '{target_user}' is not a registered user.")
            target_invalid_content = f"Invalid user. There is no '{target_user}' in registered user."
            target_invalid_message = ServerMessage(target_invalid_content, ServerMessageType.ERROR)
            self.clientSocket.sendall(pickle.dumps(target_invalid_message))
            return
        
        # when you are in the target's block list, you can't send message to your target
        if self.username in blocker_list[target_user]:
            if server_print : print(f"[Announcement] : The requester is blocked by '{target_user}'.")
            stop_sending_content = f"Your message could not be delivered as the recipient has blocked you."
            stop_sending_message = ServerMessage(stop_sending_content, ServerMessageType.ANNONCEMENT)
            self.clientSocket.sendall(pickle.dumps(stop_sending_message))
            return
        else:
            target_message = self.message_content["message"]
            # if the target user is online, loop through the thread_list and send message
            for thread in clientThread_list:
                if thread.login == True:
                    if thread.username == target_user and thread.is_alive():
                        if server_print : print(f"[Messaging] : send '{target_message}' from '{self.username}' to '{target_user}'")
                        message_content = f"[message] {self.username} : {target_message}"
                        message_send = ServerMessage(message_content, ServerMessageType.ANNONCEMENT)
                        thread.clientSocket.sendall(pickle.dumps(message_send))
                        return
            # if the target_user is offline, store the message into stored_message_list['target_user']
            stored_message_content = f"[message] {self.username} : {target_message}"
            message_stored = ServerMessage(stored_message_content, ServerMessageType.ANNONCEMENT)
            stored_message_list[target_user].append(message_stored)
            if server_print : print("[store] Storing message")
            return
    
    def process_broadcast(self):
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        if server_print : print(f"[broadcast] {self.username} is broadcasting {self.message_content['message']}")        
        
        for target_user in UserData.keys():
            # do not send broadcst message to myself
            if target_user == self.username:
                continue
            
            # check if target user is online
            # online: loop through thread_list and send message
            # offline: store the broadcast message into stored_message_list
            
            is_user_online = False
            for online_user in OnLine_list[:]:
                if online_user[0] == target_user:
                    is_user_online = True
                    break
            
            if is_user_online == True:
                if server_print : print(f"[broadcast] {target_user} is currently online")
                # check if self.user is block by target_user
                if self.username in blocker_list[target_user]:      # online but blocked you, return
                    # tell self.user that somebody has blocked you
                    blocked_message_content = "Your message could not be delivered to some recipients"
                    blocked_message = ServerMessage(blocked_message_content, ServerMessageType.ANNONCEMENT)
                    self.clientSocket.sendall(pickle.dumps(blocked_message))
                    continue
                else:                                               # online and not blocked you, send message via thread.socket
                    for thread in clientThread_list:
                        if thread.login == True:
                            if thread.username == target_user:
                                broadcast_message_content = f"[broadcast] {self.username} : " + self.message_content["message"]
                                broadcast_message = ServerMessage(broadcast_message_content, ServerMessageType.ANNONCEMENT)
                                thread.clientSocket.sendall(pickle.dumps(broadcast_message))
                                if debug : print(f"[broadcast] send message '{broadcast_message_content}' to '{target_user}' successfully.")
                                continue
            else:
                if server_print : print(f"[broadcast] '{target_user}' is currently offline")
                if self.username in blocker_list[target_user]:
                    # tell self.user that somebody has blocked you
                    blocked_message_content = "Your message could not be delivered to some recipients"
                    blocked_message = ServerMessage(blocked_message_content, ServerMessageType.ANNONCEMENT)
                    self.clientSocket.sendall(pickle.dumps(blocked_message))
                    continue
                else:
                    global stored_message_list
                    stored_message_content = f"[broadcast] {self.username} : " + self.message_content["message"]
                    message_stored = ServerMessage(stored_message_content, ServerMessageType.ANNONCEMENT)
                    stored_message_list[target_user].append(message_stored)
                    if debug : print(f"[broadcast] store message '{stored_message_content}' for '{target_user}' successfully.")
                    continue
    
    def process_whoelse(self):
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        for (username, login_time) in OnLine_list:
            if username != self.username:
                if self.username not in blocker_list[username]:     # only when you are not in that user's block list
                    whoelse_messge = ServerMessage(username, ServerMessageType.ANNONCEMENT)
                    self.clientSocket.sendall(pickle.dumps(whoelse_messge))
        return
    
    def process_whoelsesince(self):
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        time_now = datetime.datetime.now()
        if server_print : print(f"[whoelsesince] : CurrentTime - {time_now.strftime('%Y-%m-%d %H:%M:%S')}")
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
            if self.username not in blocker_list[username]:     # only when you are not in that user's block list
                whoelse_messge = ServerMessage(username, ServerMessageType.ANNONCEMENT)
                self.clientSocket.sendall(pickle.dumps(whoelse_messge))
        return
    
    def process_block(self):
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        blocked_user = self.message_content["user"]
        if server_print : print(f"[block] {self.username} is blocking {blocked_user}")    # print info on server
        
        # validate the blocked_user
        if blocked_user not in UserData.keys():
            target_invalid_content = f"Invalid user"
            if server_print : print(f"[block] block failed : " + target_invalid_content)  # print info on server

            target_invalid_message = ServerMessage(target_invalid_content, ServerMessageType.ERROR)
            self.clientSocket.sendall(pickle.dumps(target_invalid_message))
            return
        
        # normal case
        if self.username != blocked_user and blocked_user not in blocker_list[self.username]:
            blocker_list[self.username].append(blocked_user)    # append the user from blocker_list
            if server_print : print(f"[block] block success !")                           # print info on server
            if debug : print(f"[block] Current blocker_list == {blocker_list}")    # print info on server
            
            blocked_message_content = f"{blocked_user} is blocked."
            blocked_message = ServerMessage(blocked_message_content, ServerMessageType.ANNONCEMENT)
            self.clientSocket.sendall(pickle.dumps(blocked_message))
        else:
            # you can't block yourself
            if self.username == blocked_user:
                error_message_content = f"You can't block yourself!"
            # you can't block a blocked user
            elif blocked_user in blocker_list[self.username]:
                error_message_content = f"{blocked_user} is already blocked."
            if server_print : print(f"[block] block failed : " + error_message_content)   # print info on server
            
            error_message = ServerMessage(error_message_content, ServerMessageType.ERROR)
            self.clientSocket.sendall(pickle.dumps(error_message))
        return
    
    def process_unblock(self):
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        unblocked_user = self.message_content["user"]
        if server_print : print(f"[unblock] {self.username} is unblocking {unblocked_user}")

        # validate the unblocked_user
        if unblocked_user not in UserData.keys():
            target_invalid_content = f"Invalid user"
            if server_print : print(f"[unblock] unblock failed : " + target_invalid_content)  # print info on server
            
            target_invalid_message = ServerMessage(target_invalid_content, ServerMessageType.ERROR)
            self.clientSocket.sendall(pickle.dumps(target_invalid_message))
            return
        
        # normal case
        if self.username != unblocked_user and unblocked_user in blocker_list[self.username]:
            blocker_list[self.username].remove(unblocked_user)      # remove the user from blocker_list
            if server_print : print(f"[unblock] unblock success !")                           # print info on server
            if debug : print(f"[unblock] Current blocker_list == {blocker_list}")    # print info on server
            
            unblocked_message_content = f"{unblocked_user} is unblocked."
            unblocked_message = ServerMessage(unblocked_message_content, ServerMessageType.ANNONCEMENT)
            self.clientSocket.sendall(pickle.dumps(unblocked_message))
        else:
            # you can't unblock yourself
            if self.username == unblocked_user:
                error_message_content = f"You can't unblock yourself!"
            # you can't unblock a non-blocked user
            elif unblocked_user not in blocker_list[self.username]:
                error_message_content = f"{unblocked_user} was not blocked."
            if server_print : print(f"[unblock] unblock failed : " + error_message_content)   # print info on server
            
            error_message = ServerMessage(error_message_content, ServerMessageType.ERROR)
            self.clientSocket.sendall(pickle.dumps(error_message))
        return
    
    def process_logout(self):
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        # get logout message, print diconnected announcement
        self.clientAlive = False
        if server_print : print(f"===== {self.username} disconnected - {self.clientAddress}")
        logout_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if server_print : print(f"===== Logout Time - {logout_time}")
        
        # remove user from online list
        for user in OnLine_list[:]:
            if user[0] == self.username:
                OnLine_list.remove(user)
                
        # log out broadcast
        self.process_logout_broadcast()
        return

    def process_logout_broadcast(self):
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        # broadcast logout message to all unblocked user
        for thread in clientThread_list:
            # only tell the online people
            if thread.login == True:
                if thread.username != self.username and thread.is_alive():
                    # only announce to the people who did not block you
                    if self.username not in blocker_list[thread.username]:
                        broadcast_message_content = {"logout_user" : self.username}
                        broadcast_message = ServerMessage(broadcast_message_content, ServerMessageType.LOGOUT_ANNOUNCEMENT)
                        thread.clientSocket.sendall(pickle.dumps(broadcast_message))

    def process_timeout(self):
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        # send timeout server reply
        timeout_message = ServerMessage("Timeout ! Client has been terminated.", ServerMessageType.TIMEOUT)
        self.clientSocket.sendall(pickle.dumps(timeout_message))
        # process logout
        self.process_logout()
        return
    
    def process_startprivate(self):
        global UserData, OnLine_list, Log_history, login_blocked_list, clientThread_list, blocker_list, stored_message_list
        
        # check if target user blocks the requester
        
        target_user = self.message_content["user"]
        for thread in clientThread_list:
            if thread.login == True:
                if thread.username == target_user and thread.is_alive():
                    if server_print : print(f"[request] {self.username} Request {thread.username} for private connection.")
                    
                    # anouncement for start private request
                    startprivate_announcement = ServerMessage(f"{self.username} would like to private message.", ServerMessageType.ANNONCEMENT)
                    thread.clientSocket.sendall(pickle.dumps(startprivate_announcement))
                    
                    time.sleep(0.01)
                    
                    startprivate_message = ServerMessage({'requester':self.username}, ServerMessageType.ASK_FOR_PRIVATE_CONNECTION)
                    thread.clientSocket.sendall(pickle.dumps(startprivate_message))
                    
                    return
        # cannot find target user in thread_list, return target offline error
        if server_print : print(f"[Error] Cannot send request to '{target_user}', target user is offline.")
        offline_error_message = ServerMessage(f"'{target_user}'' is currenly offline.", ServerMessageType.ERROR)
        self.clientSocket.sendall(pickle.dumps(offline_error_message))

        return
    
    def process_stopprivate(self):
        target_user = self.message_content['user']
        deluser = self.message_content['deluser']
        for thread in clientThread_list:
            if thread.login == True:
                if thread.username == target_user and thread.is_alive():
                    stopprivate_message = ServerMessage({"deluser": deluser}, ServerMessageType.STOP_AND_DELETE_PRIVATE)
                    thread.clientSocket.sendall(pickle.dumps(stopprivate_message))
                    return
        # can not execute the stopprivate from requester
        if server_print : print(f"[Error] : Can not execute the stopprivate from requester.")
        error_message_content = f"Stop private messaging with '{target_user}' can not be executed."
        error_message = ServerMessage(error_message_content, ServerMessageType.ERROR)
        self.clientSocket.sendall(pickle.dumps(error_message))
        return
    
    def process_stopped_private_feedback(self):
        feedback_user = self.message_content['deleteduser']
        for thread in clientThread_list:
            if thread.login == True:
                if thread.username == feedback_user and thread.is_alive():
                    stopped_confirm_message_content = f"Your Private Messaging with {self.username} has been terminated."
                    stopped_confirm_message = ServerMessage(stopped_confirm_message_content, ServerMessageType.STOPPED_PRIVATE_CONFIRM)
                    thread.clientSocket.sendall(pickle.dumps(stopped_confirm_message))
                    return
        error_message_content = f"Stop private messaging confirmation can not be send back to {feedback_user}"
        error_message = ServerMessage(error_message_content, ServerMessageType.ERROR)
        self.clientSocket.sendall(pickle.dumps(error_message))
        return
    
    
if server_print : print("\n===== Server is running =====")
if server_print : print("===== Waiting for connection request from clients...=====")


while True:
    serverSocket.listen()
    clientSockt, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSockt)
    # add the new thread to thread_list
    clientThread_list.append(clientThread)
    clientThread.start()