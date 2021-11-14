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

def MessageContentByType(input_message:str):
    input_list = input_message.split(" ")
    message_type = StringToMessageType(input_list[0])
    
    if message_type == MessageType.MESSAGE:
        user = input_list[1]
        message = " ".join(input_list[2:])
        return [{"user":user, "message":message}, message_type]
    elif message_type == MessageType.BROADCAST:
        message = " ".join(input_list[1:])
        return [{"message":message}, message_type]
    elif message_type == MessageType.WHOELSE:
        return [{}, message_type]
    elif message_type == MessageType.WHOELSESINCE:
        time = int(input_list[1])
        return [{"time":time}, message_type]
    elif message_type == MessageType.BLOCK:
        user = input_list[1]
        return [{"user":user}, message_type]
    elif message_type == MessageType.UNBLOCK:
        user = input_list[1]
        return [{"user":user}, message_type]
    elif message_type == MessageType.LOGOUT:
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
    else:
        return MessageType.NOCOMMAND
    

if __name__ == '__main__':
    LoadUserData('credentials1.txt')
    # CheckUserNameWithPassword('hans', 'falcon*solo')