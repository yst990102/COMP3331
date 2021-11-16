from socket import socket
import socket

if __name__ == "__main__":
    client02 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientaddress02 = ("localhost", 3001)
    client02.bind(clientaddress02)

    clientaddress01 = ("localhost", 56126)
    client02.connect(clientaddress01)
    
    while True:
        message = input("Enter a string : ")
        if message == 'quit':
            break
        client02.sendall(message.encode())
        
        data = clientSockt.recv(1024)
        receivedMessage = data.decode()
        
        print(f"{receivedMessage}")
    
    client02.close()