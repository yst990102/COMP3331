# !/usr/bin/python3
from Message import MessageType


def LoadUserData(filename):
    UserDataFile = open(filename, 'r')
    UserData = {}
    for DataLine in UserDataFile:
        [username, password] = DataLine.split(" ")
        password = password.replace('\n', '')
        UserData.update({username:password})
    UserDataFile.close()
    return UserData

def AddUserDataToTXT(filename, userdata):
    UserDataFile = open(filename, 'a')
    UserDataFile.write(userdata['username'] + " " + userdata['password'] + "\n")
    UserDataFile.close()
    return

def InitializeBlockerList(userdata:dict):
    blocker_list = {}
    for user in userdata.keys():
        blocker_list.update({user:[]})
    return blocker_list

def InitializeStoredMessageList(userdata:dict):
    stored_message_list = {}
    for user in userdata.keys():
        stored_message_list.update({user:[]})
    return stored_message_list

def MessageContentByType(input_message:str):
    input_list = input_message.split(" ")
    input_list = list(filter(None, input_list)) # remove none and empty string in list
    
    message_type = StringToMessageType(input_list[0])
    
    if message_type == MessageType.MESSAGE:
        # argument error
        if len(input_list) < 3:
            return [{}, MessageType.ARGUMENT_ERROR]

        user = input_list[1]
        message = " ".join(input_list[2:])
        return [{"user":user, "message":message}, message_type]
    elif message_type == MessageType.BROADCAST:
        # argument error
        if len(input_list) < 2:
            return [{}, MessageType.ARGUMENT_ERROR]
        
        message = " ".join(input_list[1:])
        return [{"message":message}, message_type]
    elif message_type == MessageType.WHOELSE:
        # argument error
        if len(input_list) != 1:
            return [{}, MessageType.ARGUMENT_ERROR]
        
        return [{}, message_type]
    elif message_type == MessageType.WHOELSESINCE:
        # argument error
        if len(input_list) != 2:
            return [{}, MessageType.ARGUMENT_ERROR]
        
        time = int(input_list[1])
        return [{"time":time}, message_type]
    elif message_type == MessageType.BLOCK:
        # argument error
        if len(input_list) != 2:
            return [{}, MessageType.ARGUMENT_ERROR]
        
        user = input_list[1]
        return [{"user":user}, message_type]
    elif message_type == MessageType.UNBLOCK:
        # argument error
        if len(input_list) != 2:
            return [{}, MessageType.ARGUMENT_ERROR]
        
        user = input_list[1]
        return [{"user":user}, message_type]
    elif message_type == MessageType.LOGOUT:
        # argument error
        if len(input_list) != 1:
            return [{}, MessageType.ARGUMENT_ERROR]
        
        return [{}, message_type]
    elif message_type == MessageType.STARTPRIVATE:
        # argument error
        if len(input_list) != 2:
            return [{}, MessageType.ARGUMENT_ERROR]
        
        user = input_list[1]
        return [{"user":user}, message_type]
    elif message_type == MessageType.PRIVATE:
        # argument error
        if len(input_list) < 3:
            return [{}, MessageType.ARGUMENT_ERROR]
        
        user = input_list[1]
        message = " ".join(input_list[2:])
        return [{"user":user, "message":message}, message_type]
    elif message_type == MessageType.STOPPRIVATE:
        # argument error
        if len(input_list) != 2:
            return [{}, MessageType.ARGUMENT_ERROR]
        
        user = input_list[1]
        return [{"user":user}, message_type]
    elif message_type == MessageType.YES:
        # argument error
        if len(input_list) != 1:
            return [{}, MessageType.ARGUMENT_ERROR]
        
        return [{}, message_type]
    elif message_type == MessageType.NO:
        # argument error
        if len(input_list) != 1:
            return [{}, MessageType.ARGUMENT_ERROR]
        
        return [{}, message_type]
    elif message_type == MessageType.NOCOMMAND:
        return [{}, message_type]
        

def StringToMessageType(string:str):
    if string == "message":
        return MessageType.MESSAGE
    elif string == "broadcast":
        return MessageType.BROADCAST
    elif string == "whoelse":
        return MessageType.WHOELSE
    elif string == "whoelsesince":
        return MessageType.WHOELSESINCE
    elif string == "block":
        return MessageType.BLOCK
    elif string == "unblock":
        return MessageType.UNBLOCK
    elif string == "logout":
        return MessageType.LOGOUT
    elif string == "startprivate":
        return MessageType.STARTPRIVATE
    elif string == "private":
        return MessageType.PRIVATE
    elif string == "stopprivate":
        return MessageType.STOPPRIVATE
    elif string == "y":
        return MessageType.YES
    elif string == "n":
        return MessageType.NO
    else:
        return MessageType.NOCOMMAND
    

if __name__ == '__main__':
    LoadUserData('credentials1.txt')
    # CheckUserNameWithPassword('hans', 'falcon*solo')