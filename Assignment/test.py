from datetime import datetime
from socket import socket
import socket
from time import sleep, mktime
from Message import Message

if __name__ == "__main__":
    # client01 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # clientaddress01 = ("127.0.0.1", 13005)
    # client01.bind(clientaddress01)
    
    # client01.connect(("127.0.0.1", 13017))
    
    # print("connection set up")
    
    # sleep(1)
    
    # client01.send("fuck u 3331".encode())
    
    # data = client01.recv(1024)
    # print(data.decode())
    
    # sleep(1)
    
    # print(client01.getsockname())
    
    # client01.close()
    
    time1 = datetime.now()
    print(time1)
    print(mktime(time1.timetuple()))
    
    sleep(2)
    time2 = datetime.now()
    print(time2)
    print(mktime(time2.timetuple()))