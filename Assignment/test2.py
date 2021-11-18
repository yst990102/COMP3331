# !/usr/bin/python3
from socket import socket
import socket
from time import sleep

if __name__ == "__main__":
    client02 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientaddress02 = ("127.0.0.1", 13017)
    client02.bind(clientaddress02)
    
    client02.listen()
    client1_socket, client1_address = client02.accept()
    
    print("connection set up")

    data = client1_socket.recv(1024)
    print(data.decode())

    sleep(1)
    
    client1_socket.send("fuck u 2, 3311".encode())
    
    print(client02.getsockname())
    print(client1_socket.getsockname())
    
    client02.close()
    