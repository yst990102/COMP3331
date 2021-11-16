from socket import socket
import socket

from Message import Message

if __name__ == "__main__":
    client01 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientaddress01 = ("127.0.0.1", 3000)
    client01.bind(clientaddress01)
    

    print("client01 set up")
    
    client01.listen()
    clientSockt, clientAddress = client01.accept()
    
    while True:
        data = clientSockt.recv(1024)
        receivedMessage = data.decode()
        
        print(f"{receivedMessage}")
        
        message = input("Enter a string : ")
        if message == 'quit':
            break
        client01.sendall(message.encode())
