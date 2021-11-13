def LoadUserData(filename):
    UserDataFile = open(filename, 'r')
    UserData = []
    for DataLine in UserDataFile:
        [username, password] = DataLine.split(" ")
        UserData.append({username:password})
    print(UserData)
    UserDataFile.close()
    return UserData

def CheckUserNameWithPassword(username, password):
    credential = open('credentials.txt','r')
    try:
        for line in credential:
            print(line)
    finally:
        credential.close()
    return

def MessageFormatChecker(message, message_type):
    

if __name__ == '__main__':
    LoadUserData('credentials1.txt')
    # CheckUserNameWithPassword('hans', 'falcon*solo')