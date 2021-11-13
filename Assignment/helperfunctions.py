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

if __name__ == '__main__':
    LoadUserData('credentials1.txt')
    # CheckUserNameWithPassword('hans', 'falcon*solo')